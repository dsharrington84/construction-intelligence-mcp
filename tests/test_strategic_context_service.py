from datetime import date

from construction_intelligence_mcp.adapters.executive_knowledge_adapter import (
    ExecutiveKnowledgeRecord,
)
from construction_intelligence_mcp.models.project import ProjectDetail
from construction_intelligence_mcp.models.strategic_context import SourceConfidence
from construction_intelligence_mcp.server import fetch_strategic_context
from construction_intelligence_mcp.services.project_scope_classifier import ProjectScopeClassifier
from construction_intelligence_mcp.services.strategic_context_service import StrategicContextService


def project(project_id: str = "P-1") -> ProjectDetail:
    item = ProjectDetail(
        project_id=project_id,
        title="Bridge preservation on Route 5",
        description="Rehabilitate bridge deck",
        district=7,
        county="Los Angeles",
        route="5",
        project_type="Bridge",
        primary_scope="Other",
        advertisement_date=date(2028, 1, 1),
        advertisement_fiscal_year=2028,
        raw_record={"program": "SHOPP"},
    )
    item.classified_scope = ProjectScopeClassifier().classify(item)
    item.primary_scope = item.classified_scope.primary_scope.value
    return item


class Projects:
    def __init__(self, item: ProjectDetail | None = None) -> None:
        self.item = item

    def fetch_project(self, project_id: str) -> ProjectDetail | None:
        return self.item if self.item and self.item.project_id == project_id else None


class Knowledge:
    def __init__(self, records: list[ExecutiveKnowledgeRecord]) -> None:
        self.records = records

    def fetch_records(self) -> list[ExecutiveKnowledgeRecord]:
        return self.records


def finding(evidence_id: str, **values) -> ExecutiveKnowledgeRecord:
    return ExecutiveKnowledgeRecord(
        evidence_id=evidence_id,
        source_document="2028 State Highway Plan",
        source_year=2028,
        source_section_id=f"section-{evidence_id}",
        source_heading="Investment priorities",
        governed_finding=f"Certified finding {evidence_id}",
        refined_status="certified",
        **values,
    )


def service(records: list[ExecutiveKnowledgeRecord], item: ProjectDetail | None = None):
    return StrategicContextService(Projects(item or project()), Knowledge(records))  # type: ignore[arg-type]


def test_direct_program_and_supporting_evidence_produce_high_confidence() -> None:
    result = service(
        [
            finding("B", districts=[7], objectives=["Reduce lifecycle risk"]),
            finding("A", programs=["SHOPP"], expected_outcomes=["Reliable assets"]),
        ]
    ).fetch_strategic_context("P-1")

    assert result is not None
    assert result.source_confidence == SourceConfidence.HIGH
    assert [item.evidence_id for item in result.evidence] == ["A", "B"]
    assert result.programs[0].evidence_ids == ["A"]
    assert result.evidence[0].source_section_id == "section-A"


def test_district_and_scope_theme_alignment_are_supporting_and_deterministic() -> None:
    result = service(
        [
            finding("scope", strategic_themes=["Bridge Rehabilitation"]),
            finding("district", districts=[7], policy_drivers=["District asset plan"]),
        ]
    ).fetch_strategic_context("P-1")

    assert result is not None
    assert result.source_confidence == SourceConfidence.MODERATE
    assert [item.evidence_id for item in result.evidence] == ["district", "scope"]
    assert all(item.evidence_strength == "SUPPORTING" for item in result.evidence)


def test_statewide_only_is_limited_and_no_evidence_is_explicit_none() -> None:
    contextual = service(
        [finding("state", geographic_applicability="statewide", strategic_themes=["Resilience"])]
    ).fetch_strategic_context("P-1")
    empty = service([]).fetch_strategic_context("P-1")

    assert contextual is not None and contextual.source_confidence == SourceConfidence.LIMITED
    assert empty is not None and empty.source_confidence == SourceConfidence.NONE
    assert empty.evidence == [] and empty.programs == []


def test_duplicate_evidence_is_removed_and_conclusion_lineage_is_merged() -> None:
    duplicate = finding("same", districts=[7], programs=["Asset Preservation"])
    result = service([duplicate, duplicate]).fetch_strategic_context("P-1")

    assert result is not None
    assert len(result.evidence) == 1
    assert result.programs[0].evidence_ids == ["same"]


def test_missing_project_returns_none() -> None:
    context_service = StrategicContextService(Projects(None), Knowledge([]))  # type: ignore[arg-type]
    assert context_service.fetch_strategic_context("missing") is None


def test_mcp_serializes_governed_context(monkeypatch) -> None:
    context_service = service([finding("direct", project_id="P-1", programs=["SHOPP"])])
    monkeypatch.setattr(
        "construction_intelligence_mcp.server._strategic_context_service", lambda: context_service
    )

    response = fetch_strategic_context("P-1")

    assert response is not None
    assert response["strategic_context_id"] == "strategic-context:P-1"
    assert response["evidence"][0]["evidence_strength"] == "DIRECT"
