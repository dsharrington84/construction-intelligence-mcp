from datetime import date

import pytest
from pydantic import ValidationError

from construction_intelligence_mcp.models.opportunity import Opportunity, OpportunitySearchRequest
from construction_intelligence_mcp.models.project import ProjectDetail, ProjectSummary
from construction_intelligence_mcp.services.opportunity_service import OpportunityService


def project(
    project_id: str,
    *,
    district: int | None = 7,
    scope: str = "Bridge Replacement",
    value: float | None = 10_000_000,
    advertisement_date: date | None = date(2026, 6, 1),
    fiscal_year: int | None = 2026,
    description: str | None = "Replace bridge deck",
) -> ProjectSummary:
    return ProjectSummary(
        project_id=project_id,
        title=f"Project {project_id}",
        description=description,
        district=district,
        county="Los Angeles" if district is not None else None,
        route="5" if district is not None else None,
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

    def fetch_project(self, project_id: str):
        match = next((item for item in self.projects if item.project_id == project_id), None)
        if match is None:
            return None
        return ProjectDetail(**match.model_dump())


@pytest.fixture
def service() -> OpportunityService:
    projects = [
        project("P-1", district=7, value=50_000_000, advertisement_date=date(2026, 3, 1)),
        project(
            "P-2",
            district=8,
            scope="Pavement Rehabilitation",
            value=20_000_000,
            advertisement_date=date(2026, 2, 1),
            description="Cold plane and overlay pavement",
        ),
        project("P-3", district=4, value=80_000_000, advertisement_date=date(2026, 1, 1)),
        project(
            "P-4",
            district=11,
            value=None,
            advertisement_date=None,
            fiscal_year=2027,
        ),
    ]
    return OpportunityService(StubProjectService(projects))  # type: ignore[arg-type]


def test_default_search_uses_southern_california_market_and_retains_lineage(
    service: OpportunityService,
) -> None:
    opportunities = service.search_opportunities(OpportunitySearchRequest())

    assert [item.project_id for item in opportunities] == ["P-2", "P-1", "P-4"]
    assert all(isinstance(item, Opportunity) for item in opportunities)
    assert all(
        item.opportunity_id == f"project-opportunity:{item.project_id}" for item in opportunities
    )
    assert len({item.opportunity_id for item in opportunities}) == len(opportunities)
    assert all(item.why_it_surfaced for item in opportunities)


@pytest.mark.parametrize(
    ("search_request", "expected"),
    [
        (OpportunitySearchRequest(districts=[8]), ["P-2"]),
        (OpportunitySearchRequest(scope="pavement"), ["P-2"]),
        (OpportunitySearchRequest(minimum_programmed_value=30_000_000), ["P-1"]),
        (
            OpportunitySearchRequest(
                advertisement_start=date(2026, 2, 15),
                advertisement_end=date(2026, 12, 31),
            ),
            ["P-1"],
        ),
        (OpportunitySearchRequest(text="overlay"), ["P-2"]),
    ],
)
def test_search_filters_work_independently(service, search_request, expected) -> None:
    assert [item.project_id for item in service.search_opportunities(search_request)] == expected


def test_search_filters_work_in_combination(service: OpportunityService) -> None:
    request = OpportunitySearchRequest(
        districts=[7, 8],
        scope="bridge",
        minimum_programmed_value=25_000_000,
        advertisement_start=date(2026, 1, 1),
        advertisement_end=date(2026, 6, 1),
        text="deck",
    )

    opportunities = service.search_opportunities(request)

    assert [item.project_id for item in opportunities] == ["P-1"]
    assert len(opportunities[0].why_it_surfaced) == 5


def test_missing_value_and_date_are_governed_not_invented(service: OpportunityService) -> None:
    opportunity = service.fetch_opportunity("project-opportunity:P-4")

    assert opportunity is not None
    assert opportunity.programmed_value is None
    assert opportunity.advertisement_date is None
    assert opportunity.advertisement_fiscal_year == 2027
    assert opportunity.source_confidence == "high"


def test_fetch_opportunity_returns_typed_object_or_none(service: OpportunityService) -> None:
    opportunity = service.fetch_opportunity("project-opportunity:P-1")

    assert isinstance(opportunity, Opportunity)
    assert opportunity.project_id == "P-1"
    assert service.fetch_opportunity("project-opportunity:missing") is None
    assert service.fetch_opportunity("P-1") is None


def test_ranking_is_deterministic_and_limit_is_applied_after_scope_filter(
    service: OpportunityService,
) -> None:
    opportunities = service.search_opportunities(OpportunitySearchRequest(limit=2))

    assert [item.project_id for item in opportunities] == ["P-2", "P-1"]


def test_search_delegates_governed_filters_to_project_service(service: OpportunityService) -> None:
    request = OpportunitySearchRequest(districts=[7], text="bridge", limit=1)

    service.search_opportunities(request)

    delegated = service.project_service.last_request  # type: ignore[attr-defined]
    assert delegated.districts == [7]
    assert delegated.text == "bridge"
    assert delegated.limit == 1000


def test_request_validation_rejects_invalid_window() -> None:
    with pytest.raises(ValidationError, match="advertisement_start"):
        OpportunitySearchRequest(
            advertisement_start=date(2027, 1, 1), advertisement_end=date(2026, 1, 1)
        )
