from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, field_validator

DEFAULT_MARKET_DISTRICTS = [7, 8, 11, 12]


class MarketSummaryRequest(BaseModel):
    """Parameters for a forward-looking market summary."""

    as_of_date: date = Field(default_factory=date.today)
    districts: list[int] = Field(default_factory=lambda: list(DEFAULT_MARKET_DISTRICTS))

    @field_validator("districts")
    @classmethod
    def normalize_districts(cls, value: list[int]) -> list[int]:
        normalized = sorted(set(value))
        invalid = [district for district in normalized if district < 1 or district > 12]
        if invalid:
            raise ValueError(f"Invalid Caltrans districts: {invalid}")
        if not normalized:
            raise ValueError("At least one district is required")
        return normalized


class MarketMetrics(BaseModel):
    project_count: int = Field(ge=0)
    total_programmed_value: float = Field(ge=0)
    median_project_value: float | None = Field(default=None, ge=0)
    minimum_project_value: float | None = Field(default=None, ge=0)
    maximum_project_value: float | None = Field(default=None, ge=0)


class DistrictMarketSummary(MarketMetrics):
    district: int


class WorkTypeMarketSummary(MarketMetrics):
    work_type: str


class MarketPeriod(BaseModel):
    start_date: date
    end_date: date
    label: str
    date_basis: str
    prior_period_change: float | None = None


class MarketCoverage(BaseModel):
    projects_with_programmed_value: int = Field(ge=0)
    projects_missing_programmed_value: int = Field(ge=0)
    programmed_value_coverage: float = Field(ge=0, le=1)
    projects_using_fiscal_year_proxy: int = Field(ge=0)
    projects_excluded_without_date: int = Field(ge=0)
    source_result_limit: int = Field(ge=1)
    source_result_limit_reached: bool
    limitations: list[str] = Field(default_factory=list)


class MarketSummary(BaseModel):
    period: MarketPeriod
    districts_included: list[int]
    overall: MarketMetrics
    by_district: list[DistrictMarketSummary]
    by_work_type: list[WorkTypeMarketSummary]
    coverage: MarketCoverage
