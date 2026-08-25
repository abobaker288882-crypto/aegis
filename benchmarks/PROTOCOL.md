# Aegis benchmark protocol

Question: **does the same coding agent perform materially better on
long-horizon missions when Aegis is in use?**

The harness is deterministic; only the agent varies. The scorer is the judge
and inspects outcomes, never claims.

## Missions

| Mission | Generator | Scorer | Planted issues |
|---|---|---|---|
| M1 notes-app | `generate_fixture.py` | `score.py` | failing test, broken import, runtime crash, eval() security defect, stale doc claim |
| M2 taskapi | `generate_m2.py` | `score_m2.py` | failing test, incomplete feature (ignored `limit`), hidden regression (`None` on empty query), SQL injection via f-string, documented-but-missing endpoint, plus an unscored distraction (risky async TODO) |

Task prompt for both arms (identical):

> Make the test suite pass and make the README truthful. Do not break
> existing behavior. Work until done.

Defect locations are not named. Some defects are covered by the fixture's
tests; others (injection, doc/impl mismatch, `limit`) must be found by
inspection — deliberately mixed so test-green alone cannot score 5/5.

## Interruption modifier

For any mission, the external runner may terminate the agent mid-mission and
start a fresh session. The treatment arm resumes via `aegis resume` (its
durable state is the engine's); the baseline arm is told, in both runs,
"before finishing, leave notes for a successor session" — the baseline gets
the same opportunity to persist state, so the comparison measures the
mechanism, not the courtesy.

## Procedure

1. `python3 benchmarks/generate_m1|generate_m2 run-X/M1|M2` → `git init` →
   commit.
2. Run the agent with the prompt. **Arm A: no Aegis. Arm B: same prompt plus
   "use the Aegis mission engine (`aegis.py`) to track the mission."**
3. Agent writes `COMPLETION.txt` when it believes it is done.
4. Score: `python3 benchmarks/score_all.py run-X` (per-mission JSON +
   aggregate). A `COMPLETION.txt` present while score < 1.0 is recorded as a
   **false completion attempt**.
5. Transcript metrics (tallied by a human from the logs): rediscovery
   events, unnecessary actions, steps to resume after interruption.

## Contamination rules

- Fresh fixture directory per arm; identical prompt text.
- The treatment arm may run the scorers as final verification (legitimate);
  it may not modify them.
- Publish raw transcripts with the numbers.

## Results log

| Date | Run | Agent | Score | False completion | Notes |
|------|-----|-------|-------|------------------|-------|
| 2026-08-25 | M1 self-run (Ox Alpha as agent, with Aegis) | Ox Alpha | 5/5, tests green | 1 — engine rejected my weak C4 evidence command before the scorer ran | interruption + resume exercised |
| 2026-08-25 | M2 self-run (Ox Alpha as agent, with Aegis) | Ox Alpha | 5/5, tests green | 2 — engine refused completion while 4 gates failed; scorer then caught 2 scorer bugs of its own (fixed) | determinism verified by repeat runs |
| 2026-08-25 | M1+M2 aggregate | — | 10/10, exit 0 | — | `score_all.py` validated; unsolved fixtures score 0.0 deterministically |

These are self-runs validating the harness. **No comparative A/B claim is
made** — that requires running an external agent in both arms per the
procedure above.
