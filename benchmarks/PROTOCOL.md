# Aegis benchmark protocol

Question: **does the same coding agent perform materially better on a
long-horizon mission when Aegis is in use?**

The harness is deterministic; only the agent varies.

## Fixture

`python3 benchmarks/generate_fixture.py <dir>` produces a broken "notes app"
with five planted defects (failing test, broken import, runtime crash, eval()
security defect, stale documentation). `python3 benchmarks/score.py <dir>`
objectively checks each defect and prints JSON — it is the judge, never the
agent.

## Metrics

| Metric | Source |
|---|---|
| defects_fixed / 5 | score.py |
| tests_pass | score.py |
| false completion claims | agent declares done while score < 5/5 |
| rediscovery events | agent re-inspecting an already-fixed defect (manual tally from transcript) |
| recovery steps after interruption | commands needed after a forced session break |
| evidence quality | gates backed by executed commands vs claims |

## A/B procedure

1. `generate_fixture.py run-a` → git init → commit.
2. Give the agent the task prompt: *"Fix this project so the test suite
   passes and every documented feature is real. Work until done."*
   **Run WITHOUT Aegis.** Record transcript, then `score.py run-a`.
3. `generate_fixture.py run-b` → git init → commit.
4. Same prompt, plus: *"Use the Aegis mission engine
   (`python3 <path>/aegis.py`) to track the mission."* Agent runs
   `aegis init` with one criterion per defect, works via `aegis next`,
   records evidence per fix, checkpoints mid-mission.
5. **Force an interruption** in both runs at the same point (new session).
   Measure recovery steps.
6. `score.py run-b`. Compare all metrics.

## Contamination rules

- Fresh fixture directory per run; identical prompt text.
- The agent must not read `score.py` internals during run-b gating (it may
  run it as a final check — that is legitimate verification).
- Report raw transcripts alongside scores. No cherry-picking.

## Results log

| Date | Run | Agent | Score | False-completion | Notes |
|------|-----|-------|-------|------------------|-------|
| 2026-08-25 | self-run (Ox Alpha as agent, with Aegis) | Ox Alpha | 5/5, tests_pass true | 1 (caught by engine: weak C4/C5 evidence rejected before scorer ran) | infrastructure validated; interruption + resume exercised mid-mission |

The self-run validates the harness end-to-end. A true A/B result requires
running an external agent both ways per the procedure above — until that
happens, no comparative claim is made.
