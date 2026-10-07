from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.services.github_client import parse_pr_url
from app.services.llm_reviewer import ReviewComment


class ReviewCreate(BaseModel):
    pr_url: str = Field(examples=["https://github.com/SagaKale19/Pr-review-service/pull/1"])

    @field_validator("pr_url")
    @classmethod
    def validate_pr_url(cls, v: str) -> str:
        parse_pr_url(v)  # raises ValueError -> FastAPI returns 422
        return v.strip()


class ReviewOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # read directly from ORM objects

    id: int
    repo_owner: str
    repo_name: str
    pr_number: int
    pr_title: str | None
    status: str
    summary: str | None
    comments: list[ReviewComment] | None
    model_used: str | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime