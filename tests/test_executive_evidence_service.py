from pathlib import Path

import duckdb
import pytest

from construction_intelligence_mcp.adapters.executive_evidence_adapter import (
    CdpPhysicalImplementationMapping,
)
from construction_intelligence_mcp.models.executive_evidence import ExecutiveEvidence
from construction_intelligence_mcp.services.executive_evidence_service import (
    ExecutiveEvidenceService,
)


@pytest.fixture
def database(tmp_path: Path) -> Path:
    path = tmp_path / "executive.duckdb"
    connection = duckdb.connect(str(path))
    connection.execute("CREATE SCHEMA certified")
    connection.execute("CREATE SCHEMA shadow")
    connection.execute("CREATE SCHEMA staging")
    connection.execute("CREATE TABLE shadow.executive_evidence (placeholder VARCHAR)")
    connection.execute("CREATE TABLE staging.executive_evidence (placeholder VARCHAR)")
    connection.execute(
        """
        CREATE TABLE certified.executive_evidence (
            evidence_id VARCHAR,
            evidence_type VARCHAR,
            source_document VARCHAR,
            source_document_id VARCHAR,
            source_section_id VARCHAR,
            refined_section_id VARCHAR,
            source_asset_id VARCHAR,
            source_text VARCHAR,
            refinement_status VARCHAR,
            limitations VARCHAR,
            program VARCHAR,
            strategic_theme VARCHAR
        )
        """
    )
    connection.executemany(
        "INSERT INTO certified.executive_evidence VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (
                "E-2",
                "policy",
                "Executive Plan",
                "DOC-1",
                "SEC-2",
                "REF-2",
                "ART-1",
                "Invest in freight mobility.",
                "USABLE_WITH_LIMITATION",
                "Planning document",
                "SHOPP",
                "Freight",
            ),
            (
                "E-1",
                "objective",
                "Executive Plan",
                "DOC-1",
                "SEC-1",
                "REF-1",
                "ART-1",
                "Improve bridge resilience.",
                "USABLE",
                None,
                "SHOPP",
                "Resilience",
            ),
            (
                "E-3",
                "note",
                "Executive Plan",
                "DOC-1",
                "SEC-3",
                "REF-3",
                "ART-1",
                "Context only.",
                "CONTEXT_ONLY",
                None,
                None,
                None,
            ),
            (
                "E-4",
                "draft",
                "Executive Plan",
                "DOC-1",
                "SEC-4",
                "REF-4",
                "ART-1",
                "Needs review.",
                "REVIEW_REQUIRED",
                None,
                None,
                None,
            ),
            (
                "E-5",
                "draft",
                "Executive Plan",
                "DOC-1",
                "SEC-5",
                "REF-5",
                "ART-1",
                "Excluded.",
                "EXCLUDED",
                None,
                None,
                None,
            ),
            (
                "E-6",
                "draft",
                "Executive Plan",
                "DOC-1",
                "SEC-6",
                "REF-6",
                "ART-1",
                "Mystery.",
                "MYSTERY",
                None,
                None,
                None,
            ),
            (
                "E-1",
                "duplicate",
                "Executive Plan",
                "DOC-1",
                "SEC-7",
                "REF-7",
                "ART-1",
                "Duplicate.",
                "USABLE",
                None,
                None,
                None,
            ),
            (
                "E-7",
                "broken",
                None,
                "DOC-1",
                "SEC-8",
                "REF-8",
                "ART-1",
                "No document.",
                "USABLE",
                None,
                None,
                None,
            ),
            (
                None,
                "broken",
                "Executive Plan",
                "DOC-1",
                "SEC-9",
                "REF-9",
                "ART-1",
                "No identity.",
                "USABLE",
                None,
                None,
                None,
            ),
        ],
    )
    connection.close()
    return path


@pytest.fixture
def accepted_mapping() -> list[CdpPhysicalImplementationMapping]:
    return [
        CdpPhysicalImplementationMapping(
            product_identifier="CDP-001",
            relation="certified.executive_evidence",
            certification_status="ACCEPTED",
            relation_role="certified_current",
        )
    ]


def test_explicit_accepted_schema_qualified_mapping_succeeds(
    database: Path,
    accepted_mapping: list[CdpPhysicalImplementationMapping],
) -> None:
    result = ExecutiveEvidenceService(database, accepted_mapping).fetch_executive_evidence()

    assert result.diagnostics.final_evidence_count == 3
    assert result.diagnostics.selected_relation == '"certified"."executive_evidence"'


def test_missing_mapping_fails(database: Path) -> None:
    with pytest.raises(RuntimeError, match="No accepted CDP-001 physical implementation mapping"):
        ExecutiveEvidenceService(database, [])


def test_mapping_with_non_accepted_status_fails(database: Path) -> None:
    mapping = [
        CdpPhysicalImplementationMapping(
            product_identifier="CDP-001",
            relation="certified.executive_evidence",
            certification_status="IN_REVIEW",
        )
    ]

    with pytest.raises(RuntimeError, match="not accepted/current"):
        ExecutiveEvidenceService(database, mapping)


def test_mapping_to_nonexistent_relation_fails(database: Path) -> None:
    mapping = [
        CdpPhysicalImplementationMapping(
            product_identifier="CDP-001",
            relation="certified.missing_evidence",
            certification_status="ACCEPTED",
        )
    ]

    with pytest.raises(RuntimeError, match="does not exist"):
        ExecutiveEvidenceService(database, mapping)


def test_two_accepted_mappings_fail_as_ambiguous(database: Path) -> None:
    mappings = [
        CdpPhysicalImplementationMapping("CDP-001", "certified.executive_evidence", "ACCEPTED"),
        CdpPhysicalImplementationMapping("CDP-001", "shadow.executive_evidence", "ACCEPTED"),
    ]

    with pytest.raises(RuntimeError, match="Ambiguous CDP-001 physical implementation mappings"):
        ExecutiveEvidenceService(database, mappings)


def test_same_relation_name_in_two_schemas_does_not_cause_implicit_selection(
    database: Path,
) -> None:
    mapping = [
        CdpPhysicalImplementationMapping(
            product_identifier="CDP-001",
            relation="executive_evidence",
            certification_status="ACCEPTED",
        )
    ]

    with pytest.raises(RuntimeError, match="schema-qualified relation"):
        ExecutiveEvidenceService(database, mapping)


@pytest.mark.parametrize(
    "role",
    ["staging", "candidate", "history", "archive", "quarantine"],
)
def test_prohibited_relation_roles_are_rejected(database: Path, role: str) -> None:
    mapping = [
        CdpPhysicalImplementationMapping(
            product_identifier="CDP-001",
            relation="certified.executive_evidence",
            certification_status="ACCEPTED",
            relation_role=role,
        )
    ]

    with pytest.raises(RuntimeError, match="prohibited relation role"):
        ExecutiveEvidenceService(database, mapping)


def test_required_concept_validation_remains_enforced(tmp_path: Path) -> None:
    path = tmp_path / "missing_required.duckdb"
    connection = duckdb.connect(str(path))
    connection.execute("CREATE SCHEMA certified")
    connection.execute(
        """
        CREATE TABLE certified.executive_evidence (
            evidence_id VARCHAR,
            evidence_type VARCHAR,
            source_document VARCHAR,
            source_section_id VARCHAR,
            refinement_status VARCHAR
        )
        """
    )
    connection.close()
    mapping = [
        CdpPhysicalImplementationMapping(
            product_identifier="CDP-001",
            relation="certified.executive_evidence",
            certification_status="ACCEPTED",
        )
    ]

    with pytest.raises(RuntimeError, match="unresolved required concepts: source_text"):
        ExecutiveEvidenceService(path, mapping)


def test_evidence_assembly_preserves_source_text_lineage_and_order(
    database: Path,
    accepted_mapping: list[CdpPhysicalImplementationMapping],
) -> None:
    result = ExecutiveEvidenceService(database, accepted_mapping).fetch_executive_evidence()

    assert [item.evidence_id for item in result.evidence] == ["E-1", "E-2", "E-3"]
    assert all(isinstance(item, ExecutiveEvidence) for item in result.evidence)
    first = result.evidence[0]
    assert first.source_text == "Improve bridge resilience."
    assert first.source_document == "Executive Plan"
    assert first.source_section_id == "SEC-1"
    assert first.source_lineage.source_relation == '"certified"."executive_evidence"'
    assert first.source_lineage.source_keys["refined_section_id"] == "REF-1"
    assert first.semantic_metadata == {"program": "SHOPP", "strategic_theme": "Resilience"}


def test_eligibility_duplicates_and_diagnostics(
    database: Path,
    accepted_mapping: list[CdpPhysicalImplementationMapping],
) -> None:
    diagnostics = (
        ExecutiveEvidenceService(database, accepted_mapping).fetch_executive_evidence().diagnostics
    )

    assert diagnostics.selected_relation == '"certified"."executive_evidence"'
    assert diagnostics.relation_role == "executive_certified_data_product"
    assert diagnostics.join_path == [diagnostics.selected_relation]
    assert diagnostics.eligible_evidence_count == 6
    assert diagnostics.rejected_evidence_count == 6
    assert diagnostics.duplicate_evidence_count == 1
    assert diagnostics.final_evidence_count == 3
    assert diagnostics.source_text_coverage == 1
    assert diagnostics.source_document_coverage == pytest.approx(8 / 9)
    assert diagnostics.lineage_coverage == pytest.approx(8 / 9)
    assert diagnostics.unknown_statuses == ["MYSTERY"]
    assert diagnostics.status_distribution["REVIEW_REQUIRED"] == 1
