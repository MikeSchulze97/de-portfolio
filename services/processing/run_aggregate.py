from pathlib import Path
import json
import argparse
from collections import Counter
import os

if os.getenv("DATA_DIR"):
    PROJECT_ROOT = Path(os.getenv("DATA_DIR")).parent
else:
    PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
AGG_DIR = PROJECT_ROOT / "data" / "aggregated"
STATE_FILE = PROJECT_ROOT / "data" / "_checkpoints" / "aggregated_partitions_state.json"


def load_state() -> dict[str, float]:
    if not STATE_FILE.exists():
        return {}
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))


def save_state(state: dict[str, float]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(
        json.dumps(state, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def partition_key(partition_dir: Path) -> str:
    return f"{partition_dir.parent.name}/{partition_dir.name}"


def events_file(partition_dir: Path) -> Path:
    return partition_dir / "events.jsonl"


def aggregate_one_partition(partition_dir: Path) -> dict:
    date_part = partition_dir.parent.name.replace("date=", "")
    hour_part = partition_dir.name.replace("hour=", "")

    counts = Counter()

    fpath = events_file(partition_dir)
    if fpath.exists():
        with fpath.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                event = json.loads(line)
                counts[event.get("event_type", "unknown")] += 1

        return {
            "date": date_part,
            "hour": hour_part,
            "event_type_counts": dict(counts),
            "source": "events.jsonl",
        }

    part_files = sorted(partition_dir.glob("part-*.json"))
    if not part_files:
        return {
            "date": date_part,
            "hour": hour_part,
            "event_type_counts": {},
            "note": "no input files found (events.jsonl missing and no part-*.json)",
        }

    for pf in part_files:
        with pf.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                event = json.loads(line)
                counts[event.get("event_type", "unknown")] += 1

    return {
        "date": date_part,
        "hour": hour_part,
        "event_type_counts": dict(counts),
        "source": "spark_part_files",
    }


def resolve_partition(partition: str) -> Path:
    partition = partition.strip().replace("\\", "/")
    if not partition.startswith("date=") or "/hour=" not in partition:
        raise ValueError("Partition must look like: date=YYYY-MM-DD/hour=HH")
    return PROCESSED_DIR / partition


def list_partitions() -> list[Path]:
    if not PROCESSED_DIR.exists():
        print(f"[ERROR] processed dir not found: {PROCESSED_DIR}")
        return []

    partitions = []
    for date_dir in sorted(PROCESSED_DIR.glob("date=*")):
        for hour_dir in sorted(date_dir.glob("hour=*")):
            partitions.append(hour_dir)
    return partitions


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate processed events")
    parser.add_argument("--partition", type=str, help="Aggregate a single partition (date=YYYY-MM-DD/hour=HH)")
    parser.add_argument("--force", action="store_true", help="Re-aggregate even if partition is already in state file")
    args = parser.parse_args()

    state = load_state()

    if args.partition:
        partitions = [resolve_partition(args.partition)]
    else:
        partitions = list_partitions()

    print(f"[INFO] Found partitions: {len(partitions)}")

    to_process = []
    for p in partitions:
        key = partition_key(p)
        if args.force or key not in state:
            to_process.append(p)

    print(f"[INFO] To aggregate now: {len(to_process)} (force={args.force})")

    if not to_process:
        print("[INFO] Nothing to do")
        return

    for partition_dir in to_process:
        result = aggregate_one_partition(partition_dir)

        out_dir = AGG_DIR / partition_dir.parent.name / partition_dir.name
        out_dir.mkdir(parents=True, exist_ok=True)

        out_file = out_dir / "event_counts.json"
        out_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

        state[partition_key(partition_dir)] = out_file.stat().st_mtime

    save_state(state)
    print(f"[OK] Aggregation complete. Written: {len(to_process)}")


if __name__ == "__main__":
    main()