from __future__ import annotations

from io import StringIO
from pathlib import Path

import duckdb

from construction_intelligence_mcp.models.executive_evidence import (
    ExecutiveEvidence,
    ExecutiveEvidenceDiagnostics,
    ExecutiveEvidenceLineage,
    ExecutiveEvidenceResult,
)
from construction_intelligence_mcp.models.project import ProjectDetail, ProjectSummary
from construction_intelligence_mcp.models.strategic_context import (
    EvidenceStrength,
    SourceConfidence,
    StrategicContext,
    StrategicEvidence,
)
from construction_intelligence_mcp.runtime import certify_program100 as certification_module
from construction_intelligence_mcp.runtime.certify_program100 import (
    BLOCKED_PROJECT_LINKAGE_MESSAGE,
    CertificationResult,
    CertificationStatus,
    certify_program100,
    run_certification,
)


def _create_certification_database(path: Path, *, include_evidence: bool = True) -> None:
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
        ),
        (
            '01-100001',
            'Northern California roadway project',
            'Roadway work outside Southern California.',
            1,
            'Mendocino',
            '1',
            'Mendocino',
            'Roadway',
            99000000,
            DATE '2027-01-15',
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
    if include_evidence:
        connection.execute(
            """
            INSERT INTO certified.executive_evidence VALUES
            (
                'E-100',
                'objective',
                'Caltrans Executive Plan',
                'SEC-7',
                'Caltrans prioritizes bridge reliability investments in Southern California.',
                'USABLE',
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


def test_certification_command_runs_runtime_first_and_reports_blocked_certification(
    tmp_path: Path,
) -> None:
    database = tmp_path / "certification.duckdb"
    _create_certification_database(database)
    output = StringIO()

    exit_code = run_certification(environment=_environment(database), stdout=output)

    report = output.getvalue()
    assert exit_code == 1
    assert "PASS ExecutiveEvidence returns rows" in report
    assert "Certification result: BLOCKED" in report
    assert BLOCKED_PROJECT_LINKAGE_MESSAGE in report


def test_certification_command_stops_when_runtime_validation_fails() -> None:
    output = StringIO()

    exit_code = run_certification(environment={}, stdout=output)

    report = output.getvalue()
    assert exit_code == 1
    assert "FAIL CI_DATABASE configured" in report
    assert "Runtime validation failed; intelligence execution was not attempted." in report
    assert "Governed Southern California project" not in report


def test_certification_command_selects_southern_california_project(tmp_path: Path) -> None:
    database = tmp_path / "southern.duckdb"
    _create_certification_database(database)
    output = StringIO()

    run_certification(environment=_environment(database), stdout=output)

    report = output.getvalue()
    assert "Project ID: 07-100001" in report
    assert "District: 7" in report
    assert "Project ID: 01-100001" not in report


def test_certification_command_reports_no_defensible_matching_evidence(tmp_path: Path) -> None:
    database = tmp_path / "no_match.duckdb"
    _create_certification_database(database)
    output = StringIO()

    exit_code = run_certification(environment=_environment(database), stdout=output)

    report = output.getvalue()
    assert exit_code == 1
    assert BLOCKED_PROJECT_LINKAGE_MESSAGE in report
    assert "Evidence count: 0" in report
    assert "No defensible Executive evidence matched the governed project." in report


def test_certification_report_is_deterministic(tmp_path: Path) -> None:
    database = tmp_path / "deterministic.duckdb"
    _create_certification_database(database)
    first = StringIO()
    second = StringIO()

    first_exit_code = run_certification(environment=_environment(database), stdout=first)
    second_exit_code = run_certification(environment=_environment(database), stdout=second)

    assert first_exit_code == second_exit_code == 1
    assert first.getvalue() == second.getvalue()


def test_certification_report_includes_evidence_and_lineage_output(tmp_path: Path) -> None:
    database = tmp_path / "lineage.duckdb"
    _create_certification_database(database)
    output = StringIO()

    run_certification(environment=_environment(database), stdout=output)

    report = output.getvalue()
    assert "Accepted Executive evidence diagnostics" in report
    assert 'Selected relation: "certified"."executive_evidence"' in report
    assert "Evidence ID: E-100" in report
    assert "Source document: Caltrans Executive Plan" in report
    assert "Source section: SEC-7" in report
    assert "Source keys: {'evidence_id': 'E-100'" in report
    assert (
        "Semantic metadata keys: ['expected_outcome', 'objective', 'policy_driver', 'program', 'strategic_theme']"
        in report
    )


def test_certification_runtime_validation_requires_nonempty_evidence(tmp_path: Path) -> None:
    database = tmp_path / "empty.duckdb"
    _create_certification_database(database, include_evidence=False)
    output = StringIO()

    exit_code = run_certification(environment=_environment(database), stdout=output)

    report = output.getvalue()
    assert exit_code == 1
    assert "FAIL ExecutiveEvidence returns rows" in report
    assert "Governed Southern California project" not in report


def test_typed_certification_result_failed_for_runtime_validation_failure() -> None:
    result = certify_program100(environment={})

    assert result.status == CertificationStatus.FAILED
    assert result.exit_code == 1
    assert result.reason == "Runtime validation failed; intelligence execution was not attempted."
    assert result.limitations == (result.reason,)
    assert "FAIL CI_DATABASE configured" in result.report
    assert "Certification result: FAILED" in result.report
    assert "Governed Southern California project" not in result.report


def test_cli_output_and_exit_code_are_derived_from_typed_result(monkeypatch) -> None:
    typed_result = CertificationResult(
        status=CertificationStatus.BLOCKED,
        exit_code=7,
        report="typed report\n",
        reason="typed reason",
        limitations=("typed reason",),
    )
    monkeypatch.setattr(
        certification_module,
        "certify_program100",
        lambda *, environment=None: typed_result,
    )
    output = StringIO()

    exit_code = run_certification(environment={"IGNORED": "1"}, stdout=output)

    assert exit_code == typed_result.exit_code
    assert output.getvalue() == typed_result.report


def test_typed_certification_result_pass_when_defensible_project_linkage_exists(
    monkeypatch,
) -> None:
    _install_passing_program100_fakes(monkeypatch)

    result = certify_program100(environment=_typed_environment())

    assert result.status == CertificationStatus.PASS
    assert result.exit_code == 0
    assert result.reason is None
    assert result.limitations == ()
    assert "Certification result: PASS" in result.report
    assert "Evidence ID: E-PASS" in result.report
    assert "Relationship: explicit_project_linkage" in result.report


def test_typed_certification_result_blocked_for_insufficient_project_linkage_metadata(
    tmp_path: Path,
) -> None:
    database = tmp_path / "blocked.duckdb"
    _create_certification_database(database)

    result = certify_program100(environment=_environment(database))

    assert result.status == CertificationStatus.BLOCKED
    assert result.exit_code == 1
    assert result.reason == BLOCKED_PROJECT_LINKAGE_MESSAGE
    assert BLOCKED_PROJECT_LINKAGE_MESSAGE in result.limitations
    assert "Certification result: BLOCKED" in result.report
    assert "Evidence count: 0" in result.report


def test_typed_certification_result_and_report_are_deterministic(tmp_path: Path) -> None:
    database = tmp_path / "typed_deterministic.duckdb"
    _create_certification_database(database)

    first = certify_program100(environment=_environment(database))
    second = certify_program100(environment=_environment(database))

    assert first == second
    assert first.report == second.report


def _typed_environment() -> dict[str, str]:
    return {
        "CI_DATABASE": "/governed/program100.duckdb",
        "CDP001_EXECUTIVE_EVIDENCE_RELATION": "certified.executive_evidence",
        "CDP001_EXECUTIVE_EVIDENCE_STATUS": "ACCEPTED",
        "CDP001_EXECUTIVE_EVIDENCE_RELATION_ROLE": "certified_current",
    }


def _install_passing_program100_fakes(monkeypatch) -> None:
    project = ProjectDetail(
        project_id="07-PASS",
        title="Linked Southern California project",
        description="Governed linked project.",
        district=7,
        county="Los Angeles",
        route="101",
        primary_scope="Bridge",
    )
    lineage = ExecutiveEvidenceLineage(
        source_relation='"certified"."executive_evidence"',
        source_keys={"evidence_id": "E-PASS", "source_section_id": "SEC-PASS"},
        source_section_id="SEC-PASS",
    )
    evidence = ExecutiveEvidence(
        evidence_id="E-PASS",
        evidence_type="objective",
        source_document="Executive Plan",
        source_section_id="SEC-PASS",
        source_text="This certified evidence explicitly links to project 07-PASS.",
        refinement_status="USABLE",
        source_lineage=lineage,
        semantic_metadata={"program": "SHOPP"},
    )
    evidence_result = ExecutiveEvidenceResult(
        evidence=[evidence],
        diagnostics=ExecutiveEvidenceDiagnostics(
            selected_relation='"certified"."executive_evidence"',
            relation_role="executive_certified_data_product",
            eligible_evidence_count=1,
            rejected_evidence_count=0,
            duplicate_evidence_count=0,
            source_text_coverage=1,
            source_document_coverage=1,
            lineage_coverage=1,
            final_evidence_count=1,
        ),
    )
    context = StrategicContext(
        project_id="07-PASS",
        strategic_context_id="strategic-context:07-PASS",
        evidence=[
            StrategicEvidence(
                evidence_id="E-PASS",
                source_document="Executive Plan",
                source_section_id="SEC-PASS",
                source_excerpt="This certified evidence explicitly links to project 07-PASS.",
                relationship_to_project="explicit_project_linkage",
                evidence_strength=EvidenceStrength.DIRECT,
                source_lineage=lineage,
            )
        ],
        source_confidence=SourceConfidence.MODERATE,
    )

    class FakeProjectService:
        def __init__(self, database: Path) -> None:
            self.database = database

        def search_projects(self, request) -> list[ProjectSummary]:
            return [ProjectSummary(**project.model_dump(exclude={"raw_record"}))]

        def fetch_project(self, project_id: str) -> ProjectDetail | None:
            return project if project_id == project.project_id else None

    class FakeExecutiveEvidenceService:
        def __init__(self, database: Path, mappings) -> None:
            self.database = database
            self.mappings = mappings

        def fetch_executive_evidence(self, *, limit=None) -> ExecutiveEvidenceResult:
            return evidence_result

    class FakeStrategicContextService:
        def __init__(self, project_provider, executive_evidence_provider) -> None:
            self.project_provider = project_provider
            self.executive_evidence_provider = executive_evidence_provider

        def fetch_strategic_context(self, project_id: str) -> StrategicContext | None:
            return context if project_id == project.project_id else None

    class FakeProjectIntelligenceService:
        def __init__(self, *args) -> None:
            self.args = args

        def fetch_project_intelligence(self, project_id: str):
            return type("FakeProjectIntelligence", (), {"project": project})()

    class PassthroughService:
        def __init__(self, *args) -> None:
            self.args = args

    monkeypatch.setattr(
        certification_module,
        "run_validation",
        lambda *, environment, stdout: stdout.write("PASS fake runtime\n") and 0,
    )
    monkeypatch.setattr(certification_module, "ProjectService", FakeProjectService)
    monkeypatch.setattr(
        certification_module, "ExecutiveEvidenceService", FakeExecutiveEvidenceService
    )
    monkeypatch.setattr(
        certification_module, "StrategicContextService", FakeStrategicContextService
    )
    monkeypatch.setattr(
        certification_module, "ProjectIntelligenceService", FakeProjectIntelligenceService
    )
    monkeypatch.setattr(certification_module, "MarketService", PassthroughService)
    monkeypatch.setattr(certification_module, "OpportunityService", PassthroughService)
