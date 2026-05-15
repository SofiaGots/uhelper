import json
from pathlib import Path

import pytest

from src.data.repository import UniversityRepository


def _write_sample(path: Path, data: list[dict]) -> Path:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    return path


SAMPLE = [
    {
        "name": "МГУ",
        "city": "Москва",
        "programs": ["Математика", "Информатика"],
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
    },
    {
        "name": "СПбГУ",
        "city": "Санкт-Петербург",
        "programs": ["Информатика", "Юриспруденция"],
        "budget_requirements": {"min_score": 270},
        "paid_requirements": {"min_score": 200},
        "tuition_fee": 280000,
        "application_deadlines": {"main": "25 июля"},
        "program_details": [
            {
                "name": "Информатика",
                "ege_subjects": ["Математика", "Русский язык", "Информатика"],
                "budget_score": 280,
                "paid_score": 210,
            }
        ],
    },
]


def test_load_and_search(tmp_path: Path) -> None:
    path = _write_sample(tmp_path / "uni.json", SAMPLE)
    repo = UniversityRepository(path)
    repo.load()
    assert len(repo.all) == 2

    results = repo.search("Москва")
    assert len(results) == 1
    assert results[0].name == "МГУ"

    results = repo.search_by_city("петербург")
    assert len(results) == 1
    assert results[0].name == "СПбГУ"

    results = repo.search_by_program("Информатика")
    assert len(results) == 2

    results = repo.filter_by_min_score(280)
    assert len(results) == 1
    assert results[0].name == "МГУ"


def test_not_loaded_raises(tmp_path: Path) -> None:
    repo = UniversityRepository(tmp_path / "ignored.json")
    with pytest.raises(RuntimeError, match="not loaded"):
        _ = repo.all


def test_missing_file(tmp_path: Path) -> None:
    repo = UniversityRepository(tmp_path / "nonexistent.json")
    with pytest.raises(FileNotFoundError):
        repo.load()
