import time
import pandas as pd
import requests
from pathlib import Path
import os

# Resolve project root depending on runtime (local vs Docker)
if os.getenv("DATA_DIR"):
    PROJECT_ROOT = Path(os.getenv("DATA_DIR"))
else:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Path to input CSV
if os.getenv("DATA_DIR"):
    CSV_PATH = PROJECT_ROOT / "input" / "data.csv"
else:
    CSV_PATH = PROJECT_ROOT / "data" / "input" / "data.csv"

# Target Ingestion API
INGEST_URL = os.getenv("INGEST_URL", "http://localhost:8000/ingest")

# Delay between events to simulate streaming
DELAY_SECONDS = 1


def main():
    print("Loading CSV data...")

    df = pd.read_csv(CSV_PATH, encoding="cp1252")
    print(f"Loaded {len(df)} rows")

    for index, row in df.iterrows():
        event = {
            "event_type": "ecommerce_transaction",
            "payload": row.to_dict()
        }

        try:
            response = requests.post(
                INGEST_URL,
                json=event,
                timeout=10
            )

            if response.status_code == 200:
                print(f"Sent event {index + 1}")
            else:
                print(
                    f"Failed event {index + 1}: "
                    f"{response.status_code} - {response.text}"
                )

        except Exception as e:
            print(f"Error sending event {index + 1}: {e}")

        time.sleep(DELAY_SECONDS)


if __name__ == "__main__":
    main()
