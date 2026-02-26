# Specification Quality Checklist: <feature-name>

- Feature: FEAT-<NNN>
- Spec: `<user-specified>/<NNN>-<feature-name>/feature.spec.md`
- Created: <ISO-8601 UTC>
- Author: Spec Agent

**Purpose**: Validate spec completeness and quality before Architect dispatch. All items must pass before the spec can be handed off. Failing items must be resolved or escalated to human.

---

## Content Quality

- [ ] No implementation details (no languages, frameworks, APIs, libraries, or infrastructure references)
- [ ] Focused on user value and business needs — written so a non-technical stakeholder understands it
- [ ] All mandatory sections present and completed: Problem, Scope (in/out), Requirements, Acceptance Criteria, Invariants, Edge Cases

## Requirement Completeness

- [ ] Zero `[NEEDS CLARIFICATION]` markers remain in the spec
- [ ] All requirements are testable and unambiguous — no vague qualifiers ("fast", "robust", "intuitive")
- [ ] Success criteria are measurable (include specific metrics: time, counts, rates, percentages)
- [ ] Success criteria are technology-agnostic (no mention of databases, frameworks, or infrastructure)
- [ ] All acceptance scenarios are defined with Given/When/Then format
- [ ] Edge cases are concrete scenarios ("What happens when X?" not "Handle edge cases")
- [ ] Scope is clearly bounded — both in-scope and out-of-scope lists are present
- [ ] External dependencies and assumptions are identified

## Spec Integrity

- [ ] FEAT number assigned and unique (verified against existing `<SHOP_ROOT>/reports/pipeline/` folders)
- [ ] Content hash computed and recorded in header metadata
- [ ] Constitution Compliance table completed — all 8 articles marked COMPLIES / EXCEPTION / N/A
- [ ] Open Questions list is empty, or all remaining questions have an owner and a resolution target date

## Acceptance Criteria Quality

- [ ] Every requirement (REQ-XX) has at least one acceptance criterion
- [ ] Each AC has a priority tag: [P1], [P2], or [P3]
- [ ] P1 ACs are independently testable — each can be verified without other stories being complete
- [ ] No AC requires knowledge of the implementation to evaluate

---

## Validation Results

| Item | Status | Issue Found |
|------|--------|-------------|
| Content Quality | — | |
| Requirement Completeness | — | |
| Spec Integrity | — | |
| AC Quality | — | |

**Overall**: PASS / FAIL — [summary of issues if any]

## Notes

- Mark items complete: change `[ ]` to `[x]`
- Document specific issues found inline
- Items marked FAIL require spec updates before Architect dispatch
- If an item cannot pass after 3 revision attempts, document the blocker and escalate to human
