from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

DEFAULT_MARKET_DISTRICTS = [7, 8, 11, 12]


class OpportunitySearchRequest(BaseModel):
    districts: list[int] = Field(default_factory=lambda: list(DEFAULT_MARKET_DISTRICTS))
    scope: str | None = None
    advertisement_start: date | None = None
    advertisement_end: date | None = None
    minimum_programmed_value: float | None = Field(default=None, ge=0)
    text: str | None = None
    limit: int = Field(default=100, ge=1, le=1000)

    @field_validator("districts")
    @classmethod
    def normalize_districts(cls, value: list[int]) -> list[int]:
        normalized = sorted(set(value))
        invalid = [district for district in normalized if district < 1 or district > 12]
        if invalid:
            raise ValueError(f"Invalid Caltrans districts: {invalid}")
        return normalized

    @field_validator("scope", "text")
    @classmethod
    def normalize_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None

    @model_validator(mode="after")
    def validate_advertisement_window(self) -> OpportunitySearchRequest:
        if (
            self.advertisement_start is not None
            and self.advertisement_end is not None
            and self.advertisement_start > self.advertisement_end
        ):
            raise ValueError("advertisement_start must be on or before advertisement_end")
        return self


class Opportunity(BaseModel):
    opportunity_id: str
    project_id: str
    title: str
    district: int | None = None
    county: str | None = None
    route: str | None = None
    advertisement_date: date | None = None
    advertisement_fiscal_year: int | None = None
    programmed_value: float | None = None
    primary_scope: str
    why_it_surfaced: list[str] = Field(min_length=1)
    source_confidence: Literal["high", "moderate", "limited"]
