from construction_intelligence_mcp.models.project_intelligence import (
    IntelligenceEvidence,
    ProjectIntelligence,
)
from construction_intelligence_mcp.services.opportunity_context_service import (
    OpportunityContextService,
)

from test_project_intelligence_service import governed_market, governed_project


class StubProjectIntelligenceService:
    def __init__(self, intelligence: ProjectIntelligence | None) -> None:
        self.intelligence = intelligence

    def fetch_project_intelligence(self, project_id: str) -> ProjectIntelligence | None:
        if self.intelligence is None or self.intelligence.project.project_id != project_id:
            return None
        return self.intelligence


def observation(category: str, statement: str, source: str) -> dict:
    return {
        "category": category,
        "statement": statement,
        "evidence": [{"source": source, "statement": f"Evidence for {statement}"}],
    }


def intelligence(**contexts) -> ProjectIntelligence:
    project = governed_project()
    return ProjectIntelligence(
        project=project.model_dump(),
        classification=project.classified_scope,
        market={"market_outlook": governed_market(), "market_trend": None},
        opportunity=None,
        **contexts,
    )


def test_missing_intelligence_is_explicit_and_does_not_invent_explanations() -> None:
    service = OpportunityContextService(StubProjectIntelligenceService(intelligence()))  # type: ignore[arg-type]

    context = service.fetch_opportunity_context("P-1")

    assert context is not None
    assert context.confidence == "limited"
    assert context.opportunity_drivers == []
    assert context.strengths == []
    assert context.weaknesses == []
    assert context.risks == []
    assert context.reasons_surfaced == []
    assert context.portfolio_value == ["Programmed value is $42,000,000."]
    assert service.fetch_opportunity_context("missing") is None


def test_full_intelligence_is_explanatory_typed_and_evidence_backed() -> None:
    full = intelligence(
        executive_signals=[observation("strength", "Matches strategic geography", "strategy")],
        contractor_signals=[observation("risk", "Two incumbent bidders observed", "contractor")],
        cost_signals=[observation("weakness", "Volatile material history", "cost")],
    )
    service = OpportunityContextService(StubProjectIntelligenceService(full))  # type: ignore[arg-type]

    context = service.fetch_opportunity_context("P-1")

    assert context is not None
    assert context.confidence == "high"
    assert context.strengths == ["Matches strategic geography"]
    assert context.weaknesses == ["Volatile material history"]
    assert context.risks == ["Two incumbent bidders observed"]
    assert all(isinstance(item, IntelligenceEvidence) for item in context.evidence)
    assert {item.source for item in context.evidence} == {
        "strategy",
        "contractor",
        "cost",
        "project_intelligence.programmed_value",
    }


def test_output_and_evidence_ordering_are_deterministic() -> None:
    observations = [
        observation("strength", "Zulu", "z-source"),
        observation("strength", "Alpha", "a-source"),
        observation("strength", "Alpha", "a-source"),
    ]
    service = OpportunityContextService(  # type: ignore[arg-type]
        StubProjectIntelligenceService(intelligence(executive_signals=observations))
    )

    context = service.fetch_opportunity_context("P-1")

    assert context is not None
    assert context.strengths == ["Alpha", "Zulu"]
    assert [(item.source, item.statement) for item in context.evidence] == sorted(
        {(item.source, item.statement) for item in context.evidence}
    )
