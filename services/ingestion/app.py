from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import json
from pathlib import Path
import os

app = FastAPI(title="Ingestion Service")

# Project root: .../de-portfolio
DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))
RAW_DIR = DATA_DIR / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

class Event(BaseModel):
    event_type: str
    payload: dict

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/ingest")
def ingest_event(event: Event):
    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%S%f")
    filename = f"{ts}_{event.event_type}.json"
    filepath = RAW_DIR / filename

    with filepath.open("w", encoding="utf-8") as f:
        json.dump(event.model_dump(), f, ensure_ascii=False)

    return {"status": "stored", "file": filename}
