from datetime import date

from construction_intelligence_mcp.models.market import MarketSummary, MarketSummaryRequest
from construction_intelligence_mcp.models.project import ProjectSummary
from construction_intelligence_mcp.services.market_service import MarketService


def project(
    project_id: str,
    *,
    district: int = 7,
    scope: str = "Bridge Replacement",
    value: float | None = 10_000_000,
    advertisement_date: date | None = date(2026, 9, 1),
    fiscal_year: int | None = None,
) -> ProjectSummary:
    return ProjectSummary(
        project_id=project_id,
        title=f"Project {project_id}",
        district=district,
        primary_scope=scope,
        programmed_value=value,
        advertisement_date=advertisement_date,
        advertisement_fiscal_year=fiscal_year,
    )


class StubProjectService:
    def __init__(self, projects: list[ProjectSummary]) -> None:
        self.projects = projects
        self.last_request = None

    def search_projects(self, request):
        self.last_request = request
        return list(self.projects)


def test_market_summary_reconciles_distinct_projects_and_values() -> None:
    projects = [
        project("P-1", district=7, value=10_000_000),
        project("P-1", district=7, value=10_000_000),
        project("P-2", district=8, scope="Pavement", value=30_000_000),
        project("P-3", district=11, scope="Pavement", value=None),
        project("OUT-DISTRICT", district=4),
        project("OUT-DATE", district=12, advertisement_date=date(2028, 1, 1)),
    ]
    stub = StubProjectService(projects)
    service = MarketService(stub)  # type: ignore[arg-type]

    result = service.summarize_market(MarketSummaryRequest(as_of_date=date(2026, 8, 4)))

    assert isinstance(result, MarketSummary)
    assert result.districts_included == [7, 8, 11, 12]
    assert result.overall.project_count == 3
    assert result.overall.total_programmed_value == 40_000_000
    assert result.overall.median_project_value == 20_000_000
    assert result.overall.minimum_project_value == 10_000_000
    assert result.overall.maximum_project_value == 30_000_000
    assert sum(item.project_count for item in result.by_district) == result.overall.project_count
    assert sum(item.total_programmed_value for item in result.by_district) == 40_000_000
    assert sum(item.project_count for item in result.by_work_type) == result.overall.project_count
    assert sum(item.total_programmed_value for item in result.by_work_type) == 40_000_000
    assert stub.last_request.districts == [7, 8, 11, 12]
    assert stub.last_request.limit == 1000


def test_missing_values_and_date_proxies_are_governed_as_coverage() -> None:
    projects = [
        project("VALUED", value=5_000_000),
        project("MISSING", district=8, value=None),
        project(
            "PROXY",
            district=11,
            value=15_000_000,
            advertisement_date=None,
            fiscal_year=2027,
        ),
        project("UNDATED", district=12, advertisement_date=None, fiscal_year=None),
    ]
    service = MarketService(StubProjectService(projects))  # type: ignore[arg-type]

    result = service.summarize_market(MarketSummaryRequest(as_of_date=date(2026, 8, 4)))

    assert result.period.end_date == date(2027, 8, 3)
    assert result.period.prior_period_change is None
    assert "fiscal year" in result.period.date_basis
    assert result.coverage.projects_with_programmed_value == 2
    assert result.coverage.projects_missing_programmed_value == 1
    assert result.coverage.programmed_value_coverage == 2 / 3
    assert result.coverage.projects_using_fiscal_year_proxy == 1
    assert result.coverage.projects_excluded_without_date == 1
    assert any("Prior-period" in item for item in result.coverage.limitations)


def test_custom_district_scope_and_empty_market_are_typed() -> None:
    service = MarketService(StubProjectService([]))  # type: ignore[arg-type]

    result = service.summarize_market(
        MarketSummaryRequest(as_of_date=date(2026, 8, 4), districts=[12, 7, 7])
    )

    assert result.districts_included == [7, 12]
    assert result.overall.project_count == 0
    assert result.overall.median_project_value is None
    assert [item.district for item in result.by_district] == [7, 12]
    assert result.by_work_type == []
