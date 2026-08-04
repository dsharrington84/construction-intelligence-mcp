from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, Field, field_validator


class ProjectSearchRequest(BaseModel):
    districts: list[int] | None = None
    advertisement_start: date | None = None
    advertisement_end: date | None = None
    minimum_programmed_value: float | None = Field(default=None, ge=0)
    text: str | None = None
    limit: int = Field(default=100, ge=1, le=1000)

    @field_validator("districts")
    @classmethod
    def normalize_districts(cls, value: list[int] | None) -> list[int] | None:
        if value is None:
            return None
        normalized = sorted(set(value))
        invalid = [district for district in normalized if district < 1 or district > 12]
        if invalid:
            raise ValueError(f"Invalid Caltrans districts: {invalid}")
        return normalized


class ProjectSummary(BaseModel):
    project_id: str
    title: str
    description: str | None = None
    district: int | None = None
    county: str | None = None
    route: str | None = None
    location: str | None = None
    primary_scope: str
    programmed_value: float | None = None
    advertisement_date: date | None = None
    advertisement_fiscal_year: int | None = None
    why_it_surfaced: list[str] = Field(default_factory=list)
    source_fields: dict[str, str | None] = Field(default_factory=dict)


class ProjectDetail(ProjectSummary):
    raw_record: dict[str, Any] = Field(default_factory=dict)
