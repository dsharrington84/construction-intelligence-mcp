from __future__ import annotations

from io import StringIO
from pathlib import Path

import duckdb

from construction_intelligence_mcp.runtime.validate import main, run_validation


def _create_database(path: Path, *, rows: bool = True, missing_source_text: bool = False) -> None:
    connection = duckdb.connect(str(path))
    connection.execute("CREATE SCHEMA certified")
    source_text_column = "" if missing_source_text else "source_text VARCHAR,"
    connection.execute(
        f"""
        CREATE TABLE certified.executive_evidence (
            evidence_id VARCHAR,
            evidence_type VARCHAR,
            source_document VARCHAR,
            source_section_id VARCHAR,
            {source_text_column}
            refinement_status VARCHAR
        )
        """
    )
    if rows:
        connection.execute(
            """
            INSERT INTO certified.executive_evidence VALUES
            ('E-1', 'objective', 'Executive Plan', 'SEC-1', 'Improve bridges.', 'USABLE')
            """
        )
    connection.close()


def _environment(database: Path) -> dict[str, str]:
    return {
        "CI_DATABASE": str(database),
        "CDP001_EXECUTIVE_EVIDENCE_RELATION": "certified.executive_evidence",
        "CDP001_EXECUTIVE_EVIDENCE_STATUS": "ACCEPTED",
        "CDP001_EXECUTIVE_EVIDENCE_RELATION_ROLE": "certified_current",
    }


def test_runtime_validator_passes_all_checks(tmp_path: Path) -> None:
    database = tmp_path / "valid.duckdb"
    _create_database(database)
    output = StringIO()

    exit_code = run_validation(environment=_environment(database), stdout=output)

    assert exit_code == 0
    lines = output.getvalue().splitlines()
    assert lines == [
        "PASS CI_DATABASE configured",
        "PASS DuckDB file exists",
        "PASS DuckDB readable",
        "PASS CDP001_EXECUTIVE_EVIDENCE_RELATION configured",
        "PASS Relation schema-qualified",
        "PASS Mapping status ACCEPTED or CURRENT",
        "PASS Mapping role certified_current",
        "PASS Relation exists",
        "PASS Required ExecutiveEvidence concepts resolve",
        "PASS ExecutiveEvidence returns rows",
    ]


def test_runtime_validator_stops_at_missing_database_configuration() -> None:
    output = StringIO()

    exit_code = run_validation(environment={}, stdout=output)

    assert exit_code == 1
    assert output.getvalue() == "FAIL CI_DATABASE configured: CI_DATABASE is not configured.\n"


def test_runtime_validator_stops_at_nonexistent_database(tmp_path: Path) -> None:
    output = StringIO()

    exit_code = run_validation(
        environment={"CI_DATABASE": str(tmp_path / "missing.duckdb")},
        stdout=output,
    )

    assert exit_code == 1
    assert output.getvalue().startswith("PASS CI_DATABASE configured\nFAIL DuckDB file exists:")


def test_runtime_validator_requires_schema_qualified_relation(tmp_path: Path) -> None:
    database = tmp_path / "valid.duckdb"
    _create_database(database)
    environment = _environment(database) | {
        "CDP001_EXECUTIVE_EVIDENCE_RELATION": "executive_evidence"
    }
    output = StringIO()

    exit_code = run_validation(environment=environment, stdout=output)

    assert exit_code == 1
    assert "FAIL Relation schema-qualified:" in output.getvalue()


def test_runtime_validator_requires_accepted_or_current_mapping_status(tmp_path: Path) -> None:
    database = tmp_path / "valid.duckdb"
    _create_database(database)
    environment = _environment(database) | {"CDP001_EXECUTIVE_EVIDENCE_STATUS": "IN_REVIEW"}
    output = StringIO()

    exit_code = run_validation(environment=environment, stdout=output)

    assert exit_code == 1
    assert "FAIL Mapping status ACCEPTED or CURRENT:" in output.getvalue()


def test_runtime_validator_requires_certified_current_role(tmp_path: Path) -> None:
    database = tmp_path / "valid.duckdb"
    _create_database(database)
    environment = _environment(database) | {"CDP001_EXECUTIVE_EVIDENCE_RELATION_ROLE": "staging"}
    output = StringIO()

    exit_code = run_validation(environment=environment, stdout=output)

    assert exit_code == 1
    assert "FAIL Mapping role certified_current:" in output.getvalue()


def test_runtime_validator_reports_missing_relation(tmp_path: Path) -> None:
    database = tmp_path / "valid.duckdb"
    _create_database(database)
    environment = _environment(database) | {
        "CDP001_EXECUTIVE_EVIDENCE_RELATION": "certified.missing"
    }
    output = StringIO()

    exit_code = run_validation(environment=environment, stdout=output)

    assert exit_code == 1
    assert "FAIL Relation exists:" in output.getvalue()


def test_runtime_validator_reports_unresolved_required_concepts(tmp_path: Path) -> None:
    database = tmp_path / "missing_concepts.duckdb"
    _create_database(database, rows=False, missing_source_text=True)
    output = StringIO()

    exit_code = run_validation(environment=_environment(database), stdout=output)

    assert exit_code == 1
    assert (
        "FAIL Required ExecutiveEvidence concepts resolve: Executive Certified Data Product has unresolved"
        in output.getvalue()
    )


def test_runtime_validator_reports_zero_evidence_rows(tmp_path: Path) -> None:
    database = tmp_path / "empty.duckdb"
    _create_database(database, rows=False)
    output = StringIO()

    exit_code = run_validation(environment=_environment(database), stdout=output)

    assert exit_code == 1
    assert "FAIL ExecutiveEvidence returns rows:" in output.getvalue()


def test_runtime_module_usage_requires_validate_argument() -> None:
    output = StringIO()

    exit_code = main([], stdout=output)

    assert exit_code == 2
    assert output.getvalue() == "Usage: python -m construction_intelligence_mcp.runtime validate\n"
