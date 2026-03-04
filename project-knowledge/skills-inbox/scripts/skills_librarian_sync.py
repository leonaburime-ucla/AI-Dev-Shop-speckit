#!/usr/bin/env python3
"""Monthly upstream sync for Skills Librarian.

- Fetches configured upstream SKILL.md sources
- Compares SHA256 against local state
- Stages changed sources in skills-inbox/external/<date>-<id>/SKILL.md
- Writes audit report to reports/skills-audit/
- Updates state.json
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[3]
SOURCES_PATH = ROOT / "project-knowledge" / "skills-inbox" / "sources.json"
STATE_PATH = ROOT / "project-knowledge" / "skills-inbox" / "state.json"
INBOX_EXTERNAL = ROOT / "project-knowledge" / "skills-inbox" / "external"
REPORTS_DIR = ROOT / "reports" / "skills-audit"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_raw(repo: str, path: str) -> bytes:
    url = f"https://raw.githubusercontent.com/{repo}/main/{path}"
    with urlopen(url, timeout=30) as resp:
        return resp.read()


def ensure_dirs() -> None:
    INBOX_EXTERNAL.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def main() -> int:
    ensure_dirs()
    now = datetime.now(timezone.utc)
    date_tag = now.strftime("%Y-%m-%d")
    timestamp = now.isoformat()

    sources = load_json(SOURCES_PATH, [])
    state = load_json(STATE_PATH, {})

    changed = []
    unchanged = []
    errors = []

    for src in sources:
        sid = src["id"]
        repo = src["repo"]
        rel_path = src["path"]
        canonical = src.get("canonical", "")

        try:
            content = fetch_raw(repo, rel_path)
            new_hash = sha256_bytes(content)
            prev_hash = state.get(sid, {}).get("hash")

            if prev_hash != new_hash:
                stage_dir = INBOX_EXTERNAL / f"{date_tag}-{sid}"
                stage_dir.mkdir(parents=True, exist_ok=True)
                (stage_dir / "SKILL.md").write_bytes(content)
                (stage_dir / "metadata.json").write_text(
                    json.dumps(
                        {
                            "id": sid,
                            "repo": repo,
                            "path": rel_path,
                            "canonical": canonical,
                            "previous_hash": prev_hash,
                            "new_hash": new_hash,
                            "fetched_at_utc": timestamp,
                        },
                        indent=2,
                    )
                    + "\n",
                    encoding="utf-8",
                )
                changed.append((sid, repo, rel_path, canonical, prev_hash, new_hash, str(stage_dir)))
                state[sid] = {
                    "hash": new_hash,
                    "repo": repo,
                    "path": rel_path,
                    "canonical": canonical,
                    "last_checked_utc": timestamp,
                    "last_changed_utc": timestamp,
                }
            else:
                unchanged.append((sid, repo, rel_path, canonical, new_hash))
                existing = state.get(sid, {})
                state[sid] = {
                    **existing,
                    "hash": new_hash,
                    "repo": repo,
                    "path": rel_path,
                    "canonical": canonical,
                    "last_checked_utc": timestamp,
                    "last_changed_utc": existing.get("last_changed_utc", timestamp),
                }
        except (URLError, HTTPError, TimeoutError) as exc:
            errors.append((sid, repo, rel_path, str(exc)))

    STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    report_path = REPORTS_DIR / f"{date_tag}-monthly-upstream-check.md"
    with report_path.open("w", encoding="utf-8") as f:
        f.write("# Skills Librarian Monthly Upstream Check\n\n")
        f.write(f"- Checked at (UTC): {timestamp}\n")
        f.write(f"- Sources tracked: {len(sources)}\n")
        f.write(f"- Changed: {len(changed)}\n")
        f.write(f"- Unchanged: {len(unchanged)}\n")
        f.write(f"- Errors: {len(errors)}\n\n")

        if changed:
            f.write("## Changed Sources (Staged for Librarian Review)\n\n")
            for row in changed:
                sid, repo, rel_path, canonical, prev_hash, new_hash, stage_dir = row
                f.write(f"- `{sid}` from `{repo}`\n")
                f.write(f"  - Upstream path: `{rel_path}`\n")
                f.write(f"  - Canonical target: `{canonical}`\n")
                f.write(f"  - Previous hash: `{prev_hash}`\n")
                f.write(f"  - New hash: `{new_hash}`\n")
                f.write(f"  - Staged at: `{stage_dir}`\n")
        else:
            f.write("## Changed Sources\n\n")
            f.write("No upstream changes detected.\n")

        if unchanged:
            f.write("\n## Unchanged Sources\n\n")
            for sid, repo, rel_path, canonical, current_hash in unchanged:
                f.write(f"- `{sid}` ({repo}) hash unchanged: `{current_hash}`\n")

        if errors:
            f.write("\n## Fetch Errors\n\n")
            for sid, repo, rel_path, err in errors:
                f.write(f"- `{sid}` ({repo}/{rel_path}): `{err}`\n")

    print(f"report={report_path}")
    print(f"changed_count={len(changed)}")
    print(f"errors_count={len(errors)}")

    # Exit code semantics for automation:
    # 0 = no changes
    # 2 = changes detected (review needed)
    # 1 = fetch errors occurred
    if errors:
        return 1
    if changed:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
