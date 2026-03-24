# Swarm Consensus Command (/consensus)

## Purpose
To invoke the multi-model Swarm Consensus skill to solve a complex problem using the combined reasoning of available CLI LLM tools (Gemini, Claude, Codex).

## Usage
Provide a mode and question. The active agent will dispatch this prompt to available LLM CLIs, collate independent responses, and synthesize a final `consensus-report.md`.

## Arguments
- `[mode] [controls] [prompt]`
- `mode`: `single-pass` (default) or `debate`
- `controls` (optional): `max_rounds=<int>`, `min_confidence=<0.0-1.0>`, `swarm_timeout_seconds=<int>`, `claude_model=<id>`, `gemini_model=<id>`, and/or `codex_model=<id>`
- `prompt`: the detailed question or architectural problem to analyze

---

**Directive:**
Act as a Swarm Consensus Coordinator.

1. Parse `$ARGUMENTS`:
   - Detect mode from first token when it is `single-pass` or `debate`; otherwise default to `single-pass`.
   - Detect optional controls anywhere in args: `max_rounds=<int>`, `min_confidence=<0.0-1.0>`, `swarm_timeout_seconds=<int>`, `claude_model=<id>`, `gemini_model=<id>`, and `codex_model=<id>`.
   - Remaining text is the prompt.
   - Defaults if omitted: `max_rounds=3`, `min_confidence=0.90`, `swarm_timeout_seconds=300`.
2. Load the Swarm Consensus skill from `<AI_DEV_SHOP_ROOT>/skills/swarm-consensus/SKILL.md`.
3. Follow prerequisite checks to verify which CLIs (`claude`, `gemini`, `codex`) are installed, capture CLI version strings, and resolve the planned model for each peer.
4. If any peer model is inferred rather than explicitly pinned for this run, or the exact resolved model ID cannot be proven, stop before dispatch and print a confirmation gate:
   `Planned peer models: Claude=<resolved-or-inferred>, Gemini=<resolved-or-inferred>, Codex=<resolved-or-inferred>. Reply with "run" to proceed or override with claude_model=..., gemini_model=..., codex_model=....`
5. If models are already explicit or the user confirms the inferred plan, print preflight with the planned models and CLI versions.
6. If the question depends on repo-specific or project-specific context, create a shared context packet first using `skills/swarm-consensus/references/context-packet-template.md`. Before writing it, if the user has not already specified retained vs local-only, ask:
   `Save context packet? Reply "save packet" to retain it in reports/swarm-consensus/context/ or "local only" to keep it in .local-artifacts/swarm-consensus/context/.`
   Save local-only packets to `.local-artifacts/swarm-consensus/context/CTX-<slug>-<YYYY-MM-DD>.md` by default. If the user explicitly wants it retained, save or promote it to `reports/swarm-consensus/context/`.
7. Treat the current host model as the `Primary` participant. Do not add a same-family child/subagent as an extra voting peer unless the user explicitly asks for one; if used, keep it non-voting and exclude it from agreement math.
8. Run consensus in the chosen mode:
   - `single-pass`: independent first pass + one synthesis.
   - `debate`: independent first pass + bounded debate rounds until `min_confidence` agreement or `max_rounds`.
   - Apply `swarm_timeout_seconds` as the total wall-clock budget for peer dispatch across the whole run.
9. Prefer structured output modes for peer CLIs when available. Parse `stdout` only as the peer answer; keep `stderr` as diagnostics.
10. Treat transient peer failures such as `429`/`503` or clear capacity/rate-limit errors as retryable within the remaining `swarm_timeout_seconds` budget.
11. Before writing the final report, if the user has not already specified retained vs local-only vs inline-only, ask:
   `Save consensus report? Reply "save report" to retain it in reports/swarm-consensus/runs/, "local only" to keep it in .local-artifacts/swarm-consensus/runs/, or "inline only" for no file.`
   Save the final report to `.local-artifacts/swarm-consensus/runs/<timestamp>-consensus-report.md` by default. If the user explicitly wants a retained artifact, save it to `reports/swarm-consensus/runs/<timestamp>-consensus-report.md` instead. If the user wants inline-only output, skip file creation. Follow the Step 5 template from `skills/swarm-consensus/SKILL.md` exactly.
12. In `debate` mode, include round-by-round movement in an optional `## Debate Trace` section, but do not omit or rename the mandatory Step 5 sections (`The Swarm`, `Dispatch Diagnostics`, `Individual Responses`, `Synthesis`, `Decision Ledger`, `Final Recommendation`).
