from pathlib import Path
from datetime import datetime
import json
import argparse
import os

if os.getenv("DATA_DIR"):
    PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", "/"))
else:
    PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
QUARANTINE_DIR = PROJECT_ROOT / "data" / "quarantine"
CHECKPOINT_FILE = PROJECT_ROOT / "data" / "_checkpoints" / "processed_raw_files.txt"


def load_checkpoint() -> set[str]:
    if not CHECKPOINT_FILE.exists():
        return set()

    lines = CHECKPOINT_FILE.read_text(encoding="utf-8").splitlines()
    cleaned = {ln.strip() for ln in lines if ln.strip()}
    return cleaned


def append_checkpoint(filenames: list[str]) -> None:
    existing = load_checkpoint()
    new_items = [name for name in filenames if name and name not in existing]

    if not new_items:
        return

    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with CHECKPOINT_FILE.open("a", encoding="utf-8") as f:
        for name in new_items:
            f.write(name + "\n")


def parse_event_time_from_filename(filename: str) -> datetime:
    ts = filename.split("_")[0]
    return datetime.strptime(ts, "%Y%m%dT%H%M%S%f")


def validate_event(event: dict) -> tuple[bool, str]:
    if not isinstance(event, dict):
        return False, "event_not_dict"

    if "event_type" not in event:
        return False, "missing_event_type"

    if "payload" not in event:
        return False, "missing_payload"

    if not isinstance(event["payload"], dict):
        return False, "payload_not_dict"

    return True, "ok"


def run_batch(limit: int | None = None) -> None:
    processed_already = load_checkpoint()

    raw_files = sorted(RAW_DIR.glob("*.json"))
    to_process = [f for f in raw_files if f.name not in processed_already]

    if limit is not None:
        to_process = to_process[:limit]

    checkpoint_lines = CHECKPOINT_FILE.read_text(encoding="utf-8").splitlines() if CHECKPOINT_FILE.exists() else []

    print(f"[INFO] Found {len(raw_files)} raw files")
    print(f"[INFO] Already processed (unique): {len(processed_already)}")
    print(f"[INFO] Checkpoint lines (raw): {len(checkpoint_lines)}")
    print(f"[INFO] To process now: {len(to_process)}")

    if not to_process:
        print("[INFO] Nothing to do")
        return

    written: list[str] = []
    quarantined = 0
    processed_ok = 0

    for f in to_process:
        try:
            with f.open("r", encoding="utf-8-sig") as file:
                event = json.load(file)

            is_valid, reason = validate_event(event)
            if not is_valid:
                event_time = parse_event_time_from_filename(f.name)
                date_part = event_time.strftime("%Y-%m-%d")
                hour_part = event_time.strftime("%H")

                bad_dir = QUARANTINE_DIR / f"date={date_part}" / f"hour={hour_part}"
                bad_dir.mkdir(parents=True, exist_ok=True)
                bad_file = bad_dir / "bad_events.jsonl"

                bad_record = {
                    "reason": reason,
                    "source_file": f.name,
                    "raw_event": event,
                }

                with bad_file.open("a", encoding="utf-8") as out:
                    out.write(json.dumps(bad_record, ensure_ascii=False) + "\n")

                quarantined += 1
                written.append(f.name)
                continue

            event_time = parse_event_time_from_filename(f.name)
            date_part = event_time.strftime("%Y-%m-%d")
            hour_part = event_time.strftime("%H")

            out_dir = PROCESSED_DIR / f"date={date_part}" / f"hour={hour_part}"
            out_dir.mkdir(parents=True, exist_ok=True)

            out_file = out_dir / "events.jsonl"

            processed_event = {
                "event_type": event.get("event_type"),
                "event_time": event_time.isoformat(),
                "source_file": f.name,
                "payload": event.get("payload"),
            }

            with out_file.open("a", encoding="utf-8") as out:
                out.write(json.dumps(processed_event, ensure_ascii=False) + "\n")

            written.append(f.name)
            processed_ok += 1

        except Exception as e:
            try:
                event_time = parse_event_time_from_filename(f.name)
                date_part = event_time.strftime("%Y-%m-%d")
                hour_part = event_time.strftime("%H")
            except Exception:
                date_part = "unknown-date"
                hour_part = "unknown-hour"

            bad_dir = QUARANTINE_DIR / f"date={date_part}" / f"hour={hour_part}"
            bad_dir.mkdir(parents=True, exist_ok=True)
            bad_file = bad_dir / "bad_events.jsonl"

            bad_record = {
                "reason": "json_read_or_parse_error",
                "error": str(e),
                "source_file": f.name,
            }

            with bad_file.open("a", encoding="utf-8") as out:
                out.write(json.dumps(bad_record, ensure_ascii=False) + "\n")

            quarantined += 1
            written.append(f.name)
            print(f"[WARN] Quarantined {f.name}: {e}")

    append_checkpoint(written)

    print(f"[INFO] processed_ok: {processed_ok}")
    print(f"[INFO] quarantined: {quarantined}")
    print("[OK] Batch completed")
    print(f"[OK] Written events: {len(written)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None, help="Process at most N raw files")
    args = parser.parse_args()
    run_batch(limit=args.limit)