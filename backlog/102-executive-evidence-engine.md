# 102 — Executive Evidence Engine

Status: IN_REVIEW

Dependency: 101 accepted and explicit CDP-001 physical implementation mapping configured.

## Purpose

Plan and implement the translation boundary between the Executive Certified Data Product and
downstream intelligence.

The planned engine must consume the certified CDP contract and produce canonical ExecutiveEvidence
objects. It must not produce Strategic Context.

## Objective

Implement, after CDP-001 acceptance, an Executive Evidence Engine that returns certified, normalized, lineage-preserving
ExecutiveEvidence objects.

## Architectural Responsibility

The Evidence Engine:

- consumes CDP-001;
- isolates physical warehouse implementation;
- validates certified joins and eligibility;
- normalizes governed evidence;
- preserves lineage;
- exposes diagnostics;
- does not interpret evidence for a specific project.

## Inputs

Only inputs guaranteed by accepted CDP-001 are valid inputs. Do not consume undocumented physical
Executive relations, diagnostic profiler output, or candidate fields as certified contract. Runtime
consumption must use exactly one explicit accepted schema-qualified CDP-001 physical implementation
mapping supplied by application composition/configuration, never relation-name discovery.

## Output

The output is:

```text
ExecutiveEvidence
```

Required concepts must come from accepted CDP-001. Expected concepts may include:

- evidence_id;
- evidence_type;
- source_document;
- source_section_id;
- source_text or source_excerpt;
- refinement_status;
- semantic metadata;
- source_lineage;
- limitations.

Do not finalize fields that remain unresolved in Initiative 101. Reference the accepted CDP
contract instead of duplicating it.

## Adapter Boundary

All DuckDB discovery and SQL must remain inside adapters or repositories. The service layer
consumes normalized evidence and must not know physical Executive relation names or SQL joins.

## Certification Behavior

The engine must reject:

- unknown or ineligible statuses;
- missing evidence identity;
- missing required lineage;
- missing required evidence content;
- ambiguous join paths;
- zero-overlap joins;
- uncontrolled many-to-many multiplication;
- duplicate evidence identity;
- staging, candidate, exception, review, quarantine, or excluded records unless explicitly permitted by CDP-001.

## Diagnostics

The engine must expose diagnostics for:

- selected relations;
- relation roles;
- join path;
- join coverage;
- status distribution;
- source-text coverage;
- source-document coverage;
- unmatched lineage count;
- duplicate evidence count;
- final eligible record count;
- unknown status count;
- rejected relation/path summaries.

## MCP or Service Exposure

Expose a narrow governed interface such as:

```text
fetch_executive_evidence(...)
```

Do not require a public MCP tool unless the accepted architecture specifically needs one.
Strategic Context must be able to consume the engine without DuckDB knowledge.

## Tests

Controlled tests must cover:

- evidence assembly;
- source-text preservation;
- source-document lineage;
- source-section lineage;
- status eligibility;
- CONTEXT_ONLY handling;
- excluded/review-required handling;
- unknown status rejection;
- duplicate prevention;
- deterministic ordering;
- zero-overlap rejection;
- ambiguous join rejection;
- many-to-many rejection;
- actual CI_DATABASE nonzero evidence population.

## Definition of Done

Initiative 102 is done when:

- CDP-001 is accepted before implementation begins.
- The engine returns canonical ExecutiveEvidence objects matching the accepted contract.
- The engine preserves certified source-document and source-section lineage.
- The engine rejects ineligible, ambiguous, duplicate, and zero-overlap evidence paths.
- Diagnostics report relation roles, join coverage, status distribution, lineage coverage, and final eligible record count.
- Actual CI_DATABASE integration demonstrates nonzero eligible Executive evidence.
- Tests and checks pass.
- Review accepts the engine as sufficient input for Initiative 103.

## Unlock Condition

103 becomes READY only when 102 is implemented, certified, and reviewed.
