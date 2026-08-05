# AGENTS.md

## Engineering Workflow

Before implementing any capability:

1. Read `docs/000-CONSTITUTION.md`.
2. Identify the Program.
3. Identify the Certified Data Product.
4. Verify Constitutional alignment.

If implementation conflicts with the Constitution:

STOP.

Document the conflict.

Do not implement around the architecture.

## Mission

Build and maintain the Construction Intelligence service layer that exposes governed construction business objects to applications, MCP clients, and future APIs.

This repository is the intelligence engine. It sits between certified data products and consumer applications.

```text
Certified DuckDB objects
        ↓
Construction Intelligence services
        ↓
MCP / CLI / future API
        ↓
Opportunity Pipeline and other consumers
```

## Operating Mode

Work as a production software engineer.

Before implementing any intelligence capability, read `docs/000-CONSTITUTION.md` and the relevant Certified Data Product contract.

- Inspect the repository before changing code.
- Make the smallest coherent change that completes the assigned objective.
- Do not redesign settled architecture unless the task explicitly requires it.
- Do not stop at plans, pseudocode, or partial scaffolding.
- Run tests and lint before reporting completion.
- Never claim a commit, test result, file change, or runtime result that does not exist.
- Surface blockers immediately and precisely.

## Repository Boundaries

### This repository owns

- Business models.
- Business services.
- Read-only adapters to governed data sources.
- MCP tools and transport.
- CLI diagnostics and smoke tests.
- Service-level tests.

### This repository does not own

- Source-document parsing.
- Warehouse construction.
- Canonical data materialization.
- Direct mutation of the Caltrans DuckDB warehouse.
- Consumer HTML dashboards unless explicitly added as a separate client package.

The source data platform remains in `Caltrans-Processing`.

## Architecture Rules

### 1. DuckDB access belongs in adapters

Only code under:

```text
src/construction_intelligence_mcp/adapters/
```

may open DuckDB connections or execute SQL.

Services, models, MCP tools, CLIs, and consumers must not contain SQL.

### 2. Services return business objects

Services return Pydantic models or typed Python collections of business models.

Do not return:

- pandas DataFrames;
- NumPy arrays;
- raw DuckDB cursors;
- unnamed tuples;
- database-specific objects.

### 3. Models use business language

Expose business concepts such as:

- `project_id`;
- `description`;
- `district`;
- `route`;
- `county`;
- `programmed_value`;
- `advertisement_date`;
- `primary_scope`.

Do not leak warehouse implementation names unless required for lineage or diagnostics.

### 4. MCP is a transport layer

MCP tools call services. They do not contain business logic or SQL.

The same services must remain reusable by MCP, CLI, future REST APIs, tests, and local consumers.

### 5. Read-only by default

All warehouse connections must be read-only unless a future task explicitly authorizes a governed write path.

Never modify the source DuckDB during search, fetch, smoke tests, or integration tests.

### 6. Preserve explainability

Derived classifications or opportunity signals must expose their basis. Avoid opaque scores unless the contract explicitly defines and tests them.

### 7. Prefer schema-adaptive reads with governed failure

The service may resolve compatible canonical fields dynamically, but it must:

- identify the source relation used;
- identify required resolved fields;
- fail clearly when required concepts cannot be resolved;
- never silently substitute unrelated fields;
- never invent missing business values.

## Current Service Contract

### `ProjectService`

`ProjectService` is the governed interface for project discovery.

It must support:

- district filtering;
- advertisement start and end filtering;
- minimum programmed value filtering;
- free-text filtering;
- bounded result limits;
- fetching one project by `project_id`;
- clear diagnostics for missing databases, relations, and required fields.

Consumers must use `ProjectService` rather than query `ci_market_state` directly.

## Coding Standards

- Python 3.12 or newer.
- Use type hints on public functions and methods.
- Use Pydantic for external and service business contracts.
- Use `pathlib.Path` for filesystem paths.
- Use context managers for database connections.
- Prefer focused modules over large multipurpose files.
- Keep functions small enough to test independently.
- Use descriptive names; avoid abbreviations that obscure business meaning.
- Do not introduce a dependency without a concrete need.
- Keep line length within Ruff configuration.

## Test Requirements

Every functional change must include or update tests.

Minimum completion gate:

```bash
pip install -e ".[dev]"
pytest -q
ruff check .
```

Before modifying code, run the existing suite when practical. After modifying code, all tests and Ruff checks must pass.

### Test strategy

- Unit tests must not require the production DuckDB.
- Integration tests may use `CI_DATABASE` when available.
- Integration tests must skip clearly when the configured database is unavailable.
- Tests must never mutate the source database.
- Add regression tests for every corrected defect.
- Validate both successful results and governed failure behavior.

## Environment

Primary environment variable:

```bash
export CI_DATABASE="/mnt/c/Users/dshar/Desktop/Caltrans_Pricing_Data/database/caltrans_pricing.duckdb"
```

Do not hard-code alternate user-specific paths into new modules. Use configuration with a documented default only where the existing application contract requires it.

## Git Workflow

- Start work from the requested base branch.
- Create a focused feature branch unless instructed otherwise.
- Keep commits coherent and truthful.
- Do not mix unrelated cleanup into a feature commit.
- Never force-push or rewrite shared history unless explicitly authorized.
- Do not commit secrets, local databases, virtual environments, caches, or generated private data.

Recommended branch naming:

```text
feature/<short-objective>
fix/<short-defect>
chore/<short-maintenance-task>
```

## Completion Report

When a task is complete, report only verifiable results:

- branch name;
- commit SHA or pull request;
- files changed;
- commands run;
- test and Ruff results;
- remaining limitations or skipped validations.

Do not report speculative future work unless asked.

## Product Direction

The primary consumer workflow is project-centered:

```text
Market intelligence
        ↓
Potential opportunities
        ↓
Selected pursuit portfolio
        ↓
Opportunity review
        ↓
Future contractor and cost intelligence
```

The platform should help an estimator answer:

- Which projects deserve attention?
- Why did each project surface?
- Where are the opportunities by district and scope?
- What does the selected pursuit portfolio provide the company?

Do not turn the service layer into a generic CRM, a dashboard-only product, or an opaque scoring engine.

## Current Priority

Complete and stabilize project discovery before expanding into opportunity, market, contractor, or cost services.

Do not add new service domains unless the assigned task explicitly requests them.
