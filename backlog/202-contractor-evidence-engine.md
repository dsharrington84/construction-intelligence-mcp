# 202 — Contractor Evidence Engine

Status: BLOCKED_BY_CONTRACT

Dependency: 201 accepted.

Program: Program 200 — Contractor Intelligence.

Certified Data Product: CDP-002 — Contractor Certified Data Product.

## Constitutional Alignment

Initiative 202 remains **BLOCKED_BY_CONTRACT until CDP-002 is accepted**. Planning may continue,
but implementation must not begin until Initiative 201 accepts the governed CDP-002 contract and
identifies exactly one current physical implementation mapping.

This initiative aligns with the Constitution by keeping Processing Pipeline outputs behind a
Certified Data Product boundary, translating accepted CDP-002 facts into Intelligence Layer business
objects, preserving evidence and lineage, and failing clearly when the certified basis is missing,
ambiguous, or incomplete. It mirrors the successful Program 100 architecture used by the Executive
Evidence Engine: canonical model, explicit accepted mapping, read-only adapter, service-level
eligibility rules, diagnostics, and certification tests.

## Purpose

Plan the translation boundary between the Contractor Certified Data Product and downstream
Contractor Intelligence.

This initiative must not be implemented until CDP-002 is accepted. It consumes the accepted
Contractor Certified Data Product and produces canonical ContractorEvidence. It must not produce
ContractorContext, opportunity recommendations, cost intelligence, scoring, CRM behavior,
application workflow, or source data processing.

## Initiative-Level Responsibilities

The future Contractor Evidence Engine will be responsible for:

- consuming only the accepted CDP-002 contract;
- requiring exactly one accepted/current schema-qualified CDP-002 implementation mapping;
- isolating DuckDB and SQL inside adapters;
- translating accepted physical rows into canonical ContractorEvidence business objects;
- applying governed eligibility and rejection rules;
- preserving certified source lineage, limitations, and explainability;
- exposing diagnostics for review and certification;
- providing a narrow service interface reusable by future MCP, CLI, REST, tests, and consumers.

## Initiative-Level Non-Goals

Initiative 202 must not:

- implement ContractorEvidence before CDP-002 acceptance;
- create production Python during planning;
- assume, infer, discover, or finalize fields not guaranteed by CDP-002;
- consume undocumented DuckDB relations, profiler output, staging tables, quarantine tables,
  candidate fields, or processing internals;
- perform relation-name discovery to find CDP-002;
- mutate the source DuckDB warehouse;
- implement contractor interpretation, market summaries, pursuit recommendations, opaque scores,
  bid strategy, cost intelligence, contractor context, or application UI behavior.

## Planned Output

The planned output is:

```text
ContractorEvidence
```

The canonical model must use business language and may plan concepts such as:

- `evidence_id`;
- `contractor_id`;
- `contractor_name`;
- `evidence_type`;
- `contract_id`;
- participation role;
- bid rank;
- bid amount;
- bid status;
- district;
- project type;
- bid date;
- prime contractor;
- subcontractor;
- relationship type;
- source lineage;
- eligibility;
- limitations.

These concepts are planning targets only. The implementation task must not finalize required fields,
types, enumerations, or eligibility states unless they are guaranteed by accepted CDP-002.

## Codex-Ready Implementation Tasks

### 202A — Canonical ContractorEvidence model

**Dependency:** CDP-002 accepted by Initiative 201, including guaranteed business concepts,
eligibility states, lineage requirements, and limitations semantics.

**Files likely affected:**

- `src/construction_intelligence_mcp/models/contractor_evidence.py`
- `src/construction_intelligence_mcp/models/__init__.py` if model exports are used
- `tests/` model or service test modules added for Contractor Evidence

**Task:** Define the canonical ContractorEvidence business contract and companion diagnostics/result
models after CDP-002 acceptance. The model must preserve certified contractor identity, evidence
identity, evidence category, contract or project linkage, bid/award facts when guaranteed,
contractor relationship facts when guaranteed, source lineage, eligibility, and limitations. It
should follow the Program 100 pattern of a canonical evidence model, lineage model, diagnostics
model, and result wrapper, but must use contractor business language and the accepted CDP-002
contract.

**Field planning constraints:**

- Plan for `evidence_id`, `contractor_id`, `contractor_name`, `evidence_type`, `contract_id`,
  participation role, bid rank, bid amount, bid status, district, project type, bid date, prime
  contractor, subcontractor, relationship type, source lineage, eligibility, and limitations.
- Mark fields as required only when CDP-002 guarantees them for eligible evidence.
- Represent missing optional-but-certified facts as explicit `None` values or limitations, not
  invented defaults.
- Use Pydantic models and typed Python collections.
- Keep warehouse implementation names out of business objects except where required for lineage or
  diagnostics.

**Non-goals:**

- Do not create the model until CDP-002 is accepted.
- Do not add SQL, DuckDB access, service logic, MCP tools, or scoring.
- Do not finalize contractor, bid, award, relationship, or eligibility fields that CDP-002 does not
  guarantee.

**Acceptance criteria:**

- Canonical ContractorEvidence, ContractorEvidenceLineage, ContractorEvidenceDiagnostics, and
  ContractorEvidenceResult models exist and match accepted CDP-002 terminology.
- Required fields exactly match accepted CDP-002 guarantees.
- Optional fields and limitations clearly express certified absence, uncertainty, or constrained use.
- The model can represent bid participation, prime/subcontractor relationship evidence, and lineage
  only to the extent accepted by CDP-002.
- Public functions/classes use type hints.

**Failure behavior:**

- Model validation rejects missing required certified identity, evidence identity, required lineage,
  and invalid accepted enumerations.
- Optional absent facts do not fail validation unless CDP-002 defines them as required for eligible
  evidence.

**Test requirements:**

- Unit tests validate successful construction for each accepted evidence type.
- Unit tests validate missing required identity, evidence identity, lineage, and invalid eligibility
  values.
- Unit tests validate limitations and optional fields for partially certified evidence.
- Tests must not require production DuckDB.

### 202B — Explicit physical implementation mapping

**Dependency:** CDP-002 accepted by Initiative 201 with exactly one current physical implementation
relation approved for Contractor Evidence consumption.

**Files likely affected:**

- `src/construction_intelligence_mcp/adapters/contractor_evidence_adapter.py`
- `src/construction_intelligence_mcp/config.py` or equivalent composition module if existing
  configuration patterns require it
- `tests/` adapter configuration tests
- Documentation or smoke-test files only if existing contracts require them

**Task:** Define the explicit physical implementation mapping mechanism for CDP-002. Runtime
consumption must require exactly one accepted/current schema-qualified CDP-002 implementation
mapping supplied by application composition or configuration.

**Mapping requirements:**

- The mapping identifies product `CDP-002`.
- The mapping includes a schema-qualified relation name.
- The mapping includes an accepted/current certification status.
- The mapping includes a certified-current relation role or equivalent accepted role.
- Ambiguous, missing, stale, rejected, candidate, staging, diagnostic, review, quarantine,
  temporary, archive, or non-schema-qualified mappings fail clearly.
- Relation-name discovery is prohibited.

**Non-goals:**

- Do not implement relation-name discovery or schema scanning as selection logic.
- Do not select between multiple accepted mappings.
- Do not infer current implementation from table naming conventions.
- Do not accept candidate or profiler relations as certified implementations.

**Acceptance criteria:**

- The adapter/configuration layer accepts exactly one accepted/current CDP-002 mapping.
- Missing mappings produce a clear governed error.
- More than one accepted/current mapping produces a clear ambiguity error.
- Non-schema-qualified mappings fail before SQL execution.
- Prohibited relation roles fail before evidence assembly.

**Failure behavior:**

- Missing CDP-002 mapping: fail with a message that no accepted/current CDP-002 mapping is
  configured.
- Multiple accepted/current mappings: fail with listed configured relations.
- Stale or unaccepted mapping: fail with configured status details.
- Prohibited role: fail with the prohibited role.
- Missing physical relation: fail with the selected schema-qualified relation.

**Test requirements:**

- Unit tests for no mapping, stale mapping, multiple mappings, prohibited roles,
  non-schema-qualified relations, and missing physical relations.
- Tests must use temporary DuckDB fixtures, not production DuckDB.

### 202C — Contractor Evidence adapter

**Dependency:** 202A and 202B complete; CDP-002 accepted with required concepts and physical mapping.

**Files likely affected:**

- `src/construction_intelligence_mcp/adapters/contractor_evidence_adapter.py`
- `src/construction_intelligence_mcp/services/contractor_evidence_service.py`
- `tests/` adapter and service fixtures for Contractor Evidence

**Task:** Implement read-only translation from the accepted CDP-002 physical implementation into
normalized row dictionaries or typed adapter records that the service converts into canonical
ContractorEvidence. All DuckDB connections and SQL remain inside the adapter. The adapter must use
only the explicit mapping from 202B.

**Adapter requirements:**

- Open DuckDB through existing read-only adapter patterns.
- Query only the accepted mapped CDP-002 relation.
- Resolve only CDP-002-guaranteed concepts or explicitly accepted compatible names.
- Identify the selected relation and resolved fields for diagnostics.
- Return deterministic ordering by accepted evidence identity and any CDP-002-defined tie-breaker.
- Never silently substitute unrelated fields or invent missing values.

**Non-goals:**

- Do not place SQL in services, models, MCP tools, CLIs, or tests except fixture setup.
- Do not join to undocumented processing tables.
- Do not mutate the source database.
- Do not implement contractor scoring or interpretation.

**Acceptance criteria:**

- Adapter fetches rows from exactly one accepted CDP-002 relation using read-only access.
- Required accepted concepts are validated before evidence assembly.
- Missing required concepts fail with available columns and unresolved concepts.
- The service receives business-oriented records, not DataFrames, cursors, unnamed tuples, or
  database-specific objects.
- Deterministic ordering is enforced.

**Failure behavior:**

- Missing database, missing relation, missing required concept, ambiguous field resolution, or SQL
  execution failure produces a clear governed error.
- Empty relations are allowed only if CDP-002 permits empty certified coverage; otherwise fail or
  expose the accepted governed limitation.

**Test requirements:**

- Unit tests with fixture relations for successful adapter translation.
- Unit tests for missing required concepts, empty relation behavior, deterministic ordering, and
  read-only behavior.
- Integration tests may use `CI_DATABASE` only when configured and must skip clearly when absent.

### 202D — Eligibility and rejection rules

**Dependency:** 202A through 202C complete; CDP-002 accepted eligibility states and rejection rules.

**Files likely affected:**

- `src/construction_intelligence_mcp/services/contractor_evidence_service.py`
- `src/construction_intelligence_mcp/models/contractor_evidence.py`
- `tests/` service eligibility and rejection tests

**Task:** Implement governed service-level eligibility and rejection rules for ContractorEvidence
assembly. The service applies business rules to adapter records and returns canonical evidence plus
diagnostics.

**Rules to define from accepted CDP-002:**

- **Duplicates:** reject duplicate evidence identities or duplicate identity/linkage combinations as
  defined by CDP-002; count them in diagnostics.
- **Unresolved identities:** reject rows missing required contractor identity or accepted identity
  resolution; preserve limitations only when CDP-002 permits contextual use.
- **Unranked bidders:** include, reject, or mark with limitations according to CDP-002 eligibility.
- **Preference-ineligible bidders:** reject or mark ineligible according to accepted preference rules;
  never treat preference-ineligible bids as comparable eligible bids unless CDP-002 explicitly allows
  it.
- **Missing bid amounts:** reject when bid amount is required for the evidence type; otherwise retain
  only with explicit limitation.
- **Conflicting contractor names:** reject ambiguous identity evidence unless CDP-002 defines a
  certified resolution; expose conflicts in diagnostics or limitations.
- **Quarantined rows:** always reject unless CDP-002 explicitly certifies a quarantine-reviewed state
  as eligible; do not consume quarantine relations.
- **Incomplete lineage:** reject rows missing required lineage; retain optional lineage gaps only when
  accepted and surfaced as limitations.

**Non-goals:**

- Do not infer identity resolution beyond CDP-002.
- Do not compare or score contractors.
- Do not create opportunity recommendations, bid strategy, or market intelligence.
- Do not silently downgrade rejected rows into eligible evidence.

**Acceptance criteria:**

- Eligibility and rejection behavior exactly matches accepted CDP-002.
- Every rejected category listed above is covered by deterministic logic and diagnostics.
- Eligible evidence preserves limitations and lineage.
- Unknown eligibility, bid status, participation role, relationship type, or evidence type fails or
  is rejected according to the accepted contract.
- Results are deterministic and bounded when a limit is supplied.

**Failure behavior:**

- Unknown states are rejected and surfaced in diagnostics unless CDP-002 defines a governed failure.
- Duplicate, ambiguous, quarantined, and incomplete-lineage rows do not appear as eligible evidence.
- If all rows are rejected and CDP-002 requires nonzero eligible coverage, fail clearly; otherwise
  return an empty result with diagnostics.

**Test requirements:**

- Unit tests for duplicate rows, unresolved identities, unranked bidders, preference-ineligible
  bidders, missing bid amounts, conflicting contractor names, quarantined rows, incomplete lineage,
  unknown states, deterministic ordering, and limit behavior.
- Tests validate both eligible output and rejected diagnostics.
- Tests do not require production DuckDB.

### 202E — Diagnostics

**Dependency:** 202A through 202D complete; CDP-002 accepted diagnostic requirements.

**Files likely affected:**

- `src/construction_intelligence_mcp/models/contractor_evidence.py`
- `src/construction_intelligence_mcp/services/contractor_evidence_service.py`
- `tests/` diagnostics tests
- CLI or smoke-test files only if existing service diagnostics patterns require them

**Task:** Implement governed diagnostics for the Contractor Evidence Engine so certification review
can inspect selected inputs, coverage, rejection behavior, and final evidence population.

**Required diagnostic concepts:**

- selected relation;
- eligible rows;
- rejected rows;
- duplicate rows;
- identity coverage;
- lineage coverage;
- bid-rank coverage;
- bid-amount coverage;
- relationship coverage;
- final evidence count.

Diagnostics may include additional CDP-002-defined distributions such as eligibility status,
evidence type, participation role, bid status, district, project type, relationship type, or
rejection reason when accepted by the contract.

**Non-goals:**

- Do not expose private processing internals beyond lineage and diagnostics required for audit.
- Do not hide rejected rows behind only a final count when CDP-002 requires reason-level review.
- Do not report invented coverage for concepts not present in CDP-002.

**Acceptance criteria:**

- Diagnostics report selected relation, eligible rows, rejected rows, duplicate rows, identity
  coverage, lineage coverage, bid-rank coverage, bid-amount coverage, relationship coverage, and
  final evidence count.
- Coverage denominators are documented and deterministic.
- Rejection counts reconcile to input row counts.
- Diagnostics distinguish ineligible, duplicate, incomplete, ambiguous, and unknown-state rows when
  CDP-002 requires that distinction.
- Diagnostics are returned with every service result and exposed in certification tests.

**Failure behavior:**

- Diagnostics construction must not mask evidence assembly failures.
- If required diagnostic concepts cannot be computed from accepted CDP-002, implementation must fail
  clearly or document the accepted limitation; it must not fabricate values.

**Test requirements:**

- Unit tests for all required diagnostic counts and coverage ratios.
- Tests verify count reconciliation and zero-row behavior.
- Tests verify unknown/rejected status reporting.
- Integration diagnostics tests may use `CI_DATABASE` when available and skip clearly otherwise.

### 202F — Unit and integration certification

**Dependency:** 202A through 202E complete; CDP-002 accepted; implementation ready for review.

**Files likely affected:**

- `tests/test_contractor_evidence_model.py` or equivalent
- `tests/test_contractor_evidence_adapter.py` or equivalent
- `tests/test_contractor_evidence_service.py` or equivalent
- `tests/test_contractor_evidence_integration.py` or equivalent
- `pyproject.toml` only if existing test markers require update
- CI or smoke-test files only if already used for Program 100 certification

**Task:** Define and implement certification tests and review gates proving the Contractor Evidence
Engine is a governed, read-only, lineage-preserving consumer of accepted CDP-002.

**Certification requirements:**

- Unit tests use temporary fixtures and do not require production DuckDB.
- Integration tests use `CI_DATABASE` only when configured and skip clearly when unavailable.
- Tests never mutate the source DuckDB.
- Tests cover successful evidence assembly, required lineage, eligibility, limitations, rejection
  categories, deterministic ordering, diagnostics, and governed empty-result behavior.
- Actual certified data product integration demonstrates nonzero eligible ContractorEvidence when
  CDP-002 requires nonzero certified coverage.
- Ruff and the full pytest suite pass.

**Non-goals:**

- Do not certify CDP-002 itself; Initiative 201 owns CDP acceptance.
- Do not test private processing pipeline internals.
- Do not require production data for unit tests.
- Do not add broad unrelated cleanup to certification changes.

**Acceptance criteria:**

- Tests prove the engine consumes only the accepted mapping and rejects unaccepted mappings.
- Tests prove all 202D rejection categories.
- Tests prove all 202E diagnostics.
- Tests prove the service returns Pydantic business objects and typed collections, not database
  objects.
- Certification review accepts ContractorEvidence as sufficient input for Initiative 203.

**Failure behavior:**

- Missing `CI_DATABASE` causes integration tests to skip with a clear reason.
- Configured but unavailable `CI_DATABASE` causes integration tests to skip or fail according to the
  repository's established integration-test convention.
- Any mutation attempt, undocumented relation access, or SQL outside adapters fails review.

**Test requirements:**

- `pip install -e ".[dev]"`
- `pytest -q`
- `ruff check .`
- `git diff --check`
- Review evidence showing no production Python was created before CDP-002 acceptance during planning.

## Initiative-Level Validation

The future engine must fail clearly or surface governed limitations for:

- missing accepted CDP-002 contract;
- missing or ambiguous accepted/current schema-qualified CDP-002 mapping;
- missing physical mapped relation;
- missing required contractor business identity;
- missing required evidence identity;
- missing required lineage;
- unknown or ineligible certification, bid, participation, or relationship states;
- ambiguous contractor, contract, bid, project, prime, subcontractor, or relationship linkage;
- duplicate evidence identity;
- unsupported evidence categories;
- quarantined, staging, review, candidate, diagnostic, archive, or excluded rows;
- empty eligible evidence where CDP-002 requires nonzero certified coverage.

## Engine Review Gate

Before Initiative 202 can be marked implemented and reviewed:

- Initiative 201 must be accepted and CDP-002 must be current.
- The implementation must identify Program 200 and CDP-002 in review notes.
- Exactly one accepted/current schema-qualified CDP-002 mapping must be configured.
- No relation-name discovery may be present.
- All DuckDB and SQL access must remain inside adapters.
- Services must return canonical ContractorEvidence business objects.
- Diagnostics must reconcile input, rejected, duplicate, eligible, and final evidence counts.
- Tests and Ruff must pass.
- Integration certification must either demonstrate accepted CDP-002 evidence population or skip
  clearly when the certified database is unavailable.

## Definition of Done

Initiative 202 is implementation-ready when this planning backlog is accepted, but it remains
**BLOCKED_BY_CONTRACT until CDP-002 is accepted**.

Initiative 202 is done only after future implementation proves that:

- Initiative 201 was accepted before implementation began.
- The engine returns canonical ContractorEvidence matching accepted CDP-002.
- The engine preserves certified lineage, eligibility, and limitations.
- The engine rejects ineligible, ambiguous, duplicate, quarantined, unsupported, and incomplete
  evidence paths.
- Diagnostics report selected relation, eligible rows, rejected rows, duplicate rows, identity
  coverage, lineage coverage, bid-rank coverage, bid-amount coverage, relationship coverage, and
  final evidence count.
- Tests and checks pass.
- Review accepts ContractorEvidence as sufficient input for Initiative 203.

## Unlock Condition

203 becomes READY only when 202 is implemented, certified, and reviewed after CDP-002 acceptance.
