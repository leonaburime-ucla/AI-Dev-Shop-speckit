---
name: system-blueprint
version: 1.0.0
last_updated: 2026-03-03
description: Use when shaping a project at macro level before feature specs: define domains/components, ownership boundaries, integration map, and spec decomposition plan.
---

# Skill: System Blueprint

This skill produces a macro-level architecture planning artifact before detailed feature specs.

## Purpose

Provide a high-level system layout so Spec Agent knows what to spec and at what granularity.

This stage exists to prevent downstream spec drift: if specs are written before macro boundaries are clear, they often encode the wrong granularity, assumptions, and ownership model. That causes rework in Architect/TDD/Programmer later.

- This is problem-space and system-shape planning.
- This is not a feature-level ADR.
- This does not make binding micro-level implementation decisions.

## When to Use

Run before Spec when one or more are true:

- Multi-domain system or unclear bounded contexts.
- Unclear ownership of data or integration boundaries.
- Expected parallel team/slice delivery.
- Greenfield product with uncertain system decomposition.

## Inputs

- Product vision / vibe output / discovery notes.
- Constraints: compliance, latency, reliability, budget, timeline.
- Existing architecture context (if extending an existing system).

## Skill Loading Priority

1. Primary: this skill (`system-blueprint`) controls process and artifact shape.
2. Secondary (always): `<AI_DEV_SHOP_ROOT>/skills/design-patterns/SKILL.md` for macro architecture option language and tradeoff framing.
3. Secondary (always): `<AI_DEV_SHOP_ROOT>/skills/architecture-decisions/SKILL.md` for system-driver framing (without producing ADR decisions here).
4. Conditional tertiary skills (load only when needed):
   - `sql-data-modeling` for ambiguous data ownership boundaries
   - `api-contracts` for integration-heavy domain boundaries
   - `change-management` for legacy migration planning
   - `performance-engineering` for strict NFR-driven topology decisions

## Exploration Requirement (mandatory)

Before finalizing the blueprint, run a short exploratory tradeoff discussion with the human:

1. Present 2-3 plausible macro stack directions.
2. Explain tradeoffs in plain language (delivery speed, complexity, scalability, operations, cost, team fit).
3. Ask what the user prefers or wants to avoid.
4. Reflect the chosen direction in the blueprint with rationale.

This stage should help the user learn options and choose intentionally, not receive a one-shot static output.

## Required Output

Write one artifact using `<AI_DEV_SHOP_ROOT>/templates/system-blueprint-template.md` to:

`<AI_DEV_SHOP_ROOT>/reports/pipeline/<NNN>-<project-or-feature>/system-blueprint.md`

The output must include:

1. Macro components/domains and responsibilities.
2. Ownership boundaries and integration map.
3. High-level runtime/data topology.
4. Explicit risks and unknowns.
5. Spec decomposition plan (what spec packages to write next).

## Guardrails

- Do not produce a feature-level ADR.
- Do not lock low-level implementation patterns.
- Keep stack direction non-binding unless a hard constraint already exists.
- Use `[OWNERSHIP UNCLEAR]` markers where needed; unresolved markers block Spec decomposition approval.

## Handoff Contract

- Inputs used
- Blueprint summary
- Risks/open unknowns
- Recommended next assignee: Spec Agent
