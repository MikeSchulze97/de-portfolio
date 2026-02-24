import time
import pandas as pd
import requests
from pathlib import Path
import os

DATA_DIR = Path(os.getenv("DATA_DIR", "/data"))
CSV_PATH = Path(os.getenv("CSV_PATH", str(DATA_DIR / "input" / "data.csv")))
INGEST_URL = os.getenv("INGEST_URL", "http://ingestion:8000/ingest")
DELAY_SECONDS = int(os.getenv("DELAY_SECONDS", "1"))

def main() -> None:
    print(f"[Generator] CSV_PATH={CSV_PATH}")
    print(f"[Generator] INGEST_URL={INGEST_URL}")
    print(f"[Generator] DELAY_SECONDS={DELAY_SECONDS}")

    df = pd.read_csv(CSV_PATH, encoding="cp1252")
    print(f"[Generator] Loaded rows: {len(df)}")

    for idx, row in df.iterrows():
        event = {"event_type": "ecommerce_transaction", "payload": row.to_dict()}

        try:
            r = requests.post(INGEST_URL, json=event, timeout=10)
            if r.status_code == 200:
                print(f"[Generator] Sent event {idx + 1}")
            else:
                print(f"[Generator] Failed event {idx + 1}: {r.status_code} - {r.text}")
        except Exception as e:
            print(f"[Generator] Error sending event {idx + 1}: {e}")

        time.sleep(DELAY_SECONDS)

if __name__ == "__main__":
    main()