"""Metadata construction helpers (loadData/metadata.py).
Provides build_metadata() to centralize how we attach fields to each vector.
"""
from __future__ import annotations
from typing import Dict, Any

def build_metadata(rec: dict, text: str, truncate_len: int) -> Dict[str, Any]:
    base = {
        "text": text[:truncate_len],
        "len": len(text),
        "road_class": rec.get("road_class"),
        "surface": rec.get("surface"),
        "weather": rec.get("weather"),
        "incidents": rec.get("incident_count"),
        "safety_score": rec.get("safety_score"),
    }
    # Pinecone requires values to be str/number/bool/list(str); drop None
    return {k: v for k, v in base.items() if v is not None}
