# 203 — Contractor Intelligence

Status: BLOCKED_BY_IMPLEMENTATION

Dependencies:

- 201 accepted.
- 202 certified.

## Purpose

Plan Contractor Intelligence that consumes ContractorEvidence and produces ContractorContext.

This initiative must not be implemented until ContractorEvidence is certified and reviewed. It does
not implement opportunity scoring, bid/no-bid recommendations, cost intelligence, services,
adapters, MCP tools, or application behavior during this planning task.

## Business Purpose

Explain contractor participation and historical market behavior for governed projects using only
certified ContractorEvidence.

Contractor Intelligence must support project-centered understanding without recommending whether
to pursue a project, estimating what it should cost, or assigning an opportunity score.

## Inputs

- Governed Project object when later integrated through Project Intelligence.
- ContractorEvidence from Initiative 202.
- Accepted matching, confidence, evidence-strength, and limitation rules.

Required input concepts are Pending Contract until Initiatives 201 and 202 are accepted.

## Outputs

The planned output is:

```text
ContractorContext
```

Expected responsibilities include representing:

- project identifier when project context is requested;
- contractor participation context;
- historical market behavior context;
- governed evidence references;
- confidence;
- evidence strength;
- limitations.

Specific ContractorContext fields are Pending Contract. Every non-empty conclusion must reference
one or more valid ContractorEvidence records.

## Matching Rules

Pending Contract.

Matching rules must be deterministic, reviewable, and evidence-backed. Contractor Intelligence must
not use fuzzy matching, randomness, ungoverned heuristics, or physical storage assumptions unless a
future accepted contract explicitly authorizes and tests them.

## Confidence

Pending Contract.

Confidence must reflect evidence strength, completeness, lineage quality, and limitations. It must
not represent pursuit confidence, contractor preference, bid/no-bid attractiveness, cost confidence,
or opportunity score.

## Evidence Strength

Pending Contract.

Evidence strength levels must be defined before implementation and must distinguish direct,
supporting, and contextual contractor evidence if those concepts are accepted by the contract.
Broad market context must not be represented as direct project-specific contractor evidence unless
certified evidence supports that relationship.

## Limitations

ContractorContext must surface limitations when evidence is incomplete, contextual, ambiguous,
missing, or otherwise restricted by the accepted contracts.

A valid project may return no contractor conclusions, no contractor evidence, confidence NONE if
accepted by contract, and explicit limitations. Contractor Intelligence must not force conclusions
where no defensible evidence exists.

## Tests

Future implementation tests must cover, at minimum:

- ContractorEvidence consumption without direct DuckDB access;
- deterministic matching behavior;
- confidence calculation from accepted rules;
- evidence-strength assignment from accepted rules;
- limitation propagation;
- no-evidence result behavior;
- evidence deduplication;
- conclusion-to-evidence validation;
- Project Intelligence integration when authorized;
- MCP serialization when authorized;
- rejection of opportunity scoring, bid/no-bid recommendation, and cost inference behavior.

## Review Gate

Can the platform explain contractor participation and historical market behavior using only
governed contractor evidence?

## Definition of Done

Initiative 203 is done only when:

- Initiatives 201 and 202 are accepted and certified as required.
- ContractorContext consumes ContractorEvidence rather than physical contractor storage.
- Matching, confidence, evidence strength, and limitations follow accepted rules.
- Every non-empty contractor conclusion references governed evidence.
- Empty or limited results remain governed and explainable.
- Project Intelligence integration is reviewed, if authorized.
- Tests and checks pass.
- The Program 200 review gate succeeds.
