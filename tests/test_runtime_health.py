from __future__ import annotations

from io import StringIO
from pathlib import Path
import subprocess
import sys
from typing import TextIO

from construction_intelligence_mcp.runtime.certify_program100 import (
    CertificationResult,
    CertificationStatus,
)
from construction_intelligence_mcp.runtime.health import (
    HealthStatus,
    build_health_report,
    main,
    render_health_report,
)


def _write_platform_docs(repository_root: Path) -> None:
    (repository_root / "docs/runtime").mkdir(parents=True)
    (repository_root / "docs/000-CONSTITUTION.md").write_text("constitution")
    (repository_root / "docs/runtime/001-runtime-contract.md").write_text("runtime")
    (repository_root / "docs/runtime/004-operations-guide.md").write_text("operations")


def _passing_validator(*, stdout: TextIO) -> int:
    stdout.write("PASS CI_DATABASE configured\n")
    stdout.write("PASS DuckDB file exists\n")
    stdout.write("PASS DuckDB readable\n")
    stdout.write("PASS CDP001_EXECUTIVE_EVIDENCE_RELATION configured\n")
    stdout.write("PASS Relation schema-qualified\n")
    stdout.write("PASS Mapping status ACCEPTED or CURRENT\n")
    stdout.write("PASS Mapping role certified_current\n")
    stdout.write("PASS Relation exists\n")
    stdout.write("PASS Required ExecutiveEvidence concepts resolve\n")
    stdout.write("PASS ExecutiveEvidence returns rows\n")
    return 0


def _failing_validator(*, stdout: TextIO) -> int:
    stdout.write("PASS CI_DATABASE configured\n")
    stdout.write("FAIL DuckDB file exists: missing\n")
    return 1


def _certifier(status: CertificationStatus) -> CertificationResult:
    return CertificationResult(status=status, message=f"certification {status.value}")


def test_health_report_ready_when_runtime_and_certification_pass(tmp_path: Path) -> None:
    _write_platform_docs(tmp_path)

    report = build_health_report(
        validator=_passing_validator,
        certifier=lambda: _certifier(CertificationStatus.PASS),
        repository_root=tmp_path,
    )
    output = render_health_report(report)

    assert report.overall_status is HealthStatus.READY
    assert "Runtime Validator.............PASS" in output
    assert "CI_DATABASE...................PASS" in output
    assert "Executive Mapping.............PASS" in output
    assert "Executive Evidence............PASS" in output
    assert "Strategic Context.............PASS" in output
    assert "Program 100...................READY" in output
    assert "Program 200...................NOT INSTALLED" in output
    assert "Program 300...................NOT INSTALLED" in output
    assert "Program 100 Demonstration.....PASS" in output
    assert "Platform Status...............READY" in output


def test_health_report_blocked_when_runtime_validator_fails(tmp_path: Path) -> None:
    _write_platform_docs(tmp_path)
    certification_calls = 0

    def certifier() -> CertificationResult:
        nonlocal certification_calls
        certification_calls += 1
        return _certifier(CertificationStatus.PASS)

    report = build_health_report(
        validator=_failing_validator,
        certifier=certifier,
        repository_root=tmp_path,
    )
    output = render_health_report(report)

    assert certification_calls == 0
    assert report.overall_status is HealthStatus.BLOCKED
    assert "Runtime Validator.............BLOCKED" in output
    assert "CI_DATABASE...................BLOCKED" in output
    assert "Program 100...................BLOCKED" in output
    assert "Program 100 Demonstration.....BLOCKED" in output
    assert "Strategic Context.............BLOCKED" in output
    assert "Platform Status...............BLOCKED" in output


def test_health_report_blocked_when_program_100_certification_failed(
    tmp_path: Path,
) -> None:
    _write_platform_docs(tmp_path)

    report = build_health_report(
        validator=_passing_validator,
        certifier=lambda: _certifier(CertificationStatus.FAILED),
        repository_root=tmp_path,
    )
    output = render_health_report(report)

    assert report.overall_status is HealthStatus.BLOCKED
    assert "Program 100...................BLOCKED" in output
    assert "Program 100 Demonstration.....BLOCKED" in output
    assert "Strategic Context.............BLOCKED" in output
    assert "Platform Status...............BLOCKED" in output


def test_health_report_not_ready_when_program_100_certification_blocked(
    tmp_path: Path,
) -> None:
    _write_platform_docs(tmp_path)

    report = build_health_report(
        validator=_passing_validator,
        certifier=lambda: _certifier(CertificationStatus.BLOCKED),
        repository_root=tmp_path,
    )
    output = render_health_report(report)

    assert report.overall_status is HealthStatus.NOT_READY
    assert "Program 100...................NOT READY" in output
    assert "Program 100 Demonstration.....NOT CERTIFIED" in output
    assert "Strategic Context.............NOT CERTIFIED" in output
    assert "Platform Status...............NOT READY" in output


def test_health_report_consumes_typed_certification_result(tmp_path: Path) -> None:
    _write_platform_docs(tmp_path)
    certification_result = CertificationResult(
        status=CertificationStatus.PASS,
        message="typed result was consumed",
    )
    certification_calls = 0

    def certifier() -> CertificationResult:
        nonlocal certification_calls
        certification_calls += 1
        return certification_result

    report = build_health_report(
        validator=_passing_validator,
        certifier=certifier,
        repository_root=tmp_path,
    )

    assert certification_calls == 1
    assert report.overall_status is HealthStatus.READY


def test_health_report_surfaces_validator_warning_state(tmp_path: Path) -> None:
    _write_platform_docs(tmp_path)

    def validator(*, stdout: TextIO) -> int:
        stdout.write("PASS CI_DATABASE configured\n")
        stdout.write("PASS DuckDB file exists\n")
        stdout.write("WARNING DuckDB readable\n")
        return 1

    report = build_health_report(
        validator=validator,
        certifier=lambda: _certifier(CertificationStatus.PASS),
        repository_root=tmp_path,
    )

    assert "CI_DATABASE...................WARNING" in render_health_report(report)


def test_health_report_marks_missing_platform_docs_not_installed(tmp_path: Path) -> None:
    report = build_health_report(
        validator=_passing_validator,
        certifier=lambda: _certifier(CertificationStatus.PASS),
        repository_root=tmp_path,
    )
    output = render_health_report(report)

    assert "Constitution..................NOT INSTALLED" in output
    assert "Runtime Contract..............NOT INSTALLED" in output
    assert "Operations Guide..............NOT INSTALLED" in output


def test_health_module_usage_requires_health_argument() -> None:
    output = StringIO()

    exit_code = main([], stdout=output)

    assert exit_code == 2
    assert output.getvalue() == "Usage: python -m construction_intelligence_mcp.runtime health\n"


def test_runtime_commands_remain_available() -> None:
    commands = ("validate", "certify-program100", "health")

    for command in commands:
        completed = subprocess.run(
            [sys.executable, "-m", "construction_intelligence_mcp.runtime", command],
            check=False,
            env={"PYTHONPATH": "src"},
            capture_output=True,
            text=True,
        )

        assert completed.returncode in {0, 1}
        assert "Usage:" not in completed.stdout
