---
name: skills-registry
version: 1.0.0
last_updated: 2026-02-26
description: Maps every shared skill to the agents that use it. Reference when dispatching agents or updating skills.
---

# Skills Registry

All agents draw from `<SHOP_ROOT>/skills/`. Do not duplicate skill content in agent files — reference the skill file instead.

| Skill | Used By |
|---|---|
| `skills/spec-writing/SKILL.md` | Spec Agent |
| `skills/test-design/SKILL.md` | TDD Agent |
| `skills/architecture-decisions/SKILL.md` | Architect, Programmer |
| `skills/code-review/SKILL.md` | Code Review Agent |
| `skills/refactor-patterns/SKILL.md` | Refactor Agent |
| `skills/coordination/SKILL.md` | Coordinator |
| `skills/context-engineering/SKILL.md` | Coordinator, Observer |
| `skills/memory-systems/SKILL.md` | Coordinator |
| `skills/tool-design/SKILL.md` | Programmer |
| `skills/agent-evaluation/SKILL.md` | Observer |
| `skills/codebase-analysis/SKILL.md` | CodeBase Analyzer |
| `skills/architecture-migration/SKILL.md` | CodeBase Analyzer |
| `skills/design-patterns/SKILL.md` | Architect, CodeBase Analyzer |
| `skills/frontend-react-orcbash/SKILL.md` | Programmer (React frontends) |
| `skills/sql-data-modeling/SKILL.md` | Database Agent |
| `skills/postgresql/SKILL.md` | Database Agent, Supabase Sub-Agent |
| `skills/supabase/SKILL.md` | Supabase Sub-Agent |
| `skills/enterprise-spec/SKILL.md` | Spec Agent (enterprise contexts) |
| `skills/evaluation/eval-rubrics.md` | Observer |
| `skills/swarm-consensus/SKILL.md` | All agents (opt-in via Coordinator) |
| `skills/observability-implementation/SKILL.md` | Architect, Programmer, Security Agent |
| `skills/devops-delivery/SKILL.md` | DevOps Agent |
| `skills/security-review/SKILL.md` | Security, Code Review, DevOps |
| `skills/performance-engineering/SKILL.md` | TestRunner Agent, Architect |
| `skills/api-contracts/SKILL.md` | Spec Agent, Code Review Agent, Docs Agent |
| `skills/frontend-accessibility/SKILL.md` | Code Review Agent, QA/E2E Agent |
| `skills/e2e-test-architecture/SKILL.md` | QA/E2E Agent, TDD Agent |
| `skills/rag-ai-integration/SKILL.md` | Architect, Programmer, Database Agent |
| `skills/change-management/SKILL.md` | Programmer, DevOps Agent, Architect, Database Agent |
| `skills/infrastructure-as-code/SKILL.md` | DevOps Agent, Architect |
| `skills/vibe-coding/SKILL.md` | VibeCoder Agent (optional, Agent Direct Mode) |
| `project-knowledge/tool-permission-policy.md` | All agents (security guardrails) |
| `project-knowledge/data-classification.md` | All agents (PII and secret handling) |
| `project-knowledge/model-routing.md` | Coordinator (dispatch tier selection) |
| `project-knowledge/escalation-policy.md` | Coordinator (retry budgets and escalation triggers) |
| `project-knowledge/agent-performance-scorecard.md` | Observer (quality tracking) |
