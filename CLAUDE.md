# {{APP_NAME}}

{{One line about the product, e.g. "React Native mobile app with a Laravel backend."}}

<!--
  This file comes from mobile-dev-agents. Replace every {{PLACEHOLDER}} once when you adopt the
  agents, then delete this comment. The role skills read the "Project profile" below for the
  stack, paths and commands, so keep it accurate as the project changes.
-->

## Project profile

Every role skill reads this section before it starts. It is the only place the skills learn
the project's stack, paths and commands.

| Key | Value |
| --- | --- |
| App name | {{APP_NAME}} |
| Mobile app | {{e.g. React Native (Expo SDK 52), TypeScript}} in `{{mobile/}}` |
| Backend | {{e.g. Laravel 11, PHP 8.3, MySQL}} in `{{backend/}}` |
| Backend stack guide | `.claude/stacks/backend/{{laravel}}.md` |
| Frontend stack guide | `.claude/stacks/frontend/{{react-native}}.md` |
| Prototypes | `{{docs/prototypes/}}` (HTML, Figma links, screenshots) |
| Task handoff folders | `docs/tasks/` |
| Supported phones | {{320}} to {{440}} pt wide (smallest to largest phone you support) |
| Platforms | {{iOS and Android}} |

### Commands

Run from the folder named in the profile. Per slice, run only the scoped commands; run the
full suites once when the whole task is complete.

| Purpose | Backend | Mobile |
| --- | --- | --- |
| Tests for one slice | `{{php artisan test --filter=<Name>}}` | `{{npx jest <paths>}}` |
| Full test suite | `{{php artisan test}}` | `{{npm test}}` |
| Lint / format check | `{{vendor/bin/pint --test}}` | `{{npm run lint}}` |
| Type check / static analysis | `{{vendor/bin/phpstan analyse}}` | `{{npx tsc --noEmit}}` |
| Run locally | `{{php artisan serve}}` | `{{npx expo start}}` |
| E2E (if any) | n/a | `{{maestro test .maestro/}}` |
| Screenshots | n/a | `{{how to capture: simulator, Expo web + Playwright, Maestro…}}` |

## How work gets done

The `cto` skill (`.claude/skills/cto/SKILL.md`) is the only entry point. It receives a task or a
prototype and breaks it into feature tasks (a prototype is only broken down, never built by the
CTO). For each feature it creates a separate backend task and frontend task when needed, and
runs intake on each one: task folder and `00-brief.md` with goal, user stories, numbered
acceptance criteria, design references, backend/frontend and out of scope.

A frontend task that depends on a changed API starts once its backend task is accepted.
Use the existing API reference for unchanged APIs, or declare that the change is local-only.

- Backend: `be-architect` → `be-planner` → per slice `be-developer` → `be-tester` → `be-reviewer`
- Frontend: `fe-designer` → `fe-planner` → per slice `fe-developer` → `fe-tester` → `fe-reviewer`

The role skills hand off to each other directly and do not route back through the CTO. When a
task finishes, the CTO checks that it works perfectly and matches the prototype or requested
task, and that is the end.

Handoff documents live in `docs/tasks/<YYYY-MM-DD>-<slug>-backend/` and `-frontend/`.

## Non-negotiables

- Backend: DDD layering (Domain / Application / Infrastructure / Interface), DTOs at every
  boundary, TDD, SOLID, strict types, thin controllers.
- Frontend: Atomic Design (atoms → molecules → organisms → templates → screens), strict typing,
  theme tokens only, every screen state implemented, faithful to the prototype.

## Speed rules

- Independent features run in parallel (separate worktrees, merged into the task branch as each
  finishes). Respect real dependencies between features.
- Per slice, run only the fast checks for that slice: its tests, lint and type check. Live API
  runs, screenshots against the prototype, running against the real backend and the full test
  suites run at CTO acceptance for the reviewed source revision.

## Project-specific rules

{{Anything the agents must always follow in this project: naming, i18n, analytics, feature
flags, release process, design-system quirks. Delete this section if there is nothing.}}

## Run checkpoints and retries

Keep one `run.md` in each task folder. The active role records the task, current role,
slice (if any), attempt, source commit, status, and last evidence path. Before invoking
the next role, record that role and slice as pending. The receiving role marks the
stage running before acting. When a role cannot invoke its successor in this session,
leave that successor pending and report how to resume. Append transitions with timestamps and retain prior outcomes.
Publish the checkpoint with the task work so a resumed session can find it.

Allow the initial implementation and up to two repair attempts per slice or task-level
review/acceptance gate. Track the budget against the original failing gate through
Developer, Tester and Reviewer handoffs so it cannot reset during a repair. A failed check with actionable evidence goes through the normal
repair handoff and consumes one repair attempt. A missing prerequisite, unavailable
runner, or exhausted repair budget sets `BLOCKED`. Record the failing stage, reason,
evidence and prerequisite for resuming, then stop the chain and tell the user. Keep
unrelated tasks independent. On resume, check the current diff and source revision
before reusing evidence. An interrupted running stage must reconcile its existing
changes and reports before repeating work.
