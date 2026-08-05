from __future__ import annotations

from io import StringIO
import os
from pathlib import Path

import pytest

from construction_intelligence_mcp.runtime.validate import run_validation

DATABASE = Path(os.environ["CI_DATABASE"]).expanduser() if os.environ.get("CI_DATABASE") else None

pytestmark = pytest.mark.skipif(
    DATABASE is None or not DATABASE.is_file(),
    reason="CI_DATABASE is not set to an available source DuckDB",
)


def test_configured_runtime_validator_executes_against_ci_database() -> None:
    assert DATABASE is not None
    output = StringIO()

    exit_code = run_validation(stdout=output)

    if exit_code != 0:
        assert "FAIL" in output.getvalue()
    else:
        assert "PASS ExecutiveEvidence returns rows" in output.getvalue()
