"""Main ingestion orchestrator for semanticAnalysis.vectorDB.

Usage:
  1) Preferred (module execution):
       python -m semanticAnalysis.vectorDB.main_ingestion
  2) Direct script path (fallback adjusts sys.path automatically):
       python semanticAnalysis/vectorDB/main_ingestion.py

Loads road segment CSV, embeds text with SentenceTransformer, and upserts to Pinecone.
"""
from __future__ import annotations
import os
import sys
from typing import List, Dict, Any

# Fallback to ensure package imports work when run as a script
if __package__ is None or __package__ == "":
    this_dir = os.path.dirname(os.path.abspath(__file__))
    semantic_root = os.path.dirname(this_dir)          # semanticAnalysis/vectorDB -> semanticAnalysis
    project_root = os.path.dirname(semantic_root)      # project root
    if project_root not in sys.path:
        sys.path.append(project_root)
    __package__ = "semanticAnalysis.vectorDB"

from sentence_transformers import SentenceTransformer  # type: ignore
from pinecone import Pinecone  # type: ignore

from .config import (
    PINECONE_INDEX_NAME,
    EMBEDDING_MODEL_NAME,
    INGEST_LIMIT,
    TEXT_TRUNCATE_LEN,
    CSV_PATH,
)
from .dataIngestion.vector_db import init_pinecone, create_index_if_not_exists, upsert_vectors
from .dataIngestion.metadata import build_metadata
from .dataLoading.data_loader import load_data


def embed_texts(model: SentenceTransformer, texts: List[str]):
    return model.encode(texts, show_progress_bar=False, batch_size=32, convert_to_numpy=True)


def main() -> None:
    print("[Ingestion] Starting ingestion pipeline...")
    df = load_data(CSV_PATH)
    if df.empty:
        print(f"[Ingestion] No data loaded from '{CSV_PATH}'. Exiting.")
        return

    if INGEST_LIMIT and len(df) > INGEST_LIMIT:
        df = df.head(INGEST_LIMIT)
        print(f"[Ingestion] Truncated dataset to first {INGEST_LIMIT} rows.")

    # Initialize Pinecone and ensure index exists
    pc: Pinecone = init_pinecone()
    create_index_if_not_exists(pc, PINECONE_INDEX_NAME, dimension=384)  # MiniLM-L6-v2 dimension
    index = pc.Index(PINECONE_INDEX_NAME)

    # Load embedding model
    print(f"[Ingestion] Loading embedding model '{EMBEDDING_MODEL_NAME}' ...")
    embed_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    # Build records list (simulate richer metadata if needed later)
    records: List[Dict[str, Any]] = []
    for row in df.itertuples(index=False):
        records.append({
            "id": str(getattr(row, "id")),
            "text": getattr(row, "text"),
            # Placeholders for optional fields if later extended
            "road_class": None,
            "surface": None,
            "weather": None,
            "incident_count": None,
            "safety_score": None,
        })

    # Prepare embedding inputs
    texts = [r["text"] for r in records]
    print(f"[Ingestion] Embedding {len(texts)} texts...")
    embeddings = embed_texts(embed_model, texts)

    vectors = []
    for rec, emb in zip(records, embeddings):
        meta = build_metadata(rec, rec["text"], TEXT_TRUNCATE_LEN)
        vectors.append((rec["id"], emb.tolist(), meta))

    print(f"[Ingestion] Upserting {len(vectors)} vectors to index '{PINECONE_INDEX_NAME}' ...")
    upsert_vectors(index, vectors)
    print("[Ingestion] Done.")


if __name__ == "__main__":  # pragma: no cover
    main()
