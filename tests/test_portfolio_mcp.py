from construction_intelligence_mcp.models.portfolio import Portfolio, PortfolioRequest
from construction_intelligence_mcp.server import fetch_portfolio


class StubPortfolioService:
    def fetch_portfolio(self, request: PortfolioRequest) -> Portfolio:
        assert request.opportunity_ids == ["project-opportunity:P-1"]
        return Portfolio(
            total_revenue=0,
            revenue_basis="Test basis",
            capacity_indicators={
                "project_count": 0,
                "projects_with_known_value": 0,
                "projects_missing_value": 0,
            },
            strategic_alignment={
                "aligned_project_count": 0,
                "selective_project_count": 0,
                "partner_or_non_target_project_count": 0,
                "unknown_project_count": 0,
                "basis": "Test basis",
            },
            portfolio_story="Test story",
        )


def test_fetch_portfolio_mcp_response(monkeypatch) -> None:
    monkeypatch.setattr(
        "construction_intelligence_mcp.server._portfolio_service", StubPortfolioService
    )

    response = fetch_portfolio(["project-opportunity:P-1"])

    assert response["total_revenue"] == 0
    assert response["capacity_indicators"]["project_count"] == 0
    assert response["portfolio_story"] == "Test story"
