import json
from pathlib import Path

from scripts.load_universities import load_from_file

SAMPLE = [
    {
        "name": "МГУ",
        "city": "Москва",
        "programs": ["Математика"],
        "budget_requirements": {"min_score": 290},
        "paid_requirements": {"min_score": 220},
        "tuition_fee": 350000,
        "application_deadlines": {"main": "20 июля"},
        "program_details": [
            {
                "name": "Математика",
                "ege_subjects": ["Математика", "Русский язык", "Физика"],
                "budget_score": 290,
                "paid_score": 220,
            }
        ],
    }
]


def test_load_from_file(tmp_path: Path) -> None:
    path = tmp_path / "universities.json"
    path.write_text(json.dumps(SAMPLE, ensure_ascii=False), encoding="utf-8")
    result = load_from_file(path)
    assert len(result) == 1
    assert result[0].name == "МГУ"


def test_load_default_dataset() -> None:
    default_path = Path(__file__).resolve().parent.parent / "data" / "universities.json"
    assert default_path.exists(), "Default dataset not found"
    result = load_from_file(default_path)
    assert len(result) == 10
