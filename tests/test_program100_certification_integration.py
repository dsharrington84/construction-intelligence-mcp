from __future__ import annotations

from io import StringIO
import os
from pathlib import Path

import pytest

from construction_intelligence_mcp.runtime.certify_program100 import run_certification

DATABASE = Path(os.environ["CI_DATABASE"]).expanduser() if os.environ.get("CI_DATABASE") else None

pytestmark = pytest.mark.skipif(
    DATABASE is None or not DATABASE.is_file(),
    reason="CI_DATABASE is not set to an available source DuckDB",
)


def test_program100_certification_command_executes_against_ci_database() -> None:
    output = StringIO()

    exit_code = run_certification(stdout=output)

    if exit_code != 0:
        assert "CERTIFICATION FAILED" in output.getvalue()
    else:
        report = output.getvalue()
        assert "Certification result: PASS" in report
        assert "Evidence ID:" in report
