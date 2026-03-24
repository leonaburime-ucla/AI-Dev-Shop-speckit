# External Audit Report

**Date:** <ISO-8601>
**Scope:** <work-log | current-diff | staged | last-commit | custom>
**Focus:** <the user's audit question>
**Audit Packet:** <path>
**Dispatch Packet:** <peer-readable path or "same as audit packet">
**Auditor CLI:** <claude | gemini | codex>
**Requested Model:** <requested or "n/a">
**Resolved Model:** <exact model name/version or "not proven">
**Selection Source:** <per_run_override | saved_preference | local_cli_proof | unknown>
**CLI Version:** <version>
**Timeout:** <seconds>
**Audit Status:** <Responded | Failed | Timed out | Retry exhausted | Not installed>

## Work Log
- <what you did>
- <why>
- <verification run or not run>

## Auditor Diagnostics
| Field | Value |
|---|---|
| Output mode | <json | text> |
| stdout parser | <field or end marker> |
| stderr summary | <short summary> |
| Attempts | <count> |
| Final status | <Responded | Failed | Timed out | Retry exhausted | Not installed> |

## What The External LLM Said

### Findings By Severity
- <succinct but faithful summary of the auditor's findings>

### Blockers
- <real blockers, or "none">

### Optional Improvements
- <non-blocking improvements, or "none">

### Strengths
- <what the auditor said looked solid, or "none stated">

## Coordinator Response

### Agree
<what you agree with and why>

### Change
<what you think should change as a result>

### Disagree
<what you disagree with and why>

## Audit Outcome
- <keep as-is | patch now | request second auditor | stop because blocked>
- <brief reason>

## Decision Points For User
- <keep as-is / patch now / save retained report / request a second auditor / etc.>
