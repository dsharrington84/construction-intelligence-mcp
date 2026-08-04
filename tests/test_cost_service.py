from datetime import date
from pathlib import Path
from typing import Any

import duckdb
import pytest

from construction_intelligence_mcp.models.cost import CostConfidence, CostContext
from construction_intelligence_mcp.server import fetch_cost_context
from construction_intelligence_mcp.services.cost_service import CostService
from construction_intelligence_mcp.services.project_service import ProjectService


class StubHistory:
    source_relation = 'main."ci_cost_history"'

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows

    def fetch_observations(self) -> list[dict[str, Any]]:
        return self.rows


@pytest.fixture
def project_service(tmp_path: Path) -> ProjectService:
    path = tmp_path / "cost.duckdb"
    connection = duckdb.connect(str(path))
    connection.execute(
        """
        CREATE TABLE ci_market_state (
            project_id VARCHAR, project_description VARCHAR, district INTEGER,
            programmed_value DOUBLE, advertisement_date DATE
        )
        """
    )
    connection.execute(
        "INSERT INTO ci_market_state VALUES ('TARGET', 'Replace bridge', 7, 140, '2026-01-01')"
    )
    connection.close()
    return ProjectService(path)


def observation(
    project_id: str,
    district: int,
    cost: float,
    unit_price: float,
    factor: float = 1.0,
) -> dict[str, Any]:
    return {
        "project_id": project_id,
        "contract_number": f"C-{project_id}",
        "description": "Historical bridge replacement",
        "primary_scope": "Bridge Replacement",
        "district": district,
        "bid_date": date(2024, 1, int(project_id[-1])),
        "historical_cost": cost,
        "bid_item_code": "19-001",
        "bid_item_description": "Structure excavation",
        "quantity": 10,
        "unit": "CY",
        "unit_price": unit_price,
        "escalation_factor": factor,
        "escalation_source": "Certified Construction Cost Index",
    }


def test_historical_matches_escalation_confidence_and_variance(
    project_service: ProjectService,
) -> None:
    rows = [
        observation("P-1", 7, 100, 10, 1.1),
        observation("P-2", 8, 120, 12, 1.0),
        observation("P-3", 7, 150, 15, 1.0),
    ]
    context = CostService(project_service, StubHistory(rows)).fetch_cost_context("TARGET")

    assert isinstance(context, CostContext)
    assert [item.project_id for item in context.comparable_projects] == ["P-3", "P-1", "P-2"]
    assert context.comparable_projects[0].match_basis == "Same primary scope and district"
    assert context.comparable_projects[-1].match_basis == "Same primary scope statewide"
    assert context.historical_cost is not None
    assert context.historical_cost.baseline_cost == 120
    assert context.historical_unit_prices[0].statistics.median == 12
    assert context.bid_item_distribution[0].total_quantity == 30
    assert context.escalation_basis.applied is True
    assert context.escalation_basis.source == "Certified Construction Cost Index"
    assert context.cost_confidence == CostConfidence.MODERATE
    assert context.variance is not None
    assert context.variance.amount == 20
    assert len(context.evidence) == 3


def test_duplicate_history_is_removed(project_service: ProjectService) -> None:
    row = observation("P-1", 7, 100, 10)
    context = CostService(project_service, StubHistory([row, dict(row)])).fetch_cost_context(
        "TARGET"
    )

    assert context is not None
    assert len(context.evidence) == 1
    assert context.historical_cost is not None
    assert context.historical_cost.statistics.observation_count == 1


def test_unknown_cost_is_explicit(project_service: ProjectService) -> None:
    context = CostService(project_service, StubHistory([])).fetch_cost_context("TARGET")

    assert context is not None
    assert context.cost_confidence == CostConfidence.NONE
    assert context.historical_cost is None
    assert context.comparable_projects == []
    assert context.limitations
    assert CostService(project_service, StubHistory([])).fetch_cost_context("missing") is None


def test_mixed_units_are_separate_distributions(project_service: ProjectService) -> None:
    rows = [observation("P-1", 7, 100, 10), observation("P-2", 7, 110, 5)]
    rows[1]["unit"] = "TON"

    context = CostService(project_service, StubHistory(rows)).fetch_cost_context("TARGET")

    assert context is not None
    assert [(item.bid_item_code, item.unit) for item in context.historical_unit_prices] == [
        ("19-001", "CY"),
        ("19-001", "TON"),
    ]


def test_schema_adaptive_adapter_reads_governed_history(tmp_path: Path) -> None:
    path = tmp_path / "integrated.duckdb"
    connection = duckdb.connect(str(path))
    connection.execute(
        "CREATE TABLE ci_market_state (project_id VARCHAR, project_description VARCHAR)"
    )
    connection.execute("INSERT INTO ci_market_state VALUES ('TARGET', 'Replace bridge')")
    connection.execute(
        """
        CREATE TABLE ci_cost_history (
            project_id VARCHAR, primary_scope VARCHAR, award_amount DOUBLE,
            item_code VARCHAR, unit VARCHAR, bid_unit_price DOUBLE
        )
        """
    )
    connection.execute(
        "INSERT INTO ci_cost_history VALUES ('OLD', 'Bridge Replacement', 100, '1', 'EA', 10)"
    )
    connection.close()

    context = CostService(ProjectService(path)).fetch_cost_context("TARGET")

    assert context is not None
    assert context.historical_cost is not None
    assert context.historical_cost.baseline_cost == 100
    assert context.evidence[0].source_relation.endswith('"ci_cost_history"')


class StubCostService:
    def fetch_cost_context(self, project_id: str) -> CostContext | None:
        if project_id != "TARGET":
            return None
        return CostContext(
            project_id=project_id,
            escalation_basis={"applied": False, "method": "Nominal historical dollars"},
        )


def test_fetch_cost_context_mcp_serializes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "construction_intelligence_mcp.server._cost_service", lambda: StubCostService()
    )

    response = fetch_cost_context("TARGET")

    assert response is not None
    assert response["project_id"] == "TARGET"
    assert response["cost_confidence"] == "NONE"
    assert fetch_cost_context("missing") is None
