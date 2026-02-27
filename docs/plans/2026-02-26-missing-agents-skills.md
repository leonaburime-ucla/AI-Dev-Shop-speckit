# Missing Agents and Skills — Implementation Spec
- Date: 2026-02-26
- Status: APPROVED FOR IMPLEMENTATION
- Author: Coordinator (Review Mode)

## Context

Based on a full audit of the current pipeline and skills library. The implementing agent must
create all files listed below following existing conventions in this repo. Read at least two
existing `agents/*/skills.md` files and two existing `skills/*/SKILL.md` files before starting
to ensure correct format and tone.

Do NOT modify any file not listed in this spec. Do NOT refactor existing files beyond what
is listed under "Existing Files to Update."

---

## Updated Pipeline (target state)

```
[CodeBase Analyzer] → Spec → [Red-Team] → Architect → [Database] → TDD → Programmer → [QA/E2E] → TestRunner → Code Review → [Refactor] → Security → [DevOps] → [Docs] → Done
```

- `[Observer]` passive across all stages when enabled
- `[...]` stages are optional; dispatched by Coordinator when spec/ADR triggers them
- All new stages follow existing handoff contract format

---

## Part 1 — New Agents

Create `agents/<name>/skills.md` for each. Follow the format of existing agent skills files
exactly (Version, Last Updated, Skills, Role, Required Inputs, Workflow, Output Format,
Escalation Rules, Guardrails).

---

### 1. DevOps Agent

**Folder:** `agents/devops/`

**Pipeline position:** After Security, before Done. Also dispatched by Coordinator alongside
Architect when spec triggers the infrastructure harness (new or modified infrastructure
resources).

**Skills to list:**
- `<SHOP_ROOT>/skills/devops-delivery/SKILL.md`
- `<SHOP_ROOT>/skills/infrastructure-as-code/SKILL.md`
- `<SHOP_ROOT>/skills/change-management/SKILL.md`
- `<SHOP_ROOT>/skills/architecture-decisions/SKILL.md`

**Role:** Owns everything between "code is done" and "code is in production." Writes
Dockerfiles, CI/CD pipeline configs, IaC declarations, deployment runbooks, health check
definitions, and environment configuration. Does not write application code.

**Required Inputs:**
- `<SHOP_ROOT>/reports/pipeline/<NNN>-<feature-name>/adr.md` (deployment topology, infra constraints)
- `<SHOP_ROOT>/reports/security/SEC-<feature-id>-<YYYY-MM-DD>.md` (security findings that affect environment config)
- Active spec (for infrastructure requirements in NFRs)
- Coordinator directive with explicit scope (new infra, updated CI, deployment runbook only, etc.)
- Existing CI/CD configs and Dockerfiles in the codebase (if any)

**Workflow:**
1. Read ADR for deployment topology — identify what infrastructure resources this feature requires
2. Read security findings — identify any environment config or secrets handling requirements
3. Assess what already exists (existing Dockerfiles, CI configs) vs what needs to be created or modified
4. Write or update Dockerfile(s) following multi-stage build patterns from `devops-delivery` skill
5. Write or update CI/CD pipeline config — include lint, test, build, security scan, deploy stages
6. Write IaC declarations for any new infrastructure resources required (do not provision — declare)
7. Write deployment runbook: pre-deploy checks, deploy steps, post-deploy verification, rollback procedure
8. Write health check definition for each new service or endpoint
9. Report to Coordinator with output summary and any blocking pre-conditions (infra that must exist before deploy)

**Output Format:**
Write to `<SHOP_ROOT>/reports/pipeline/<NNN>-<feature-name>/devops.md`.

Contents:
- Infrastructure pre-conditions (what must exist before deployment)
- Dockerfile changes or new files (with paths)
- CI/CD config changes or new files (with paths)
- IaC declarations (with paths)
- Deployment runbook (ordered steps, rollback procedure)
- Health check endpoints and expected responses
- Environment variables required (names only — never values)

**Escalation Rules:**
- Infrastructure resource that cannot be declared without production access → escalate to human
- Deployment topology conflicts with ADR decisions → route back to Architect
- Security finding requires environment-level mitigation (firewall rule, WAF config) → escalate to human

**Guardrails:**
- Never provision infrastructure directly — declare and document only
- Never write secrets or credential values into any file
- Never modify application source code
- Environment variable names are permitted in configs; values are never permitted

---

### 2. QA/E2E Agent

**Folder:** `agents/qa-e2e/`

**Pipeline position:** After Programmer, before TestRunner. Dispatched by Coordinator when
the spec includes user-journey acceptance criteria or frontend interactions.

**Skills to list:**
- `<SHOP_ROOT>/skills/e2e-test-architecture/SKILL.md`
- `<SHOP_ROOT>/skills/test-design/SKILL.md`
- `<SHOP_ROOT>/skills/security-review/SKILL.md` (for auth flow E2E coverage)

**Role:** Owns the E2E test layer. Writes browser-level tests (Playwright) that validate
acceptance criteria from the user's perspective. Defines fixture strategy, test data policy,
and flaky test prevention rules. Does not replace TDD unit/integration tests — sits above them.

**Required Inputs:**
- Active spec (full content + hash) — user journeys and frontend ACs
- `<SHOP_ROOT>/reports/pipeline/<NNN>-<feature-name>/adr.md` (module boundaries, auth patterns)
- `<SHOP_ROOT>/reports/pipeline/<NNN>-<feature-name>/test-certification.md` (TDD coverage map — to avoid duplicating what unit/integration tests already cover)
- Coordinator directive specifying which ACs require E2E coverage

**Workflow:**
1. Read spec ACs and identify which require browser-level or user-journey validation
2. Read test certification to understand existing coverage — E2E tests cover journeys, not logic already covered at unit/integration level
3. Define fixture strategy: what test data is needed, how it is seeded and cleaned up
4. Write E2E tests using Playwright following patterns in `e2e-test-architecture` skill
5. Apply anti-flake rules from the skill — no hard waits, proper selectors, isolated contexts
6. Tag each test with the AC it covers
7. Verify tests pass against the current implementation. If a test fails, determine whether the cause is a spec gap, a bug in the implementation, or a test error — report each accordingly
8. Write E2E strategy document summarizing coverage, fixture approach, and flaky test policy for this feature
9. Report to Coordinator with test count per AC and any ACs that cannot be E2E tested (with reason)

**Output Format:**
- E2E test files in the project's test directory (path confirmed with Coordinator before writing)
- `<SHOP_ROOT>/reports/pipeline/<NNN>-<feature-name>/e2e-strategy.md` containing:
  - AC coverage map (which ACs have E2E tests, which do not and why)
  - Fixture strategy and setup/teardown approach
  - Flaky test risk assessment for each test
  - CI integration requirements (browser install, environment vars needed)

**Escalation Rules:**
- AC that is untestable at E2E level (third-party auth, hardware dependency) → document as untestable with reason, do not skip silently
- Test environment does not support browser automation → escalate to human
- E2E tests reveal spec ambiguity not caught by TDD → route to Spec Agent

**Guardrails:**
- Never write E2E tests that duplicate logic already covered by unit or integration tests
- Never use hard waits (`waitForTimeout`) — use `waitForSelector`, `waitForResponse`, or role-based locators
- Never use brittle CSS class selectors — use ARIA roles, labels, and test IDs
- Never modify application source code
- Test data must use synthetic PII patterns from `data-classification.md`

---

### 3. Docs Agent

**Folder:** `agents/docs/`

**Pipeline position:** After DevOps (or after Security if DevOps is skipped), before Done.
Dispatched by Coordinator on every pipeline completion unless Coordinator explicitly marks
documentation as N/A (internal tooling only).

**Skills to list:**
- `<SHOP_ROOT>/skills/api-contracts/SKILL.md` (for OpenAPI generation)
- `<SHOP_ROOT>/skills/spec-writing/SKILL.md` (for structured, precise writing)

**Role:** Owns user-facing documentation output for the feature. Generates OpenAPI specs
from `api.spec.md`, writes user guides, maintains `CHANGELOG.md`, and produces release
notes from the ADR and spec. Does not write implementation code or specs.

**Required Inputs:**
- Active spec (full content) — `feature.spec.md`, `api.spec.md`
- `<SHOP_ROOT>/reports/pipeline/<NNN>-<feature-name>/adr.md` (architectural decisions worth surfacing in release notes)
- `<SHOP_ROOT>/reports/security/SEC-<feature-id>-<YYYY-MM-DD>.md` (security findings that affect user-facing behavior, e.g. new auth requirements)
- Existing `CHANGELOG.md` (to append correctly)
- Coordinator directive specifying doc deliverables required for this feature

**Workflow:**
1. Read api.spec.md — generate or update OpenAPI 3.x YAML spec from the endpoint definitions
2. Read feature.spec.md — identify user-facing behavior changes worth documenting
3. Read ADR — extract any architectural decisions that affect how users or integrators interact with the system
4. Write or update user guide section for the feature
5. Append CHANGELOG.md entry following Keep a Changelog format (Added/Changed/Deprecated/Removed/Fixed/Security)
6. Write release notes summary (one paragraph, non-technical audience)
7. Report to Coordinator with list of files created or modified

**Output Format:**
- `openapi.yaml` or appended section in existing OpenAPI file (path confirmed with Coordinator)
- Updated `CHANGELOG.md` with new entry at top of Unreleased section
- `<SHOP_ROOT>/reports/pipeline/<NNN>-<feature-name>/release-notes.md` (one paragraph release notes + full change summary)
- User guide file(s) (path confirmed with Coordinator based on project's doc structure)

**Escalation Rules:**
- API behavior in implementation differs from api.spec.md → do not document the implementation, route to Spec Agent
- Release notes require business context not in the spec → escalate to human for input
- Breaking API change not flagged in spec → flag to Coordinator before documenting

**Guardrails:**
- Document what the spec says, not what the implementation does — if they differ, flag it
- Never include internal system details (ADR trade-offs, implementation decisions) in user-facing docs
- Never include secrets, PII, or SENSITIVE-BUSINESS data in any doc output
- CHANGELOG entries must follow Keep a Changelog format exactly

---

## Part 2 — New Skills

Create `skills/<name>/SKILL.md` for each. Follow format of existing skill files exactly.
Read at least `skills/security-review/SKILL.md` and `skills/test-design/SKILL.md` for
reference format before writing.

---

### 1. observability-implementation

**Folder:** `skills/observability-implementation/`

**Consumed by:** Architect (design phase), Programmer (implementation), Security Agent
(log data exposure review)

**Purpose:** Provides implementation-level guidance for meeting Constitution Article VIII
(Observability). Currently the constitution requires structured signals on all production
paths but no skill exists to guide how to implement them.

**Contents to include:**

**Structured Logging:**
- Log levels and when to use each (DEBUG, INFO, WARN, ERROR, FATAL)
- Structured log format: always JSON in production, include `timestamp`, `level`, `service`, `trace_id`, `span_id`, `message`, `context` fields
- What to log at each application layer (HTTP handler, service, repository)
- What never to log: secrets, PII, full request bodies containing sensitive fields — reference `data-classification.md`
- Correlation ID propagation: inject at edge, forward through all downstream calls

**Metrics:**
- Counter, gauge, histogram — when to use each
- Standard metrics every service must emit: request count, error rate, latency histogram (p50/p95/p99), saturation (queue depth, connection pool usage)
- OpenTelemetry SDK setup pattern (language-agnostic: describe the concept, link to SDK docs)
- Prometheus exposition format when applicable

**Distributed Tracing:**
- Span creation: when to create a new span (service boundary, external call, significant internal operation)
- Span attributes: required (service name, operation name, span kind) and recommended (user ID hash — not raw, feature flag values, resource identifiers)
- Context propagation across HTTP and message queue boundaries (W3C TraceContext headers)
- Sampling strategy guidance: always-on for errors, probabilistic for success paths

**Alerting Design (for Architect to specify in ADR):**
- Alert on symptoms (high error rate, high latency) not causes (CPU usage, memory)
- Alert thresholds must be defined in the spec as NFRs — not added post-launch
- Every alert must have a runbook reference

**Implementation Checklist for Programmer Agent:**
- [ ] Correlation ID injected at first entry point and propagated to all outbound calls
- [ ] All external I/O instrumented (HTTP calls, DB queries, queue publishes/consumes)
- [ ] Error paths produce structured log entry with error type, message, and stack trace
- [ ] Request latency histogram emitted per endpoint
- [ ] Health check endpoint returns 200 with service metadata (version, uptime)
- [ ] No secrets or raw PII in any log output

---

### 2. devops-delivery

**Folder:** `skills/devops-delivery/`

**Consumed by:** DevOps Agent

**Purpose:** CI/CD pipeline patterns, Docker build standards, deployment strategies, and
environment management for the pipeline's delivery output.

**Contents to include:**

**Dockerfile Standards:**
- Multi-stage builds: separate build stage from runtime stage
- Non-root user in runtime stage
- No secrets in Dockerfile — use build args for build-time values, environment variables for runtime
- Layer caching strategy: copy dependency manifests before source code
- Health check instruction in Dockerfile

**CI/CD Pipeline Stages (GitHub Actions reference pattern):**
- lint and type-check (fast, blocks everything)
- unit and integration tests (parallel where possible)
- build and push image (only on success)
- security scan (image scan + SAST — reference `security-review` skill for what to scan)
- deploy to staging (automatic on main merge)
- smoke test against staging
- deploy to production (manual approval gate or automated with rollback trigger)

**Deployment Strategies:**
- Rolling: replace instances one at a time; zero downtime but mixed versions briefly active
- Blue/Green: run two identical environments, switch traffic; instant rollback, higher infra cost
- Canary: route small % of traffic to new version; catch issues before full rollout; requires feature flag or load balancer support
- Choose based on: criticality of service, rollback speed requirement, infra cost tolerance

**Environment Management:**
- Promote artifacts (not source) through environments: dev → staging → production
- Environment-specific config via environment variables — never baked into the image
- Secrets via secrets manager — never in environment variable plaintext in CI config

**Health Checks and Readiness:**
- Liveness probe: is the process alive? (simple HTTP 200)
- Readiness probe: is the service ready to receive traffic? (checks DB connection, downstream dependencies)
- Never route traffic before readiness probe passes

**Rollback Procedure Template:**
- Define rollback trigger (error rate threshold, latency threshold)
- Previous image tag must be available and pinned
- Database migrations must be backward-compatible with previous version (never drop columns in same release as stop-writing)

---

### 3. performance-engineering

**Folder:** `skills/performance-engineering/`

**Consumed by:** TestRunner Agent (when performance harness active), Architect (design
constraints), enterprise-spec shift-left harness

**Purpose:** Standardizes performance validation in the standard pipeline. Extracts and
generalizes the performance harness from `enterprise-spec/SKILL.md` Section 5 so it is
available to all projects, not just enterprise-classified ones.

Note to implementing agent: The enterprise-spec performance harness (Section 5) remains
unchanged. This skill provides the how-to guidance that the harness references.

**Contents to include:**

**When Performance Validation is Required:**
- Any spec with a latency NFR (p50/p95/p99 target)
- Any spec with a throughput NFR (requests per second, concurrent users)
- Any spec with an availability SLA
- When none of the above: performance validation is optional (document as N/A in pipeline state)

**Load Testing Tools:**
- k6: JavaScript-based, CI-friendly, good for HTTP APIs — preferred default
- autocannon: Node.js, minimal setup, good for quick HTTP benchmarks
- Artillery: YAML-driven, good for complex scenarios
- Never use unit test timing assertions as performance tests — they do not simulate real load

**Test Scenario Design:**
- Warm-up phase: ramp from 0 to target load over 30 seconds (avoids cold-start skew)
- Sustained load phase: hold target load for 60+ seconds
- Measure: p50, p95, p99 latency; error rate; throughput (req/s)
- Simulate realistic payloads — not empty requests

**Pass/Fail Criteria:**
- p99 latency must meet spec NFR target
- Error rate during load test must be < 0.1% (unless spec specifies otherwise)
- A result 0-10% over p99 target: warning (Engineering Lead acknowledgment required before merge)
- A result >10% over p99 target: hard failure (blocks merge)

**Result Artifacts:**
- Load test results must be captured as CI artifacts and attached to the PR
- Results must include: tool used, scenario description, VU count, duration, p50/p95/p99 values, error rate, pass/fail verdict

**Common Performance Failure Modes:**
- N+1 query: one query per row instead of one query total — fix with eager loading or batching
- Missing database index: full table scan on filtered query — fix with index on filter column(s)
- Synchronous blocking I/O in hot path: network call or disk read blocking the event loop
- Cold-start latency: first request penalty — warm up before measuring

---

### 4. api-contracts

**Folder:** `skills/api-contracts/`

**Consumed by:** Spec Agent (when validating api.spec.md), Code Review Agent (backward compatibility check), Docs Agent (when generating OpenAPI)

**Purpose:** Governs API contract design, completeness, versioning, and backward
compatibility. Covers what the existing api-patterns.md design reference does not: contract
validation, versioning enforcement, and consumer-driven testing.

**Contents to include:**

**What a Complete API Contract Requires (per endpoint):**
- HTTP method and path
- Path parameters, query parameters, request headers (name, type, required/optional, constraints)
- Request body schema (all fields, types, required/optional, validation rules, examples)
- Response schemas for each status code: 200/201, 400, 401, 403, 404, 409, 422, 429, 500 minimum
- Auth requirement (none / API key / Bearer JWT / session)
- Rate limit (requests per window, per what scope: IP / user / API key)
- Idempotency behavior (is POST idempotent? Is it safe to retry? What is the idempotency key?)

**OpenAPI 3.x Generation Rules:**
- Every endpoint in api.spec.md maps to one OpenAPI path + operation object
- Request/response schemas use JSON Schema — no `$ref` to undefined schemas
- Examples are required for all request and response bodies
- `operationId` must be unique, snake_case, verb-first (e.g. `create_invoice`, `list_invoices`)

**Versioning Strategy:**
- URL versioning (`/v1/`, `/v2/`) — simple, cache-friendly, explicit
- Header versioning (`Accept: application/vnd.api+json;version=2`) — cleaner URLs, harder to test in browser
- Choose one strategy at project start and apply consistently
- Never change versioning strategy mid-project

**Breaking vs Non-Breaking Changes:**
Non-breaking (additive — no version bump required):
- New optional request field
- New response field
- New endpoint
- New optional query parameter
- New status code on an existing endpoint

Breaking (requires version bump and migration plan):
- Removing or renaming a field (request or response)
- Changing a field type
- Making an optional field required
- Removing an endpoint
- Changing auth requirement
- Changing error response structure

**Consumer-Driven Contract Testing (Pact):**
- Consumer defines expectations (request shape + response shape it needs)
- Provider verifies it can satisfy those expectations
- Pact broker stores contracts between teams
- Use when: multiple teams consume your API, or you have a public API with versioned consumers

---

### 5. frontend-accessibility

**Folder:** `skills/frontend-accessibility/`

**Consumed by:** Code Review Agent (when reviewing frontend code), QA/E2E Agent (for a11y
test coverage)

**Purpose:** WCAG 2.1 AA compliance guidance for frontend code review and E2E testing.
Currently entirely absent from the pipeline despite Article VIII (Observability) touching
the user-facing layer.

**Contents to include:**

**WCAG 2.1 AA — What to Check in Code Review:**

Perceivable:
- All non-text content has a text alternative (`alt` on images, `aria-label` or `aria-labelledby` on icon buttons)
- Color is not the only means of conveying information (error state must also have text or icon, not just red color)
- Minimum contrast ratio: 4.5:1 for normal text, 3:1 for large text and UI components
- No content flashes more than 3 times per second

Operable:
- All functionality accessible via keyboard (Tab, Shift+Tab, Enter, Space, Arrow keys)
- Visible focus indicator on all interactive elements — never `outline: none` without a replacement
- Skip navigation link for pages with repeated navigation
- No keyboard traps — user can always Tab out of a component

Understandable:
- Form inputs have associated `<label>` elements (not just placeholder text)
- Error messages identify the field and describe the error — not just "invalid input"
- Language attribute on `<html>` element

Robust:
- Semantic HTML — use `<button>` for buttons, `<a>` for links, heading hierarchy (`<h1>` → `<h2>` → `<h3>`)
- ARIA roles only when native HTML semantics are insufficient
- ARIA attributes used correctly — do not add `aria-label` to elements that already have visible text

**Common Violations to Flag in Code Review:**
- `<div onClick>` instead of `<button>` — not keyboard accessible, no ARIA role
- `<img>` without `alt` attribute
- `<input>` without associated `<label>` (placeholder is not a label)
- Interactive element with no visible focus state
- Hardcoded color values with insufficient contrast
- Error state communicated only via color change

**E2E Testing for Accessibility (axe-core integration):**
- Inject `@axe-core/playwright` in E2E tests
- Run `checkA11y()` after each page navigation and after dynamic content loads
- Configure to WCAG 2.1 AA ruleset
- Treat Critical and Serious violations as test failures
- Moderate violations are warnings — log but do not fail

**Keyboard Navigation Test Checklist:**
- [ ] Can reach all interactive elements via Tab
- [ ] Can activate buttons with Enter and Space
- [ ] Can navigate dropdowns/menus with Arrow keys
- [ ] Modals trap focus correctly (Tab stays inside modal while open)
- [ ] Focus returns to trigger element when modal closes
- [ ] Skip link present and functional on pages with navigation

---

### 6. e2e-test-architecture

**Folder:** `skills/e2e-test-architecture/`

**Consumed by:** QA/E2E Agent, TDD Agent (when spec ACs require user-journey coverage)

**Purpose:** Stable E2E test patterns using Playwright. Anti-flake rules, fixture strategy,
selector discipline, and CI integration.

**Contents to include:**

**When to Write E2E Tests vs Unit/Integration Tests:**
- E2E tests: user journeys, multi-step workflows, full auth flows, critical happy paths
- Integration tests (TDD layer): service boundaries, API contracts, database interactions
- Unit tests (TDD layer): pure logic, transformations, validators
- Rule: E2E tests are expensive to run and maintain — write them for journeys, not for logic

**Playwright Patterns:**

Page Object Model:
- One class per page or major UI component
- Class exposes user actions (methods), not DOM selectors
- Example: `invoicePage.fillLineItem({ description, quantity, price })` not `page.fill('#desc', 'x')`
- Selectors live only in the page object — never in the test body

Selector Hierarchy (most to least preferred):
1. ARIA role + accessible name: `getByRole('button', { name: 'Save Invoice' })`
2. Label: `getByLabel('Invoice Number')`
3. Test ID: `getByTestId('invoice-submit')` (requires `data-testid` attribute in component)
4. Text: `getByText('Submit')` (fragile for i18n — use sparingly)
5. CSS class or XPath: never use in E2E tests

**Anti-Flake Rules:**
- Never use `waitForTimeout` or `page.waitForTimeout` — always wait for a specific condition
- Use `waitForResponse` when an action triggers an API call
- Use `waitForSelector` or role-based locator assertions when waiting for UI state
- Use `page.waitForLoadState('networkidle')` only when truly needed — prefer explicit waits
- Isolate test data: each test creates its own fixtures and cleans up after itself
- Never share mutable state between tests
- Tests must pass in any order and in parallel

**Fixture Strategy:**
- Seed fixtures via API calls (not by manipulating DB directly) — this tests the API too
- Clean up fixtures in `afterEach` — do not rely on test order for cleanup
- Use factory functions for fixture creation — makes test setup readable
- Synthetic data only — follow `data-classification.md` PII patterns

**Auth in E2E Tests:**
- Never re-test the auth flow in every test — log in once via API and store session state
- Playwright `storageState` for session persistence across tests in a file
- One auth fixture per role (admin, regular user, guest) — reused across all tests needing that role

**CI Integration:**
- E2E tests run in headless mode on CI
- Browser must be installed in CI image (`npx playwright install --with-deps`)
- Parallel workers: use `--workers=4` or match CI machine core count
- Retry on failure: `--retries=1` in CI only (never locally — masks flaky tests)
- Test artifacts: screenshots and traces on failure (`--trace=on-first-retry`)

---

### 7. rag-ai-integration

**Folder:** `skills/rag-ai-integration/`

**Consumed by:** Architect (when spec involves AI/LLM features), Programmer (implementation
guidance), Database Agent (vector DB schema design)

**Purpose:** Guidance for building RAG pipelines and LLM integration layers. The pipeline
targets an AI dev shop audience but currently has no skill for building AI features.

**Contents to include:**

**RAG Architecture Components:**
- Document ingestion pipeline: source → chunk → embed → store
- Retrieval pipeline: query → embed query → similarity search → rerank → context assembly
- Generation: assembled context + query → LLM → response

**Chunking Strategies:**
- Fixed-size: simple, predictable, loses semantic boundaries — use only as baseline
- Sentence/paragraph-aware: respects natural language boundaries — preferred for prose
- Semantic: split on topic shifts — best quality, highest compute cost
- Chunk size guidance: 256–512 tokens for factual retrieval, 512–1024 for narrative content
- Overlap: 10–20% overlap between chunks to avoid cutting context at boundaries
- Always store chunk metadata: source document ID, page/section, character offset

**Vector Database Selection:**
- pgvector (Postgres extension): suitable for < 1M vectors, existing Postgres infrastructure
- Pinecone / Weaviate / Qdrant: suitable for > 1M vectors or when dedicated vector ops needed
- Supabase: includes pgvector support — use when project already uses Supabase (see `supabase` skill)
- Index type: HNSW preferred over IVFFlat for most use cases (better recall, slower build)

**Embedding Models:**
- Use the same model for ingestion and retrieval — never mix models
- Dimension size tradeoff: larger = better quality, higher cost and storage
- Common choices: OpenAI `text-embedding-3-small` (1536d, cost-effective), `text-embedding-3-large` (3072d, higher quality)
- Store the model name and version alongside embeddings — model changes require re-embedding

**Retrieval Quality:**
- Similarity threshold: filter results below cosine similarity 0.7 — do not pass low-quality context to LLM
- Hybrid search: combine vector similarity with keyword search (BM25) for better recall on specific terms
- Reranking: use cross-encoder reranker on top-k results before passing to LLM (improves precision)
- Retrieved context window: stay within LLM context limit — prioritize highest-scoring chunks

**LLM Integration Patterns:**
- System prompt: define role, output format, and constraints — keep stable across requests
- User prompt: query + assembled context — clearly delimit context from query
- Never inject unvalidated user input directly into system prompt (prompt injection risk — reference `security-review` skill)
- Temperature: 0 for factual retrieval tasks, 0.3-0.7 for generative tasks
- Max tokens: always set — never allow unbounded generation

**Evaluation:**
- Retrieval quality: precision@k (are retrieved chunks relevant?), recall@k (are all relevant chunks retrieved?)
- Generation quality: faithfulness (does response contradict retrieved context?), answer relevance
- Use LLM-as-judge for automated evaluation — reference `skills/evaluation/eval-rubrics.md`
- Establish baseline before tuning — cannot improve what you do not measure

**Cost Management:**
- Cache embedding results — same text should not be re-embedded
- Cache LLM responses for identical query+context pairs (TTL based on content change frequency)
- Log token usage per request — set budget alerts

---

### 8. change-management

**Folder:** `skills/change-management/`

**Consumed by:** Programmer Agent (migration mode), DevOps Agent, Architect (when spec involves breaking changes to data model or API)

**Purpose:** Safe patterns for shipping breaking changes: feature flags, dual writes,
backfills, and cutover gates.

**Contents to include:**

**The Expand-Contract Pattern (preferred for breaking changes):**
Phase 1 — Expand: add new capability alongside old (new column, new endpoint, new behavior behind flag). Old and new code both work.
Phase 2 — Migrate: move traffic/data to new capability. Monitor.
Phase 3 — Contract: remove old capability once migration is complete and verified.
Rule: never skip phases. Combining expand + contract in one deployment is a breaking change.

**Feature Flags:**
- Use for: rolling out new behavior incrementally, enabling rollback without redeployment, A/B testing
- Flag types: boolean (on/off), percentage rollout (0-100%), user segment (specific user IDs or groups)
- Naming: `<feature>_<description>_enabled` — e.g. `invoice_v2_line_items_enabled`
- Default value: false for new features (off by default), true for kill switches (enabled by default)
- Flag lifecycle: create → enable for internal → canary → full rollout → remove flag from code
- Never leave flags in code permanently — schedule removal after full rollout

**Dual-Write Pattern:**
- When: migrating data from one storage location or shape to another
- Write to both old and new path simultaneously during migration window
- Read from old path until new path is verified complete and consistent
- Switch reads to new path only after backfill is complete and verified
- Stop writing to old path only after reads have moved and been stable

**Backfill Design:**
- Backfill jobs must be idempotent — safe to run multiple times
- Process in batches (1000-10000 rows per batch) with sleep between batches to avoid lock contention
- Record progress (last processed ID or timestamp) — resumable if interrupted
- Verify row count before and after: `SELECT COUNT(*) WHERE new_field IS NULL` should reach 0
- Run backfill on non-peak hours for large datasets

**Cutover Gates:**
Observable conditions that must be true before proceeding to the next phase. Each gate must be:
- Measurable (a metric, a count, a test result — not "looks good")
- Automated where possible (CI check, monitoring alert threshold)
- Time-bounded (wait no more than X hours before escalating)

Example gates:
- Error rate on new path < 0.1% for 30 minutes
- Backfill complete: `SELECT COUNT(*) WHERE new_field IS NULL = 0`
- All E2E tests passing against new path
- p99 latency on new path ≤ spec NFR target

**Rollback Triggers and Procedures:**
- Define rollback trigger before deployment (not after something breaks)
- Rollback trigger examples: error rate > 1%, p99 latency > 2x target, data inconsistency detected
- Rollback procedure must be documented, tested, and executable by any on-call engineer
- Database schema changes: never destructive in the deploy that introduces new behavior (separate deploy)

---

### 9. infrastructure-as-code

**Folder:** `skills/infrastructure-as-code/`

**Consumed by:** DevOps Agent, Architect (when ADR involves infrastructure topology)

**Purpose:** IaC declaration patterns for infrastructure required by pipeline-delivered
features. Covers what to declare, how to structure it, and what never to do.

**Contents to include:**

**What IaC Covers:**
- Compute (servers, containers, serverless functions)
- Storage (databases, object storage, queues, caches)
- Networking (load balancers, DNS, firewall rules, VPCs)
- IAM (roles, policies, service accounts)
- Secrets (references to secrets manager entries — never values)

**Tool Selection Guidance:**
- Terraform: most widely used, large provider ecosystem, HCL syntax, state management required
- Pulumi: same as Terraform but in real programming languages (TypeScript, Python) — preferred when team is already in those languages
- AWS CDK: TypeScript/Python, AWS-only, good for AWS-native teams
- Platform-native (Vercel, Railway, Render): use platform's config files for simple deployments — do not over-engineer

**Structure Conventions:**
- Separate modules by concern: `networking/`, `compute/`, `storage/`, `iam/`
- Environments via workspaces or variable files — not separate module trees
- State backend: remote state (S3 + DynamoDB lock for Terraform) — never local state in a team context
- Pin provider versions: `~> 4.0` not `>= 4.0` — prevents unexpected major version upgrades

**What to Declare vs What to Assume:**
- Declare: any resource the feature requires that does not already exist
- Assume: shared infrastructure (VPC, base networking) — reference by output/data source, do not recreate
- Never declare production databases in feature branch IaC — database schema changes go through Database Agent + migration pipeline

**Secrets in IaC:**
- Never store secret values in IaC code or state
- Reference secrets manager entries by path/ARN only
- IAM policy grants the service role access to the specific secret path
- Example: `aws_secretsmanager_secret_version` data source — read at runtime, not at plan time

**Drift Detection:**
- IaC drift = infrastructure state differs from declared state
- CI should run `terraform plan` (or equivalent) on every PR touching IaC files
- A plan with unexpected changes blocks merge — investigate before applying

---

## Part 3 — Existing Files to Update

Make targeted additions only. Do not restructure or rewrite existing content.

---

### agents/testrunner/skills.md
Add to Skills section:
```
- `<SHOP_ROOT>/skills/performance-engineering/SKILL.md` — load test execution and pass/fail criteria (activated when performance harness constraints exist in tasks.md)
- `<SHOP_ROOT>/skills/e2e-test-architecture/SKILL.md` — E2E test execution reference
```

Add to Workflow, after existing step 2 (test execution):
```
2a. If `tasks.md` contains a `## Constraints — Performance` section: execute load tests per the benchmark targets using the tool specified in the constraints. Capture results as artifacts. Apply pass/fail criteria from `<SHOP_ROOT>/skills/performance-engineering/SKILL.md`. A hard failure blocks the same as a failing test.
```

---

### agents/code-review/skills.md
Add to Skills section:
```
- `<SHOP_ROOT>/skills/frontend-accessibility/SKILL.md` — WCAG 2.1 AA checklist (activated when diff includes frontend components)
- `<SHOP_ROOT>/skills/api-contracts/SKILL.md` — backward compatibility and contract validation
```

Add to Workflow, after existing security surface step:
```
X. If diff includes frontend components: review against `<SHOP_ROOT>/skills/frontend-accessibility/SKILL.md` WCAG 2.1 AA checklist. Flag violations as Required (Critical/Serious axe-core severity) or Recommended (Moderate severity).
Y. If diff includes API changes: run OpenAPI backward compatibility diff and consumer-driven contract checks (if applicable).
```

---

### agents/architect/skills.md
Add to Skills section:
```
- `<SHOP_ROOT>/skills/observability-implementation/SKILL.md` — instrumentation design (Constitution Article VIII)
- `<SHOP_ROOT>/skills/performance-engineering/SKILL.md` — when spec has latency/throughput NFRs
- `<SHOP_ROOT>/skills/change-management/SKILL.md` — when spec involves breaking changes to API or data model
- `<SHOP_ROOT>/skills/rag-ai-integration/SKILL.md` — when spec involves LLM or vector search features
```

---

### agents/programmer/skills.md
Add to Skills section:
```
- `<SHOP_ROOT>/skills/observability-implementation/SKILL.md` — instrumentation implementation (Constitution Article VIII compliance)
- `<SHOP_ROOT>/skills/change-management/SKILL.md` — execute phase-by-phase rollouts (feature flags, dual writes) during migrations
- `<SHOP_ROOT>/skills/architecture-migration/SKILL.md` — execute safe phased migrations
```

Add to Workflow, before Step 1:
```
0. If dispatched with a `MIGRATION-*.md` context: read the authorized phase, implement scaffolding, dual-write logic, and backfill scripts as needed.
```

Add to Guardrails:
```
- Every new code path that performs external I/O (HTTP call, DB query, queue operation) must include observability instrumentation per `<SHOP_ROOT>/skills/observability-implementation/SKILL.md` — this is a Constitution Article VIII requirement, not optional
```

---

### agents/spec/skills.md
Add to Skills section:
```
- `<SHOP_ROOT>/skills/api-contracts/SKILL.md` — for validating api.spec.md completeness per the contract checklist
```

Add to Workflow, after existing DoD checklist step:
```
X. Validate `api.spec.md` contract completeness. Ensure every endpoint maps perfectly to OpenAPI 3.x generation rules.
```

---

### project-knowledge/skills-registry.md
Add rows for all new skills:
```
| `skills/observability-implementation/SKILL.md` | Architect, Programmer, Security Agent |
| `skills/devops-delivery/SKILL.md` | DevOps Agent |
| `skills/performance-engineering/SKILL.md` | TestRunner Agent, Architect |
| `skills/api-contracts/SKILL.md` | Spec Agent, Code Review Agent, Docs Agent |
| `skills/frontend-accessibility/SKILL.md` | Code Review Agent, QA/E2E Agent |
| `skills/e2e-test-architecture/SKILL.md` | QA/E2E Agent, TDD Agent |
| `skills/rag-ai-integration/SKILL.md` | Architect, Programmer, Database Agent |
| `skills/change-management/SKILL.md` | Programmer, DevOps Agent, Architect |
| `skills/infrastructure-as-code/SKILL.md` | DevOps Agent, Architect |
```

---

### AGENTS.md
1. Update the pipeline diagram to the target state shown at the top of this document
2. Add the 3 new agents (DevOps, QA/E2E, Docs) to the agents table with a one-line description each

---

### workflows/multi-agent-pipeline.md
1. Update both pipeline diagrams (Full Path and Ideal Path) to match the target pipeline
2. Add Stage-by-Stage Context Injection entries for each new agent (following the same format as existing entries)

Injection context for each new agent:

**QA/E2E Agent:**
- Active spec (full content + hash)
- `<SHOP_ROOT>/reports/pipeline/<NNN>-<feature-name>/adr.md`
- `<SHOP_ROOT>/reports/pipeline/<NNN>-<feature-name>/test-certification.md`
- `<SHOP_ROOT>/skills/e2e-test-architecture/SKILL.md`
- Coordinator directive specifying which ACs require E2E coverage

**DevOps Agent:**
- `<SHOP_ROOT>/reports/pipeline/<NNN>-<feature-name>/adr.md`
- `<SHOP_ROOT>/reports/security/SEC-<feature-id>-<YYYY-MM-DD>.md`
- Active spec NFR section
- `<SHOP_ROOT>/skills/devops-delivery/SKILL.md`
- `<SHOP_ROOT>/skills/infrastructure-as-code/SKILL.md`
- Coordinator directive specifying scope (new infra / CI update / runbook only / full)

**Docs Agent:**
- Active spec: `feature.spec.md`, `api.spec.md`
- `<SHOP_ROOT>/reports/pipeline/<NNN>-<feature-name>/adr.md`
- `<SHOP_ROOT>/reports/security/SEC-<feature-id>-<YYYY-MM-DD>.md`
- Existing `CHANGELOG.md`
- `<SHOP_ROOT>/skills/api-contracts/SKILL.md`
- Coordinator directive specifying doc deliverables required

---

### README.md
1. Update `## The Fourteen Agents` heading to `## The Seventeen Agents`
2. Add all 3 new agents to the agent table with a one-line description each
3. Add new agent folders (`agents/devops/`, `agents/qa-e2e/`, `agents/docs/`) to the Repository Layout tree
4. Add new skill folders (`skills/observability-implementation/`, `skills/devops-delivery/`, `skills/performance-engineering/`, `skills/api-contracts/`, `skills/frontend-accessibility/`, `skills/e2e-test-architecture/`, `skills/rag-ai-integration/`, `skills/change-management/`, `skills/infrastructure-as-code/`) to the Repository Layout tree

---

### skills/coordination/SKILL.md
Add 3 new routing branches to The Routing Decision Tree, before the `All checks pass?` leaf:
```
├─ MIGRATION-*.md exists and human approved execution?
│   └─ Route to: Programmer Agent (in migration execution mode)
│       Context: migration plan, ADR, db-model.md, authorized phase number
│
├─ Spec has user-journey ACs or frontend interactions?
│   └─ Route to: QA/E2E Agent (after Programmer completes)
│       Context: spec, ADR, test-certification.md, which ACs need E2E coverage
│
├─ Pipeline complete, feature has infrastructure requirements (new services, deployment changes)?
│   └─ Route to: DevOps Agent
│       Context: ADR, security findings, spec NFR section, existing CI/CD configs
│
├─ Pipeline complete, feature is user-facing (not internal tooling only)?
│   └─ Route to: Docs Agent
│       Context: spec, ADR, security findings, CHANGELOG.md
```

---

### workflows/pipeline-state-format.md
Add the 3 new pipeline stages to the stage enum or stage list so the Coordinator can track them in `.pipeline-state.md`:
- `qa-e2e`
- `devops`
- `docs`

---

### agents/database/skills.md
Add to Skills section:
```
- `<SHOP_ROOT>/skills/change-management/SKILL.md` — expand-contract pattern for safe schema migrations (when migration involves breaking schema changes)
```

---

## Summary — Files to Create

```
agents/devops/skills.md
agents/qa-e2e/skills.md
agents/docs/skills.md

skills/observability-implementation/SKILL.md
skills/devops-delivery/SKILL.md
skills/performance-engineering/SKILL.md
skills/api-contracts/SKILL.md
skills/frontend-accessibility/SKILL.md
skills/e2e-test-architecture/SKILL.md
skills/rag-ai-integration/SKILL.md
skills/change-management/SKILL.md
skills/infrastructure-as-code/SKILL.md
```

## Summary — Files to Update

```
agents/testrunner/skills.md
agents/code-review/skills.md
agents/architect/skills.md
agents/programmer/skills.md
agents/spec/skills.md
agents/database/skills.md
project-knowledge/skills-registry.md
skills/coordination/SKILL.md
workflows/pipeline-state-format.md
AGENTS.md
README.md
workflows/multi-agent-pipeline.md
```
