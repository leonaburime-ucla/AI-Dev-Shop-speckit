# Framework

This folder groups the toolkit-owned framework surface that controls how ADS runs.

## Layout

- `spec-providers/` defines the active planning provider boundary and provider profiles
- `templates/` holds framework templates consumed by agents and workflows
- `workflows/` defines pipeline rules, state formats, and conventions
- `slash-commands/` holds reusable command templates for hosts that support or emulate slash commands
- `governance/`, `memory/`, `operations/`, `routing/`, and `examples/` hold static toolkit guidance that used to be mixed into `project-knowledge/`

## Write Rules

- Treat everything under `framework/` as read-only during normal host-project feature work unless the user is explicitly maintaining ADS itself.
- For toolkit maintenance that needs the repo-local workspace mirror, write retained artifacts to `project-knowledge/reports/`.
- For toolkit maintenance scratch output, use `project-knowledge/.local-artifacts/`.
