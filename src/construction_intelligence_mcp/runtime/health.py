from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from io import StringIO
from pathlib import Path
import sys
from typing import Callable, TextIO

from construction_intelligence_mcp.runtime.certify_program100 import (
    CertificationResult,
    CertificationStatus,
    certify_program100,
)
from construction_intelligence_mcp.runtime.validate import run_validation

PLATFORM_VERSION = "1.0"
_REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


class HealthStatus(StrEnum):
    """Allowed health report states."""

    PASS = "PASS"
    WARNING = "WARNING"
    NOT_INSTALLED = "NOT INSTALLED"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"
    READY = "READY"
    NOT_READY = "NOT READY"
    NOT_CERTIFIED = "NOT CERTIFIED"


@dataclass(frozen=True)
class HealthLine:
    """One display line in a health report section."""

    label: str
    status: HealthStatus


@dataclass(frozen=True)
class RuntimeValidationResult:
    """Parsed result from the runtime validator."""

    exit_code: int
    checks: dict[str, HealthStatus]


def main(argv: list[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    """Run the platform health report command."""

    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments != ["health"]:
        stdout.write("Usage: python -m construction_intelligence_mcp.runtime health\n")
        return 2
    report = build_health_report()
    stdout.write(render_health_report(report))
    return 0 if report.overall_status is HealthStatus.READY else 1


@dataclass(frozen=True)
class HealthReport:
    """Complete Construction Intelligence Platform health report."""

    version: str
    platform: tuple[HealthLine, ...]
    runtime: tuple[HealthLine, ...]
    programs: tuple[HealthLine, ...]
    business: tuple[HealthLine, ...]
    overall_status: HealthStatus


def build_health_report(
    *,
    validator: Callable[..., int] = run_validation,
    certifier: Callable[[], CertificationResult] = certify_program100,
    repository_root: Path = _REPOSITORY_ROOT,
) -> HealthReport:
    """Build health by consuming the Runtime Validator and installed platform docs."""

    validation = _run_runtime_validator(validator)
    runtime_passed = validation.exit_code == 0
    certification = certifier() if runtime_passed else None
    program_100_demonstration = _program_100_demonstration_status(runtime_passed, certification)
    program_100_status = _program_100_status(runtime_passed, certification)
    overall_status = _overall_status(runtime_passed, certification)

    return HealthReport(
        version=PLATFORM_VERSION,
        platform=(
            HealthLine(
                "Constitution", _document_status(repository_root, "docs/000-CONSTITUTION.md")
            ),
            HealthLine(
                "Runtime Contract",
                _document_status(repository_root, "docs/runtime/001-runtime-contract.md"),
            ),
            HealthLine(
                "Runtime Validator",
                HealthStatus.PASS if runtime_passed else HealthStatus.BLOCKED,
            ),
            HealthLine(
                "Operations Guide",
                _document_status(repository_root, "docs/runtime/004-operations-guide.md"),
            ),
        ),
        runtime=(
            HealthLine(
                "CI_DATABASE",
                _status_for_any(
                    validation, ("CI_DATABASE configured", "DuckDB file exists", "DuckDB readable")
                ),
            ),
            HealthLine(
                "Executive Mapping",
                _status_for_any(
                    validation,
                    (
                        "CDP001_EXECUTIVE_EVIDENCE_RELATION configured",
                        "Relation schema-qualified",
                        "Mapping status ACCEPTED or CURRENT",
                        "Mapping role certified_current",
                        "Relation exists",
                    ),
                ),
            ),
            HealthLine(
                "Executive Evidence",
                _status_for_any(
                    validation,
                    (
                        "Required ExecutiveEvidence concepts resolve",
                        "ExecutiveEvidence returns rows",
                    ),
                ),
            ),
            HealthLine("Strategic Context", _strategic_context_status(overall_status)),
        ),
        programs=(
            HealthLine("Program 100", program_100_status),
            HealthLine("Program 200", HealthStatus.NOT_INSTALLED),
            HealthLine("Program 300", HealthStatus.NOT_INSTALLED),
        ),
        business=(
            HealthLine("Program 100 Demonstration", program_100_demonstration),
            HealthLine("Platform Status", overall_status),
        ),
        overall_status=overall_status,
    )


def render_health_report(report: HealthReport) -> str:
    """Render a health report as human-readable operational text."""

    lines = [
        "Construction Intelligence Platform",
        "==================================",
        "",
        _format_line("Version", report.version),
        "",
        "Platform",
        *[_format_line(line.label, line.status.value) for line in report.platform],
        "",
        "Runtime",
        *[_format_line(line.label, line.status.value) for line in report.runtime],
        "",
        "Programs",
        *[_format_line(line.label, line.status.value) for line in report.programs],
        "",
        "Business Readiness",
        *[_format_line(line.label, line.status.value) for line in report.business],
    ]
    return "\n".join(lines) + "\n"


def _run_runtime_validator(validator: Callable[..., int]) -> RuntimeValidationResult:
    output = StringIO()
    exit_code = validator(stdout=output)
    return RuntimeValidationResult(
        exit_code=exit_code, checks=_parse_validator_output(output.getvalue())
    )


def _parse_validator_output(output: str) -> dict[str, HealthStatus]:
    checks: dict[str, HealthStatus] = {}
    for line in output.splitlines():
        if line.startswith("PASS "):
            checks[line.removeprefix("PASS ")] = HealthStatus.PASS
        elif line.startswith("WARNING "):
            checks[line.removeprefix("WARNING ")] = HealthStatus.WARNING
        elif line.startswith("FAIL "):
            name = line.removeprefix("FAIL ").split(":", maxsplit=1)[0]
            checks[name] = HealthStatus.BLOCKED
    return checks


def _status_for_any(
    validation: RuntimeValidationResult,
    check_names: tuple[str, ...],
    *,
    missing_status: HealthStatus = HealthStatus.UNKNOWN,
) -> HealthStatus:
    statuses = [validation.checks.get(name) for name in check_names]
    if HealthStatus.BLOCKED in statuses:
        return HealthStatus.BLOCKED
    if HealthStatus.WARNING in statuses:
        return HealthStatus.WARNING
    if all(status is HealthStatus.PASS for status in statuses):
        return HealthStatus.PASS
    return missing_status


def _program_100_demonstration_status(
    runtime_passed: bool, certification: CertificationResult | None
) -> HealthStatus:
    if not runtime_passed:
        return HealthStatus.BLOCKED
    if certification is None:
        return HealthStatus.UNKNOWN
    if certification.status is CertificationStatus.PASS:
        return HealthStatus.PASS
    if certification.status is CertificationStatus.BLOCKED:
        return HealthStatus.NOT_CERTIFIED
    return HealthStatus.BLOCKED


def _program_100_status(
    runtime_passed: bool, certification: CertificationResult | None
) -> HealthStatus:
    if not runtime_passed:
        return HealthStatus.BLOCKED
    if certification is None:
        return HealthStatus.UNKNOWN
    if certification.status is CertificationStatus.PASS:
        return HealthStatus.READY
    if certification.status is CertificationStatus.BLOCKED:
        return HealthStatus.NOT_READY
    return HealthStatus.BLOCKED


def _overall_status(
    runtime_passed: bool, certification: CertificationResult | None
) -> HealthStatus:
    if not runtime_passed:
        return HealthStatus.BLOCKED
    if certification is None:
        return HealthStatus.UNKNOWN
    if certification.status is CertificationStatus.PASS:
        return HealthStatus.READY
    if certification.status is CertificationStatus.BLOCKED:
        return HealthStatus.NOT_READY
    return HealthStatus.BLOCKED


def _strategic_context_status(overall_status: HealthStatus) -> HealthStatus:
    return HealthStatus.PASS if overall_status is HealthStatus.READY else HealthStatus.UNKNOWN


def _document_status(repository_root: Path, relative_path: str) -> HealthStatus:
    return (
        HealthStatus.PASS
        if (repository_root / relative_path).is_file()
        else HealthStatus.NOT_INSTALLED
    )


def _format_line(label: str, value: str) -> str:
    return f"{label:.<30}{value}"
