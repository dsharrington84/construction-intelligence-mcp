from datetime import date

import pytest

from construction_intelligence_mcp.models.opportunity import Opportunity
from construction_intelligence_mcp.models.portfolio import Portfolio, PortfolioRequest
from construction_intelligence_mcp.services.portfolio_service import PortfolioService


def opportunity(
    project_id: str,
    *,
    district: int | None,
    scope: str,
    value: float | None,
    confidence: str = "high",
    fiscal_year: int | None = 2027,
) -> Opportunity:
    return Opportunity(
        opportunity_id=f"project-opportunity:{project_id}",
        project_id=project_id,
        title=f"Project {project_id}",
        district=district,
        advertisement_date=date(2027, 1, 1),
        advertisement_fiscal_year=fiscal_year,
        programmed_value=value,
        primary_scope=scope,
        why_it_surfaced=["Selected for review"],
        source_confidence=confidence,
    )


class StubOpportunityService:
    def __init__(self, opportunities: list[Opportunity]) -> None:
        self.opportunities = {item.opportunity_id: item for item in opportunities}

    def fetch_opportunity(self, opportunity_id: str) -> Opportunity | None:
        return self.opportunities.get(opportunity_id)


def service(opportunities: list[Opportunity]) -> PortfolioService:
    return PortfolioService(StubOpportunityService(opportunities))  # type: ignore[arg-type]


def test_empty_portfolio() -> None:
    portfolio = service([]).fetch_portfolio(PortfolioRequest())

    assert isinstance(portfolio, Portfolio)
    assert portfolio.selected_projects == []
    assert portfolio.total_revenue == 0
    assert portfolio.district_exposure == []
    assert portfolio.capacity_indicators.project_count == 0
    assert portfolio.portfolio_story.startswith("No opportunities")


def test_single_project_portfolio() -> None:
    selected = opportunity("P-1", district=7, scope="Bridge Replacement", value=20_000_000)

    portfolio = service([selected]).fetch_portfolio(
        PortfolioRequest(opportunity_ids=[selected.opportunity_id])
    )

    assert portfolio.total_revenue == 20_000_000
    assert portfolio.district_exposure[0].name == "District 7"
    assert portfolio.market_exposure[0].name == "Bridge"
    assert portfolio.strategic_alignment.aligned_project_count == 1


def test_multiple_districts_are_aggregated() -> None:
    selected = [
        opportunity("P-1", district=7, scope="Bridge Replacement", value=30_000_000),
        opportunity("P-2", district=8, scope="Bridge Rehabilitation", value=10_000_000),
        opportunity("P-3", district=7, scope="Drainage", value=10_000_000),
    ]

    portfolio = service(selected).fetch_portfolio(
        PortfolioRequest(opportunity_ids=[item.opportunity_id for item in selected])
    )

    by_district = {item.name: item for item in portfolio.district_exposure}
    assert by_district["District 7"].project_count == 2
    assert by_district["District 7"].programmed_value == 40_000_000
    assert by_district["District 8"].share_of_known_revenue == 0.2
    assert portfolio.capacity_indicators.largest_district_share == pytest.approx(2 / 3)


def test_mixed_opportunities_have_explainable_risk_and_alignment() -> None:
    selected = [
        opportunity("P-1", district=7, scope="Pavement Rehabilitation", value=5_000_000),
        opportunity(
            "P-2", district=8, scope="Safety Improvements", value=None, confidence="moderate"
        ),
        opportunity("P-3", district=None, scope="Other", value=15_000_000, confidence="limited"),
    ]

    portfolio = service(selected).fetch_portfolio(
        PortfolioRequest(opportunity_ids=[item.opportunity_id for item in selected])
    )

    assert {item.risk: item.project_count for item in portfolio.risk_distribution} == {
        "Low": 1,
        "Moderate": 1,
        "High": 1,
    }
    assert portfolio.strategic_alignment.aligned_project_count == 1
    assert portfolio.strategic_alignment.selective_project_count == 1
    assert portfolio.strategic_alignment.unknown_project_count == 1
    assert portfolio.capacity_indicators.projects_missing_value == 1


def test_portfolio_aggregation_and_missing_selection_failure() -> None:
    selected = [
        opportunity("P-1", district=7, scope="Bridge Replacement", value=25_000_000),
        opportunity("P-2", district=7, scope="ITS / Electrical", value=75_000_000),
    ]
    portfolio = service(selected).fetch_portfolio(
        PortfolioRequest(opportunity_ids=[item.opportunity_id for item in selected])
    )

    assert portfolio.total_revenue == 100_000_000
    assert portfolio.capacity_indicators.average_known_project_value == 50_000_000
    assert portfolio.capacity_indicators.largest_project_share == 0.75
    assert sum(item.programmed_value for item in portfolio.market_exposure) == 100_000_000
    assert portfolio.strategic_alignment.partner_or_non_target_project_count == 1

    with pytest.raises(ValueError, match="not found"):
        service(selected).fetch_portfolio(PortfolioRequest(opportunity_ids=["missing"]))
