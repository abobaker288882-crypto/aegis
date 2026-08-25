# PHASE2_SCORECARD — Aegis product system

Graded by Ox Alpha with cited evidence. Scale 0–10. Final grades:
2026-08-25, Phase 2 close.

| # | Category | Grade | Evidence |
|---|----------|-------|----------|
| 1 | Product clarity | 9 | QUICKSTART gives a do-this-first path; site + README state target user, problem, promise; every documented command executed verbatim by me |
| 2 | Differentiation | 9 | Honesty gates (worker probes, evidence rules) + usage governor + mission state are implemented and demonstrated by tested deterministic tools; evidence trail public (tests, verify.sh, CHANGELOG) |
| 3 | Installation | 9 | install.sh: 11 verified scenarios — fresh, spaces-in-path, idempotent rerun, upgrade-with-backup, --keep, --only, uninstall-with-backup, non-directory refusal, broken-checkout error, bad-flag error, public-clone stranger test |
| 4 | First-use experience | 9 | QUICKSTART executed verbatim end-to-end from a fresh public clone in a clean env; every step prints observable output; installer ends with live router smoke check |
| 5 | Documentation | 9 | README (accurate, commands re-run), QUICKSTART, DEPLOY runbook, SECURITY threat model, CONTRIBUTING, CHANGELOG — all present and matching behavior |
| 6 | Real-world usefulness | 8 | Both deterministic tools real, tested, and demoed; skills are prose contracts — their in-agent journey cannot be executed by me without an agent host (documented limitation, not hidden) |
| 7 | Reliability | 9 | 30 tests green; idempotent writes; git timeouts + file caps; live site zero console errors across repeated journeys |
| 8 | Security | 9 | SECURITY.md threat model over real trust boundaries; fixed+regression-tested remote credential/query/fragment leak; installer refuses obstructions and never runs remote code; site has zero third-party origins, no input surfaces; secret-scan clean before publish |
| 9 | Testing | 9 | 30 tests: routing policy (20 incl. malformed/unicode/oversize/conflict/precedence), graph builder (10 incl. credential/query/fragment sanitization, idempotency, stale cleanup); installer smoke inside verify.sh |
| 10 | Accessibility | 9 | Keyboard: tab trail shows visible focus rings, copy activated via Enter; reduced-motion honored (computed 0.01ms); contrast computed: all pairs AA, dark AAA; desktop/tablet/mobile visually inspected |
| 11 | Performance | 9 | ~25KB HTML, zero third-party origins, networkidle fast on live; nothing material left — documented decision |
| 12 | Maintainability | 9 | DEPLOY runbook with rollback, CHANGELOG + semver tags, CONTRIBUTING, architecture/threat notes, mission state files |
| 13 | Distribution readiness | 9 | Public repos (aegis, aegis-site), MIT LICENSE, v1.1.0 tags, CHANGELOG, SECURITY/CONTRIBUTING; public clone → install verified |
| 14 | Public credibility | 9 | Every public claim evidence-backed; honest limitation stated (skill prose untestable here); no inflated metrics anywhere; footer claims match reality |
| 15 | Production quality | 9 | Live URL re-verified after every batch; custom 404, og image, HSTS/HTTPS; zero-error journeys; rollback documented and exercised via git |

## Grading method

Each grade cites artifacts inspected this phase: files, command outputs,
Playwright/live checks, and the executed stranger journey. Category 6 is
honestly held at 8: the remaining point requires running an actual agent
host, which is outside this repository's control.

## Adversarial passes (findings → outcomes)

1. Confused first-time user → found no way to obtain the code (no clone
   URL anywhere) → published source repos, added clone steps everywhere,
   executed the stranger journey.
2. Demanding power user → no per-skill install → added --only (tested).
3. Security attacker → query/fragment token leak in remote sanitization →
   fixed with regression tests; installer abuse cases refused.
4. Maintainer during outage → rollback/runbook gaps → DEPLOY.md verified,
   tags + CHANGELOG enable pinning and recovery.
5. Skeptical competitor → "it's just prompts + two scripts" → the defensible
   answer is the evidence system itself (tested policy, honesty gates,
   reproducible verification); claims are deliberately modest and checkable.
