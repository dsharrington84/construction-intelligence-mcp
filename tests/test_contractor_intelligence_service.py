from datetime import date

from construction_intelligence_mcp.models.contractor import ContractorConfidence
from construction_intelligence_mcp.services.contractor_intelligence_service import (
    ContractorIntelligenceService,
)
from test_project_intelligence_service import StubProjectService, governed_project


class StubHistoryRepository:
    source_relation = '"main"."ci_contractor_history"'

    def __init__(self, rows):
        self.rows = rows

    def fetch_history(self):
        return self.rows


def history_rows():
    return [
        {
            "contractor_id": "A",
            "contractor_name": "Alpha Construction",
            "project_id": "H-1",
            "contract_number": "07-1001",
            "district": 7,
            "project_type": "Bridge Replacement",
            "role": "prime",
            "bid_rank": 1,
            "was_awarded": True,
            "activity_date": date(2025, 1, 2),
            "self_performed": True,
        },
        {
            "contractor_id": "A",
            "contractor_name": "Alpha Construction",
            "project_id": "H-2",
            "contract_number": "11-2002",
            "district": 11,
            "project_type": "Bridge Replacement",
            "role": "prime",
            "bid_rank": 2,
            "was_awarded": False,
            "activity_date": date(2024, 2, 3),
            "self_performed": None,
        },
        {
            "contractor_id": "B",
            "contractor_name": "Beta Specialty",
            "project_id": "H-1",
            "contract_number": "07-1001",
            "district": 7,
            "project_type": "Bridge Replacement",
            "role": "sub",
            "bid_rank": None,
            "was_awarded": False,
            "activity_date": date(2025, 1, 2),
            "self_performed": False,
        },
        {
            "contractor_id": "C",
            "contractor_name": "Wrong Scope Inc",
            "project_id": "H-3",
            "district": 7,
            "project_type": "Drainage",
            "role": "prime",
            "was_awarded": True,
        },
        {
            "contractor_id": None,
            "contractor_name": None,
            "project_id": "H-4",
            "district": 7,
            "project_type": "Bridge Replacement",
            "role": "prime",
        },
    ]


def service(rows=None):
    return ContractorIntelligenceService(
        StubProjectService(governed_project()),  # type: ignore[arg-type]
        StubHistoryRepository(history_rows() if rows is None else rows),  # type: ignore[arg-type]
    )


def test_historical_winner_filters_scope_and_ranks_district_presence() -> None:
    context = service().fetch_contractor_context("P-1")

    assert context is not None
    assert [candidate.contractor_name for candidate in context.likely_pursuers] == [
        "Alpha Construction",
        "Beta Specialty",
    ]
    assert [candidate.contractor_name for candidate in context.historical_winners] == [
        "Alpha Construction"
    ]
    alpha = context.likely_pursuers[0]
    assert alpha.comparable_project_count == 2
    assert alpha.district_project_count == 1
    assert alpha.market_share == 1
    assert alpha.historical_competitiveness == "HISTORICAL_WINNER"
    assert alpha.self_perform_indicators == ["Explicit historical self-perform record"]
    assert "Wrong Scope Inc" not in context.district_presence


def test_every_candidate_has_preserved_evidence() -> None:
    context = service().fetch_contractor_context("P-1")

    assert context is not None
    assert len(context.evidence) == 3
    assert context.evidence[0].contract_number == "07-1001"
    assert context.evidence[0].source_relation == '"main"."ci_contractor_history"'
    evidence_ids = {item.evidence_id for item in context.evidence}
    assert all(set(candidate.evidence_ids) <= evidence_ids for candidate in context.likely_pursuers)


def test_unknown_contractor_history_returns_explicit_empty_context() -> None:
    context = service([]).fetch_contractor_context("P-1")

    assert context is not None
    assert context.confidence is ContractorConfidence.NONE
    assert context.likely_pursuers == []
    assert context.evidence == []


def test_unknown_project_returns_none() -> None:
    intelligence = ContractorIntelligenceService(
        StubProjectService(None),  # type: ignore[arg-type]
        StubHistoryRepository([]),  # type: ignore[arg-type]
    )

    assert intelligence.fetch_contractor_context("missing") is None
