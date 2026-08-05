# Construction Intelligence MCP

## Platform Governance

Every contributor should begin with the platform governance documents before reading implementation documentation:

1. [Constitution](docs/000-CONSTITUTION.md)
2. [AGENTS](AGENTS.md)
3. [PROGRAMS](docs/PROGRAMS.md)

The Constitution is the highest authority for platform architecture. Repository guidance, roadmap documentation, and implementation work must align with it.

`ProjectService` is the governed project-discovery interface for the Construction
Intelligence Platform. It reads the canonical `ci_market_state` table from DuckDB in
read-only mode and returns Pydantic business objects rather than DataFrames. Consumers
use service methods or MCP tools and do not need SQL.


## Certified Data Products

- [Executive Knowledge Certified Data Product](docs/data-products/100-executive-certified-data-product.md)

## Install

Python 3.12 or newer is required.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

Set the source database for integration tests, the smoke test, and MCP:

```bash
export CI_DATABASE=/absolute/path/to/caltrans_pricing.duckdb
```

The database is always opened read-only; this project does not modify the source DuckDB.

## Test and lint

```bash
python -m pytest
python -m ruff check .
```

Tests backed by the actual `ci_market_state` schema run when `CI_DATABASE` points to an
available file. Otherwise, those integration tests are reported as skipped.

## Smoke test

```bash
construction-intelligence-mcp smoke-test
```

The command prints the resolved source table, identifier and description fields, the
total project count for Southern California districts 7, 8, 11, and 12, and five sample
business objects.

## Launch MCP

The default transport is SSE on `0.0.0.0:8000`:

```bash
construction-intelligence-mcp serve
```

To select the transport or listener explicitly:

```bash
CI_MCP_TRANSPORT=sse CI_MCP_HOST=127.0.0.1 CI_MCP_PORT=8000 construction-intelligence-mcp serve
```

The MCP tools are `search_projects` and `fetch_project`.
