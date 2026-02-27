# Startup Reminders

Tracks one-time setup prompts. The Coordinator reads this file on every startup
and skips any reminder listed under Dismissed.

To re-enable a reminder, tell the Coordinator: "re-enable reminder: <name>"
or delete the line from the Dismissed section.

---

## Dismissed

(none)

---

## slash-commands-setup

Available commands: `/spec` `/plan` `/tasks` `/implement` `/review` `/clarify` `/agent` `/consensus`

### Claude Code

Run once:
```bash
cp -r <SHOP_ROOT>/templates/commands/ .claude/commands/
```
Then type `/spec`, `/plan`, `/consensus`, etc. directly in chat.

### Gemini CLI

Slash commands are not natively supported. Use Option B:
paste the contents of `<SHOP_ROOT>/templates/commands/<command>.md` as your message.

### Codex CLI

Slash commands are not natively supported. Use Option B:
paste the contents of `<SHOP_ROOT>/templates/commands/<command>.md` as your message.

### Claude.ai (web)

Slash commands and filesystem access are not available. Use Option B:
open `<SHOP_ROOT>/templates/commands/<command>.md` on your machine, copy the contents,
and paste as your message. You will also need to paste relevant project files manually.

### Generic LLM

Slash commands are not supported. Use Option B:
open `<SHOP_ROOT>/templates/commands/<command>.md` on your machine, copy the contents,
and paste as your prompt along with any relevant project files.

### Host Detection

- Task tool + Bash tool available → Claude Code
- Bash tool available, no Task tool → Gemini CLI or Codex CLI (check system context)
- No tool access → Claude.ai or Generic LLM
- If uncertain, ask the user which host they are on
