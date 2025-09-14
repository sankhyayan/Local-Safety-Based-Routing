from sentence_transformers import SentenceTransformer
import os

from config import PINECONE_INDEX_NAME  # type: ignore
from loadData.vector_db import init_pinecone, create_index_if_not_exists, upsert_vectors  # type: ignore

from loadData.load_data import load_segments  # type: ignore


def main():
    limit = int(os.getenv("INGEST_LIMIT", "100"))
    records = load_segments()[:limit]
    model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    texts = [r.get("text") or f"Segment {r['id']} {r.get('road_class','')}" for r in records]
    embeddings = model.encode(texts)

    pc = init_pinecone()
    index = create_index_if_not_exists(pc, PINECONE_INDEX_NAME, embeddings.shape[1])

    vectors = []
    for rec, emb in zip(records, embeddings):
        rid = str(rec.get("id"))
        text = rec.get("text", "")
        meta = {
            "text": text[:512],  # truncate long
            "len": len(text),
            "road_class": rec.get("road_class"),
            "surface": rec.get("surface"),
            "weather": rec.get("weather"),
            "incidents": rec.get("incident_count"),
            "safety_score": rec.get("safety_score"),
        }
        vectors.append((rid, emb.tolist(), meta))
    upsert_vectors(index, vectors)

    print(f"Upserted {len(vectors)} road segment vectors into '{PINECONE_INDEX_NAME}'.")


if __name__ == "__main__":
    main()
