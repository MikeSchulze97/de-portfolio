from pathlib import Path
import json
import os
import argparse
import psycopg2


def project_root() -> Path:
    # Keep consistent with your existing pattern
    data_dir = os.getenv("DATA_DIR")
    if data_dir:
        return Path(data_dir).parent
    return Path(__file__).resolve().parents[2]


def aggregated_dir(root: Path) -> Path:
    return root / "data" / "aggregated"


def iter_event_counts_files(base: Path):
    # data/aggregated/date=YYYY-MM-DD/hour=HH/event_counts.json
    yield from base.glob("date=*/hour=*/event_counts.json")


def parse_partition_file(path: Path):
    payload = json.loads(path.read_text(encoding="utf-8"))

    date_str = payload.get("date")
    hour_str = payload.get("hour")
    counts = payload.get("event_type_counts", {})

    if not date_str or hour_str is None:
        return None

    try:
        hour_int = int(hour_str)
    except ValueError:
        return None

    if not isinstance(counts, dict) or not counts:
        return []

    rows = []
    for event_type, cnt in counts.items():
        try:
            cnt_int = int(cnt)
        except (ValueError, TypeError):
            cnt_int = 0
        rows.append((date_str, hour_int, str(event_type), cnt_int))
    return rows


def connect():
    host = os.getenv("PGHOST", "postgres")
    port = int(os.getenv("PGPORT", "5432"))
    db = os.getenv("PGDATABASE", "analytics")
    user = os.getenv("PGUSER", "analytics")
    pw = os.getenv("PGPASSWORD", "analytics")

    return psycopg2.connect(host=host, port=port, dbname=db, user=user, password=pw)


UPSERT_SQL = """
INSERT INTO event_counts (date, hour, event_type, count)
VALUES (%s, %s, %s, %s)
ON CONFLICT (date, hour, event_type)
DO UPDATE SET
  count = EXCLUDED.count,
  updated_at = NOW();
"""


def run_load(force: bool = False) -> None:
    root = project_root()
    agg_base = aggregated_dir(root)

    if not agg_base.exists():
        print(f"[ERROR] aggregated dir not found: {agg_base}")
        return

    files = sorted(list(iter_event_counts_files(agg_base)))
    print(f"[INFO] Found aggregated files: {len(files)}")

    if not files:
        print("[INFO] Nothing to load")
        return

    loaded_rows = 0
    loaded_files = 0

    with connect() as conn:
        with conn.cursor() as cur:
            for fpath in files:
                rows = parse_partition_file(fpath)
                if rows is None:
                    continue
                if not rows:
                    # No counts or invalid structure; skip
                    continue

                cur.executemany(UPSERT_SQL, rows)
                loaded_rows += len(rows)
                loaded_files += 1

        conn.commit()

    print(f"[OK] Loaded files: {loaded_files}, rows upserted: {loaded_rows}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reserved for symmetry with other tasks (currently not used).",
    )
    args = parser.parse_args()
    run_load(force=args.force)