import json, csv, pathlib

BASE_RELATIVE_JSONL = pathlib.Path("semanticAnalysis/generateData/data/chandigarh_roads_sample.jsonl")
BASE_RELATIVE_CSV = pathlib.Path("semanticAnalysis/generateData/data/chandigarh_roads_sample.csv")


def load_segments(path: str | None = None):
    """Load road segment records from JSONL (preferred) or CSV.
    Returns list of dicts. Minimal parsing; assumes file is well-formed.
    """
    if path:
        candidate = pathlib.Path(path)
    else:
        candidate = BASE_RELATIVE_JSONL if BASE_RELATIVE_JSONL.exists() else BASE_RELATIVE_CSV

    if not candidate.exists():
        raise FileNotFoundError(f"Dataset file not found: {candidate}")

    records: list[dict] = []
    if candidate.suffix == ".jsonl":
        with candidate.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                records.append(json.loads(line))
    else:  # CSV fallback
        with candidate.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert basic numerics if present
                for k in ["id","distance_m","incident_count","safety_score"]:
                    if k in row and row[k] != "":
                        try:
                            row[k] = float(row[k]) if k != "id" else int(row[k])
                        except ValueError:
                            pass
                records.append(row)
    return records
