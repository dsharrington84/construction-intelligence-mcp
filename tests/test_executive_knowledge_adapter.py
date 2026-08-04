from pathlib import Path

import duckdb
import pytest

from construction_intelligence_mcp.adapters.duckdb_adapter import DuckDBAdapter
from construction_intelligence_mcp.adapters.executive_knowledge_adapter import (
    ExecutiveKnowledgeAdapter,
)


def create_normalized_warehouse(database: Path) -> None:
    connection = duckdb.connect(str(database))
    connection.execute(
        """
        CREATE TABLE ci_executive_knowledge_section_refined_v4 (
            refined_section_key VARCHAR,
            source_section_key VARCHAR,
            refined_status VARCHAR,
            programs VARCHAR,
            districts VARCHAR,
            geographic_applicability VARCHAR
        );
        CREATE TABLE ci_executive_knowledge_section_source (
            section_key VARCHAR,
            section_text VARCHAR,
            section_heading VARCHAR,
            source_asset_id VARCHAR,
            source_page_number INTEGER
        );
        CREATE TABLE ci_executive_source_asset (
            source_asset_id VARCHAR,
            source_asset_title VARCHAR,
            document_year INTEGER,
            document_version VARCHAR
        );
        """
    )
    connection.executemany(
        "INSERT INTO ci_executive_knowledge_section_source VALUES (?, ?, ?, ?, ?)",
        [
            ("S-1", "Certified safety finding", "Safety", "D-1", 4),
            ("S-2", "Certified context finding", "Context", "D-1", 5),
            ("S-3", "Excluded finding", "Review", "D-1", 6),
        ],
    )
    connection.execute(
        "INSERT INTO ci_executive_source_asset VALUES ('D-1', '2025 Strategic Plan', 2025, 'final')"
    )
    connection.executemany(
        "INSERT INTO ci_executive_knowledge_section_refined_v4 VALUES (?, ?, ?, ?, ?, ?)",
        [
            ("E-1", "S-1", "USABLE", '["SHOPP"]', "[7]", None),
            ("E-2", "S-2", "USABLE_WITH_LIMITATION", None, None, "statewide"),
            ("E-3", "S-3", "REVIEW_REQUIRED", None, None, None),
            ("E-4", "S-3", "EXCLUDED", None, None, None),
            ("E-5", "S-2", "CONTEXT_ONLY", None, None, "statewide"),
        ],
    )
    connection.close()


def test_three_relation_governed_assembly_preserves_lineage_and_statuses(tmp_path: Path) -> None:
    database = tmp_path / "executive.duckdb"
    create_normalized_warehouse(database)

    adapter = ExecutiveKnowledgeAdapter(DuckDBAdapter(database))
    records = adapter.fetch_records()

    assert adapter.source_relation.endswith('"ci_executive_knowledge_section_refined_v4"')
    assert adapter.base_section_relation.endswith('"ci_executive_knowledge_section_source"')
    assert adapter.source_document_relation.endswith('"ci_executive_source_asset"')
    assert [record.evidence_id for record in records] == ["E-1", "E-2", "E-5"]
    assert records[0].source_document == "2025 Strategic Plan"
    assert records[0].source_section_id == "S-1"
    assert records[0].governed_finding == "Certified safety finding"
    assert records[0].programs == ["SHOPP"]
    assert records[0].districts == [7]
    assert records[0].source_year == 2025
    assert records[0].source_lineage["b__source_page_number"] == "4"
    assert adapter.eligible_record_counts_by_status() == {
        "CONTEXT_ONLY": 1,
        "USABLE": 1,
        "USABLE_WITH_LIMITATION": 1,
    }


def test_inline_document_identity_uses_two_relation_assembly(tmp_path: Path) -> None:
    database = tmp_path / "inline.duckdb"
    create_normalized_warehouse(database)
    connection = duckdb.connect(str(database))
    connection.execute(
        "ALTER TABLE ci_executive_knowledge_section_source ADD source_file_name VARCHAR"
    )
    connection.execute(
        "UPDATE ci_executive_knowledge_section_source SET source_file_name = 'plan.pdf'"
    )
    connection.execute("DROP TABLE ci_executive_source_asset")
    connection.close()

    adapter = ExecutiveKnowledgeAdapter(DuckDBAdapter(database))

    assert adapter.source_document_relation is None
    assert adapter.fetch_records()[0].source_document == "plan.pdf"


def test_incompatible_higher_refined_version_is_skipped(tmp_path: Path) -> None:
    database = tmp_path / "versions.duckdb"
    create_normalized_warehouse(database)
    connection = duckdb.connect(str(database))
    connection.execute(
        "CREATE TABLE ci_executive_knowledge_section_refined_v99 "
        "(refined_section_key VARCHAR, refined_status VARCHAR)"
    )
    connection.close()

    adapter = ExecutiveKnowledgeAdapter(DuckDBAdapter(database))

    assert adapter.source_relation.endswith('"ci_executive_knowledge_section_refined_v4"')


def test_missing_base_lineage_has_actionable_diagnostic(tmp_path: Path) -> None:
    database = tmp_path / "missing-base.duckdb"
    connection = duckdb.connect(str(database))
    connection.execute(
        "CREATE TABLE ci_executive_knowledge_section_refined_v8 "
        "(refined_section_key VARCHAR, source_section_key VARCHAR, refined_status VARCHAR)"
    )
    connection.close()

    with pytest.raises(RuntimeError, match="base-content.*join path") as error:
        ExecutiveKnowledgeAdapter(DuckDBAdapter(database))

    assert "ci_executive_knowledge_section_refined_v8" in str(error.value)
    assert "source_section_id=source_section_key" in str(error.value)


def test_missing_document_lineage_has_actionable_diagnostic(tmp_path: Path) -> None:
    database = tmp_path / "missing-document.duckdb"
    connection = duckdb.connect(str(database))
    connection.execute(
        """
        CREATE TABLE ci_executive_knowledge_section_refined (
            refined_section_key VARCHAR, source_section_key VARCHAR, refined_status VARCHAR
        );
        CREATE TABLE ci_executive_knowledge_section_source (
            section_key VARCHAR, section_text VARCHAR
        );
        """
    )
    connection.close()

    with pytest.raises(RuntimeError, match="source-document join path"):
        ExecutiveKnowledgeAdapter(DuckDBAdapter(database))


def test_duplicate_evidence_is_deterministically_deduplicated(tmp_path: Path) -> None:
    database = tmp_path / "duplicates.duckdb"
    create_normalized_warehouse(database)
    connection = duckdb.connect(str(database))
    connection.execute(
        "INSERT INTO ci_executive_knowledge_section_refined_v4 VALUES "
        "('E-1', 'S-1', 'USABLE', NULL, NULL, NULL)"
    )
    connection.close()

    adapter = ExecutiveKnowledgeAdapter(DuckDBAdapter(database))
    records = adapter.fetch_records()

    assert [record.evidence_id for record in records].count("E-1") == 1
    assert adapter.duplicate_evidence_id_count == 1


def test_unmatched_lineage_is_counted(tmp_path: Path) -> None:
    database = tmp_path / "unmatched.duckdb"
    create_normalized_warehouse(database)
    connection = duckdb.connect(str(database))
    connection.execute(
        "INSERT INTO ci_executive_knowledge_section_refined_v4 VALUES "
        "('E-X', 'missing', 'USABLE', NULL, NULL, NULL)"
    )
    connection.close()

    adapter = ExecutiveKnowledgeAdapter(DuckDBAdapter(database))
    adapter.fetch_records()

    assert adapter.unmatched_refined_section_count == 1


def test_discovery_uses_one_connection_for_all_candidate_schemas(tmp_path: Path) -> None:
    database = tmp_path / "connections.duckdb"
    create_normalized_warehouse(database)

    class CountingAdapter(DuckDBAdapter):
        connection_count = 0

        def connect(self):
            self.connection_count += 1
            return super().connect()

    adapter = CountingAdapter(database)
    executive = ExecutiveKnowledgeAdapter(adapter)

    assert adapter.connection_count == 1
    executive.fetch_records()
    assert adapter.connection_count == 2


def test_zero_overlap_newer_path_is_rejected_for_valid_lower_version(tmp_path: Path) -> None:
    database = tmp_path / "overlap.duckdb"
    create_normalized_warehouse(database)
    connection = duckdb.connect(str(database))
    connection.execute(
        "CREATE TABLE ci_executive_knowledge_section_refined_v9 AS "
        "SELECT refined_section_key, 'OTHER-' || source_section_key source_section_key, "
        "refined_status, programs, districts, geographic_applicability "
        "FROM ci_executive_knowledge_section_refined_v4"
    )
    connection.close()

    adapter = ExecutiveKnowledgeAdapter(DuckDBAdapter(database))

    assert adapter.source_relation.endswith('"ci_executive_knowledge_section_refined_v4"')
    rejected = [
        path
        for path in adapter.candidate_path_diagnostics
        if path["refined_relation"].endswith('"ci_executive_knowledge_section_refined_v9"')
    ]
    assert rejected
    assert {path["rejection_reason"] for path in rejected} == {"zero eligible lineage overlap"}


def test_candidate_relation_is_not_treated_as_governed_base_content(tmp_path: Path) -> None:
    database = tmp_path / "candidate.duckdb"
    create_normalized_warehouse(database)
    connection = duckdb.connect(str(database))
    connection.execute(
        "CREATE TABLE ci_executive_semantic_candidate_v20 AS "
        "SELECT section_key, section_text, source_asset_id, "
        "'Candidate label' source_asset_title "
        "FROM ci_executive_knowledge_section_source"
    )
    connection.close()

    adapter = ExecutiveKnowledgeAdapter(DuckDBAdapter(database))

    assert "candidate" not in adapter.base_section_relation
    assert not any(
        "candidate" in path["base_relation"] for path in adapter.candidate_path_diagnostics
    )


def test_many_to_many_path_is_rejected_for_governed_many_to_one_path(tmp_path: Path) -> None:
    database = tmp_path / "multiplication.duckdb"
    create_normalized_warehouse(database)
    connection = duckdb.connect(str(database))
    connection.execute(
        "CREATE TABLE ci_executive_knowledge_section_current AS "
        "SELECT * FROM ci_executive_knowledge_section_source"
    )
    connection.execute(
        "INSERT INTO ci_executive_knowledge_section_current "
        "SELECT * FROM ci_executive_knowledge_section_source WHERE section_key = 'S-1'"
    )
    connection.close()

    adapter = ExecutiveKnowledgeAdapter(DuckDBAdapter(database))

    assert adapter.base_section_relation.endswith('"ci_executive_knowledge_section_source"')
    multiplied = [
        path
        for path in adapter.candidate_path_diagnostics
        if path["base_relation"].endswith('"ci_executive_knowledge_section_current"')
    ]
    assert multiplied
    assert all("many-to-many" in path["rejection_reason"] for path in multiplied)


def test_status_normalization_and_diagnostics_reconcile(tmp_path: Path) -> None:
    database = tmp_path / "diagnostics.duckdb"
    create_normalized_warehouse(database)
    connection = duckdb.connect(str(database))
    connection.execute(
        "UPDATE ci_executive_knowledge_section_refined_v4 "
        "SET refined_status = ' usable ' WHERE refined_section_key = 'E-1'"
    )
    connection.execute(
        "INSERT INTO ci_executive_knowledge_section_refined_v4 VALUES "
        "('E-X', 'NOT-THERE', 'USABLE', NULL, NULL, NULL)"
    )
    connection.close()

    adapter = ExecutiveKnowledgeAdapter(DuckDBAdapter(database))
    records = adapter.fetch_records()
    metrics = adapter.diagnostics["selected_path_metrics"]

    assert "E-1" in {record.evidence_id for record in records}
    assert metrics["eligible_refined_rows"] == 4
    assert metrics["matched_refined_rows"] == 3
    assert metrics["unmatched_refined_rows"] == 1
    assert metrics["rows_surviving_required_fields"] == 3
    assert metrics["rows_converted_to_records"] == 3
    assert metrics["rows_removed_as_duplicate_evidence_ids"] == 0
    assert adapter.diagnostics == adapter.diagnostics
