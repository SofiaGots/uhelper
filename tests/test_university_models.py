import pytest
from pydantic import ValidationError

from src.models.university import ProgramDetail, ScoreRequirement, University


def test_university_valid() -> None:
    uni = University(
        name="МГУ",
        city="Москва",
        programs=["Математика", "Физика"],
        budget_requirements=ScoreRequirement(min_score=290),
        paid_requirements=ScoreRequirement(min_score=220),
        tuition_fee=350000,
        application_deadlines={"main": "20 июля"},
        program_details=[
            ProgramDetail(
                name="Математика",
                ege_subjects=["Математика", "Русский язык", "Физика"],
                budget_score=290,
                paid_score=220,
            )
        ],
    )
    assert uni.name == "МГУ"
    assert uni.budget_requirements.min_score == 290
    assert uni.program_details[0].budget_score == 290


def test_university_negative_tuition() -> None:
    with pytest.raises(ValidationError):
        University(
            name="Bad",
            city="Nowhere",
            programs=["Test"],
            budget_requirements=ScoreRequirement(min_score=100),
            paid_requirements=ScoreRequirement(min_score=50),
            tuition_fee=-1,
            application_deadlines={"main": "1 jan"},
            program_details=[],
        )


def test_program_detail_optional_scores() -> None:
    detail = ProgramDetail(name="Test", ege_subjects=["A", "B"])
    assert detail.budget_score is None
    assert detail.paid_score is None


@pytest.mark.asyncio
async def test_university_model_validate_from_json() -> None:
    raw = {
        "name": "СПбГУ",
        "city": "Санкт-Петербург",
        "programs": ["Информатика", "Физика"],
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
    }
    uni = University.model_validate(raw)
    assert uni.city == "Санкт-Петербург"
    assert len(uni.program_details) == 1
