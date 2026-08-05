import os
from pathlib import Path

import pytest

from construction_intelligence_mcp.services.executive_evidence_service import (
    ExecutiveEvidenceService,
)

DATABASE = Path(os.environ["CI_DATABASE"]).expanduser() if os.environ.get("CI_DATABASE") else None
MAPPED_RELATION = os.environ.get("CDP001_EXECUTIVE_EVIDENCE_RELATION")
MAPPING_STATUS = os.environ.get("CDP001_EXECUTIVE_EVIDENCE_STATUS")

pytestmark = pytest.mark.skipif(
    DATABASE is None or not DATABASE.is_file(),
    reason="CI_DATABASE is not set to an available source DuckDB",
)


def test_configured_ci_database_requires_accepted_cdp_001_mapping() -> None:
    assert DATABASE is not None
    if MAPPED_RELATION and MAPPING_STATUS and MAPPING_STATUS.upper() in {"ACCEPTED", "CURRENT"}:
        pytest.skip("CI_DATABASE has an accepted CDP-001 mapping; use the nonzero evidence test")

    with pytest.raises(RuntimeError, match="CDP-001 physical implementation mapping"):
        ExecutiveEvidenceService(DATABASE)


@pytest.mark.skipif(
    not MAPPED_RELATION or (MAPPING_STATUS or "").upper() not in {"ACCEPTED", "CURRENT"},
    reason="CDP-001 accepted physical implementation mapping is not configured",
)
def test_actual_ci_database_returns_nonzero_executive_evidence() -> None:
    assert DATABASE is not None
    result = ExecutiveEvidenceService(DATABASE).fetch_executive_evidence(limit=25)

    assert result.diagnostics.final_evidence_count > 0
    assert result.evidence
    assert all(item.evidence_id for item in result.evidence)
    assert all(item.source_text for item in result.evidence)
    assert all(item.source_lineage.source_keys for item in result.evidence)
