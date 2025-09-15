"""Data loading and batching utilities (loadData/data_loader.py).

Provides:
- load_data(file_path): load only required columns (id,text) from CSV.
- prepare_data_for_upsert(df, batch_size): yield batches of (id, text, metadata_dict).
"""
from __future__ import annotations
import pandas as pd
from typing import Generator, List, Tuple, Dict, Any


def load_data(file_path: str) -> pd.DataFrame:
    """Load only 'id' and 'text' columns for efficiency; drop rows missing either."""
    df = pd.read_csv(file_path, usecols=["id", "text"])
    df = df.dropna(subset=["id", "text"])  # ensure critical columns present
    return df


def prepare_data_for_upsert(
    df: pd.DataFrame,
    batch_size: int,
) -> Generator[List[Tuple[str, str, Dict[str, Any]]], None, None]:
    """Yield batches of (id, raw_text, metadata) tuples ready for embedding & upsert."""
    batch: List[Tuple[str, str, Dict[str, Any]]] = []
    for row in df.itertuples(index=False):
        rid = str(getattr(row, "id"))
        text: str = getattr(row, "text", "")
        metadata = {"text": text[:512], "length": len(text)}
        batch.append((rid, text, metadata))
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
