# AI Dev Shop (speckit) — Gemini CLI Entry Point

`<AI_DEV_SHOP_ROOT>` means the path to this toolkit folder (typically `AI-Dev-Shop-speckit/`).

**CRITICAL INSTRUCTION:** Read `<AI_DEV_SHOP_ROOT>/AGENTS.md` on startup for full operating instructions: all agent definitions, pipeline stages, routing rules, convergence policy, dispatch protocol, slash commands, and human checkpoints.

## Gemini CLI: Spawning Agents

Use your available tools to dispatch each specialized agent. Include their `<AI_DEV_SHOP_ROOT>/agents/<name>/skills.md`, the relevant `<AI_DEV_SHOP_ROOT>/skills/*/SKILL.md` files listed in their Skills section, the active spec with hash, and the specific task directive.

## Gemini CLI: Slash Command Setup

To activate slash commands, copy the command files once:

```bash
cp -r <AI_DEV_SHOP_ROOT>/templates/commands/gemini/ .gemini/commands/
```

Then use `/spec`, `/plan`, `/tasks`, `/implement`, `/review`, `/clarify` directly in chat. If you haven't done the copy yet, use Option B from `<AI_DEV_SHOP_ROOT>/AGENTS.md` — paste the template contents directly as a prompt.
