from datetime import date

from construction_intelligence_mcp.models.market import (
    DistrictMarketSummary,
    MarketCoverage,
    MarketMetrics,
    MarketPeriod,
    MarketSummary,
    WorkTypeMarketSummary,
)
from construction_intelligence_mcp.models.opportunity import Opportunity
from construction_intelligence_mcp.models.project import ProjectDetail
from construction_intelligence_mcp.models.project_intelligence import ProjectIntelligence
from construction_intelligence_mcp.services.project_intelligence_service import (
    ProjectIntelligenceService,
)
from construction_intelligence_mcp.services.project_scope_classifier import ProjectScopeClassifier


def governed_project() -> ProjectDetail:
    project = ProjectDetail(
        project_id="P-1",
        title="Replace Route 5 bridge",
        description="Replace existing bridge",
        district=7,
        county="Los Angeles",
        route="5",
        location="At Main Street",
        primary_scope="Other",
        programmed_value=42_000_000,
        advertisement_date=date(2027, 2, 1),
        advertisement_fiscal_year=2027,
    )
    project.classified_scope = ProjectScopeClassifier().classify(project)
    project.primary_scope = project.classified_scope.primary_scope.value
    return project


def governed_market() -> MarketSummary:
    metrics = MarketMetrics(project_count=1, total_programmed_value=42_000_000)
    return MarketSummary(
        period=MarketPeriod(
            start_date=date(2026, 8, 4),
            end_date=date(2027, 8, 3),
            label="Next 12 months",
            date_basis="Exact advertisement date",
            prior_period_change=None,
        ),
        districts_included=[7],
        overall=metrics,
        by_district=[
            DistrictMarketSummary(district=7, project_count=1, total_programmed_value=42_000_000)
        ],
        by_work_type=[
            WorkTypeMarketSummary(
                work_type="Bridge Replacement",
                project_count=1,
                total_programmed_value=42_000_000,
            )
        ],
        coverage=MarketCoverage(
            projects_with_programmed_value=1,
            projects_missing_programmed_value=0,
            programmed_value_coverage=1,
            projects_using_fiscal_year_proxy=0,
            projects_excluded_without_date=0,
            source_result_limit=1000,
            source_result_limit_reached=False,
        ),
    )


class StubProjectService:
    def __init__(self, project: ProjectDetail | None) -> None:
        self.project = project

    def fetch_project(self, project_id: str) -> ProjectDetail | None:
        if self.project is not None and self.project.project_id == project_id:
            return self.project
        return None


class StubMarketService:
    def __init__(self, market: MarketSummary) -> None:
        self.market = market
        self.request = None

    def summarize_market(self, request):
        self.request = request
        return self.market


class StubOpportunityService:
    def __init__(self, opportunity: Opportunity) -> None:
        self.opportunity = opportunity
        self.opportunity_id = None

    def fetch_opportunity(self, opportunity_id: str) -> Opportunity | None:
        self.opportunity_id = opportunity_id
        return self.opportunity


def test_existing_project_composes_all_available_intelligence() -> None:
    project = governed_project()
    market_service = StubMarketService(governed_market())
    opportunity = Opportunity(
        opportunity_id="project-opportunity:P-1",
        project_id="P-1",
        title=project.title,
        district=7,
        primary_scope=project.primary_scope,
        why_it_surfaced=["Available as a governed potential-pursuit project"],
        source_confidence="high",
    )
    opportunity_service = StubOpportunityService(opportunity)
    service = ProjectIntelligenceService(
        StubProjectService(project),  # type: ignore[arg-type]
        market_service,  # type: ignore[arg-type]
        opportunity_service,  # type: ignore[arg-type]
    )

    result = service.fetch_project_intelligence("P-1")

    assert isinstance(result, ProjectIntelligence)
    assert result.project.model_dump() == {
        "project_id": "P-1",
        "title": "Replace Route 5 bridge",
        "description": "Replace existing bridge",
        "district": 7,
        "county": "Los Angeles",
        "route": "5",
        "location": "At Main Street",
        "advertisement_date": date(2027, 2, 1),
        "advertisement_fiscal_year": 2027,
        "programmed_value": 42_000_000,
    }
    assert result.classification is project.classified_scope
    assert result.market.district_summary.district == 7
    assert result.market.work_type_summary.work_type == "Bridge Replacement"
    assert result.market.market_outlook is market_service.market
    assert result.market.market_trend is None
    assert result.opportunity is opportunity
    assert opportunity_service.opportunity_id == "project-opportunity:P-1"
    assert market_service.request.districts == [7]
    assert result.contractor_signals == []
    assert result.cost_signals == []


def test_missing_project_returns_none_without_calling_other_services() -> None:
    class UnexpectedService:
        def __getattr__(self, name):
            raise AssertionError(f"Unexpected service access: {name}")

    service = ProjectIntelligenceService(
        StubProjectService(None),  # type: ignore[arg-type]
        UnexpectedService(),  # type: ignore[arg-type]
        UnexpectedService(),  # type: ignore[arg-type]
    )

    assert service.fetch_project_intelligence("missing") is None
