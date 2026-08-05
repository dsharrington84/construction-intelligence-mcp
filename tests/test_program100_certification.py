from __future__ import annotations

from io import StringIO
from pathlib import Path

import duckdb

from construction_intelligence_mcp.runtime.certify_program100 import run_certification


def _create_certification_database(path: Path, *, include_matching_evidence: bool = True) -> None:
    connection = duckdb.connect(str(path))
    connection.execute(
        """
        CREATE TABLE ci_market_state (
            project_id VARCHAR,
            project_title VARCHAR,
            project_description VARCHAR,
            district INTEGER,
            county VARCHAR,
            route VARCHAR,
            location VARCHAR,
            project_type VARCHAR,
            programmed_amount DOUBLE,
            advertisement_date DATE,
            advertisement_fiscal_year INTEGER
        )
        """
    )
    connection.execute(
        """
        INSERT INTO ci_market_state VALUES
        (
            '07-100001',
            'Los Angeles bridge rehabilitation',
            'Bridge rehabilitation on Route 101 in Los Angeles County.',
            7,
            'Los Angeles',
            '101',
            'Los Angeles',
            'Bridge',
            42000000,
            DATE '2027-03-15',
            2027
        )
        """
    )
    connection.execute("CREATE SCHEMA certified")
    connection.execute(
        """
        CREATE TABLE certified.executive_evidence (
            evidence_id VARCHAR,
            evidence_type VARCHAR,
            source_document VARCHAR,
            source_section_id VARCHAR,
            source_text VARCHAR,
            refinement_status VARCHAR,
            district VARCHAR,
            program VARCHAR,
            objective VARCHAR,
            policy_driver VARCHAR,
            expected_outcome VARCHAR,
            strategic_theme VARCHAR,
            source_document_id VARCHAR,
            source_asset_id VARCHAR,
            refined_section_id VARCHAR,
            producing_pipeline VARCHAR,
            pipeline_version VARCHAR
        )
        """
    )
    district = "7" if include_matching_evidence else "1"
    connection.execute(
        """
        INSERT INTO certified.executive_evidence VALUES
        (
            'E-100',
            'objective',
            'Caltrans Executive Plan',
            'SEC-7',
            'Caltrans prioritizes bridge reliability investments in District 7.',
            'USABLE',
            ?,
            'SHOPP',
            'Improve bridge reliability',
            'Asset condition',
            'Reduced bridge risk',
            'State highway preservation',
            'DOC-1',
            'ASSET-1',
            'REF-1',
            'executive-pipeline',
            '1.0'
        )
        """,
        [district],
    )
    connection.close()


def _environment(database: Path) -> dict[str, str]:
    return {
        "CI_DATABASE": str(database),
        "CDP001_EXECUTIVE_EVIDENCE_RELATION": "certified.executive_evidence",
        "CDP001_EXECUTIVE_EVIDENCE_STATUS": "ACCEPTED",
        "CDP001_EXECUTIVE_EVIDENCE_RELATION_ROLE": "certified_current",
    }


def test_certification_command_runs_runtime_and_generates_business_report(tmp_path: Path) -> None:
    database = tmp_path / "certification.duckdb"
    _create_certification_database(database)
    output = StringIO()

    exit_code = run_certification(environment=_environment(database), stdout=output)

    report = output.getvalue()
    assert exit_code == 0
    assert "PASS ExecutiveEvidence returns rows" in report
    assert "Certification result: PASS" in report
    assert "Project ID: 07-100001" in report
    assert "fetch_project() returned" in report
    assert "fetch_strategic_context() returned eligible Executive evidence" in report
    assert "fetch_project_intelligence() integrated Strategic Context" in report
    assert "Evidence ID: E-100" in report
    assert "Improve bridge reliability" in report


def test_certification_command_stops_when_runtime_validation_fails() -> None:
    output = StringIO()

    exit_code = run_certification(environment={}, stdout=output)

    report = output.getvalue()
    assert exit_code == 1
    assert "FAIL CI_DATABASE configured" in report
    assert "Runtime validation failed; intelligence execution was not attempted." in report
    assert "Governed Southern California project" not in report


def test_certification_command_fails_without_matching_southern_california_evidence(
    tmp_path: Path,
) -> None:
    database = tmp_path / "no_match.duckdb"
    _create_certification_database(database, include_matching_evidence=False)
    output = StringIO()

    exit_code = run_certification(environment=_environment(database), stdout=output)

    report = output.getvalue()
    assert exit_code == 1
    assert (
        "No Southern California governed project received defensible eligible Executive evidence"
        in report
    )
