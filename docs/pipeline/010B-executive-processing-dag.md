# 010B — Executive Processing DAG

## Evidence-backed pipeline DAG

```mermaid
flowchart LR
    external[(External Executive DuckDB\nnot available)]
    unknown[External producer\nnot present / unknown]
    profiler[010A read-only warehouse profiler]
    relations[Relation inventory]
    joins[Join inventory]
    semantics[Semantic-name inventory]

    unknown -. "unverifiable production edge" .-> external
    external -->|read-only catalog and data inspection| profiler
    profiler --> relations
    profiler --> joins
    profiler --> semantics
```

The dotted edge is explicitly unknown. There are no evidence-backed raw-document, OCR, section,
fragment, extraction, refinement, semantic assembly, certification, or promotion nodes.

## Warehouse dependency graph

No relation-to-relation edge is established because the checked-in 010A relation inventory is
empty and this repository contains no Executive relation producer.

## Script dependency graph

```mermaid
flowchart LR
    operator[Operator-provided database path] --> profiler[reverse_engineer_executive_warehouse.py]
    repository[Repository source tree] --> scanner[reverse_engineer_executive_pipeline.py]
    profiler --> warehouse_json[data/output/warehouse/*.json]
    scanner --> pipeline_json[data/output/pipeline/*.json]
```

The two scripts are independent diagnostic tools. Neither invokes the other or materializes a
warehouse relation.

## Table dependency graph

```mermaid
flowchart TB
    none[No Executive table definitions or writes discovered]
```

## Semantic generation graph

```mermaid
flowchart LR
    term[Semantic search terms] --> profiler[Catalog matcher]
    profiler --> candidates[Uncertified diagnostic matches]
```

This graph describes discovery only. It does not generate governed executive knowledge.
