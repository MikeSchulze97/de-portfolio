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

    if not fpath.exists():
        return {
            "date": date_part,
            "hour": hour_part,
            "event_type_counts": {},
            "note": "events.jsonl not found",
        }

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
    }


def resolve_partition(partition: str) -> Path:
    partition = partition.strip().replace("\\", "/")
    if not partition.startswith("date=") or "/hour=" not in partition:
        raise ValueError("Partition must look like: date=YYYY-MM-DD/hour=HH")
    return PROCESSED_DIR / partition


def list_partitions() -> None:
    if not PROCESSED_DIR.exists():
        print(f"[ERROR] processed dir not found: {PROCESSED_DIR}")
        return

    partitions = sorted([p for p in PROCESSED_DIR.glob("date=*/hour=*") if p.is_dir()])

    if not partitions:
        print("[INFO] No partitions found")
        return

    print("[INFO] Available partitions:")
    for p in partitions:
        print(f"  - {partition_key(p)}")


def run_aggregate(force: bool = False, partition: str | None = None) -> None:
    if not PROCESSED_DIR.exists():
        print(f"[ERROR] processed dir not found: {PROCESSED_DIR}")
        return

    state = load_state()

    if partition:
        part_dir = resolve_partition(partition)
        if not part_dir.exists():
            print(f"[ERROR] partition not found: {part_dir}")
            return
        partitions = [part_dir]
    else:
        partitions = sorted([p for p in PROCESSED_DIR.glob("date=*/hour=*") if p.is_dir()])

    print(f"[INFO] Found partitions: {len(partitions)}")

    to_process: list[tuple[Path, str, float]] = []
    for part in partitions:
        key = partition_key(part)
        fpath = events_file(part)
        mtime = fpath.stat().st_mtime if fpath.exists() else 0.0
        last = state.get(key, -1.0)

        if force or mtime > last:
            to_process.append((part, key, mtime))

    print(f"[INFO] To aggregate now: {len(to_process)} (force={force})")

    if not to_process:
        print("[INFO] Nothing to do")
        return

    written = 0
    for part, key, mtime in to_process:
        result = aggregate_one_partition(part)

        out_dir = AGG_DIR / part.parent.name / part.name
        out_dir.mkdir(parents=True, exist_ok=True)

        out_file = out_dir / "event_counts.json"
        with out_file.open("w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        state[key] = mtime
        written += 1

    save_state(state)
    print(f"[OK] Aggregation complete. Written: {written}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Recompute even if state says up-to-date")
    parser.add_argument(
        "--partition",
        type=str,
        default=None,
        help="Aggregate only one partition: date=YYYY-MM-DD/hour=HH",
    )
    parser.add_argument(
        "--list-partitions",
        action="store_true",
        help="List available processed partitions and exit",
    )

    args = parser.parse_args()

    if args.list_partitions:
        list_partitions()
    else:
        run_aggregate(force=args.force, partition=args.partition)