# Skills Inbox

Quarantine area for external skill inputs.

## Point of This Inbox
- Create a single staging gate for external skills before they influence active agent behavior.
- Prevent overlapping or conflicting skills from being loaded directly into canonical `skills/`.
- Let `Skills Librarian` extract only net-new guidance, then merge it into one canonical domain skill.
- Preserve traceability by moving reviewed files to `archive/` and recording decisions in `reports/skills-audit/`.

## Rules
- Only `Skills Librarian` reads/writes here for ingestion work.
- Do not treat files here as active skills.
- After review, move each file to `archive/` with a decision note in audit report.
- Automation scripts for inbox processing live in `project-knowledge/skills-inbox/scripts/`.
- Workflow template copy is stored at `project-knowledge/skills-inbox/workflows/skills-librarian-monthly.yml`.

## Workflow Template Note
- `workflows/skills-librarian-monthly.yml` is a local backup of the monthly GitHub Actions automation.
- It checks upstream skill sources, stages changed snapshots, writes audit reports, and opens a review issue when changes are detected.
- If your push credential lacks GitHub `workflow` scope, keep using this local copy until you can push `.github/workflows/...` with proper permissions.

## Naming
Use: `YYYY-MM-DD-<source>-<skill>.md`

Example:
`2026-03-04-obra-superpowers-test-driven-development.md`
