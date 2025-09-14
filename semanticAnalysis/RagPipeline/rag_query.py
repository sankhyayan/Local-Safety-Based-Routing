"""Minimal RAG script (embedding -> vector search -> generation) using Hugging Face Hub.

Usage (PowerShell):
  $env:PINECONE_API_KEY = "<pinecone_key>"
  $env:PINECONE_INDEX_NAME = "safety-route-demo"
  $env:HF_MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"
  $env:HUGGINGFACE_API_TOKEN = "<hf_token>"
  python semanticAnalysis/rag_query.py --query "Which segment is safest?"
"""

import os
import argparse
from typing import List, Dict, Any

from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from huggingface_hub import InferenceClient


def load_env() -> dict:
    load_dotenv()
    cfg = {
        "pinecone_api_key": os.getenv("PINECONE_API_KEY"),
        "pinecone_index": os.getenv("PINECONE_INDEX_NAME", "safety-route-demo"),
        "hf_model": os.getenv("HF_MODEL_NAME"),
        # Support either HUGGINGFACE_API_TOKEN or HF_TOKEN (chat boilerplate uses HF_TOKEN)
        "hf_token": os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_API_TOKEN"),
        "k": int(os.getenv("RAG_TOP_K", "5")),
        "max_new_tokens": int(os.getenv("GEN_MAX_NEW_TOKENS", "160")),
        "temperature": float(os.getenv("GEN_TEMPERATURE", "0.7")),
    }
    missing = [k for k,v in cfg.items() if k in {"pinecone_api_key","hf_model","hf_token"} and not v]
    if missing:
        raise SystemExit(f"Missing required environment variables for: {', '.join(missing)}")
    return cfg


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Minimal RAG query")
    p.add_argument("--query", required=False, help="User question")
    p.add_argument("--k", type=int, help="Override top-k retrieval")
    return p.parse_args()


def get_query(args: argparse.Namespace) -> str:
    if args.query:
        return args.query
    # fallback to interactive input
    try:
        return input("Enter your question: ").strip()
    except KeyboardInterrupt:
        raise SystemExit(0)


def retrieve(index, embed_model: SentenceTransformer, query: str, k: int):
    q_emb = embed_model.encode(query).tolist()
    resp = index.query(vector=q_emb, top_k=k, include_metadata=True)
    matches = resp.get("matches", []) if isinstance(resp, dict) else getattr(resp, "matches", [])
    context_texts: List[str] = []
    rows: List[str] = []
    metas: Dict[str, Dict[str, Any]] = {}
    for m in matches:
        meta = m.get("metadata") if isinstance(m, dict) else getattr(m, "metadata", {})
        mid = m.get("id") if isinstance(m, dict) else getattr(m, "id", "?")
        score = m.get("score") if isinstance(m, dict) else getattr(m, "score", None)
        if isinstance(meta, dict):
            metas[str(mid)] = meta
        text = meta.get("text") if isinstance(meta, dict) else None
        if text:
            context_texts.append(text)
        rows.append(f"- id={mid} score={score:.4f}" if isinstance(score,(int,float)) else f"- id={mid} score=?")
    return context_texts, rows, metas



 # (Removed numeric deterministic selection; always using LLM)


def build_system_message(context_chunks: List[str]) -> str:
    # Optional: extract simple lines with safety scores
    # (Keeps current approach; can be expanded if you store IDs separately)
    ctx = "\n---\n".join(context_chunks)
    return (
        "You are a retrieval-augmented assistant.\n"
        "Rules:\n"
        "1. Use ONLY the context.\n"
        "2. If the user asks for a score that is not exactly present, pick the segment whose safety_score is numerically closest and state it.\n"
        "3. If you cannot even determine an approximate answer, reply exactly: I don't know.\n"
        "4. Do not invent segment IDs.\n\n"
        f"Context:\n{ctx}\n\nQuestion:"
    )


def generate_chat(client: InferenceClient, model: str, system_msg: str, user_query: str, max_new_tokens: int, temperature: float) -> str:
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_query},
        ],
        max_tokens=max_new_tokens,
        temperature=temperature,
    )
    try:
        content = completion.choices[0].message.get("content")  # newer SDK style
    except Exception:
        content = str(completion)
    content = (content or "").strip()
    if not content:
        return "I don't know"
    # Enforce instruction: if model ignored constraint and hallucinated, user can post-filter later.
    return content


def main():
    cfg = load_env()
    args = parse_args()
    query = get_query(args)
    if not query:
        raise SystemExit("Empty query.")

    k = args.k or cfg["k"]

    # init services
    pc = Pinecone(api_key=cfg["pinecone_api_key"])
    index = pc.Index(cfg["pinecone_index"])
    embed_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    client = InferenceClient(provider="hf-inference", api_key=cfg["hf_token"], timeout=90)

    # retrieval
    context_chunks, rows, metas = retrieve(index, embed_model, query, k)
    if not context_chunks:
        print("No context found in vector store.")
        return

    print("\nTop Matches:\n" + "\n".join(rows))
    print("\nRetrieved Chunks (truncated):")
    for i, chunk in enumerate(context_chunks, 1):
        preview = (chunk[:240] + "...") if len(chunk) > 240 else chunk
        print(f"[{i}] {preview}")
    system_msg = build_system_message(context_chunks)
    answer = generate_chat(
        client,
        cfg["hf_model"],
        system_msg,
        query,
        cfg["max_new_tokens"],
        cfg["temperature"],
    )
    if len(answer) > 2000:
        answer = answer[:2000] + "..."

    print("\nAnswer:\n")
    print(answer)


if __name__ == "__main__":
    main()


