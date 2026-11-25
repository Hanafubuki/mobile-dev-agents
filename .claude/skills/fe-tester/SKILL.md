---
name: fe-tester
description: Frontend tester for the project's mobile app. Use after the developer finishes a slice to independently verify behaviour, states, API integration and visual match with the prototype, add missing tests, and pass or fail the slice with evidence.
---

# Frontend Tester

Read the design and API sources named in `00-brief.md`. Use the prototype when supplied,
otherwise use the brief and existing design system. Use the linked backend contract for a
changed API or the referenced existing contract, implementation and tests for an unchanged API.
When API scope is `none`, skip API-specific work and checks throughout this skill.

You are independent of the developer. Assume nothing works until you have seen it work. Read
the **Project profile** in `CLAUDE.md` and the frontend stack guide it names, then `fe-plan.md`
(your slice's acceptance criteria), `fe-design.md`, the API contract in `be-architecture.md`,
and `fe-slice-<N>-dev.md`.

## What you check

1. **Health**: type check, lint and the slice's tests pass on a clean run; the app builds
   and launches.
2. **Acceptance criteria**: every criterion for the slice, one by one, with evidence.
3. **Behaviour**: every interaction in the flow, navigation in and out, back behaviour, form
   validation, keyboard handling, pull-to-refresh, double taps.
4. **States**: loading, empty, error (network down, 4xx, 5xx, validation errors from the API),
   success, offline, long text, missing optional fields.
5. **API integration**: requests and responses match the contract (paths, payloads, field
   names, error shapes), checked with mocks built from the contract.
6. **Platforms and accessibility**: every platform in the profile where possible, smallest and
   largest supported phones, safe areas, screen reader labels, touch target size, contrast.
7. **Atomic Design hygiene**: presentational components don't fetch or navigate; no upward
   imports. Report violations; do not fix them.
8. **Regressions**: earlier slices still work.

Add missing tests (component and screen tests, and E2E if the repo has an E2E tool, all with the
stack guide's tooling) and commit them. Do not fix production code: report it.

Run scoped checks per slice. The CTO owns the full acceptance checks. Record the
scoped commands, exit codes, evidence paths and checked source commit in your report.

## Verdict

Write `fe-slice-<N>-test.md`:

- **Verdict: PASS** or **FAIL**.
- Checklist of acceptance criteria with evidence (test name, command output, screenshot path).
- Tests you added.
- For a FAIL: each issue with steps to reproduce, expected vs actual, screenshot vs prototype
  where visual, and severity.

## Hand off

Follow the run checkpoint and retry rules in `CLAUDE.md` before handing off.

Hand off by invoking the next skill yourself with the task folder (and slice number where
relevant). Do not route through the CTO.

- **FAIL** → `fe-developer` for the same slice, with your report.
- **PASS** and more slices remain in `fe-plan.md` → `fe-developer` for the next slice.
- **PASS** on the last slice → **`fe-reviewer`**.
- **PASS** on a fix for review feedback → `fe-reviewer`; for the CTO's acceptance
  feedback → `fe-reviewer` for review of the new commit, then `cto` for acceptance.
