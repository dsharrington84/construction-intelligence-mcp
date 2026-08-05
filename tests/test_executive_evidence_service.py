from pathlib import Path

import duckdb
import pytest

from construction_intelligence_mcp.models.executive_evidence import ExecutiveEvidence
from construction_intelligence_mcp.services.executive_evidence_service import (
    ExecutiveEvidenceService,
)


@pytest.fixture
def database(tmp_path: Path) -> Path:
    path = tmp_path / "executive.duckdb"
    connection = duckdb.connect(str(path))
    connection.execute(
        """
        CREATE TABLE executive_evidence (
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
        "INSERT INTO executive_evidence VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
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


def test_evidence_assembly_preserves_source_text_lineage_and_order(database: Path) -> None:
    result = ExecutiveEvidenceService(database).fetch_executive_evidence()

    assert [item.evidence_id for item in result.evidence] == ["E-1", "E-2", "E-3"]
    assert all(isinstance(item, ExecutiveEvidence) for item in result.evidence)
    first = result.evidence[0]
    assert first.source_text == "Improve bridge resilience."
    assert first.source_document == "Executive Plan"
    assert first.source_section_id == "SEC-1"
    assert first.source_lineage.source_relation.endswith('"executive_evidence"')
    assert first.source_lineage.source_keys["refined_section_id"] == "REF-1"
    assert first.semantic_metadata == {"program": "SHOPP", "strategic_theme": "Resilience"}


def test_eligibility_duplicates_and_diagnostics(database: Path) -> None:
    diagnostics = ExecutiveEvidenceService(database).fetch_executive_evidence().diagnostics

    assert diagnostics.selected_relation.endswith('"executive_evidence"')
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


def test_ambiguous_certified_relations_fail_governed_validation(tmp_path: Path) -> None:
    path = tmp_path / "ambiguous.duckdb"
    connection = duckdb.connect(str(path))
    for relation in ("executive_evidence", "ci_executive_evidence"):
        connection.execute(
            f"""
            CREATE TABLE {relation} (
                evidence_id VARCHAR,
                evidence_type VARCHAR,
                source_document VARCHAR,
                source_section_id VARCHAR,
                source_text VARCHAR,
                refinement_status VARCHAR
            )
            """
        )
    connection.close()

    with pytest.raises(RuntimeError, match="Ambiguous Executive Certified Data Product"):
        ExecutiveEvidenceService(path)
