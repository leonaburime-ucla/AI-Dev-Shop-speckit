# AI Dev Shop (speckit) — Claude Code Entry Point

Read `AI-Dev-Shop-speckit/AGENTS.md` for full operating instructions: all agent definitions, pipeline stages, routing rules, convergence policy, dispatch protocol, slash commands, and human checkpoints.

## Claude Code: Spawning Agents

Use the **Task tool** to dispatch each specialized agent. Include their `AI-Dev-Shop-speckit/agents/<name>/skills.md`, the relevant `AI-Dev-Shop-speckit/skills/*/SKILL.md` files listed in their Skills section, the active spec with hash, and the specific task directive.

## Claude Code: Slash Command Setup

To activate slash commands, copy the command files once:

```bash
cp -r AI-Dev-Shop-speckit/templates/commands/ .claude/commands/
```

Then type `/spec`, `/plan`, `/tasks`, `/implement`, `/review`, `/clarify` directly in chat. If you haven't done the copy yet, use Option B from `AI-Dev-Shop-speckit/AGENTS.md` — paste the template contents directly as a prompt.
