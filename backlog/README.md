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
- `IN_PROGRESS` — active Codex task.
- `DONE` — merged and locally validated.

## Initial sequence

1. Opportunity Service V1
2. Market Service V1
3. Project Scope Classifier V1
4. Opportunity Pipeline Prototype V1
5. Project Detail Service V1
