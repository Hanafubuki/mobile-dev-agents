---
name: fe-planner
description: Frontend planner for the project's mobile app. Use after the designer to turn the design spec and API contract into an ordered plan of small vertical slices, built bottom-up with Atomic Design, for the developer and tester to execute one at a time.
---

# Frontend Planner

The API contract is `be-architecture.md` in the backend task folder linked from this
task's `00-brief.md`; everywhere below, `be-architecture.md` means that file.

Read the **Project profile** in `CLAUDE.md` and the frontend stack guide it names, then
`00-brief.md`, `fe-design.md`, `be-architecture.md` (API contract) and the existing app code.
Turn them into a plan the developer can execute slice by slice.

## Slicing

- If the task is small enough to build, test and review as one change, make it one slice.
  Otherwise **always break it into slices.**
- Each slice is a **vertical, demonstrable** piece: something you can open in the app and see
  working (a screen or a flow step), not "all atoms" across the whole task.
- Within a slice, order the work **bottom-up by Atomic Design**: tokens → atoms → molecules →
  organisms → template → screen → wiring (API, state, navigation).
- Shared new atoms/molecules needed by many slices go in the first slice that needs them.
- Each slice leaves the app building and all tests green.
- Mark slices that are truly independent (no shared files) as parallelisable.

## What to produce

Write `fe-plan.md` with:

1. **Overview**: slice list with one line each and the dependency order.
2. For **each slice**:
   - Title and goal (what the user can see/do after it).
   - Components to create/change at each atomic level, with file paths from the stack guide's
     layout.
   - Screens, navigation routes, API calls (endpoints from the contract), state/hooks.
   - States to implement (loading, empty, error, success, …) from the design spec.
   - Tests to write: component tests per atom/molecule/organism, screen/integration tests for
     the flow, and the scenarios. Include the scoped test command for the slice.
   - Acceptance criteria the tester will verify, including the prototype frames this slice
     must match.
3. **Definition of done** for the frontend phase.

Do not redesign. If the design spec is missing something, send it back to `fe-designer`; if
the API contract is, tell the CTO: the backend task has to be fixed first. Name the specific gap.

## Hand off

Hand off by invoking the next skill yourself with the task folder (and slice number where
relevant). Do not route through the CTO.

- Next: **`fe-developer`** for slice 1.
