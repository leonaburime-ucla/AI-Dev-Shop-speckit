# AI Dev Shop Foundation

Drop this folder into any project. Point Claude Code, Codex, or Gemini at it. Tell the Coordinator what to build.

## Dropping This Into a New Project

Copy the `<SHOP_ROOT>/` folder into your project root:

```bash
cp -r <SHOP_ROOT>/ your-project/<SHOP_ROOT>/
```

Each tool has a file it reads automatically on startup. Add the following to the right one:

**Claude Code** — add to `CLAUDE.md` at your project root (create if missing):
```
Read `<SHOP_ROOT>/AGENTS.md` for the AI Dev Shop multi-agent pipeline.
```

**Gemini CLI / OpenAI Codex** — add to `GEMINI.md` (Gemini) or `AGENTS.md` (Codex) at your project root. Paste the following into your root file:

> **Note (Codex):** Codex has shown reliability issues running multi-agent workflows — agents may fail to maintain pipeline state, drop context between stages, or not follow routing rules consistently. If you encounter this, Claude Code or Gemini CLI are more reliable choices for this system.
```
Read `<SHOP_ROOT>/AGENTS.md` for the AI Dev Shop multi-agent pipeline.

# Mandatory Startup

On the first user message in this repository (including greetings), before any reply:
1. Open and read `<SHOP_ROOT>/AGENTS.md`.
2. Provide a comprehensive welcome message that MUST include:
   - "Booted with <SHOP_ROOT>/AGENTS.md loaded."
   - A bulleted list of the 3 Coordinator modes (Review Mode, Pipeline Mode, Direct Mode) along with a 1-sentence summary explaining what each mode actually does.
3. If the file is missing or unreadable, state that explicitly and stop.

Failure to perform Mandatory Startup is a blocking error. Do not proceed with task work until corrected.
```

**Cursor** — add to `.cursor/rules/ai-dev-shop.mdc` (create if missing):
```
Multi-agent pipeline: see <SHOP_ROOT>/AGENTS.md
```

**GitHub Copilot** — add to `.github/copilot-instructions.md` (create if missing):
```
Multi-agent pipeline: see <SHOP_ROOT>/AGENTS.md
```

**Other** — add the same one-liner to whatever file your tool reads on startup, or include `<SHOP_ROOT>/AGENTS.md` manually at the start of your first session.

**Slash commands (Claude Code)** — copy the command templates once to activate `/spec`, `/plan`, `/tasks`, `/implement`, `/review`, `/clarify`, `/consensus`:
```bash
cp -r <SHOP_ROOT>/templates/commands/ .claude/commands/
```

**Slash commands (Gemini CLI)** — copy the Gemini-specific command templates:
```bash
cp -r <SHOP_ROOT>/templates/commands/gemini/ .gemini/commands/
```

**First-time setup:**
1. Edit `<SHOP_ROOT>/project-knowledge/constitution.md` — replace the default articles with your project's engineering principles, or keep the defaults
2. Fill in `<SHOP_ROOT>/project-knowledge/project_memory.md` with your project's conventions and gotchas
3. Tell the Coordinator what you want to build, or type `/spec [description]`

The Coordinator will route between agents, enforce convergence, and stop at human checkpoints.

**Verify required files are present before starting:**

```
<SHOP_ROOT>/AGENTS.md                                    ← must exist
<SHOP_ROOT>/CLAUDE.md                                    ← must exist
<SHOP_ROOT>/project-knowledge/constitution.md            ← customize articles for your project
<SHOP_ROOT>/project-knowledge/project_memory.md          ← fill in before first spec
<SHOP_ROOT>/project-knowledge/knowledge-routing.md       ← memory routing rules
<SHOP_ROOT>/project-knowledge/spec-definition-of-done.md ← spec DoD checklist
<SHOP_ROOT>/templates/spec-system/feature.spec.md        ← strict-mode spec package templates
<SHOP_ROOT>/templates/adr-template.md                    ← must exist
<SHOP_ROOT>/templates/tasks-template.md                  ← must exist
```

## How It Works

A structured multi-agent pipeline converts product intent into production code through specialized agents, each with a defined role, versioned operating procedure, and handoff contract.

```
[VibeCoder] → [CodeBase Analyzer] → Spec → [Red-Team] → Architect → [Database] → TDD → Programmer → [QA/E2E] → TestRunner → Code Review → [Refactor] → Security → [DevOps] → [Docs] → Done
```

`[VibeCoder]` is an optional starting point for fast prototyping before the structured pipeline. `[...]` stages are optional; dispatched by Coordinator when spec/ADR triggers them or when you specifically ask for them. The Coordinator owns all routing. Agents never talk to each other directly. Specs are ground truth — everything downstream is traceable to a spec version and hash.

Full operating manual: **`<SHOP_ROOT>/AGENTS.md`**

## Integration with github/spec-kit

This toolkit deeply integrates concepts from [GitHub's spec-kit](https://github.com/github/spec-kit), a spec-driven development methodology. The following spec-kit ideas are incorporated and adapted for the multi-agent pipeline:

- **Constitution framework** — `project-knowledge/constitution.md` with 8 governance articles. Every spec and ADR must comply. Violations are blocking escalations.
- **[NEEDS CLARIFICATION] markers** — inline ambiguity flags in specs, with a structured `/clarify` command to resolve them before Architect dispatch.
- **Quality checklist gate** — Spec Agent generates `requirements.md` per feature and validates the spec against it before handoff.
- **Per-feature artifact folders** — spec files live at the user-specified location in `<NNN>-<feature-name>/`; pipeline artifacts (ADR, research, tasks, test-certification, red-team findings, pipeline state) live in `<SHOP_ROOT>/reports/pipeline/<NNN>-<feature-name>/`. The `spec_path` field in `.pipeline-state.md` links the two.
- **Slash commands** — `/spec`, `/clarify`, `/plan`, `/tasks`, `/implement`, `/review`, `/consensus` as executable commands (see `templates/commands/`).
- **Research artifact** — Architect produces `research.md` before the ADR when technology choices are involved.
- **tasks.md with [P] markers** — parallelizable task list generated from the ADR, with story phases ordered by AC priority.

## Repository Layout

```
CLAUDE.md                          ← Claude Code entry point (reads AGENTS.md)
AGENTS.md                          ← Full operating manual for all agents and pipeline
├── agents/                        ← One folder per agent — lean SOP referencing skills/
│   ├── codebase-analyzer/
│   ├── coordinator/
│   ├── spec/
│   ├── red-team/
│   ├── architect/
│   ├── tdd/
│   ├── programmer/
│   ├── qa-e2e/
│   ├── testrunner/
│   ├── code-review/
│   ├── refactor/
│   ├── security/
│   ├── devops/
│   ├── docs/
│   ├── vibecoder/                ← VibeCoder Agent (optional, Agent Direct Mode)
│   ├── observer/
│   ├── database/                  ← Database Agent (domain head: schema, migrations, queries)
│   │   └── supabase/              ← Supabase Sub-Agent (RLS, PostgREST, realtime, storage)
├── skills/                        ← SKILL.md format — each skill is a self-contained folder
│   ├── spec-writing/SKILL.md
│   ├── enterprise-spec/SKILL.md   ← Overlay: cross-repo orchestration, approval matrix, harnesses
│   ├── test-design/SKILL.md
│   ├── architecture-decisions/SKILL.md
│   ├── code-review/SKILL.md
│   ├── security-review/SKILL.md
│   ├── refactor-patterns/SKILL.md
│   ├── coordination/SKILL.md
│   ├── context-engineering/SKILL.md
│   ├── memory-systems/SKILL.md
│   ├── tool-design/SKILL.md
│   ├── agent-evaluation/SKILL.md
│   ├── codebase-analysis/SKILL.md
│   ├── architecture-migration/SKILL.md
│   ├── swarm-consensus/SKILL.md   ← Multi-model consensus (OFF by default)
│   ├── sql-data-modeling/SKILL.md ← ERD, normalisation, migrations (platform-agnostic)
│   ├── postgresql/SKILL.md        ← CTEs, window functions, JSONB, triggers, FTS
│   ├── supabase/SKILL.md          ← RLS, PostgREST, realtime, storage, edge functions
│   ├── frontend-react-orcbash/SKILL.md ← Orc-BASH hexagonal pattern for React
│   ├── observability-implementation/SKILL.md ← Structured logging, metrics, tracing
│   ├── devops-delivery/SKILL.md   ← CI/CD, Docker, deployment strategies
│   ├── performance-engineering/SKILL.md ← Load testing, pass/fail criteria
│   ├── api-contracts/SKILL.md     ← Contract completeness, versioning, backward compat
│   ├── frontend-accessibility/SKILL.md ← WCAG 2.1 AA checklist
│   ├── e2e-test-architecture/SKILL.md ← Playwright patterns, anti-flake rules
│   ├── rag-ai-integration/SKILL.md ← RAG pipelines, vector DB, LLM integration
│   ├── change-management/SKILL.md ← Feature flags, dual writes, expand-contract
│   ├── infrastructure-as-code/SKILL.md ← IaC declaration patterns
│   ├── vibe-coding/SKILL.md       ← Fast exploratory prototyping (VibeCoder)
│   └── design-patterns/           ← 19+ patterns with TypeScript examples
│       ├── SKILL.md               ← index + pattern selection guide
│       └── references/            ← individual pattern files
├── project-knowledge/             ← Fill these in per project
│   ├── constitution.md            ← 8-article engineering governance (customize per project)
│   ├── project_memory.md          ← Conventions, gotchas, tribal knowledge
│   ├── knowledge-routing.md       ← Where all project memory goes (routing rules)
│   ├── spec-definition-of-done.md ← 95-item DoD checklist for strict-mode spec packages
│   ├── learnings.md               ← Failure log (append-only)
│   ├── project_notes.md           ← Open questions, deferred decisions
│   └── foundation.md              ← Source philosophy (read-only reference)
├── templates/
│   ├── spec-template.md           ← Legacy single-file format (deprecated in strict mode)
│   ├── adr-template.md
│   ├── test-certification-template.md
│   ├── constitution-template.md
│   ├── checklist-template.md
│   ├── research-template.md
│   ├── tasks-template.md
│   ├── spec-system/               ← Strict-mode 9-file spec package templates
│   │   ├── feature.spec.md        ← Canonical spec (goals, REQs, ACs, invariants, edge cases)
│   │   ├── api.spec.md            ← Typed API contracts
│   │   ├── state.spec.md          ← State shapes and transitions
│   │   ├── orchestrator.spec.md   ← Orchestrator output model
│   │   ├── ui.spec.md             ← UI component contracts
│   │   ├── errors.spec.md         ← Error code registry
│   │   ├── behavior.spec.md       ← Deterministic behavior rules (EARS syntax)
│   │   ├── traceability.spec.md   ← REQ-to-function-to-test mapping
│   │   ├── spec-dod.md            ← DoD checklist (must pass before Architect dispatch)
│   │   └── requirements.md        ← Spec quality checklist (generated by Spec Agent)
│   └── commands/                  ← Copy to .claude/commands/ to activate slash commands
│       ├── spec.md      → /spec
│       ├── clarify.md   → /clarify
│       ├── plan.md      → /plan
│       ├── tasks.md     → /tasks
│       ├── implement.md → /implement
│       ├── review.md    → /review
│       ├── consensus.md → /consensus
│       └── gemini/      ← Gemini CLI equivalents (copy to .gemini/commands/)
└── workflows/
    ├── multi-agent-pipeline.md    ← Stage-by-stage pipeline with context injection rules
    ├── job-lifecycle.md           ← Coordinator modes and job lifecycle
    ├── pipeline-state-format.md   ← .pipeline-state.md schema
    └── trace-schema.md            ← Agent trace and debug log format
```

## The Eighteen Agents

| Agent | Role |
|---|---|
| VibeCoder (optional) | Fast exploratory prototyping — optional on-ramp before the structured pipeline |
| CodeBase Analyzer | Pre-pipeline: analyzes existing codebases, produces findings reports and migration plans |
| Coordinator | Routes between agents, owns convergence, escalates to human. Starts in Review Mode. |
| Spec | Converts product intent into precise, versioned, testable specs (strict mode: 9-file package) |
| Red-Team | Adversarially probes approved specs for ambiguity, contradictions, and missing failure modes |
| Architect | Selects architecture patterns, writes ADRs, defines module boundaries |
| TDD | Writes tests against the spec before any implementation |
| Programmer | Implements code to make certified tests pass |
| QA/E2E | Writes browser-level Playwright tests from user journeys |
| TestRunner | Executes tests and reports evidence — no interpretation |
| Code Review | Reviews spec alignment, architecture, test quality, security surface |
| Refactor | Proposes (never implements) non-behavioral improvements |
| Security | Analyzes threat surface; Critical/High findings require human sign-off |
| DevOps | Produces Dockerfiles, CI/CD pipeline configs, IaC declarations |
| Docs | Produces OpenAPI specs, user guides, changelogs, release notes |
| Observer | Watches the pipeline, surfaces systemic patterns, recommends improvements |
| Database Agent | Domain head: schema design, data modeling, migrations, query review, indexing strategy |
| Supabase Sub-Agent | Supabase-specific implementation: RLS, PostgREST, realtime, storage, edge functions, auth |

## Swarm Consensus

**OFF by default.** Any agent can invoke the Swarm Consensus skill when explicitly instructed. It dispatches the same prompt to all available peer LLM CLIs (`claude`, `gemini`, `codex` — whichever are installed), collates independent responses, and synthesizes a `consensus-report.md`. The running model is always the primary; peers are subprocesses. Use `/consensus [question]` or tell any agent to use swarm consensus for a specific task.

> **Note:** Codex has shown reliability issues in multi-agent workflows and may not be a dependable peer for consensus runs. Claude Code and Gemini CLI are the recommended primary and peer models.

## Methodology

This pipeline is built on Meta-Coding (ASTRA: AI + Specs + TDD + Reference Architecture). Full source reading and philosophy: `<SHOP_ROOT>/project-knowledge/foundation.md`.
