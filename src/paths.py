# src/paths.py
import os
from pathlib import Path

# persistent data base dir (Render disk mounts here)
BASE = Path(os.getenv("DATA_DIR", "data")).resolve()
RAW_DIR = BASE / "raw"
CLEAN_DIR = BASE / "clean"
EDA_DIR = BASE / "eda"

# charts; fine to live in app image path
ART_DIR = Path(os.getenv("ART_DIR", "artifacts/eda")).resolve()

for d in (RAW_DIR, CLEAN_DIR, EDA_DIR, ART_DIR):
    d.mkdir(parents=True, exist_ok=True)

# canonical files
RAW_JSONL = RAW_DIR / "products.jsonl"
CLEAN_CSV = CLEAN_DIR / "products.csv"
