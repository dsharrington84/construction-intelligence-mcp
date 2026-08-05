# Construction Intelligence Engineering Backlog

This directory contains implementation-ready Codex tasks.

## Operating rules

- Work one task at a time unless tasks are explicitly independent.
- Read `AGENTS.md` before implementation.
- Do not redesign settled architecture.
- Consumers do not contain SQL.
- DuckDB access remains read-only and isolated in adapters.
- Services return typed business models, never DataFrames.
- Every task must finish with tests, Ruff, a commit, and a PR.

## Status values

- `READY` — dependencies satisfied and implementation may begin.
- `BLOCKED` — prerequisite work is incomplete.
- `BLOCKED_BY_CONTRACT` — accepted business contract is missing.
- `BLOCKED_BY_IMPLEMENTATION` — required implementation is missing or uncertified.
- `SUPERSEDED` — preserved historical record replaced by a newer architecture or contract.
- `IN_PROGRESS` — active Codex task.
- `DONE` — merged and locally validated.


## Program 100 — Executive Intelligence

Program 100 establishes the dependency-gated queue for explaining why Caltrans is investing in a governed project using certified Executive evidence.

| Backlog | Status | Dependency |
|---|---|---|
| [100 Executive Intelligence Program](100-executive-intelligence-program.md) | BLOCKED | 101, 102, and 103 review gates |
| [101 Executive Knowledge Certified Data Product](101-executive-certified-data-product.md) | READY | Phase 0 governance, Constitution, 010A, 010B, and warehouse inspection evidence |
| [102 Executive Evidence Engine](102-executive-evidence-engine.md) | BLOCKED_BY_CONTRACT | 101 accepted |
| [103 Strategic Context Intelligence](103-strategic-context-intelligence.md) | BLOCKED_BY_IMPLEMENTATION | 101 accepted and 102 certified |

Historical Executive research remains in:

- [010A Executive Warehouse Reverse Engineering](../docs/warehouse/010A-executive-warehouse-reverse-engineering.md)
- [010A Executive Warehouse ERD](../docs/warehouse/010A-executive-warehouse-erd.md)
- [010A Executive Lineage Graph](../docs/warehouse/010A-executive-lineage-graph.md)
- [010B Executive Processing Pipeline](../docs/pipeline/010B-executive-processing-pipeline.md)
- [010B Executive Processing DAG](../docs/pipeline/010B-executive-processing-dag.md)
- [010B Executive Processing ERD](../docs/pipeline/010B-executive-processing-erd.md)

No historical Strategic Context backlog document is present in this checkout. Any prior Strategic Context plan that queries physical Executive relations directly is SUPERSEDED by the CDP → Evidence Engine → Intelligence Engine architecture.

## Initial sequence

1. Opportunity Service V1
2. Market Service V1
3. Project Scope Classifier V1
4. Opportunity Pipeline Prototype V1
5. Project Detail Service V1
