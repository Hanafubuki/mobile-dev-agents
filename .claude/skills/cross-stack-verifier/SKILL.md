---
name: cross-stack-verifier
description: Verify an API-dependent mobile feature against its real backend after frontend review and before CTO acceptance.
---

# Cross-stack verifier

Read the frontend brief, review, linked backend acceptance (when applicable), and
the API and design references in the brief. Follow the checkpoint and retry rules
in `CLAUDE.md`. Verify the exact reviewed application revision in a test environment
with seeded data and the project's actual frontend and backend. Use an isolated
context when available. Keep application code unchanged during verification.

1. Start the backend and mobile app using the Project profile. Confirm the client
   uses that backend and the intended API version.
2. Map the API-dependent acceptance criteria to real mobile interactions. Exercise
   the happy path and relevant cross-boundary conditions such as empty results,
   pagination, validation, expired sessions, and retry. Check the actual payloads
   and rendered behavior. Use scoped test accounts and avoid recording secrets or
   private data in evidence.
3. Record `cross-stack-verification.md` with source revision(s), environment,
   criterion IDs, expected and observed results, command exit codes, and evidence
   paths. Use `PASS`, `FAIL`, or `BLOCKED`. For failures, identify the likely owner
   (frontend, backend, or contract decision), with evidence and reproduction steps.
   If tooling is missing, record the prerequisite and mark the checkpoint blocked.
4. Hand the report to the CTO. A passing report on the reviewed revision satisfies
   the live integration portion of CTO acceptance. A failed report goes through
   the owning implementation, testing and review stages, then this gate reruns
   against the new revision. Escalate ambiguous ownership to the CTO for triage.

For local-only frontend work, the CTO skips this gate.
