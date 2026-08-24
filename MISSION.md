# MISSION — Aegis Production Hardening

Owner: Ox Alpha (sole intelligence; all reasoning, implementation, review, and
verification performed directly — no external models, workers, or subagents).

## Product thesis

Aegis is a suite of agent skills plus deterministic tools that turn an AI coding
agent into an accountable, usage-efficient product team: it takes a short brief
and drives it through discover → design → build → secure → test → commit →
deploy → live-verify, with explicit truthfulness rules (never fake workers,
tests, or deployments) and an explicit usage budget governor.

- Target user: power users of agentic coding tools (Codex, opencode, similar)
  who hand agents whole outcomes ("build and ship this") and need the result to
  be genuinely shipped and honestly verified, not merely generated.
- Painful problem today: agents stop at generated code or passing unit tests,
  fabricate orchestration ("workers" that never ran), burn quota on redundant
  passes, and lose cross-session context.
- Why Aegis wins: enforceable honesty gates (worker activation probes, evidence
  rules), a compact mission-graph status surface, deterministic helpers with
  tests, durable state files for resumability, and a shared local second brain.

## Scope of this mission

Everything under this repository:

1. `aegis-ceo-skills/` — flagship CEO skill (SKILL.md, references, assets,
   scripts).
2. `usage-optimizer/` — routing policy skill + tested Python router.
3. `second-brain-context/` — vault context skill + project graph builder.
4. `five-year-old/` — plain-language end-to-end ownership skill.
5. `aegis-ceo-office-site/` — public product site (Next.js 16 / vinext /
   Cloudflare Workers target).

## Measurable acceptance criteria

| # | Criterion | Evidence required |
|---|-----------|-------------------|
| AC1 | Public site explains Aegis to a first-time visitor (what/why/install) with premium, coherent design; no stale or fake demo content | Rendered HTML inspected locally |
| AC2 | Site builds clean (`pnpm build`), lints clean (`pnpm lint`), typechecks (`tsc --noEmit`) | Command exit codes |
| AC3 | Site is self-contained: no third-party script origins, safe CSP/referrer policy, dark mode + reduced-motion support, semantic headings/landmarks, keyboard-visible focus styles | Source inspection + rendered HTML |
| AC4 | Fonts resolve as designed (no undefined CSS custom property fallback to system defaults) | Source + rendered CSS inspection |
| AC5 | Root README documents the suite: purpose of each component, install path, verification commands | File present and accurate against reality |
| AC6 | `usage-optimizer` router tests pass; `build_project_graph.py` has meaningful unit tests covering discovery exclusions, label collisions, git-remote credential sanitization, and stale-note removal | `python3 -m unittest` exit code |
| AC7 | Mission/state/log files exist and accurately reflect reality at all times | Files reviewed before final response |
| AC8 | All work committed in coherent commits; working tree left coherent | `git status` + log |
| AC9 | Deployment attempted through existing authorized infra; outcome recorded truthfully (shipped, or exact blocker) | Command output in OX_LOG |

Non-goals: rewriting skill philosophy mid-mission without evidence (e.g., the
mandatory Antigravity/Gemini activation gate is a deliberate anti-fabrication
design and stays); adding paid infrastructure; creating backend features with
no user; speculative rewrites of working code.

Constraints: no external AI services; Python 3.9 stdlib only for scripts;
Node/pnpm obtained locally in temp space; deployment only through already-
configured infrastructure.
