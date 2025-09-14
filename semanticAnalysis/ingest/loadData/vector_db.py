from pinecone import Pinecone, ServerlessSpec
from config import PINECONE_API_KEY, PINECONE_ENV  # type: ignore


def init_pinecone():
    return Pinecone(api_key=PINECONE_API_KEY)


def create_index_if_not_exists(pc, index_name: str, dimension: int):
    if index_name not in [i["name"] for i in pc.list_indexes()]:
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=PINECONE_ENV or "us-east-1")
        )
    return pc.Index(index_name)


def upsert_vectors(index, data):
    """Upsert list of (id, vector) or (id, vector, metadata)."""
    formatted = []
    for item in data:
        if len(item) == 3:
            vid, vec, meta = item
            formatted.append({"id": vid, "values": vec, "metadata": meta})
        else:
            vid, vec = item
            formatted.append({"id": vid, "values": vec})
    index.upsert(vectors=formatted)
