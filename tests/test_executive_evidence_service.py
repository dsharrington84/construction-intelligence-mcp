from pathlib import Path

import duckdb
import pytest

from construction_intelligence_mcp.services.executive_evidence_service import (
    ExecutiveEvidenceService,
)


def test_engine_is_blocked_until_cdp_001_accepts_current_relation(tmp_path: Path) -> None:
    path = tmp_path / "executive.duckdb"
    connection = duckdb.connect(str(path))
    connection.execute(
        """
        CREATE TABLE executive_evidence (
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

    with pytest.raises(RuntimeError, match="CDP-001 is IN REVIEW"):
        ExecutiveEvidenceService(path)


def test_candidate_relation_names_are_not_treated_as_certified(tmp_path: Path) -> None:
    path = tmp_path / "candidate_relations.duckdb"
    connection = duckdb.connect(str(path))
    for relation in (
        "executive_certified_evidence",
        "ci_executive_evidence",
        "executive_evidence",
    ):
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

    with pytest.raises(RuntimeError, match="no current Executive Certified Data Product relation"):
        ExecutiveEvidenceService(path)
