# 010A — Executive Warehouse Reverse Engineering

## Executive Summary

The warehouse could not be inspected in this execution environment. `CI_DATABASE` was unset and
no DuckDB database was present under `/workspace`, `/mnt`, or `/tmp`. Consequently, this report
does **not** claim a warehouse map. Doing so would violate the requirement to use evidence rather
than assumed relationships.

The accompanying read-only profiler is the reproducible discovery mechanism. It searches the
catalog using relation **and column** semantics, profiles every selected relation and column,
tests plausible same-key joins, and emits the three machine-readable inventories. Run it against
the Executive Warehouse to replace the clearly marked empty evidence snapshots:

```bash
python scripts/warehouse/reverse_engineer_executive_warehouse.py \
  --database /path/to/executive.duckdb
```

## Evidence and Method

- The profiler opens DuckDB with `read_only=True`.
- Catalog discovery considers all non-system schemas and matches both relation and column names.
- Relation profiles record row counts, types, candidate single-column keys, per-column NULL and
  duplicate percentages, semantic field groups, and bounded representative records.
- Join candidates require an exact, case-insensitive shared lineage-key name. Each candidate is
  measured for distinct-key overlap, directional coverage, matched rows, output rows, and
  cardinality. It is accepted only when both distinct key sets overlap completely.
- Catalog name matches are labelled as candidates, never certified business definitions.

## Entity Inventory

No evidence-backed entities are available. See
`data/output/warehouse/executive_relation_inventory.json`; its status is `not_generated`.

## Relationship Inventory

No relationship is asserted. The profiler measures candidates, but certification additionally
requires declared constraints, warehouse metadata, or source-owner evidence.

## Semantic Concept Inventory

The discovery covers governed finding, source document, source heading, source section key,
artifact, knowledge record, project linkage, district linkage, program, objective, theme, policy
driver, and expected outcome. Their actual relation, column, meaning, grain, and coverage remain
unknown until the profiler runs against the warehouse.

## Certified Keys

None are certified. A non-null unique column is reported as a *candidate* only. Whether it is
stable, generated, natural, versioned, or a lineage key cannot be derived safely from value
uniqueness alone.

## Join Matrix

No joins were measurable without the database. The generated join inventory will contain one row
per tested relation/column pair and will explicitly retain rejected joins.

## Coverage Matrix

Coverage is not available. After execution, relation-column coverage is `100 - NULL percentage`;
join coverage is recorded independently from the left and right key sets.

## Lineage Diagram

See [010A-executive-lineage-graph.md](010A-executive-lineage-graph.md). No lineage edge is drawn
without measured or declared evidence.

## ERD

See [010A-executive-warehouse-erd.md](010A-executive-warehouse-erd.md). The evidence-state diagram
is intentionally empty rather than presenting the example topology as fact.

## Warehouse Topology

Unknown. In particular, the proposed Artifact → Document → Page → Section → Knowledge Record →
Refined Section → Semantic Knowledge sequence was **not** assumed.

## Unknown Concepts

All requested semantic concepts and all entity relationships remain unknown in the checked-in
snapshot. `governed_finding` and the certified executive lineage graph are specifically unresolved.

## Recommended Strategic Context Contract

No field source should be added to the contract yet. Before use, every contract field should carry
its qualified source relation, source column, business grain, non-null coverage, stable lineage
key, and certification evidence. Ambiguous or name-only matches should fail governed validation.

## Recommended Adapter Contract

This discovery does not change or implement an adapter. A future adapter contract should accept a
read-only database configuration, expose resolved qualified sources and lineage identifiers in
diagnostics, and fail clearly when a required concept has no single certified source.

## Recommended Future Warehouse Improvements

After evidence collection, warehouse owners should consider declared primary/foreign constraints,
a machine-readable business glossary, explicit version and current-row fields, and certification
metadata. These are recommendations only, not claims about the current warehouse.

## Completion Limitation

The reverse-engineering tooling and evidence formats are complete and tested on a synthetic
DuckDB fixture. The actual Executive Warehouse map, representative records, ERD, topology, and
certified lineage cannot be completed until the database is made available.
