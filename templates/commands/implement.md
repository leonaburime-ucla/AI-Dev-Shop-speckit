You are the Coordinator dispatching the implementation sequence.

$ARGUMENTS

The tasks.md is ready. Run the implementation pipeline:

1. Verify prerequisites: approved spec (hash recorded), approved ADR, tasks.md present in `<SHOP_ROOT>/specs/<NNN>-<feature-name>/`.
2. Dispatch **TDD Agent** with:
   - Spec: `<SHOP_ROOT>/specs/<NNN>-<feature-name>/feature.spec.md` (full content + hash)
   - ADR: `<SHOP_ROOT>/specs/<NNN>-<feature-name>/adr.md`
   - Tasks: `<SHOP_ROOT>/specs/<NNN>-<feature-name>/tasks.md`
   - Skill: `<SHOP_ROOT>/skills/test-design/SKILL.md`
   - Directive: Write failing tests for all P1 ACs before any implementation starts. Certify against spec hash.
   - Output: test certification at `<SHOP_ROOT>/specs/<NNN>-<feature-name>/test-certification.md`
3. After TDD certification, dispatch **Programmer Agent** with:
   - Spec hash (must match TDD certification hash)
   - Certified test names and which ACs they cover
   - ADR constraints
   - Relevant `<SHOP_ROOT>/project-knowledge/project_memory.md` entries
4. After each Programmer cycle, dispatch **TestRunner Agent**. Report pass/fail counts and failure clusters.
5. Advance to Code Review when ≥90% acceptance tests pass (calibrate threshold to risk — payment/auth systems may require 100%).
6. If the same tests fail after 3 cycles: escalate to human. This signals a spec gap or architecture mismatch, not a code problem.

Output each cycle: convergence percentage, failing clusters, iteration budget remaining, current stage.
