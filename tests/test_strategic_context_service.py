from __future__ import annotations

from datetime import date
import inspect

import pytest
from pydantic import ValidationError

from construction_intelligence_mcp.models.executive_evidence import (
    ExecutiveEvidence,
    ExecutiveEvidenceDiagnostics,
    ExecutiveEvidenceLineage,
    ExecutiveEvidenceResult,
)
from construction_intelligence_mcp.models.project import ProjectDetail
from construction_intelligence_mcp.models.strategic_context import (
    EvidenceStrength,
    SourceConfidence,
    StrategicConclusion,
    StrategicContext,
    StrategicEvidence,
)
from construction_intelligence_mcp.services.strategic_context_service import StrategicContextService


def project() -> ProjectDetail:
    return ProjectDetail(
        project_id="P-1",
        title="Bridge project",
        description="Replace bridge",
        district=7,
        county="Los Angeles",
        route="5",
        project_type="Bridge",
        primary_scope="Bridge Replacement",
        advertisement_date=date(2027, 2, 1),
    )


def lineage(evidence_id: str = "E-1") -> ExecutiveEvidenceLineage:
    return ExecutiveEvidenceLineage(
        source_relation='"main"."executive_evidence"',
        source_keys={"evidence_id": evidence_id},
        source_section_id="S-1",
    )


def evidence(
    evidence_id: str,
    metadata: dict,
    *,
    status: str = "USABLE",
    limitations: list[str] | None = None,
) -> ExecutiveEvidence:
    return ExecutiveEvidence(
        evidence_id=evidence_id,
        evidence_type="executive_evidence",
        source_document="Ten-Year Plan",
        source_section_id=f"S-{evidence_id}",
        source_text=f"Source text for {evidence_id}",
        refinement_status=status,  # type: ignore[arg-type]
        source_lineage=lineage(evidence_id),
        limitations=limitations or [],
        semantic_metadata=metadata,
    )


def diagnostics(**overrides) -> ExecutiveEvidenceDiagnostics:
    data = dict(
        selected_relation='"main"."executive_evidence"',
        relation_role="executive_certified_data_product",
        join_path=['"main"."executive_evidence"'],
        eligible_evidence_count=1,
        rejected_evidence_count=0,
        duplicate_evidence_count=0,
        source_text_coverage=1,
        source_document_coverage=1,
        lineage_coverage=1,
        unknown_statuses=[],
        final_evidence_count=1,
        status_distribution={"USABLE": 1},
    )
    data.update(overrides)
    return ExecutiveEvidenceDiagnostics(**data)


class ProjectStub:
    def __init__(self, value: ProjectDetail | None = None) -> None:
        self.value = value if value is not None else project()

    def fetch_project(self, project_id: str) -> ProjectDetail | None:
        return self.value if self.value and self.value.project_id == project_id else None


class EvidenceStub:
    def __init__(
        self, items: list[ExecutiveEvidence], diag: ExecutiveEvidenceDiagnostics | None = None
    ) -> None:
        self.result = ExecutiveEvidenceResult(
            evidence=items, diagnostics=diag or diagnostics(final_evidence_count=len(items))
        )

    def fetch_executive_evidence(self, *, limit: int | None = None) -> ExecutiveEvidenceResult:
        return self.result


def context(
    items: list[ExecutiveEvidence], proj: ProjectDetail | None = None
) -> StrategicContext | None:
    return StrategicContextService(ProjectStub(proj), EvidenceStub(items)).fetch_strategic_context(
        "P-1"
    )


def first_strength(result: StrategicContext) -> EvidenceStrength:
    return result.evidence[0].evidence_strength


def test_explicit_project_linkage_is_direct_and_different_project_rejected() -> None:
    result = context(
        [
            evidence("E-2", {"project_id": "P-2", "program": "SHOPP"}),
            evidence("E-1", {"project_id": "P-1", "program": "SHOPP"}),
        ]
    )
    assert result is not None
    assert [item.evidence_id for item in result.evidence] == ["E-1"]
    assert first_strength(result) == EvidenceStrength.DIRECT
    assert result.programs == [StrategicConclusion(value="SHOPP", evidence_ids=["E-1"])]


@pytest.mark.parametrize(
    ("metadata", "relationship"),
    [
        ({"program": "SHOPP", "district": 7}, "program_plus_governed_project_attribute"),
        ({"district": 7}, "district_linkage"),
        ({"county": "Los Angeles"}, "county_linkage"),
        ({"route": "5"}, "route_linkage"),
        ({"project_type": "Bridge"}, "project_type_or_asset_category_linkage"),
    ],
)
def test_attribute_alignment_is_supporting(metadata: dict, relationship: str) -> None:
    result = context([evidence("E-1", metadata | {"objective": "Preserve assets"})])
    assert result is not None
    assert first_strength(result) == EvidenceStrength.SUPPORTING
    assert result.evidence[0].relationship_to_project == relationship
    assert result.objectives[0].evidence_ids == ["E-1"]


def test_unrelated_strategic_theme_does_not_match() -> None:
    result = context([evidence("E-1", {"strategic_theme": "Resilience"})])
    assert result is not None
    assert result.evidence == []
    assert result.source_confidence == SourceConfidence.NONE


def test_context_only_without_relationship_does_not_match() -> None:
    result = context([evidence("E-1", {"program": "SHOPP"}, status="CONTEXT_ONLY")])
    assert result is not None
    assert result.evidence == []
    assert result.source_confidence == SourceConfidence.NONE


def test_context_only_with_district_linkage_is_contextual_and_creates_no_conclusion() -> None:
    result = context([evidence("E-1", {"district": 7, "program": "SHOPP"}, status="CONTEXT_ONLY")])
    assert result is not None
    assert first_strength(result) == EvidenceStrength.CONTEXTUAL
    assert result.evidence[0].relationship_to_project == "program_plus_governed_project_attribute"
    assert result.programs == []
    assert result.source_confidence == SourceConfidence.LIMITED


def test_statewide_context_only_may_match_as_contextual() -> None:
    result = context(
        [evidence("E-1", {"statewide": True, "program": "SHOPP"}, status="CONTEXT_ONLY")]
    )
    assert result is not None
    assert first_strength(result) == EvidenceStrength.CONTEXTUAL
    assert result.evidence[0].relationship_to_project == "statewide_or_document_context"
    assert result.programs == []
    assert result.source_confidence == SourceConfidence.LIMITED


def test_statewide_evidence_is_contextual() -> None:
    result = context([evidence("E-1", {"statewide": True, "policy_driver": "Safety"})])
    assert result is not None
    assert first_strength(result) == EvidenceStrength.CONTEXTUAL
    assert result.policy_drivers[0].evidence_ids == ["E-1"]
    assert result.source_confidence == SourceConfidence.LIMITED


def test_usable_with_limitation_propagates_and_reduces_confidence() -> None:
    result = context(
        [
            evidence(
                "E-1",
                {"project_id": "P-1", "program": "SHOPP"},
                status="USABLE_WITH_LIMITATION",
                limitations=["limited coverage"],
            )
        ]
    )
    assert result is not None
    assert result.limitations == ["limited coverage"]
    assert result.source_confidence == SourceConfidence.LIMITED


def test_time_horizon_rejection_and_empty_result() -> None:
    result = context([evidence("E-1", {"project_id": "P-1", "applicable_end_date": "2026-01-01"})])
    assert result is not None
    assert result.evidence == []
    assert result.source_confidence == SourceConfidence.NONE
    assert "No defensible Executive evidence matched" in result.limitations[0]


def test_duplicate_evidence_and_ordering_are_deterministic() -> None:
    result = context(
        [
            evidence("E-2", {"project_id": "P-1", "program": "B"}),
            evidence("E-1", {"project_id": "P-1", "program": "A"}),
            evidence("E-1", {"project_id": "P-1", "program": "C"}),
        ]
    )
    assert result is not None
    assert [item.evidence_id for item in result.evidence] == ["E-1", "E-2"]
    assert [item.value for item in result.programs] == ["A", "B"]


def test_model_rejects_invalid_conclusion_evidence_ids() -> None:
    strategic_evidence = StrategicEvidence(
        evidence_id="E-1",
        source_document="Doc",
        source_section_id="S-1",
        source_excerpt="text",
        relationship_to_project="explicit_project_linkage",
        evidence_strength=EvidenceStrength.DIRECT,
        source_lineage=lineage("E-1"),
    )
    with pytest.raises(ValidationError):
        StrategicContext(
            project_id="P-1",
            strategic_context_id="strategic-context:P-1",
            programs=[StrategicConclusion(value="SHOPP", evidence_ids=["missing"])],
            evidence=[strategic_evidence],
            source_confidence=SourceConfidence.MODERATE,
        )


@pytest.mark.parametrize(
    ("items", "expected"),
    [
        (
            [evidence("E-1", {"project_id": "P-1"}), evidence("E-2", {"project_id": "P-1"})],
            SourceConfidence.HIGH,
        ),
        ([evidence("E-1", {"project_id": "P-1"})], SourceConfidence.MODERATE),
        ([evidence("E-1", {"district": 7})], SourceConfidence.MODERATE),
        ([evidence("E-1", {"statewide": True})], SourceConfidence.LIMITED),
    ],
)
def test_confidence_calculation(items: list[ExecutiveEvidence], expected: SourceConfidence) -> None:
    result = context(items)
    assert result is not None
    assert result.source_confidence == expected


def test_missing_project_returns_none() -> None:
    service = StrategicContextService(ProjectStub(None), EvidenceStub([]))
    assert service.fetch_strategic_context("missing") is None


def test_service_has_no_duckdb_access_or_adapter_construction() -> None:
    source = inspect.getsource(StrategicContextService)
    assert "duckdb" not in source.lower()
    assert "ExecutiveEvidenceAdapter" not in source
