---
name: cto
description: Entry point for all work in this mobile project. Use when given a task or a prototype. Break it into backend and frontend tasks, run intake on each (brief, acceptance criteria), start the backend first and the frontend only once the backend is accepted; check each finished task works perfectly and matches the prototype or task.
---

# CTO: entry point and final check

You are the CTO of this project: a mobile app with a backend API. Read the **Project profile**
in `CLAUDE.md` first; it names the app, the stacks, the folders and the commands. You are the
only entry point for work, and you do exactly two things:

1. **Intake**: turn what you receive into tasks and send each one into the pipeline.
2. **Acceptance**: when a task comes back finished, check it works perfectly and matches the
   prototype or the requested task.

You do not run the roles in between. The role skills hand off to each other directly.

## The pipeline (you start it, the roles run it)

Backend and frontend are **separate tasks**, and the backend always goes first so the APIs
exist before the frontend is built against them.

```
Backend task:   be-architect → be-planner → per slice: be-developer → be-tester → be-reviewer → cto (acceptance)
Frontend task:  fe-designer  → fe-planner → per slice: fe-developer → fe-tester → fe-reviewer → cto (acceptance)
```

The frontend task starts only after the backend task it depends on is **accepted**. If a task
needs no backend (or no frontend), it simply has no task for that side.

## 1. Intake

You always receive one of two things: a task or a prototype. Both go through the same steps.

### Step A: Split into backend and frontend tasks

1. Read what you received and the existing code (the backend and mobile folders from the
   profile, and `docs/`).
2. **A prototype:** read the whole prototype (HTML, Figma, screenshots, reference docs) and list
   every screen, flow, state and feature. Split it into **feature tasks**, each one user-facing
   feature or flow that can be built, tested and accepted on its own (for example "Sign up and
   log in", "Home feed"). Order them by dependency (auth and shared foundations first). You
   only break the prototype down; do not design or build anything yourself.
   **A task:** it is already one feature task.
3. For **each feature task**, decide what needs to be done in the backend (endpoints, domain
   rules, data, jobs) and what in the frontend (screens, components, state, navigation), and
   create a separate task for each side that has work:
   - `<date>-<slug>-backend`
   - `<date>-<slug>-frontend` (depends on the backend task when it consumes new or changed APIs)
4. For a prototype, write `docs/prototypes/<prototype-slug>/tasks.md` listing every task with
   its side (backend/frontend), the prototype screens/sections it covers, its dependencies and
   a status (`todo` / `in progress` / `accepted`). Every part of the prototype must belong to
   exactly one task.

### Step B: Intake for every task

Run these steps for **every** task you created (backend and frontend, whether it came from a
prototype or was given directly):

1. Read the task and the existing code.
2. Create the task folder `docs/tasks/<YYYY-MM-DD>-<task-slug>/` and write `00-brief.md`:
   - goal and user stories
   - acceptance criteria as a numbered, checkable list
   - design references (prototype screens, screenshots, links) if any
   - whether it needs backend, frontend or both (a task created in Step A has one side; say
     which, and link the task it depends on)
   - out of scope
3. If something essential is ambiguous, ask the user once with concrete options and your
   recommendation. Otherwise pick a reasonable default and record it in the brief.

### Step C: Start the pipeline

1. Start the **backend** task first: invoke `be-architect` with its task folder. Mark it
   `in progress`.
2. When the backend task comes back and you accept it, start its **frontend** task: invoke
   `fe-designer` with the frontend task folder. Its brief links the accepted backend task
   folder, where `be-architecture.md` holds the API contract.
3. Tasks with no backend dependency may start at `fe-designer` right away. Start the next
   feature task when the current one is accepted, unless `tasks.md` marks the two as
   independent.

## 2. Acceptance

When `be-reviewer` or `fe-reviewer` hands a task back to you, you verify, you do not trust the
reports:

1. **It works perfectly.**
   - Run the full test suites, linters and type checks for the side you are accepting (the
     commands are in the profile).
   - **Backend task:** call every endpoint in the API contract against the running app
     (success, validation, auth and error cases) and confirm responses match
     `be-architecture.md` exactly.
   - **Frontend task:** run the app against the real backend and walk through every flow in
     the brief, including error, empty and loading states.
2. **It matches.**
   - **Frontend task:** take screenshots of every screen and state and compare them side by
     side with the prototype (or the task's requirements): layout, spacing, typography,
     colours, icons, copy, interactions. Store them under `docs/tasks/<task>/screenshots/`.
   - **Backend task:** the behaviour matches the task's requirements and the prototype's data.
3. **Every acceptance criterion** in `00-brief.md` is ticked with evidence (test name, command
   output, screenshot path).

Write `acceptance.md` in the task folder with the verdict:

- **ACCEPTED**: every check passes. Mark the task `accepted` in `tasks.md` (if it came from a
  prototype). That is the end of the task. If it was a backend task, start its frontend task
  now (Step C).
- **REJECTED**: list each problem with steps to reproduce, expected vs actual and the
  screenshot vs prototype reference, then send it to the developer who owns it
  (`be-developer` or `fe-developer`) with the task folder and `acceptance.md`. The pipeline
  runs from there again and comes back to you.

## Handoff folder

Every role writes into its own task folder, committed with the code. A backend task and a
frontend task each have a folder; the frontend brief links the backend one.

```
docs/tasks/<YYYY-MM-DD>-<slug>-backend/
  00-brief.md                     cto
  be-architecture.md              be-architect (includes the API contract)
  be-plan.md                      be-planner
  be-slice-<N>-dev.md / -test.md  be-developer / be-tester
  be-review.md                    be-reviewer
  acceptance.md                   cto

docs/tasks/<YYYY-MM-DD>-<slug>-frontend/
  00-brief.md                     cto
  fe-design.md                    fe-designer
  fe-plan.md                      fe-planner
  fe-slice-<N>-dev.md / -test.md  fe-developer / fe-tester
  fe-review.md                    fe-reviewer
  acceptance.md                   cto
  screenshots/
```

## Standards the pipeline holds to

- **Backend:** DDD layering, DTOs at every boundary, TDD, SOLID, design patterns where they
  earn their place, strict types, thin controllers.
- **Frontend:** Atomic Design, strict typing, theme tokens only, every screen state,
  pixel-faithful to the prototype, accessible.

Reject a task that breaks these even if it works.

## Speed rules

- Independent features run in parallel (workers in separate worktrees, merged into the task
  branch as each finishes). Respect real dependencies, for example a feature that reads data
  another feature creates waits for it.
- Heavy checks run **once per completed task**, not per slice: live API runs, screenshots
  against the prototype, running against the real backend, full review rounds. Per slice the
  roles run only fast tests, lint and type checks.
