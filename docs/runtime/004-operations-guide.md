# RT-001D Operations Guide

## Purpose

This guide is the first-run operations checklist for a new engineer validating the
Construction Intelligence MCP runtime and Program 100 Executive Intelligence certification
readiness. It covers platform installation, repository setup, Python environment creation,
required runtime configuration, validation, Program 100 certification checks, common failures,
and recovery steps.

Use this guide with the Runtime Contract in `docs/runtime/001-runtime-contract.md`. The Runtime
Contract is the authoritative source for runtime obligations; this guide is the operational runbook
for applying those obligations on a workstation or validation host.

## Governance alignment

Before operating or certifying the runtime, confirm the work is aligned with platform governance:

1. Read `docs/000-CONSTITUTION.md`.
2. Read `AGENTS.md`.
3. Read `docs/runtime/001-runtime-contract.md`.
4. Read `docs/PROGRAMS.md`.
5. Read `docs/data-products/100-executive-certified-data-product.md`.

Program identification:

- Program: **Program 100 — Executive Intelligence**.
- Certified Data Product: **CDP-001 — Executive Knowledge Certified Data Product**.
- Runtime boundary: this repository operates the Intelligence Layer and MCP/CLI transports. It does
  not produce, mutate, promote, or repair the source DuckDB warehouse.

Constitutional alignment:

- Runtime reads from certified data products and exposes business objects through services and MCP.
- DuckDB access remains read-only and belongs in adapters.
- CDP-001 physical implementation configuration is a runtime mapping only; it does not replace the
  storage-independent certified data product contract.
- Missing databases, missing mappings, uncertified relation roles, and unresolved required fields
  must fail clearly instead of being silently substituted.

## Platform installation

### 1. Install platform prerequisites

Install the following before cloning the repository:

- Git.
- Python 3.12 or newer.
- A shell that can activate Python virtual environments.
- Access to the governed DuckDB file used by the runtime, when integration validation or Program 100
  certification checks are required.

Verify the local tools:

```bash
git --version
python --version
```

Expected shape:

```text
git version 2.x.x
Python 3.12.x
```

If Python is older than 3.12, install a supported interpreter before continuing.

## Repository clone

Clone the repository and enter the checkout:

```bash
git clone <repository-url> construction-intelligence-mcp
cd construction-intelligence-mcp
```

Confirm the expected governance and runtime documents are available:

```bash
test -f docs/000-CONSTITUTION.md
test -f AGENTS.md
test -f docs/runtime/001-runtime-contract.md
test -f docs/PROGRAMS.md
test -f docs/data-products/100-executive-certified-data-product.md
```

If any command fails, stop and recover the correct branch or repository state before operating the
runtime.

## Python environment

Create and activate a project-local virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Confirm the CLI entry point is installed:

```bash
construction-intelligence-mcp --help
```

Expected shape:

```text
usage: construction-intelligence-mcp [-h] [{serve,smoke-test}]
```

## Required environment variables

The runtime uses environment variables for the source database, MCP listener, and CDP-001 physical
implementation mapping. Do not hard-code user-specific paths into repository files.

### Core runtime variable

| Variable | Required for | Example | Notes |
|---|---|---|---|
| `CI_DATABASE` | Smoke test, integration tests, MCP runtime, Program 100 certification checks | `/absolute/path/to/caltrans_pricing.duckdb` | Must point to a readable DuckDB file. Runtime access is read-only. |

### Program 100 CDP-001 mapping variables

| Variable | Required for | Example | Notes |
|---|---|---|---|
| `CDP001_EXECUTIVE_EVIDENCE_RELATION` | Executive Evidence, Strategic Context, Project Intelligence, Program 100 certification checks | `certified.executive_evidence` | Must be exactly one schema-qualified accepted/current physical implementation mapping. |
| `CDP001_EXECUTIVE_EVIDENCE_STATUS` | Same as above | `ACCEPTED` | Accepted values are `ACCEPTED` or `CURRENT`. |
| `CDP001_EXECUTIVE_EVIDENCE_RELATION_ROLE` | Same as above | `certified_current` | Defaults to `certified_current`; do not point to staging, candidate, history, archive, quarantine, diagnostic, temporary, exception, or review relations. |

### MCP listener variables

| Variable | Required for | Example | Notes |
|---|---|---|---|
| `CI_MCP_TRANSPORT` | MCP server launch customization | `sse` | Defaults to `sse`. |
| `CI_MCP_HOST` | MCP server launch customization | `127.0.0.1` | Defaults to `0.0.0.0`. |
| `CI_MCP_PORT` | MCP server launch customization | `8000` | Defaults to `8000`. |

### Example environment configuration

```bash
export CI_DATABASE="/absolute/path/to/caltrans_pricing.duckdb"
export CDP001_EXECUTIVE_EVIDENCE_RELATION="certified.executive_evidence"
export CDP001_EXECUTIVE_EVIDENCE_STATUS="ACCEPTED"
export CDP001_EXECUTIVE_EVIDENCE_RELATION_ROLE="certified_current"
export CI_MCP_TRANSPORT="sse"
export CI_MCP_HOST="127.0.0.1"
export CI_MCP_PORT="8000"
```

Confirm the configured values without printing secrets or private data:

```bash
python - <<'PY'
import os
from pathlib import Path

database = os.environ.get("CI_DATABASE")
print(f"CI_DATABASE set: {bool(database)}")
print(f"CI_DATABASE exists: {Path(database).expanduser().is_file() if database else False}")
print(f"CDP001 relation set: {bool(os.environ.get('CDP001_EXECUTIVE_EVIDENCE_RELATION'))}")
print(f"CDP001 status: {os.environ.get('CDP001_EXECUTIVE_EVIDENCE_STATUS', '(unset)')}")
print(
    "CDP001 role: "
    f"{os.environ.get('CDP001_EXECUTIVE_EVIDENCE_RELATION_ROLE', 'certified_current')}"
)
PY
```

Example output:

```text
CI_DATABASE set: True
CI_DATABASE exists: True
CDP001 relation set: True
CDP001 status: ACCEPTED
CDP001 role: certified_current
```

## Runtime validation

Run validation from the repository root after activating the virtual environment and exporting the
required variables.

### Static validation

```bash
git diff --check
python -m ruff check .
```

Example passing output:

```text
All checks passed!
```

### Service test validation

```bash
python -m pytest -q
```

Example passing output:

```text
41 passed in 1.23s
```

When `CI_DATABASE` is not set or is unavailable, integration tests should skip clearly instead of
mutating or creating a production database:

```text
39 passed, 2 skipped in 1.10s
```

### Runtime smoke validation

```bash
construction-intelligence-mcp smoke-test
```

Example successful output shape:

```text
Resolved source table: "main"."ci_market_state"
Resolved project identifier field: project_id
Resolved description field: description
Total Southern California projects: 12345
Five sample projects:
{"advertisement_date": "2026-01-15", "county": "Los Angeles", "description": "..."}
```

Treat the exact counts and sample projects as environment-specific. The validation succeeds when the
command resolves a governed source table, resolves required business fields, returns a bounded sample,
and does not request write access to the DuckDB file.

## Program 100 certification workflow

Program 100 certification confirms that the Executive Intelligence runtime consumes CDP-001 through
one explicit accepted/current physical implementation mapping and returns governed Executive evidence
without bypassing the Certified Data Product contract.

### 1. Confirm the Program and CDP contract

```bash
sed -n '20,45p' docs/PROGRAMS.md
sed -n '1,45p' docs/data-products/100-executive-certified-data-product.md
```

Certification target:

- Program: Program 100 — Executive Intelligence.
- Initiative dependency: 101 Executive Certified Data Product is complete.
- Runtime dependency: 102 Executive Evidence Engine consumes exactly one accepted/current CDP-001
  physical implementation mapping.

### 2. Export the certified runtime mapping

```bash
export CI_DATABASE="/absolute/path/to/caltrans_pricing.duckdb"
export CDP001_EXECUTIVE_EVIDENCE_RELATION="certified.executive_evidence"
export CDP001_EXECUTIVE_EVIDENCE_STATUS="ACCEPTED"
export CDP001_EXECUTIVE_EVIDENCE_RELATION_ROLE="certified_current"
```

The relation name above is an example. Use the actual owner-certified, schema-qualified relation for
the target environment.

### 3. Run Program 100 integration checks

```bash
python -m pytest -q tests/test_executive_evidence_integration.py tests/test_strategic_context_integration.py
```

Example successful certification output:

```text
2 passed in 0.42s
```

Example unavailable-environment output:

```text
2 skipped in 0.08s
```

A skipped result is acceptable for a developer workstation without the governed DuckDB, but it is not
a Program 100 certification result. A certification host must run with `CI_DATABASE` and the CDP-001
mapping configured so the checks execute against real governed evidence.

### 4. Run full validation after certification checks

```bash
git diff --check
python -m pytest -q
python -m ruff check .
construction-intelligence-mcp smoke-test
```

### 5. Record the certification evidence

Capture the following in the change or release record:

- Git branch and commit SHA.
- `CI_DATABASE` availability confirmation, without committing private paths if inappropriate.
- CDP-001 relation, status, and role used for validation.
- Program 100 integration-test command and result.
- Full test, Ruff, and smoke-test results.
- Any skipped validations and the reason they were skipped.

## Common failures

### `Set CI_DATABASE to the readable source DuckDB file.`

Cause: `CI_DATABASE` is unset or points to an unreadable file.

Recovery:

1. Confirm the path exists with `test -f "$CI_DATABASE"`.
2. Export an absolute path to the governed DuckDB.
3. Re-run `construction-intelligence-mcp smoke-test`.

### `No accepted CDP-001 physical implementation mapping is configured.`

Cause: Executive Evidence or Strategic Context was invoked without
`CDP001_EXECUTIVE_EVIDENCE_RELATION`.

Recovery:

1. Identify the owner-certified CDP-001 physical implementation relation.
2. Export `CDP001_EXECUTIVE_EVIDENCE_RELATION` as a schema-qualified relation.
3. Export `CDP001_EXECUTIVE_EVIDENCE_STATUS=ACCEPTED` or `CURRENT`.
4. Re-run Program 100 integration checks.

### `CDP-001 physical implementation mapping is not accepted/current.`

Cause: `CDP001_EXECUTIVE_EVIDENCE_STATUS` is unset or not one of `ACCEPTED` or `CURRENT`.

Recovery:

1. Confirm the mapping status with the data product owner.
2. Export the accepted/current status.
3. Do not work around the failure by changing code or consuming candidate relations.

### `CDP-001 physical implementation mapping must identify a schema-qualified relation.`

Cause: The mapped relation is not in `schema.relation` form.

Recovery:

1. Replace values such as `executive_evidence` with `certified.executive_evidence` or the actual
   schema-qualified certified relation.
2. Re-run the failing command.

### `Mapped CDP-001 physical implementation relation does not exist.`

Cause: The configured mapping does not exist in the configured DuckDB.

Recovery:

1. Confirm `CI_DATABASE` points to the expected warehouse.
2. Confirm the owner-certified relation name and schema.
3. Correct the mapping or recover the correct DuckDB artifact.
4. Re-run Program 100 integration checks.

### Integration tests are skipped

Cause: `CI_DATABASE` is unset or unavailable on the workstation.

Recovery:

1. For local development, note the skip in the completion report.
2. For certification, move to a host with the governed DuckDB and export the required variables.
3. Re-run the integration checks until they execute instead of skip.

### Ruff or `git diff --check` fails

Cause: Formatting, lint, trailing whitespace, or conflict-marker issues.

Recovery:

1. Fix the reported file and line.
2. Re-run `git diff --check`.
3. Re-run `python -m ruff check .`.

## Recovery checklist

When validation fails, recover in this order:

1. Stop and read the failure message completely.
2. Confirm the repository is on the intended branch and has no unrelated local modifications.
3. Confirm the virtual environment is active and dependencies are installed with
   `python -m pip install -e ".[dev]"`.
4. Confirm `CI_DATABASE` points to a readable DuckDB file.
5. Confirm Program 100 mapping variables identify exactly one accepted/current schema-qualified
   CDP-001 relation.
6. Re-run the smallest failing command.
7. Re-run the complete validation sequence before reporting completion.
8. If the failure indicates missing certified data, ambiguous lineage, unsupported relation role, or
   unavailable CDP-001 concepts, do not implement around it. Document the blocker and escalate through
   Program 100 governance.
