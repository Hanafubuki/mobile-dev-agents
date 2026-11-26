# LangGraph feature controller

This runner executes one feature ticket using the existing project role skills.
The graph controls role order, per-slice development and testing, cross-stack
verification, and a two-repair budget per failing gate. A SQLite checkpoint
stores the stage queue, evidence references, attempts, and role results.
Intake pauses for approval. A blocked stage pauses for retry or cancellation.

## Run a feature

Use Python 3.12 and a prepared application checkout containing `CLAUDE.md` and the
repository's `.claude` folder. Use a dedicated checkout for each run and one
controller process per thread. Keep the SQLite file outside the checkout.
The bundled adapter requires an authenticated Claude Code CLI and project
permissions for the actions of each role.

```sh
python3.12 -m venv .venv
.venv/bin/pip install -r orchestration/requirements.txt

adapter='["python3","/absolute/path/to/mobile-dev-agents/orchestration/claude_adapter.py"]'
.venv/bin/python orchestration/run.py --db /tmp/mobile-dev.sqlite --thread directory \
  --adapter "$adapter" start --workspace /absolute/path/to/app \
  --ticket "Add the staff directory" --scope both --api-scope changed

.venv/bin/python orchestration/run.py --db /tmp/mobile-dev.sqlite --thread directory \
  --adapter "$adapter" resume approve
```

Use `resume retry` after resolving a blocked prerequisite. Use `resume continue`
to continue a saved stage after a controller process crash. Use `resume cancel`
at a pending interrupt. Retrying a blocker preserves the repair budget.
For UI-only work, start with `--scope frontend --api-scope none`.
For mobile changes using an existing API, use `--api-scope existing`.

A custom adapter can replace the bundled CLI adapter. It receives a JSON request
on stdin from the application directory and returns one JSON object on stdout.
Requests contain the role, scope, slice ID, ticket, prior result, intake
artifacts, and request ID. A response must supply `status` as `pass`, `fail`, or
`blocked`. Planner passes need ordered `slices`. An integration failure should
supply `owner` as `backend`, `frontend`, or `contract`. Record reasons and evidence
paths as `reason` and `artifacts`. Keep the same adapter and checkout when resuming.

The controller uses the role's reported result for routing. Application edits and
the SQLite checkpoint are separate writes. An interrupted stage may execute
again with the same request ID. Adapters should reconcile existing artifacts and
edits before repeating work, and use the request ID to deduplicate side effects.
The bundled adapter asks Claude Code to reconcile its work and does not enforce
transactional application writes. This runner handles one feature per thread.
Use the skill workflow's prototype intake to split a larger prototype into
individual feature tickets.

## Verify the controller

```sh
.venv/bin/python -m unittest discover -s orchestration -v
```

These tests use scripted role results and a real SQLite checkpoint. They cover
approval, ordered slices, backend repair after a cross-stack failure, local-only
routing, manual resume, and repair-budget exhaustion.
