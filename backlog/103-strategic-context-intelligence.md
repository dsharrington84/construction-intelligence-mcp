# 103 — Strategic Context Intelligence

Status: BLOCKED_BY_IMPLEMENTATION

Dependencies:

- 101 accepted.
- 102 certified.

## Purpose

Produce project-specific strategic intelligence from ExecutiveEvidence.

Strategic Context must not query DuckDB or physical Executive warehouse relations directly.

## Objective

Explain why Caltrans is investing in a governed project using ExecutiveEvidence and governed
project attributes.

## Inputs

- Governed Project object.
- ExecutiveEvidence from Initiative 102.
- Accepted matching and confidence rules.

## Output

The output is:

```text
StrategicContext
```

Expected concepts:

- project_id;
- strategic_context_id;
- programs;
- objectives;
- policy_drivers;
- expected_outcomes;
- strategic_themes;
- evidence;
- source_confidence;
- limitations.

Every non-empty conclusion must reference one or more valid evidence IDs.

## Matching Precedence

Deterministic precedence:

1. explicit project linkage;
2. route/county/district plus program linkage;
3. project-type or asset linkage;
4. strategic-theme linkage;
5. statewide or document-level context.

Broad statewide evidence must never be represented as DIRECT project evidence.

## Evidence Strength

- DIRECT
- SUPPORTING
- CONTEXTUAL

## Confidence

- HIGH
- MODERATE
- LIMITED
- NONE

Confidence must reflect evidence strength, completeness, and limitations. It is not pursuit
confidence.

## Empty Result Rule

A valid project may return:

- no conclusions;
- no evidence;
- confidence NONE;
- explicit limitations.

Do not force context where no defensible match exists.

## Integration

Integrate into:

- ProjectIntelligence;
- `fetch_strategic_context(project_id)`;
- `fetch_project_intelligence(project_id)`.

Both MCP paths must return the same StrategicContext object.

## Prohibited Behavior

Do not:

- query DuckDB directly;
- discover Executive relations;
- redefine ExecutiveEvidence;
- use fuzzy matching;
- use an LLM;
- use randomness;
- generate unsupported programs or outcomes;
- recommend bid/no-bid;
- score opportunity attractiveness.

## Tests

Required tests:

- direct project linkage;
- route/county/district alignment;
- program alignment;
- scope/asset alignment;
- statewide contextual evidence;
- CONTEXT_ONLY restrictions;
- no-evidence result;
- deterministic ordering;
- evidence deduplication;
- conclusion-to-evidence validation;
- confidence calculation;
- limitation propagation;
- Project Intelligence integration;
- MCP serialization;
- Southern California CI_DATABASE integration.

## Program 100 Exit Gate

This initiative closes Program 100 only when the business demonstration succeeds:

Can the platform explain why Caltrans is investing in a Southern California project using only
governed, traceable Executive evidence?
