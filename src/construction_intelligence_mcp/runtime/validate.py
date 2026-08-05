from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import os
from pathlib import Path
import sys
from typing import TextIO

from construction_intelligence_mcp.adapters.duckdb_adapter import DuckDBAdapter
from construction_intelligence_mcp.adapters.executive_evidence_adapter import (
    ACCEPTED_MAPPING_STATUSES,
    CdpPhysicalImplementationMapping,
    ExecutiveEvidenceAdapter,
)
from construction_intelligence_mcp.services.executive_evidence_service import (
    ExecutiveEvidenceService,
)

CERTIFIED_CURRENT_ROLE = "certified_current"


@dataclass(frozen=True)
class ValidationCheck:
    """One runtime prerequisite validation."""

    name: str
    validate: Callable[["RuntimeValidationContext"], None]


@dataclass
class RuntimeValidationContext:
    """Mutable runtime validation state shared by ordered prerequisite checks."""

    environment: dict[str, str]
    database: Path | None = None
    duckdb_adapter: DuckDBAdapter | None = None
    mapping: CdpPhysicalImplementationMapping | None = None
    evidence_adapter: ExecutiveEvidenceAdapter | None = None


def main(argv: list[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    """Run the runtime validator command."""

    arguments = list(sys.argv[1:] if argv is None else argv)
    if arguments != ["validate"]:
        stdout.write("Usage: python -m construction_intelligence_mcp.runtime validate\n")
        return 2
    return run_validation(stdout=stdout)


def run_validation(
    *,
    environment: dict[str, str] | None = None,
    stdout: TextIO = sys.stdout,
) -> int:
    """Validate runtime prerequisites, stopping at the first failed prerequisite."""

    context = RuntimeValidationContext(
        environment=dict(os.environ if environment is None else environment)
    )
    for check in _checks():
        try:
            check.validate(context)
        except Exception as exc:  # noqa: BLE001 - validation must explain exact failed prerequisite.
            stdout.write(f"FAIL {check.name}: {exc}\n")
            return 1
        stdout.write(f"PASS {check.name}\n")
    return 0


def _checks() -> tuple[ValidationCheck, ...]:
    return (
        ValidationCheck("CI_DATABASE configured", _validate_ci_database_configured),
        ValidationCheck("DuckDB file exists", _validate_duckdb_file_exists),
        ValidationCheck("DuckDB readable", _validate_duckdb_readable),
        ValidationCheck(
            "CDP001_EXECUTIVE_EVIDENCE_RELATION configured",
            _validate_relation_configured,
        ),
        ValidationCheck("Relation schema-qualified", _validate_relation_schema_qualified),
        ValidationCheck("Mapping status ACCEPTED or CURRENT", _validate_mapping_status),
        ValidationCheck("Mapping role certified_current", _validate_mapping_role),
        ValidationCheck("Relation exists", _validate_relation_exists),
        ValidationCheck(
            "Required ExecutiveEvidence concepts resolve",
            _validate_required_concepts_resolve,
        ),
        ValidationCheck("ExecutiveEvidence returns rows", _validate_evidence_returns_rows),
    )


def _validate_ci_database_configured(context: RuntimeValidationContext) -> None:
    value = _configured_value(context, "CI_DATABASE")
    context.database = Path(value).expanduser()


def _validate_duckdb_file_exists(context: RuntimeValidationContext) -> None:
    database = _require_database(context)
    if not database.is_file():
        raise RuntimeError(f"CI_DATABASE does not point to an existing DuckDB file: {database}")


def _validate_duckdb_readable(context: RuntimeValidationContext) -> None:
    database = _require_database(context)
    adapter = DuckDBAdapter(database)
    adapter.relations()
    context.duckdb_adapter = adapter


def _validate_relation_configured(context: RuntimeValidationContext) -> None:
    _configured_value(context, "CDP001_EXECUTIVE_EVIDENCE_RELATION")


def _validate_relation_schema_qualified(context: RuntimeValidationContext) -> None:
    relation = _configured_value(context, "CDP001_EXECUTIVE_EVIDENCE_RELATION")
    if ExecutiveEvidenceAdapter._parse_schema_qualified_relation(relation) is None:
        raise RuntimeError(
            "CDP001_EXECUTIVE_EVIDENCE_RELATION must be schema-qualified as <schema>.<relation>."
        )


def _validate_mapping_status(context: RuntimeValidationContext) -> None:
    status = _configured_value(context, "CDP001_EXECUTIVE_EVIDENCE_STATUS")
    if status.upper() not in ACCEPTED_MAPPING_STATUSES:
        raise RuntimeError(
            "CDP001_EXECUTIVE_EVIDENCE_STATUS must be ACCEPTED or CURRENT; "
            f"configured value is {status!r}."
        )


def _validate_mapping_role(context: RuntimeValidationContext) -> None:
    role = _configured_value(context, "CDP001_EXECUTIVE_EVIDENCE_RELATION_ROLE")
    if role != CERTIFIED_CURRENT_ROLE:
        raise RuntimeError(
            "CDP001_EXECUTIVE_EVIDENCE_RELATION_ROLE must be certified_current; "
            f"configured value is {role!r}."
        )
    context.mapping = CdpPhysicalImplementationMapping(
        product_identifier="CDP-001",
        relation=_configured_value(context, "CDP001_EXECUTIVE_EVIDENCE_RELATION"),
        certification_status=_configured_value(context, "CDP001_EXECUTIVE_EVIDENCE_STATUS"),
        relation_role=role,
    )


def _validate_relation_exists(context: RuntimeValidationContext) -> None:
    mapping = _require_mapping(context)
    parsed = ExecutiveEvidenceAdapter._parse_schema_qualified_relation(mapping.relation)
    if parsed is None:
        raise RuntimeError("CDP-001 relation must be schema-qualified before existence validation.")
    schema, relation = parsed
    duckdb_adapter = context.duckdb_adapter or DuckDBAdapter(_require_database(context))
    qualified = (
        f"{duckdb_adapter.quote_identifier(schema)}.{duckdb_adapter.quote_identifier(relation)}"
    )
    if qualified not in duckdb_adapter.relations():
        raise RuntimeError(f"Mapped CDP-001 relation does not exist: {schema}.{relation}")


def _validate_required_concepts_resolve(context: RuntimeValidationContext) -> None:
    context.evidence_adapter = ExecutiveEvidenceAdapter(
        _require_database(context), [_require_mapping(context)]
    )


def _validate_evidence_returns_rows(context: RuntimeValidationContext) -> None:
    result = ExecutiveEvidenceService(
        _require_database(context), [_require_mapping(context)]
    ).fetch_executive_evidence()
    if not result.evidence:
        raise RuntimeError(
            "ExecutiveEvidence returned zero rows from the accepted current relation."
        )


def _configured_value(context: RuntimeValidationContext, name: str) -> str:
    value = context.environment.get(name)
    if value is None or not value.strip():
        raise RuntimeError(f"{name} is not configured.")
    return value.strip()


def _require_database(context: RuntimeValidationContext) -> Path:
    if context.database is None:
        raise RuntimeError("CI_DATABASE must be validated before this prerequisite.")
    return context.database


def _require_mapping(context: RuntimeValidationContext) -> CdpPhysicalImplementationMapping:
    if context.mapping is None:
        raise RuntimeError("CDP-001 mapping must be validated before this prerequisite.")
    return context.mapping
