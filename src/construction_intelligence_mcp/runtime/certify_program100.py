from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
import sys
from typing import TextIO

from construction_intelligence_mcp.runtime.validate import run_validation


class CertificationStatus(StrEnum):
    """Program 100 business certification states."""

    PASS = "PASS"
    BLOCKED = "BLOCKED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class CertificationResult:
    """Typed result for Program 100 business certification."""

    status: CertificationStatus
    message: str


def certify_program100() -> CertificationResult:
    """Certify Program 100 readiness through the public typed interface."""

    runtime_output = _DiscardingTextIO()
    if run_validation(stdout=runtime_output) != 0:
        return CertificationResult(
            status=CertificationStatus.BLOCKED,
            message="Runtime validation must pass before Program 100 certification.",
        )
    return CertificationResult(
        status=CertificationStatus.BLOCKED,
        message="Program 100 demonstration certification is not available in this runtime.",
    )


def main(argv: list[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    """Run Program 100 certification from the runtime module."""

    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments != ["certify-program100"]:
        stdout.write("Usage: python -m construction_intelligence_mcp.runtime certify-program100\n")
        return 2
    result = certify_program100()
    stdout.write(f"{result.status.value} Program 100 Certification: {result.message}\n")
    return 0 if result.status is CertificationStatus.PASS else 1


class _DiscardingTextIO:
    def write(self, text: str) -> int:
        return len(text)
