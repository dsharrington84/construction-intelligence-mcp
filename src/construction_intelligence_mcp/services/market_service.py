from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from statistics import median

from construction_intelligence_mcp.models.market import (
    DistrictMarketSummary,
    MarketCoverage,
    MarketMetrics,
    MarketPeriod,
    MarketSummary,
    MarketSummaryRequest,
    WorkTypeMarketSummary,
)
from construction_intelligence_mcp.models.project import ProjectSearchRequest, ProjectSummary
from construction_intelligence_mcp.services.project_service import ProjectService

_SOURCE_RESULT_LIMIT = 1000


class MarketService:
    """Aggregate governed project records into forward-looking market intelligence."""

    def __init__(self, project_service: ProjectService) -> None:
        self.project_service = project_service

    def summarize_market(self, request: MarketSummaryRequest) -> MarketSummary:
        end_date = self._one_year_later(request.as_of_date) - timedelta(days=1)
        source_projects = self.project_service.search_projects(
            ProjectSearchRequest(districts=request.districts, limit=_SOURCE_RESULT_LIMIT)
        )
        distinct_projects = self._distinct_projects(source_projects)
        included: list[ProjectSummary] = []
        proxy_count = 0
        excluded_without_date = 0
        for project in distinct_projects:
            if project.district not in request.districts:
                continue
            if project.advertisement_date is not None:
                if request.as_of_date <= project.advertisement_date <= end_date:
                    included.append(project)
                continue
            if project.advertisement_fiscal_year is not None:
                if request.as_of_date.year <= project.advertisement_fiscal_year <= end_date.year:
                    included.append(project)
                    proxy_count += 1
                continue
            excluded_without_date += 1

        by_district = [
            DistrictMarketSummary(district=district, **self._metrics(projects).model_dump())
            for district, projects in self._group_by_district(included, request.districts)
        ]
        by_work_type = [
            WorkTypeMarketSummary(work_type=work_type, **self._metrics(projects).model_dump())
            for work_type, projects in self._group_by_work_type(included)
        ]
        projects_with_value = sum(project.programmed_value is not None for project in included)
        missing_value = len(included) - projects_with_value
        coverage = projects_with_value / len(included) if included else 0.0
        limit_reached = len(source_projects) == _SOURCE_RESULT_LIMIT
        limitations = [
            "Prior-period change is unavailable in Market Service V1.",
            "Projects without an advertisement date or fiscal year are excluded.",
            "Advertisement fiscal year is treated as a calendar-year proxy when the exact date "
            + "is unavailable.",
        ]
        if limit_reached:
            limitations.append(
                "The ProjectService result limit was reached; totals may not cover every project."
            )

        return MarketSummary(
            period=MarketPeriod(
                start_date=request.as_of_date,
                end_date=end_date,
                label="Next 12 months",
                date_basis=(
                    "Exact advertisement date; advertisement fiscal year is a calendar-year proxy "
                    + "when no exact date is available."
                ),
                prior_period_change=None,
            ),
            districts_included=request.districts,
            overall=self._metrics(included),
            by_district=by_district,
            by_work_type=by_work_type,
            coverage=MarketCoverage(
                projects_with_programmed_value=projects_with_value,
                projects_missing_programmed_value=missing_value,
                programmed_value_coverage=coverage,
                projects_using_fiscal_year_proxy=proxy_count,
                projects_excluded_without_date=excluded_without_date,
                source_result_limit=_SOURCE_RESULT_LIMIT,
                source_result_limit_reached=limit_reached,
                limitations=limitations,
            ),
        )

    @staticmethod
    def _one_year_later(value: date) -> date:
        try:
            return value.replace(year=value.year + 1)
        except ValueError:
            return value.replace(year=value.year + 1, day=28)

    @staticmethod
    def _distinct_projects(projects: list[ProjectSummary]) -> list[ProjectSummary]:
        return list({project.project_id: project for project in projects}.values())

    @staticmethod
    def _metrics(projects: list[ProjectSummary]) -> MarketMetrics:
        values = [
            project.programmed_value for project in projects if project.programmed_value is not None
        ]
        return MarketMetrics(
            project_count=len(projects),
            total_programmed_value=sum(values),
            median_project_value=median(values) if values else None,
            minimum_project_value=min(values) if values else None,
            maximum_project_value=max(values) if values else None,
        )

    @staticmethod
    def _group_by_district(
        projects: list[ProjectSummary], districts: list[int]
    ) -> list[tuple[int, list[ProjectSummary]]]:
        grouped: dict[int, list[ProjectSummary]] = defaultdict(list)
        for project in projects:
            if project.district is not None:
                grouped[project.district].append(project)
        return [(district, grouped[district]) for district in districts]

    @staticmethod
    def _group_by_work_type(
        projects: list[ProjectSummary],
    ) -> list[tuple[str, list[ProjectSummary]]]:
        grouped: dict[str, list[ProjectSummary]] = defaultdict(list)
        for project in projects:
            grouped[project.primary_scope].append(project)
        return sorted(grouped.items())
