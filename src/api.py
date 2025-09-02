# src/api.py
import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from src.paths import RAW_JSONL, CLEAN_CSV

app = FastAPI(title="Slooze B2B Crawler API")

def _run(args: list[str]) -> None:
    p = subprocess.run(args, capture_output=True, text=True)
    if p.returncode != 0:
        raise HTTPException(status_code=500, detail=p.stderr or "Command failed")

@app.post("/run")
def run(site: str = "both", pages: int = 2):
    _run(["python", "-m", "src.cli", "crawl", "--site", site, "--max-pages", str(pages), "--out", str(RAW_JSONL)])
    _run(["python", "-m", "src.cli", "clean", "--inp", str(RAW_JSONL), "--out", str(CLEAN_CSV)])
    _run(["python", "-m", "src.cli", "eda", "--inp", str(CLEAN_CSV)])
    return {"ok": True, "raw": str(RAW_JSONL), "clean": str(CLEAN_CSV)}

@app.get("/download/raw")
def download_raw():
    if not RAW_JSONL.exists():
        raise HTTPException(404, "raw not found")
    return FileResponse(RAW_JSONL, filename="products.jsonl", media_type="application/json")

@app.get("/download/clean")
def download_clean():
    if not CLEAN_CSV.exists():
        raise HTTPException(404, "clean not found")
    return FileResponse(CLEAN_CSV, filename="products.csv", media_type="text/csv")
