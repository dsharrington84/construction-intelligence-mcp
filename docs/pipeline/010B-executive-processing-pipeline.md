# 010B — Executive Processing Pipeline

## Executive Summary

The complete source tree was inspected, including executable Python and shell files, SQL-like
statements, documentation, tests, and the requested directory-name vocabulary. This repository
contains **no Executive warehouse build pipeline**: no production `CREATE TABLE`, `CREATE VIEW`,
`INSERT`, `MERGE`, `UPDATE`, or `COPY` producer was found. The only DuckDB-aware Executive code is
the read-only 010A warehouse profiler; it discovers and profiles an already-built database rather
than producing one.

Therefore the production pipeline cannot be reconstructed from this checkout. In particular,
`governed_finding` is not generated, assembled, derived, or stored by production code here. It is
a discovery term in the profiler and a synthetic test-fixture column. No semantic equivalent can
be certified from source code. This is a proven repository-scope absence, not a claim that the
concept is absent from an external Executive Warehouse or its owning `Caltrans-Processing`
repository.

This result also resolves a mismatch in the supplied background: the checked-in 010A evidence
snapshots have `evidence_status: not_generated` and explicitly say the database was unavailable.
No refined-section, section-lineage, or document-lineage relation names are present in those
snapshots. Those externally reported findings cannot be promoted to code evidence here.

## Evidence and Method

`scripts/pipeline/reverse_engineer_executive_pipeline.py` recursively scans readable source and
documentation files, records SQL write/read tokens with file and line evidence, distinguishes
tests and documentation from production candidates, and writes deterministic JSON inventories.
It does not import application code, connect to DuckDB, read `CI_DATABASE`, or mutate data.

The generated inventory records every inspected file. Searches additionally covered names and
content for `scripts`, `ci`, `executive`, `knowledge`, `materialize`, `warehouse`, `refine`,
`semantic`, `fragment`, `assembly`, `pipeline`, and `framework`. Only `scripts/warehouse` existed
before this deliverable; no SQL files, migration framework, certification scripts, or source
processing packages exist in the checkout.

## Pipeline Overview

The only evidence-backed flow is:

```text
Externally produced Executive DuckDB (not present; producer unknown)
       |
       v
read-only 010A profiler
       |
       +--> relation inventory
       +--> measured join inventory
       `--> semantic-name inventory
```

This is an **inspection flow**, not a processing or promotion pipeline.

## Execution Order

There is no evidence-backed production build order. The executable order that does exist is:

1. An operator supplies an already-created DuckDB path to the 010A profiler.
2. The profiler opens it read-only and discovers candidate relations from catalog metadata.
3. It profiles relations, tests possible joins, and maps semantic name matches.
4. It writes JSON observations under `data/output/warehouse`.

OCR, section creation, fragment assembly, knowledge extraction, refinement, classification,
certification, and current promotion cannot be ordered because none is implemented here.

## Script Inventory

| Script/module | Inputs | Outputs | Purpose | Materialization |
|---|---|---|---|---|
| `scripts/warehouse/reverse_engineer_executive_warehouse.py` | Existing DuckDB catalog and selected relation contents | Three warehouse JSON inventories | Read-only profiling; not a producer | Full replacement of diagnostic JSON only |
| `scripts/pipeline/reverse_engineer_executive_pipeline.py` | Repository text files | Three pipeline JSON inventories | Read-only static evidence scan | Full deterministic replacement of diagnostics |

There are no intake, OCR, extraction, refinement, semantic assembly, warehouse build,
certification, migration, or promotion scripts in scope.

## Materialization Inventory

No production warehouse materialization was found. SQL writes recorded by the scanner occur only
in tests or prose/examples. Consequently, input tables, transformation logic, rebuild behavior,
incremental keys, version strategy, and promotion behavior are all **not evidenced**.

## Warehouse Inventory

No Executive warehouse database is checked in and `CI_DATABASE` was not changed or accessed.
The 010A inventories contain no relations. Thus there is no evidence-backed enumeration of
Executive relations in this repository, and it would be inaccurate to claim every external table
has been mapped. The machine-readable producer inventory truthfully contains zero production
relation writes.

## Transformation Graph

See [the processing DAG](010B-executive-processing-dag.md). There are no discovered production
transformation nodes or edges.

## Semantic Generation Graph

No semantic-generation code exists. Occurrences are name evidence only:

- `governed_finding` is a profiler search term and synthetic fixture column, not a producer.
- `source_document`, `source_heading`, `program`, `theme`, `objective`, `policy_driver`,
  `expected_outcome`, `region`, `district`, `project_id`, `artifact_id`,
  `knowledge_record_id`, and `section` have no evidenced Executive producer/transformation/output
  column contract.
- The closest *textual* candidate to a governed finding is the profiler's generic semantic group
  for finding-like column names. This is not a semantic equivalent: it performs catalog discovery
  and does not create or certify a value.

The complete occurrence list, including file, line, and evidence classification, is in
`executive_semantic_generation.json`.

## Producer → Consumer Graph

No warehouse producer-to-consumer edge can be established. The profiler is a downstream observer
of an unspecified external producer. Application services do not consume an Executive relation;
Project Intelligence currently exposes an empty `executive_signals` collection without querying
Executive data.

## Governed Data Contracts

### Current, intermediate, temporary, experimental, candidate, and review tables

None can be classified because no table inventory or producer code is available.

### Promotion and certified tables

No certification metadata, current-row mechanism, version columns, aliases/views, or promotion
commands were found. **No Executive table can be declared safe to consume from this evidence.**

## Current Warehouse Contract

There is no evidenced current Executive contract in this checkout. A name match, uniqueness
measurement, or inferred join from the 010A profiler is explicitly diagnostic and cannot establish
certification, stability, or business meaning.

## Unknown Concepts

All requested concepts remain unknown at the production-pipeline level: their producer,
transformation, relation, column, grain, lifecycle, and business meaning are not present in code.
This includes governed finding, source document/heading, program, theme, objective, policy driver,
expected outcome, region/district, project/artifact linkage, knowledge record ID, and section
lineage.

## Recommended Strategic Context Contract

This task does not implement Strategic Context. Before a future contract is designed, the owning
pipeline must supply, per field: qualified certified relation/column, grain, stable identifier,
source document and section lineage, derivation rule, version, current/certified status, and null
behavior. `governed_finding` must not be synthesized from a merely similar text column.

## Recommended Executive Adapter Contract

This task does not modify an adapter. A future adapter should consume only owner-certified current
relations, remain read-only, return business objects, expose source/version/lineage diagnostics,
and fail clearly when required concepts cannot be uniquely resolved. The existing profiler output
must not itself be treated as certification.

## Recommended Warehouse Improvements

For the external warehouse owner, the missing evidence could be made portable through a committed
build manifest containing script identifiers, inputs/outputs, execution order, full-versus-
incremental mode, semantic derivations, schema/version identifiers, certification checks, and the
atomic promotion mechanism. Declared keys and column-level lineage would make producer and
semantic contracts mechanically verifiable.

## Reproduction and Limitation

Run:

```bash
python scripts/pipeline/reverse_engineer_executive_pipeline.py --root . \
  --output-dir data/output/pipeline
```

The result is complete for the files in this repository at scan time. Completing the external
production DAG requires the source repository that owns Executive processing and/or an Executive
DuckDB plus its build and certification metadata. No undocumented transformation is guessed.
