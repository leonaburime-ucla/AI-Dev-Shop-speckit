# AI Dev Shop (speckit) — Claude Code Entry Point

Read `<SHOP_ROOT>/AGENTS.md` for full operating instructions: all agent definitions, pipeline stages, routing rules, convergence policy, dispatch protocol, slash commands, and human checkpoints.

## Claude Code: Spawning Agents

Use the **Task tool** to dispatch each specialized agent. Include their `<SHOP_ROOT>/agents/<name>/skills.md`, the relevant `<SHOP_ROOT>/skills/*/SKILL.md` files listed in their Skills section, the active spec with hash, and the specific task directive.

## Claude Code: Slash Command Setup

To activate slash commands, copy the command files once:

```bash
cp -r <SHOP_ROOT>/templates/commands/ .claude/commands/
```

Then type `/spec`, `/plan`, `/tasks`, `/implement`, `/review`, `/clarify` directly in chat. If you haven't done the copy yet, use Option B from `<SHOP_ROOT>/AGENTS.md` — paste the template contents directly as a prompt.
