---
name: design-patterns
version: 1.0.0
last_updated: 2026-02-22
description: Use when selecting or implementing architecture patterns including hexagonal, clean architecture, CQRS, event sourcing, event-driven, microservices, resilience, DDD tactical patterns, multi-tenant, caching, repository pattern, and more — each with TypeScript examples, tradeoffs, and when-to-use guidance.
---

# Design Patterns Library

19+ production architecture patterns with TypeScript examples, tradeoffs, testing guidance, and failure modes. Load the specific pattern file(s) relevant to the current decision — do not load all at once.

## Pattern Selection Decision Guide

| Situation | Load |
|---|---|
| Greenfield product, small team | `<SHOP_ROOT>/skills/design-patterns/references/modular-monolith.md` |
| Complex domain logic, long-lived product | `<SHOP_ROOT>/skills/design-patterns/references/clean-architecture.md` or `hexagonal-architecture.md` |
| Multiple I/O channels (HTTP + CLI + events) | `<SHOP_ROOT>/skills/design-patterns/references/hexagonal-architecture.md` |
| Feature teams, autonomous delivery | `<SHOP_ROOT>/skills/design-patterns/references/vertical-slice-architecture.md` |
| Asymmetric read/write workloads | `<SHOP_ROOT>/skills/design-patterns/references/cqrs.md` |
| Audit trail, financial, compliance | `<SHOP_ROOT>/skills/design-patterns/references/event-sourcing.md` (pair with CQRS) |
| Async cross-service side effects | `<SHOP_ROOT>/skills/design-patterns/references/event-driven-architecture.md` |
| Multi-service business transactions | `<SHOP_ROOT>/skills/design-patterns/references/reliability-patterns.md` (Saga) |
| Reliable event publishing | `<SHOP_ROOT>/skills/design-patterns/references/reliability-patterns.md` (Outbox) |
| Independent team deployment at scale | `<SHOP_ROOT>/skills/design-patterns/references/microservices.md` |
| Migrating a legacy system | `<SHOP_ROOT>/skills/design-patterns/references/strangler-fig.md` |
| Multiple client types (mobile, web, API) | `<SHOP_ROOT>/skills/design-patterns/references/api-patterns.md` (BFF) |
| Centralized auth, rate limiting at edge | `<SHOP_ROOT>/skills/design-patterns/references/api-patterns.md` (API Gateway) |
| Preventing cascade failures | `<SHOP_ROOT>/skills/design-patterns/references/resilience-patterns.md` |
| Bursty traffic, ops-light team | `<SHOP_ROOT>/skills/design-patterns/references/serverless-architecture.md` |
| Offline batch / ML pipelines | `<SHOP_ROOT>/skills/design-patterns/references/pipeline-batch-architecture.md` |
| Simple CRUD, familiar team structure | `<SHOP_ROOT>/skills/design-patterns/references/layered-architecture.md` |
| Domain layer needs data access without DB coupling | `<SHOP_ROOT>/skills/design-patterns/references/repository-pattern.md` |
| Modeling complex domain with entities, aggregates, value objects | `<SHOP_ROOT>/skills/design-patterns/references/ddd-tactical-patterns.md` |
| SaaS product with multiple isolated customers | `<SHOP_ROOT>/skills/design-patterns/references/multi-tenant-architecture.md` |
| Read-heavy workloads, expensive repeated queries, latency reduction | `<SHOP_ROOT>/skills/design-patterns/references/caching-patterns.md` |

## Common Pattern Combinations

**Event-driven modular monolith** (recommended starting point for most products):
`modular-monolith` + `event-driven-architecture` + `reliability-patterns` (Outbox)

**Audit-ready enterprise system**:
`clean-architecture` + `cqrs` + `event-sourcing`

**High-scale distributed system**:
`microservices` + `event-driven-architecture` + `reliability-patterns` + `resilience-patterns` + `api-patterns`

**Legacy migration path**:
`strangler-fig` → `modular-monolith` → `microservices` (if needed)

## All Pattern Files

See `<SHOP_ROOT>/skills/design-patterns/references/` for the full set.
