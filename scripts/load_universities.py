import json
import sys
from pathlib import Path

from src.models.university import University

DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "universities.json"


def load_from_file(data_path: Path | str) -> list[University]:
    path = Path(data_path)
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)
    raw = json.loads(path.read_text(encoding="utf-8"))
    universities = [University.model_validate(item) for item in raw]
    return universities


def main() -> None:
    data_path = sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_DATA_PATH)
    universities = load_from_file(data_path)
    print(f"Loaded {len(universities)} universities from {data_path}")
    for u in universities:
        details = len(u.program_details)
        print(f"  {u.name} ({u.city}) — {len(u.programs)} programs, {details} program details")
    print("All records valid.")


if __name__ == "__main__":
    main()
