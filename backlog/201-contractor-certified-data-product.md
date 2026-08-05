# 201 — Contractor Certified Data Product

Status: READY

Dependency: Certified v1.0 baseline and Program 100 planning progress. Initiative 201 is ready for contract-development work.

## Purpose

Define the governed business contract for the Contractor Certified Data Product.

This initiative defines the business contract only. It does not implement production code,
services, adapters, MCP tools, tests, warehouse objects, Contractor Evidence, Contractor
Intelligence, or application behavior.

## Business Purpose

Establish the certified contractor evidence boundary needed to explain contractor participation and
historical market behavior.

The contract must support future ContractorEvidence consumers without exposing processing internals
or physical storage structures. Where contractor concepts are not yet governed, they must remain
marked as Pending Contract rather than guessed.

## Business Grain

Pending Contract.

The accepted contract must define the precise business grain for contractor evidence before any
implementation begins. Candidate grains must not be treated as certified until reviewed and
accepted.

## Business Keys

Pending Contract.

The accepted contract must identify stable contractor business keys and any required project,
contract, bid, award, or source-document keys. Do not infer unsupported keys from physical storage
or diagnostic artifacts.

## Producer

Pending Contract.

The producer is expected to be a governed Contractor Processing Pipeline, but the authoritative
producer, ownership, certification responsibilities, and publication guarantees must be documented
in the accepted contract before implementation.

## Consumer Contract

The Contractor Certified Data Product must define the consumer contract for future
ContractorEvidence. The contract must identify:

- business purpose;
- business concepts;
- business grain;
- business keys;
- allowed evidence categories;
- required lineage;
- quality expectations;
- certification rules;
- eligibility and exclusion rules;
- consumer guarantees;
- known limitations;
- governed failure behavior.

Any unknown business concepts must be marked Pending Contract. The contract must not redefine
physical tables, views, files, or relation names as the certified business contract.

## Lineage

Pending Contract.

The accepted contract must preserve traceability from ContractorEvidence back to certified source
facts and any required upstream source material. Lineage must be sufficient for diagnostics,
auditability, quality review, and responsible change management.

## Certification

Pending Contract.

The accepted contract must define certification criteria before Initiative 202 can implement
ContractorEvidence. Certification must identify eligible evidence, ineligible evidence, unknown or
unsupported states, quality expectations, and required validation behavior.

## Known Limitations

Known limitations at planning time:

- Initiative 201 is ready for contract-development work; implementation of downstream Program 200 capabilities remains blocked until this contract is accepted.
- Contractor business grain is Pending Contract.
- Contractor business keys are Pending Contract.
- Contractor producer and ownership are Pending Contract.
- Contractor lineage requirements are Pending Contract.
- Contractor eligibility, exclusion, confidence, and evidence-strength rules are Pending Contract.
- No ContractorEvidence or ContractorContext implementation is authorized by this initiative.

## Acceptance Criteria

Initiative 201 is done only when:

- The Contractor Certified Data Product contract exists and is reviewed.
- The contract identifies business purpose, grain, keys, producer, lineage, certification rules,
  consumer guarantees, and limitations.
- The contract separates certified contractor facts from unresolved implementation details.
- Unknown contractor concepts are marked Pending Contract rather than guessed.
- Review accepts the contract as sufficient input for Initiative 202.

## Unlock Condition

202 becomes READY only when Initiative 201 is reviewed and accepted.
