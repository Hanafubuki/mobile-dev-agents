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

The backend task always runs first, so the APIs exist. The frontend task starts only after the
backend task is accepted.

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
  suites run once per completed task, before the review.

## Project-specific rules

{{Anything the agents must always follow in this project: naming, i18n, analytics, feature
flags, release process, design-system quirks. Delete this section if there is nothing.}}
