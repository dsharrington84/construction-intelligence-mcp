import os
from pathlib import Path

import pytest

from construction_intelligence_mcp.services.executive_evidence_service import (
    ExecutiveEvidenceService,
)

DATABASE = Path(os.environ["CI_DATABASE"]).expanduser() if os.environ.get("CI_DATABASE") else None

pytestmark = pytest.mark.skipif(
    True,
    reason="CDP-001 is IN REVIEW; no Executive relation is certified for Initiative 102 consumption",
)


def test_actual_ci_database_returns_nonzero_executive_evidence() -> None:
    assert DATABASE is not None
    result = ExecutiveEvidenceService(DATABASE).fetch_executive_evidence(limit=25)

    assert result.diagnostics.final_evidence_count > 0
    assert result.evidence
    assert all(item.evidence_id for item in result.evidence)
    assert all(item.source_text for item in result.evidence)
    assert all(item.source_lineage.source_keys for item in result.evidence)
