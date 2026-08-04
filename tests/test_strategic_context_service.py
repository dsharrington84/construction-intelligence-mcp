from __future__ import annotations

from construction_intelligence_mcp.adapters.executive_knowledge_adapter import (
    ExecutiveContractError,
    ExecutiveKnowledgeAdapter,
)
from construction_intelligence_mcp.models.project import ProjectDetail
from construction_intelligence_mcp.models.strategic_context import (
    EvidenceStrength,
    EvidenceType,
    ExecutiveEvidence,
    RefinedStatus,
    SourceConfidence,
    SourceLineage,
)
from construction_intelligence_mcp.services.strategic_context_service import StrategicContextService


def evidence(evidence_id: str, **values) -> ExecutiveEvidence:
    refined_status = values.pop("refined_status", RefinedStatus.USABLE)
    return ExecutiveEvidence(
        evidence_id=evidence_id,
        source_section_id=f"section-{evidence_id}",
        source_document="2024 Caltrans plan",
        source_excerpt="Preserved source text.",
        refined_status=refined_status,
        evidence_type=EvidenceType.REFINED_SECTION,
        source_lineage=SourceLineage(
            relations=["certified.source_section", "certified.refined_section"],
            keys={"section_id": f"section-{evidence_id}"},
        ),
        **values,
    )


def project() -> ProjectDetail:
    return ProjectDetail(
        project_id="P-1",
        title="Bridge work",
        district=7,
        county="Los Angeles",
        route="5",
        project_type="Bridge",
        primary_scope="Bridge Replacement",
    )


def test_evidence_backed_matching_statuses_deduplication_and_confidence() -> None:
    records = [
        evidence("direct", route="5", program="SHOPP", objective="Preserve bridges"),
        evidence("support", asset_category="Bridge", strategic_theme="Resilience"),
        evidence("direct", route="5", program="SHOPP", objective="Preserve bridges"),
        evidence("review", route="5", refined_status=RefinedStatus.REVIEW_REQUIRED),
        evidence("excluded", route="5", refined_status=RefinedStatus.EXCLUDED),
    ]

    result = StrategicContextService(lambda: records).fetch_strategic_context(project())

    assert [item.evidence_id for item in result.evidence] == ["direct", "support"]
    assert [item.evidence_strength for item in result.evidence] == [
        EvidenceStrength.DIRECT,
        EvidenceStrength.SUPPORTING,
    ]
    assert result.programs[0].model_dump() == {
        "value": "SHOPP",
        "evidence_ids": ["direct"],
    }
    assert result.source_confidence == SourceConfidence.HIGH
    assert result.evidence[0].source_excerpt == "Preserved source text."
    assert result.evidence[0].source_lineage.relations == [
        "certified.source_section",
        "certified.refined_section",
    ]


def test_context_only_is_contextual_and_limitations_reduce_confidence() -> None:
    record = evidence(
        "context",
        route="5",
        refined_status=RefinedStatus.CONTEXT_ONLY,
        limitations=["Source section is contextual only."],
    )

    result = StrategicContextService(lambda: [record]).fetch_strategic_context(project())

    assert result.evidence[0].evidence_strength == EvidenceStrength.CONTEXTUAL
    assert result.source_confidence == SourceConfidence.LIMITED
    assert result.limitations == ["Source section is contextual only."]


def test_no_defensible_alignment_returns_none_confidence() -> None:
    result = StrategicContextService(
        lambda: [evidence("other", district=11, program="Local program")]
    ).fetch_strategic_context(project())

    assert result.evidence == []
    assert result.source_confidence == SourceConfidence.NONE


def test_checked_in_uncertified_artifacts_fail_clearly() -> None:
    adapter = ExecutiveKnowledgeAdapter()

    assert adapter.diagnostics.certification_status == "UNAVAILABLE"
    assert adapter.diagnostics.selected_relations == []
    try:
        adapter.list_evidence()
    except ExecutiveContractError as exc:
        assert "010A relation inventory is not generated" in str(exc)
    else:
        raise AssertionError("Uncertified Executive evidence must not be returned")
