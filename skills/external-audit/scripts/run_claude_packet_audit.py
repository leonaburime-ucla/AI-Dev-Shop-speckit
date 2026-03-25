#!/usr/bin/env python3
"""Run a packet-first Claude audit with durable offloads and empty-result fallback.

This runner exists because Claude Code packet audits in JSON mode can sometimes
return a success wrapper with an empty final result. The script makes that
failure explicit, preserves raw outputs, and retries once in plain-text mode.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", required=True, help="Authoring packet path")
    parser.add_argument(
        "--dispatch",
        required=True,
        help="Peer-readable dispatch packet path",
    )
    parser.add_argument(
        "--offload-prefix",
        required=True,
        help="Prefix for raw offload files, without extension",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=300,
        help="Hard timeout for the Claude audit call",
    )
    parser.add_argument(
        "--probe-timeout-seconds",
        type=int,
        default=120,
        help="Hard timeout for the readability probe",
    )
    parser.add_argument(
        "--retain-dispatch",
        action="store_true",
        help="Keep the dispatch copy after the run",
    )
    parser.add_argument(
        "--text-retry-timeout-seconds",
        type=int,
        default=120,
        help="Hard timeout for the plain-text fallback after an empty JSON result",
    )
    return parser.parse_args()


def run_command(
    cmd: list[str],
    timeout_seconds: int,
    stdout_path: Path,
    stderr_path: Path,
) -> tuple[subprocess.CompletedProcess[str] | None, float, str | None]:
    start = time.monotonic()
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        elapsed = time.monotonic() - start
        stdout_path.write_text(completed.stdout)
        stderr_path.write_text(completed.stderr)
        return completed, elapsed, None
    except subprocess.TimeoutExpired as exc:
        elapsed = time.monotonic() - start
        stdout_path.write_text(exc.stdout or "")
        stderr_path.write_text(exc.stderr or "")
        return None, elapsed, "timeout"


def parse_json_result(raw: str) -> dict | None:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return None


def main() -> int:
    args = parse_args()

    packet = Path(args.packet)
    dispatch = Path(args.dispatch)
    offload_prefix = Path(args.offload_prefix)

    dispatch.parent.mkdir(parents=True, exist_ok=True)
    offload_prefix.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(packet, dispatch)

    probe_stdout = offload_prefix.with_name(offload_prefix.name + "-probe.stdout.json")
    probe_stderr = offload_prefix.with_name(offload_prefix.name + "-probe.stderr.txt")
    audit_stdout = offload_prefix.with_name(offload_prefix.name + "-audit.stdout.json")
    audit_stderr = offload_prefix.with_name(offload_prefix.name + "-audit.stderr.txt")
    audit_result = offload_prefix.with_name(offload_prefix.name + "-audit.result.md")
    text_stdout = offload_prefix.with_name(
        offload_prefix.name + "-audit.text-retry.stdout.txt"
    )
    text_stderr = offload_prefix.with_name(
        offload_prefix.name + "-audit.text-retry.stderr.txt"
    )
    text_result = offload_prefix.with_name(
        offload_prefix.name + "-audit.text-retry.result.md"
    )

    summary: dict[str, object] = {
        "status": "failed",
        "packet": str(packet),
        "dispatch": str(dispatch),
        "offload_prefix": str(offload_prefix),
    }

    probe_prompt = (
        f"Read the file at {dispatch} and return exactly the first Markdown heading "
        "line, nothing else."
    )
    probe_cmd = ["claude", "-p", "--output-format", "json", probe_prompt]
    probe_completed, probe_elapsed, probe_failure = run_command(
        probe_cmd,
        args.probe_timeout_seconds,
        probe_stdout,
        probe_stderr,
    )
    summary["probe"] = {
        "elapsed_seconds": round(probe_elapsed, 2),
        "failure": probe_failure,
    }
    if probe_failure:
        summary["status"] = "probe_failed"
        print(json.dumps(summary, indent=2))
        return 1

    probe_payload = parse_json_result(probe_completed.stdout)
    if probe_completed.returncode != 0 or not probe_payload or not probe_payload.get("result"):
        summary["status"] = "probe_failed"
        summary["probe"] |= {
            "returncode": probe_completed.returncode,
            "result_length": len(probe_completed.stdout),
        }
        print(json.dumps(summary, indent=2))
        return 1

    summary["probe"] |= {
        "returncode": probe_completed.returncode,
        "result": probe_payload.get("result", ""),
        "model": next(iter(probe_payload.get("modelUsage", {})), None),
    }

    audit_prompt = (
        f"Read {dispatch} and inspect only the files listed in its Files And Artifacts "
        "section using Read. Follow the packet's Auditor Instructions exactly."
    )
    audit_cmd = [
        "claude",
        "-p",
        "--allowedTools",
        "Read",
        "--output-format",
        "json",
        "--",
        audit_prompt,
    ]
    audit_completed, audit_elapsed, audit_failure = run_command(
        audit_cmd,
        args.timeout_seconds,
        audit_stdout,
        audit_stderr,
    )
    summary["audit"] = {
        "elapsed_seconds": round(audit_elapsed, 2),
        "failure": audit_failure,
    }
    if audit_failure == "timeout":
        summary["status"] = "timeout"
        print(json.dumps(summary, indent=2))
        return 1

    raw_stdout = audit_completed.stdout
    audit_payload = parse_json_result(raw_stdout)
    if audit_completed.returncode != 0 or not audit_payload:
        summary["status"] = "malformed_or_no_output"
        summary["audit"] |= {
            "returncode": audit_completed.returncode,
            "stdout_length": len(raw_stdout),
            "stderr_length": len(audit_completed.stderr),
        }
        print(json.dumps(summary, indent=2))
        return 1

    result_text = audit_payload.get("result", "")
    summary["audit"] |= {
        "returncode": audit_completed.returncode,
        "stdout_length": len(raw_stdout),
        "stderr_length": len(audit_completed.stderr),
        "num_turns": audit_payload.get("num_turns"),
        "model": next(iter(audit_payload.get("modelUsage", {})), None),
    }

    if result_text:
        audit_result.write_text(result_text)
        summary["status"] = "responded"
        summary["audit"]["result_path"] = str(audit_result)
        summary["audit"]["result_length"] = len(result_text)
    else:
        text_cmd = [
            "claude",
            "-p",
            "--allowedTools",
            "Read",
            "--",
            audit_prompt,
        ]
        text_completed, text_elapsed, text_failure = run_command(
            text_cmd,
            min(args.text_retry_timeout_seconds, args.timeout_seconds),
            text_stdout,
            text_stderr,
        )
        summary["text_retry"] = {
            "elapsed_seconds": round(text_elapsed, 2),
            "failure": text_failure,
            "timeout_seconds": min(args.text_retry_timeout_seconds, args.timeout_seconds),
        }
        if text_failure == "timeout":
            summary["status"] = "empty_result_transport_failure"
        else:
            text_output = text_completed.stdout
            summary["text_retry"] |= {
                "returncode": text_completed.returncode,
                "stdout_length": len(text_output),
                "stderr_length": len(text_completed.stderr),
            }
            if text_completed.returncode == 0 and text_output.strip():
                text_result.write_text(text_output)
                summary["status"] = "responded_text_retry"
                summary["text_retry"]["result_path"] = str(text_result)
            else:
                summary["status"] = "empty_result_transport_failure"

    if not args.retain_dispatch:
        try:
            dispatch.unlink()
        except FileNotFoundError:
            pass

    print(json.dumps(summary, indent=2))
    return 0 if summary["status"] in {"responded", "responded_text_retry"} else 1


if __name__ == "__main__":
    sys.exit(main())
