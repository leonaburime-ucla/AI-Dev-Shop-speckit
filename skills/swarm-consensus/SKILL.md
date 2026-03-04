---
name: swarm-consensus
version: 1.2.0
last_updated: 2026-03-04
description: Orchestrate a multi-model swarm by dispatching a prompt to all available LLM CLIs (whichever ones are installed), collating independent responses, and synthesizing a consensus. Supports single-pass and debate modes. Model-agnostic — the primary model is whoever is currently running this skill. OFF by default.
---

# Skill: Swarm Consensus

**This skill is OFF by default.** Only invoke it when explicitly instructed by the user or the Coordinator.

## When to Use

- User explicitly requests "consensus", "swarm analysis", or uses the `/consensus` command
- Coordinator directs a specific agent to use Swarm Consensus for a single hard task
- An ADR has profound architectural consequences and requires multi-perspective validation
- Red-Team is probing a spec for blind spots that a single model might miss

## Model-Agnostic Design

**You are the primary model.** Whatever LLM is currently running this skill is the primary reasoner. You generate your own response first, then dispatch the same prompt to any other available CLI tools, and synthesize the combined output.

The peer CLIs are external — they run as subprocesses via shell and return `stdout`. You do not know in advance which ones are installed. The prerequisite check determines this at runtime.

Supported peer CLIs:

| CLI | Invocation | Notes |
|---|---|---|
| `claude` | `claude -p "<prompt>"` | Claude Code CLI |
| `gemini` | `gemini -p "<prompt>"` | Gemini CLI |
| `codex` | `codex "<prompt>"` | OpenAI Codex CLI |

If you are Claude Code, you dispatch to `gemini` and `codex`. If you are Gemini, you dispatch to `claude` and `codex`. The skill works identically regardless of who is primary.

---

## Consensus Modes

Pick one mode explicitly at run start:

- `single-pass` (default): independent first-pass answers from all models, one synthesis pass, then final recommendation.
- `debate`: independent first-pass answers, then bounded rebuttal rounds, then final recommendation.

If the user does not specify mode, use `single-pass`.

---

## Debate Controls

Debate mode accepts runtime controls from the user:

- `max_rounds=<int>`: maximum rebuttal rounds (default `3`)
- `min_confidence=<0.0-1.0>`: minimum agreement threshold to stop early (default `0.90`)

If controls are not provided, use defaults. If provided values are invalid, state the invalid value and fall back to defaults.

---

## Step 1 — Prerequisite Check + Preflight

Before dispatching anything, run these checks via shell:

```bash
which claude && claude --version 2>/dev/null || echo "claude: not installed"
which gemini && gemini --version 2>/dev/null || echo "gemini: not installed"
which codex  && codex  --version 2>/dev/null || echo "codex: not installed"
```

From the output:
- Record which CLIs are available (installed and returning a version)
- Record the exact model version string for each available CLI — this goes in the consensus report
- Skip any CLI that is not installed — do not error, just note it as absent in the report
- Check for any user-saved model version preferences (e.g. from a prior "always use Opus for consensus" instruction) and apply them via CLI flags if the tool supports it
- Run preflight transparency announcement before asking any model:
  - `Asking question to Gemini <version>, Codex <version>, Claude <version>`
  - If a CLI is missing: `Gemini not installed` (or equivalent) in the same announcement.

A minimum viable swarm is **primary model + 1 peer**. If no peers are available, tell the user and stop — running consensus with only one model produces no value. **This is a graceful stop, not a pipeline failure.** If Swarm Consensus was invoked as part of a pipeline stage, that stage proceeds using the primary model's output alone — the pipeline is not blocked by missing peer CLIs.

### Freshness policy

Consensus runs should prefer latest or near-latest model aliases/snapshots when available:

- Claude: use explicit alias/full model via `--model` and prefer current production aliases (for example `sonnet`/`opus`) unless user pins otherwise.
- Gemini: use an explicitly configured model (`-m`) and prefer current production Gemini family.
- Codex: use an explicitly configured model (`-m`) and prefer current production Codex/GPT coding model aliases.

If a configured model appears stale, unavailable, or unknown, state it before the run and continue only if:
- the user accepts fallback, or
- a documented default fallback exists in this project.

---

## Step 2 — Prompt Formulation

Write one focused prompt that contains:
- The problem or question to analyze
- All relevant constraints and context
- The required output format (e.g. "structured recommendation with reasoning")

Keep it self-contained. The peer CLIs have no project context — everything they need must be in the prompt itself.

### Online Resource Pre-Fetch (primary model responsibility)

If the prompt requires online resources (URLs, external files, live data from the web):

1. **The primary model fetches all required resources before dispatching to peers.**
2. Embed fetched resource content into the shared prompt payload — do not pass raw URLs and expect peers to fetch independently.
3. If any required resource cannot be fetched (404, timeout, auth wall, etc.):
   - Do not proceed with a degraded prompt that omits the resource.
   - Tell the user immediately: which URL failed and why.
   - Ask whether to proceed without that resource or abort.
   - If the user says proceed, note the missing resource explicitly in the prompt so all models reason from the same incomplete-but-declared baseline.

**Rationale:** Some LLMs in the swarm may not have web access, or the same URL may return differently across models. Pre-fetching by the primary model guarantees all peers reason from identical source material.

### Prompt Transport Safety (hard requirement)

Do not pass large or untrusted prompt text directly as shell-interpolated inline strings.

1. Write the full prompt to a temporary file (for example `.swarm-prompt.txt`) or pipe it via stdin.
2. Invoke peer CLIs using file/stdin-safe patterns where possible.
3. If a tool only supports inline prompt args, apply strict escaping and note this risk in the report.
4. Never execute fetched resource content as shell code.

---

## Step 3 — Swarm Dispatch

**CRITICAL ANTI-HALLUCINATION RULE:** You MUST NOT fake, imagine, or hallucinate the responses from other models. If a CLI tool is not installed, or if the shell command fails or times out, you must strictly report that it failed or is unavailable. Do not invent a consensus or make up quotes from peer models. You are only allowed to synthesize the actual text captured from the `stdout` of the shell commands.

### First-pass anti-bias rule (hard requirement)

1. Primary model MUST produce its own answer first and freeze it.
2. Primary model MUST NOT read peer outputs until its first-pass answer is written.
3. Round-1 peer prompts MUST NOT include other models' answers.

### Anti-Truncation Protocol (hard requirement)

Do not rely on subjective "looks abrupt" checks alone.

1. Require each peer response to end with a deterministic end marker, for example `<<SWARM_END>>`.
2. If marker is missing, or response is empty/obviously partial, mark it as `Failed (Truncated)`.
3. **Truncated responses MUST NOT be included in synthesis.**
4. Tell the user inline: `[ModelName]'s response was truncated or incomplete. It has been excluded from synthesis.`

### Round 1 (all modes)

1. **Self (primary model):** Generate full first-pass response and freeze it.
2. **Each available peer CLI:** Execute via shell, capture `stdout`. Use timeout of 60 seconds per call — if a tool hangs, mark as timed out and continue.

```bash
# Example patterns — adapt to actual CLI support
# Preferred: stdin/file transport (safer than inline interpolation)
claude -p "$(cat .swarm-prompt.txt)" 2>/dev/null
gemini -p "$(cat .swarm-prompt.txt)" 2>/dev/null
codex  "$(cat .swarm-prompt.txt)"    2>/dev/null
```

If a peer CLI returns a non-zero exit code or empty output, mark it as failed in the report and exclude it from synthesis.

### Resource Fetch Failure — Peer Withdrawal Protocol

If a peer model's response contains a resource fetch failure signal (e.g. it reports it could not access a required URL, file, or external dependency needed to answer the question):

1. **Mark that peer as "Resource unavailable" in the Swarm table** — do not include its response in synthesis.
2. **Tell the user immediately**, inline, before continuing:
   > `[ModelName] could not access [resource]. It has withdrawn from this round. Continuing with [remaining models].`
3. Do not silently include a response that was built on assumptions about content the model could not read — that contaminates synthesis with hallucinated context.
4. If the *primary model* cannot fetch a required resource, it must tell the user and stop the run (or ask to proceed without it) — it cannot dispatch a degraded prompt to peers without disclosing this.
5. If after withdrawals only one model remains (primary + 0 peers), stop and inform the user: not enough participants for meaningful consensus.

---

### Debate rounds (debate mode only)

In `debate` mode, run bounded rebuttal rounds after Round 1:

1. Build a decision-point ledger (architecture choice, data model strategy, risk posture, migration approach, etc.).
2. Summarize deltas only (where models disagree) and send the summarized deltas back to each model for rebuttal. 
   - **Mid-Debate Dropout Rule:** If a model that participated in Round 1 fails to respond, times out, or reports a resource failure in Round 2+, it **withdraws from the remainder of the debate**. 
   - Do not hallucinate its rebuttal. Note its withdrawal inline to the user. Its Round 1 positions remain in the ledger but are marked as "Final (Withdrawn)".
   - Recompute active participants each round. If active participants drop below two total responders (primary + at least one peer), stop debate and report insufficient participants for meaningful consensus.
3. Repeat for up to `max_rounds`.
4. Stop early when agreement is >=`min_confidence` on decision points.

Agreement formula:
- `agreement_percent = (decision_points_with_same_outcome / total_decision_points) * 100`

If max rounds reached without reaching `min_confidence`:
- stop debate,
- declare unresolved deltas,
- provide recommendation with explicit uncertainty/tradeoff callouts.

---

## Step 4 — Synthesis

With all responses collected:

1. **Areas of agreement** — where 2+ models reached the same conclusion independently. These are strong signals. Weight them heavily.
2. **Areas of divergence** — where models disagreed. Do not average them out. Explain *why* they diverged (different assumptions, different risk weighting, different information). Present both positions clearly.
3. **Unique insights** — something only one model raised. Flag it as unverified but worth considering.
4. **Final recommendation** — your synthesized conclusion. Be explicit about which inputs drove it and why.

---

## Step 5 — Output

Produce a `consensus-report.md` (or inline if the user prefers) with this structure:

```markdown
# Consensus Report

**Date:** <ISO-8601>
**Prompt:** <the prompt used>
**Mode:** <single-pass | debate>
**Primary model:** <name>

## The Swarm
| Role | Model | Version | Status |
|---|---|---|---|
| Primary | <your model name> | <version> | Responded |
| Peer | claude | <version or "not installed"> | Responded / Failed / Failed (Truncated) / Withdrawn / Not installed / Resource unavailable |
| Peer | gemini | <version or "not installed"> | Responded / Failed / Failed (Truncated) / Withdrawn / Not installed / Resource unavailable |
| Peer | codex  | <version or "not installed"> | Responded / Failed / Failed (Truncated) / Withdrawn / Not installed / Resource unavailable |

## Individual Responses

### <Primary model name>
<Summary of primary reasoning>

### Claude (if responded)
<Summary of Claude's response>

### Gemini (if responded)
<Summary of Gemini's response>

### Codex (if responded)
<Summary of Codex's response>

## Synthesis

### Agreement
<What all responding models agreed on>

### Divergence
<Where they disagreed and why>

### Unique Insights
<Anything only one model raised>

### Decision Ledger
| Decision Point | Primary | Claude | Gemini | Codex | Agreement |
|---|---|---|---|---|---|
| <point 1> | <position> | <position> | <position> | <position> | Yes/No |

### Unresolved Deltas
<Only include if disagreement remains after synthesis/debate>

## Final Recommendation
<Synthesized conclusion with reasoning>
```

Always fill in the Swarm table completely, including models that were not installed or failed. The user should always know which models contributed.

---

## Configuration

If the user asks to set a default model version for a peer CLI (e.g. "always use Opus for Claude in consensus runs"), save that preference and apply it as a flag on future dispatches. Document what flag was used in the consensus report so the run is reproducible.
