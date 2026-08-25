# PHASE4_SCORECARD — comparative evidence, regression intelligence, anti-gaming

Graded by Ox Alpha with cited evidence. 2026-08-25, Phase 4 close.

| # | Category | Grade | Evidence |
|---|----------|-------|----------|
| 1 | Benchmark fairness | 9 | Identical prompt per arm; baseline explicitly invited to leave successor notes (same persistence opportunity); scorer blind to arm; defects unnamed in prompts; distraction issue unscored (benchmarks/PROTOCOL.md) |
| 2 | Benchmark reproducibility | 9 | Generators deterministic; repeated scorer runs byte-identical (engine-recorded evidence E2, exit 0); unsolved fixtures score 0.0 deterministically; `score_all.py` aggregate exit codes CI-usable |
| 3 | Benchmark difficulty | 9 | M2 mixes test-covered and inspection-only defects (injection, doc/impl mismatch, `limit` feature); test-green alone scores 3/5; interruption modifier defined; distraction present |
| 4 | Deterministic scoring | 9 | Scorers execute behavior (AST + subprocess + DB isolation), never read agent claims; verified across M1/M2 solved+unsolved |
| 5 | False-completion resistance | 9 | Scripted attacks all fail closed: stale evidence, unrelated-commit staleness, restore-to-revive, forged exits (caught by `verify --rerun`), deleted regression memory (advisory only), trivial commands (doctor flags; scorer outcome-based). Engine refused my real completion twice during Phase 3 and once here |
| 6 | Interruption/recovery measurement | 9 | Interruption modifier in protocol; deliberate interruption performed on this Phase 4 mission — resume brief alone reoriented the session (1/4 gates → exact remaining criteria) |
| 7 | Regression retrieval precision | 9 | Unrelated records stay silent (tested); guarded-path match required for high scores; cap 5; live demo: auth record surfaced only for auth paths |
| 8 | Regression retrieval recall | 8 | Path/area/keyword signals cover recorded history; semantic similarity (e.g., "auth" vs "login") is not matched — documented future work; recall on recorded fields is complete by construction |
| 9 | Regression explainability | 9 | Every surfaced match prints WHY (matched guard/area/keyword) plus rerun guard — tested |
| 10 | Regression integration | 9 | Auto-surfaced in `status`, `next`, `resume` (tested for all three); explicit `regressions-for` query; no manual recall needed |
| 11 | Evidence/regression coupling | 8 | Surfaced regressions carry their guard command as a suggested re-verification; deliberately NOT mandatory (conservative — weak matches must not create impossible gates), documented |
| 12 | Performance | 10→9 | 2000 regressions + 500 evidence: status 0.11s, lookup 0.07s, resume 0.10s (asserted < 2s in test); checkpoint pruning caps growth; 5MB state guard |
| 13 | Security | 9 | New attack surface covered: regression records redacted+clipped (test: ghp_ token → [REDACTED]); matching is read-only; forged evidence detected by re-execution; malicious filenames only used for matching, never written |
| 14 | Dogfood quality | 9 | Phase 4 managed by the engine itself: 4 criteria, evidence via real commands (including one honest failure when I scored the wrong fixture), archive of Phase 3 mission, deliberate interruption + resume, checkpoints at transitions |
| 15 | Real-world usefulness | 8 | Engine now prevents the two dominant long-mission failures measurably (false completion, context loss) and proactively surfaces failure history. Still gated on external A/B for the comparative claim |
| 16 | Comparative proof strength | 6 | Harness fully ready and self-validated; a true same-agent A/B requires running an external agent in both arms — genuinely outside this repository's execution context. Protocol is reproducible by anyone; no comparative number is claimed |
| 17 | Product differentiation | 9 | Explainable regression auto-surfacing + re-executable evidence + outcome-scored benchmarks is a combination I cannot find in comparable stdlib-only agent tooling; every claim is evidence-linked |

## Honest summary

The comparative question — "does Aegis make an agent better?" — now has a
fair, reproducible, attack-tested instrument and two validated missions. The
instrument itself caught real defects on both sides (engine: forged evidence
path; scorer: DB pollution, stale contract). What remains is running an
external agent in both arms; everything else is done.
