# mobile-dev-agents

A ready-made team of Claude Code agents that builds a mobile app and its backend API from a
task or a prototype. Drop it into a repository, fill in one profile, and hand a prototype to the
`cto` skill: it breaks the work into backend and frontend tasks, and a chain of specialised
roles designs, plans, builds, tests and reviews each one until the CTO accepts it.

The agents are written as [Claude Code skills](https://docs.claude.com/en/docs/claude-code/skills).
They are stack-agnostic: the skills hold the engineering rules, and a small **stack guide** maps
those rules to your framework. Guides for **Laravel** and **React Native / Expo** are included.

## What's inside

```
CLAUDE.md                         Project template: the Project profile every skill reads
.claude/
  skills/
    cto/                          Entry point: intake and final acceptance
    be-architect/                 Backend: domain model, layering, DTOs, API contract
    be-planner/                   Backend: ordered vertical slices with tests
    be-developer/                 Backend: implements one slice with TDD
    be-tester/                    Backend: verifies one slice independently
    be-reviewer/                  Backend: reviews the whole change
    fe-designer/                  Frontend: design spec from the prototype
    fe-planner/                   Frontend: ordered vertical slices, bottom-up Atomic Design
    fe-developer/                 Frontend: implements one slice
    fe-tester/                    Frontend: verifies one slice independently
    fe-reviewer/                  Frontend: reviews the whole change
  stacks/
    README.md                     How to add a stack guide
    backend/laravel.md            Laravel layout, idioms, tests, commands
    frontend/react-native.md      React Native layout, idioms, tests, commands
```

## How it works

### One entry point

You only ever talk to the **CTO** (`/cto`, or ask Claude to use the cto skill). You give it one
of two things:

- **A task**, such as "Let users reset their password".
- **A prototype**: HTML, a Figma link, screenshots or a reference doc for a whole app or flow.

The CTO never builds anything itself. It does **intake** at the start and **acceptance** at the
end.

### Intake

1. A prototype is split into **feature tasks**, each one user-facing flow that can be built and
   accepted on its own (for example "Sign up and log in", "Home feed"), ordered by dependency.
   The list goes in `docs/prototypes/<prototype>/tasks.md` with a status per task.
2. Each feature becomes a **backend task** and a **frontend task** when both sides have work.
3. Each task gets a folder in `docs/tasks/<YYYY-MM-DD>-<slug>-backend/` or `-frontend/` with a
   `00-brief.md`: goal, user stories, numbered acceptance criteria, design references, side and
   dependencies, and what is out of scope.

### The pipeline

The backend task always runs first, so the API exists before the app is built against it. The
frontend task starts only once its backend task is accepted.

```
Backend:   be-architect → be-planner → per slice: be-developer → be-tester → be-reviewer → cto
Frontend:  fe-designer  → fe-planner → per slice: fe-developer → fe-tester → fe-reviewer → cto
```

Each role invokes the next one directly; nothing routes back through the CTO until the reviewer
approves.

| Role | Writes | Does |
| --- | --- | --- |
| `be-architect` | `be-architecture.md` | Bounded contexts, aggregates, use cases, DTOs, persistence and the exact **API contract** the app consumes |
| `be-planner` | `be-plan.md` | Splits the work into small vertical slices, each with its TDD test list and acceptance criteria |
| `be-developer` | `be-slice-N-dev.md` | Builds one slice test-first, following the architecture |
| `be-tester` | `be-slice-N-test.md` | Verifies the slice against its criteria and the contract, adds missing tests, PASS/FAIL |
| `be-reviewer` | `be-review.md` | Reviews the whole diff for correctness, DDD, security and performance |
| `fe-designer` | `fe-design.md` | Tokens, Atomic Design component inventory, every screen state, interactions, accessibility |
| `fe-planner` | `fe-plan.md` | Vertical slices built bottom-up: tokens → atoms → … → screen → wiring |
| `fe-developer` | `fe-slice-N-dev.md` | Builds one slice, faithful to the prototype and the contract |
| `fe-tester` | `fe-slice-N-test.md` | Verifies behaviour, states, API use and visual match, PASS/FAIL |
| `fe-reviewer` | `fe-review.md` | Reviews the whole diff for correctness, Atomic Design, fidelity, accessibility |

Feedback loops are built in. A failed slice goes back to the developer; requested review changes
go to the developer and return through the tester; a rejected acceptance goes to the developer
and runs through the pipeline again.

### Acceptance

When a reviewer approves, the CTO verifies instead of trusting the reports: it runs the full
suites, calls every endpoint in the contract, runs the app against the real backend, screenshots
every screen and state next to the prototype, and ticks every acceptance criterion with
evidence. It writes `acceptance.md` with **ACCEPTED** or **REJECTED**. Accepting a backend task
starts its frontend task.

### Standards

- **Backend**: DDD layering (Domain / Application / Infrastructure / Interface), DTOs at every
  boundary, TDD, SOLID, strict types, thin controllers.
- **Frontend**: Atomic Design (atoms → molecules → organisms → templates → screens), strict
  typing, theme tokens only, every screen state (loading, empty, error, offline…), faithful to
  the prototype, accessible.

A task that breaks these is rejected even if it works.

### Speed

Per slice, the roles run only fast checks: the slice's tests, lint and type check. The heavy
checks (full suites, live API calls, the real backend, screenshots against the prototype) run
once per completed task. Independent features can run in parallel in separate worktrees.

## Adopting it in a project

1. **Copy the files** into the root of your app's repository:

   ```sh
   git clone https://github.com/Hanafubuki/mobile-dev-agents /tmp/mobile-dev-agents
   cp -r /tmp/mobile-dev-agents/.claude .
   cp /tmp/mobile-dev-agents/CLAUDE.md .   # or merge it into your existing CLAUDE.md
   ```

2. **Fill in the Project profile** in `CLAUDE.md`. Replace every `{{PLACEHOLDER}}`: app name,
   where the mobile app and backend live, which stack guides apply, where prototypes are kept,
   the phone widths you support, and the commands for scoped tests, full tests, lint, type check
   and running locally. The skills read nothing project-specific from anywhere else.

3. **Pick or write the stack guides.** If you use Laravel and React Native, point the profile at
   the included guides. For anything else (NestJS, Django, Rails, Go; Flutter, SwiftUI, Kotlin),
   copy the closest guide into `.claude/stacks/backend/` or `.claude/stacks/frontend/` and adapt
   its five sections, as described in [`.claude/stacks/README.md`](.claude/stacks/README.md).

4. **Add project rules** to the "Project-specific rules" section of `CLAUDE.md`, or delete it.

5. **Start work** by giving the CTO a task or a prototype:

   ```
   /cto Build the app from the prototype in docs/prototypes/onboarding/
   ```

### Project without a backend (or without an app)

The CTO only creates a task for a side that has work. For an app-only project, leave the backend
rows of the profile as `n/a`; frontend tasks then start at `fe-designer` straight away.

## Customising

- **Roles**: each skill is a single `SKILL.md`. Edit the checklists, the outputs or the handoffs
  to match how your team works. Keep the handoff file names consistent, since the next role reads
  them.
- **Standards**: change the Non-negotiables in `CLAUDE.md` and the matching sections in the
  skills together.
- **Expo projects**: enabling the Expo plugin for Claude Code in your mobile folder's
  `.claude/settings.json` gives the frontend roles Expo-specific help.

## Origin

These agents were extracted from a production React Native + Laravel app, where they built the
app feature by feature from an HTML prototype, and then made generic so any mobile project can use
them.
