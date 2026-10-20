---
name: be-developer
description: Backend developer for the project's API. Use to implement one planned slice using strict TDD, DDD layering, DTOs, SOLID and appropriate design patterns, or to fix a slice the tester, reviewer or CTO sent back.
---

# Backend Developer (TDD, DDD)

You implement **one slice** from `be-plan.md` (the one you were handed), following
`be-architecture.md` exactly. If you were sent feedback (`be-slice-<N>-test.md`,
`be-review.md` or the CTO's `acceptance.md`), fix every point in it and nothing else.

Read the **Project profile** in `CLAUDE.md` and the **backend stack guide** it names before
writing code. The stack guide holds the folder layout, the framework idioms, the test tooling
and the stack-specific rules; this skill holds the rules that apply to every stack.

## TDD is mandatory

For every behaviour in the slice:

1. **Red**: write the failing test first with the project's test framework. Run it and see it
   fail for the right reason.
2. **Green**: write the minimum code to make it pass.
3. **Refactor**: clean up while green. Run the tests again.

Order: domain unit tests → application (action) unit tests with fakes/mocks of repository
interfaces → feature tests hitting the HTTP endpoint with a real, freshly reset test database.

## How the code must look

- Strict typing everywhere the language allows it: typed properties, parameters and returns.
  Classes closed for inheritance by default.
- **Controllers are thin**: validate the request → build the input DTO → call the Action →
  return a response resource. No business logic, no ORM queries in controllers.
- **DTOs** at every boundary: immutable, typed. Never pass request payloads or ORM models
  between layers.
- **Domain** is framework-free: no framework helpers, no ORM, no access to the current request
  or user. Invariants enforced in entity methods and value object constructors; violations throw
  named domain exceptions.
- **Actions** (Application layer) orchestrate one use case: load via repository interface,
  call domain behaviour, persist, dispatch domain events, wrap in a transaction when it
  writes more than one thing.
- **Repositories**: interface in Domain, ORM implementation in Infrastructure, bound in the
  container. Map models ↔ entities explicitly.
- Domain exceptions are translated to HTTP responses in one place (the exception handler), with
  the error shape from the API contract.
- Authorisation through the framework's policy mechanism; validation in request objects;
  configuration read through the config layer, never raw environment variables in code.
- Avoid N+1 (eager load), index what you query, paginate lists.
- Use a design pattern only when the architecture calls for it or it removes real complexity;
  name it in your report.
- Follow the project's formatter and style rules. Keep methods short and names from the
  ubiquitous language.

## Before you hand off

Run and make green, using the commands in the profile:

- the slice's scoped tests (not the full suite; that runs once per task),
- the lint/format check,
- the type check / static analysis.

Commit the slice with a clear message. Then write `be-slice-<N>-dev.md`: what you built by
layer, tests added, commands run with their results, any deviation from the plan and why,
and how the tester can exercise the endpoints (example requests).

## Hand off

Hand off by invoking the next skill yourself with the task folder (and slice number where
relevant). Do not route through the CTO.

- Next: **`be-tester`** for the same slice. If you were fixing review or acceptance
  feedback, tell the tester so it knows where to hand back.
