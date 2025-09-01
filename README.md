# Slooze Take‑Home Challenge — Data Engineering (B2B Crawler + EDA)

Quickstart:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python -m src.cli crawl --site both --max-pages 2 --out data/raw/products.jsonl
python -m src.cli clean --inp data/raw/products.jsonl --out data/clean/products.csv
python -m src.cli eda --inp data/clean/products.csv
```
