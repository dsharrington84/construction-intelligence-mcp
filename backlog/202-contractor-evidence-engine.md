# 202 — Contractor Evidence Engine

Status: BLOCKED_BY_CONTRACT

Dependency: 201 accepted.

## Purpose

Plan the translation boundary between the Contractor Certified Data Product and downstream
Contractor Intelligence.

This initiative must not be implemented until the Contractor Certified Data Product is accepted.
It consumes the accepted Contractor Certified Data Product and produces canonical
ContractorEvidence. It must not produce ContractorContext, opportunity recommendations, cost
intelligence, or application behavior.

## Responsibilities

The Contractor Evidence Engine is responsible for:

- consuming only the accepted Contractor Certified Data Product contract;
- isolating physical implementation details behind governed adapter boundaries when later
  implemented;
- validating certified contractor evidence eligibility;
- normalizing governed contractor evidence into canonical ContractorEvidence;
- preserving lineage required by the accepted contract;
- exposing diagnostics for governed failure and review;
- avoiding interpretation, scoring, recommendation, or pursuit decision logic.

## Inputs

Only inputs guaranteed by the accepted Contractor Certified Data Product are valid.

Current required input concepts are Pending Contract. Do not consume undocumented physical
Contractor relations, diagnostic profiler output, candidate fields, or application assumptions as a
certified contract.

## Outputs

The planned output is:

```text
ContractorEvidence
```

Required ContractorEvidence fields are Pending Contract and must be defined by Initiative 201.
Expected output responsibilities include preserving:

- contractor business identity when certified;
- project, contract, bid, award, or market linkage when certified;
- evidence category when certified;
- source lineage;
- certification status;
- limitations;
- diagnostics required by the accepted contract.

Do not finalize output fields that remain unresolved in Initiative 201.

## Diagnostics

The engine must define diagnostics, after contract acceptance, for:

- selected certified source contract version;
- resolved required concepts;
- rejected or missing required concepts;
- eligibility distribution;
- lineage coverage;
- duplicate evidence identity counts;
- ambiguous linkage counts;
- unsupported or unknown status counts;
- final eligible ContractorEvidence count;
- governed limitations.

Diagnostic details that depend on unknown contractor fields are Pending Contract.

## Validation

The engine must fail clearly or surface governed limitations for:

- missing accepted Contractor Certified Data Product contract;
- missing required contractor business identity;
- missing required evidence identity;
- missing required lineage;
- unknown or ineligible certification states;
- ambiguous contractor or project linkage;
- duplicate evidence identity;
- unsupported evidence categories;
- empty eligible evidence where the contract requires nonzero certified coverage.

Validation rules remain Pending Contract until Initiative 201 is accepted.

## Tests

Future implementation tests must cover, at minimum:

- evidence assembly from the accepted contract;
- required lineage preservation;
- eligibility handling;
- unknown or unsupported state rejection;
- duplicate prevention;
- ambiguous linkage rejection;
- deterministic ordering;
- governed empty-result behavior;
- diagnostics for missing concepts and rejected evidence;
- actual certified data product integration when available.

Tests must not require production DuckDB for unit coverage and must never mutate source data.

## Definition of Done

Initiative 202 is done only when:

- Initiative 201 is accepted before implementation begins.
- The engine returns canonical ContractorEvidence matching the accepted contract.
- The engine preserves certified lineage and limitations.
- The engine rejects ineligible, ambiguous, duplicate, and unsupported evidence paths.
- Diagnostics report resolved concepts, eligibility, lineage coverage, rejected evidence, and final
  eligible ContractorEvidence count.
- Tests and checks pass.
- Review accepts ContractorEvidence as sufficient input for Initiative 203.

## Unlock Condition

203 becomes READY only when 202 is implemented, certified, and reviewed.
