# Evaluate feature delivery

The harness compares a single coding-agent session with the CTO skill pipeline. It
gives both modes the same ticket and application commit, saves their patches, and
runs independent acceptance and regression commands in fresh checkouts. It records
agent status, pass rates, regressions, wall time and optional cost.

## Run it

Requires Python 3.10+ and Git. Check the harness with:

```sh
python3 evaluation/self_test.py
```

For an agent experiment, provide a local Laravel/Expo repository, two adapter
commands and evaluator-owned checks. Start with [the example configuration](example.json).
Use absolute paths for the repository, adapter scripts and external checks.

```sh
python3 evaluation/run.py /absolute/path/config.json --output /tmp/mobile-eval-01 --repetitions 3
```

Each adapter runs with the candidate checkout as its working directory. It reads
the ticket from stdin, edits the checkout, and exits successfully when it has
finished. The pipeline prompt begins with `/cto`. The pipeline adapter must invoke
the CTO skill with that ticket and make the project profile and skills available
to its session. The single-agent adapter should run the same model and tools in a
fresh session without skill routing. Use the same dependency setup, time limits
and permissions for both modes. Keep setup-only files out of the submitted diff,
for example by supplying the role files in separate runner configuration or
cleaning up files added solely for setup. An adapter can write
`.evaluation-metrics.json` with a numeric `cost_usd` for the whole run.

The acceptance command must fail on the base because the feature is absent. The
regression command must pass on the base. Verify the acceptance failure reason in
the saved base log before interpreting results. Each check must prepare its own
dependencies and test data. Keep check code outside the candidate repository
and avoid exposing it to agents. Separate checkouts prevent accidental sharing.
For a blind benchmark, run the coding adapter in a sandbox that can see only the
candidate and its required tools. Run scoring separately in a disposable, restricted
environment because application code and repository test commands execute there.

The output includes `report.json`, agent and check logs, and the patch for each
run. Compare paired results by ticket and repetition. Report the number of passes,
regressions, timeouts and costs observed. The first run is a smoke test of the
experiment. Repeated runs across several tickets are needed to estimate variation.

## Suggested Laravel/Expo tickets

| Ticket | Independent acceptance check |
| --- | --- |
| Keep the payroll dashboard's date filter when navigating back | Navigate away and back after changing the filter. Verify selection survives, including offline, and no new API call occurs. |
| Add monthly staff arrivals by cost center | Seed overlapping contracts for one person and verify a single arrival for that month and cost center. Check separate centers independently. |
| Add a mobile staff directory with cursor pagination | Exercise the Expo screen against Laravel. Verify page two, empty, and retry states, and assert the displayed data comes from the API. |

For regression, keep an existing case on the same path, such as default date
filters, another staff metric, or preexisting directory behavior. The example
tickets and adapter paths are templates for your target app. The self-test uses
a small Git fixture and verifies the runner without making model calls.

## Learn from a failed run

Run the same benchmark before and after a versioned skill or workflow change.
Keep the cases, model, check commands, source commits, and repetitions fixed. Use
one failed check and its log to explain the change. The comparison pairs results
by case, commit, mode, and attempt, then points to fixed, recurring, regressed,
and inconclusive outcomes.

```sh
python3 evaluation/compare.py before/report.json after/report.json
python3 evaluation/learning_demo.py /tmp/mobile-learning-demo
```

The deterministic demo reproduces a staff directory whose mobile client reads
`items` while its backend returns `staff`. The workflow variant models the
verifier's fix by correcting the client, then reruns the unchanged acceptance
and regression checks. The unchanged single-agent variant is the control.
This exercises the feedback and comparison loop with scripted adapters.
Use real agent adapters and an independently authored Laravel/Expo suite to
measure the impact of the skill itself.
