from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CHECKPOINT_FILE = PROJECT_ROOT / "data" / "_checkpoints" / "processed_raw_files.txt"


def load_checkpoint_lines() -> list[str]:
    if not CHECKPOINT_FILE.exists():
        return []
    return CHECKPOINT_FILE.read_text(encoding="utf-8").splitlines()


def main() -> None:
    raw_names = {p.name for p in RAW_DIR.glob("*.json")}

    lines = load_checkpoint_lines()
    cleaned = [ln.strip() for ln in lines if ln.strip()]
    unique = sorted(set(cleaned))

    kept = [name for name in unique if name in raw_names]
    removed = [name for name in unique if name not in raw_names]

    CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    CHECKPOINT_FILE.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")

    print(f"[INFO] raw files: {len(raw_names)}")
    print(f"[INFO] checkpoint unique before: {len(unique)}")
    print(f"[INFO] kept: {len(kept)}")
    print(f"[INFO] removed (not in raw): {len(removed)}")

    if removed:
        print("[INFO] Example removed:")
        for x in removed[:5]:
            print(f"  - {x}")


if __name__ == "__main__":
    main()
