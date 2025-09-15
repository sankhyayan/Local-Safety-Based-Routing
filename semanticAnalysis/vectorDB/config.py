"""Configuration module for ingestion pipeline (loadData/config.py).
Loads environment variables via python-dotenv and exposes constants.
"""
from __future__ import annotations
import os
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENV = os.getenv("PINECONE_ENV", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "road-segments-index")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
INGEST_LIMIT = int(os.getenv("INGEST_LIMIT", "100"))
TEXT_TRUNCATE_LEN = int(os.getenv("TEXT_TRUNCATE_LEN", "1200"))

JSONL_PATH = os.getenv(
    "SEGMENTS_JSONL",
    "semanticAnalysis/generateData/data/chandigarh_roads_sample.jsonl",
)
CSV_PATH = os.getenv(
    "SEGMENTS_CSV",
    "D:/Thesis/Safety Route/semanticAnalysis/generateData/data/chandigarh_roads_sample.csv",
)

if not PINECONE_API_KEY:
    raise RuntimeError("PINECONE_API_KEY is required for ingestion.")
