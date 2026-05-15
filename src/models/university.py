from pydantic import BaseModel, field_validator


class ProgramDetail(BaseModel):
    name: str
    ege_subjects: list[str]
    budget_score: int | None = None
    paid_score: int | None = None


class ScoreRequirement(BaseModel):
    min_score: int


class University(BaseModel):
    name: str
    city: str
    programs: list[str]
    budget_requirements: ScoreRequirement
    paid_requirements: ScoreRequirement
    tuition_fee: int
    application_deadlines: dict[str, str]
    program_details: list[ProgramDetail]

    @field_validator("tuition_fee")
    @classmethod
    def validate_tuition(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("tuition_fee must be positive")
        return value
