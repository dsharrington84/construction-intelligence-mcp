from pathlib import Path

import duckdb
import pytest

from construction_intelligence_mcp.adapters.duckdb_adapter import DuckDBAdapter
from construction_intelligence_mcp.adapters.executive_knowledge_adapter import (
    ExecutiveKnowledgeAdapter,
)


def create_refined_relation(database: Path, version: int) -> None:
    connection = duckdb.connect(str(database))
    connection.execute(
        f"""
        CREATE TABLE ci_executive_knowledge_section_refined_v{version} (
            executive_knowledge_section_id VARCHAR,
            document_title VARCHAR,
            document_year INTEGER,
            section_lineage_id VARCHAR,
            section_heading VARCHAR,
            refined_section_summary VARCHAR,
            program_alignment VARCHAR,
            district_numbers VARCHAR,
            geographic_applicability VARCHAR,
            refinement_status VARCHAR,
            source_page_number INTEGER
        )
        """
    )
    connection.close()


def test_resolves_newest_refined_relation_and_actual_status_contract(tmp_path: Path) -> None:
    database = tmp_path / "executive.duckdb"
    create_refined_relation(database, 3)
    create_refined_relation(database, 4)
    connection = duckdb.connect(str(database))
    connection.executemany(
        """
        INSERT INTO ci_executive_knowledge_section_refined_v4
        VALUES (?, 'Plan', 2025, ?, 'Heading', ?, '["SHOPP"]', '[7]', 'statewide', ?, 12)
        """,
        [
            ("usable", "lineage-1", "Usable governed finding", "USABLE"),
            ("limited", "lineage-2", "Limited governed finding", "USABLE_WITH_LIMITATION"),
            ("context", "lineage-3", "Context governed finding", "CONTEXT_ONLY"),
            ("review", "lineage-4", "Unreviewed finding", "REVIEW_REQUIRED"),
            ("excluded", "lineage-5", "Excluded finding", "EXCLUDED"),
        ],
    )
    connection.close()

    adapter = ExecutiveKnowledgeAdapter(DuckDBAdapter(database))
    records = adapter.fetch_records()

    assert adapter.source_relation == '"main"."ci_executive_knowledge_section_refined_v4"'
    assert [record.evidence_id for record in records] == ["usable", "limited", "context"]
    assert records[0].programs == ["SHOPP"]
    assert records[0].districts == [7]
    assert records[0].source_lineage["source_page_number"] == "12"
    assert adapter.eligible_record_counts_by_status() == {
        "CONTEXT_ONLY": 1,
        "USABLE": 1,
        "USABLE_WITH_LIMITATION": 1,
    }


def test_incompatible_higher_version_is_skipped_for_compatible_lower_version(
    tmp_path: Path,
) -> None:
    database = tmp_path / "versions.duckdb"
    create_refined_relation(database, 3)
    connection = duckdb.connect(str(database))
    connection.execute(
        """
        CREATE TABLE ci_executive_knowledge_section_refined_v17 (
            section_id VARCHAR,
            refinement_status VARCHAR,
            unrelated_payload VARCHAR
        )
        """
    )
    connection.close()

    adapter = ExecutiveKnowledgeAdapter(DuckDBAdapter(database))

    assert adapter.source_relation == '"main"."ci_executive_knowledge_section_refined_v3"'
    incompatible = adapter.inspected_relations[
        '"main"."ci_executive_knowledge_section_refined_v17"'
    ]
    assert incompatible["source_document"] is None
    assert incompatible["governed_finding"] is None


def test_compatible_current_relation_outranks_versioned_relation(tmp_path: Path) -> None:
    database = tmp_path / "current.duckdb"
    create_refined_relation(database, 12)
    connection = duckdb.connect(str(database))
    connection.execute(
        """
        CREATE TABLE ci_executive_knowledge_section_certified AS
        SELECT * FROM ci_executive_knowledge_section_refined_v12
        """
    )
    connection.close()

    adapter = ExecutiveKnowledgeAdapter(DuckDBAdapter(database))

    assert adapter.source_relation == '"main"."ci_executive_knowledge_section_certified"'


def test_unversioned_refined_relation_outranks_compatible_version(tmp_path: Path) -> None:
    database = tmp_path / "refined.duckdb"
    create_refined_relation(database, 20)
    connection = duckdb.connect(str(database))
    connection.execute(
        """
        CREATE TABLE ci_executive_knowledge_section_refined AS
        SELECT * FROM ci_executive_knowledge_section_refined_v20
        """
    )
    connection.close()

    adapter = ExecutiveKnowledgeAdapter(DuckDBAdapter(database))

    assert adapter.source_relation == '"main"."ci_executive_knowledge_section_refined"'


def test_semantic_column_resolution_supports_governed_schema_variants(tmp_path: Path) -> None:
    database = tmp_path / "semantic.duckdb"
    connection = duckdb.connect(str(database))
    connection.execute(
        """
        CREATE TABLE ci_executive_knowledge_section_current (
            governed_section_uid VARCHAR,
            executive_document_key VARCHAR,
            source_parent_section_key VARCHAR,
            refined_narrative_content VARCHAR,
            quality_refinement_status VARCHAR
        )
        """
    )
    connection.close()

    adapter = ExecutiveKnowledgeAdapter(DuckDBAdapter(database))

    assert adapter.resolved_fields["evidence_id"] == "governed_section_uid"
    assert adapter.resolved_fields["source_document"] == "executive_document_key"
    assert adapter.resolved_fields["source_section_id"] == "source_parent_section_key"
    assert adapter.resolved_fields["governed_finding"] == "refined_narrative_content"
    assert adapter.resolved_fields["refined_status"] == "quality_refinement_status"


def test_failure_diagnostics_list_every_inspected_relation_and_missing_concepts(
    tmp_path: Path,
) -> None:
    database = tmp_path / "incompatible.duckdb"
    connection = duckdb.connect(str(database))
    connection.execute(
        """
        CREATE TABLE ci_executive_knowledge_section_refined_v17 (
            section_id VARCHAR,
            refinement_status VARCHAR
        );
        CREATE TABLE ci_executive_knowledge_section_refined_v18 (
            document_title VARCHAR,
            refined_text VARCHAR
        );
        """
    )
    connection.close()

    with pytest.raises(RuntimeError) as error:
        ExecutiveKnowledgeAdapter(DuckDBAdapter(database))

    message = str(error.value)
    assert "ci_executive_knowledge_section_refined_v17" in message
    assert "ci_executive_knowledge_section_refined_v18" in message
    assert "source_document" in message
    assert "source_section_id" in message
    assert "governed_finding" in message
    assert "refined_status" in message
