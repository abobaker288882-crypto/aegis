# OX_STATE — current mission state

Updated: 2026-08-24 (session 1, in progress)

## Phase

DISCOVER complete → BUILD in progress.

## Environment facts (verified)

- macOS arm64; no system Node/npm/pnpm/Homebrew. Node v22.14.0 installed by
  this session at `/var/folders/yz/wdhnj83x5x5cdr_zdxp7ctq00000gn/T/opencode/node`
  (add `node/bin` to PATH for pnpm/corepack/npx). Python 3.9.6 available.
- Network access available (nodejs.org verified).
- Workspace skills are byte-identical to installed copies at
  `~/.agents/skills/…` except none differ (diff -rq clean).
- Antigravity desktop + `agy` CLI exist on this machine but external model
  delegation is forbidden this session (user directive); not used.
- Second Brain vault exists; no Aegis-related notes found in 10 Projects.

## Baseline evidence (verified before changes)

- usage-optimizer tests: 7/7 PASS (`python3 -m unittest discover …`).
- build_project_graph.py `--help` runs OK.
- Site: `pnpm install --frozen-lockfile` OK; `pnpm build` PASS;
  `pnpm lint` PASS; `npx tsc --noEmit` PASS (exit 0).
- Live local run (`vinext start`, port 4173): `/` → 307 →
  `/aegis-ceo-office.html`; page renders a STALE demo mission ("Framing the
  usage-optimizer skill", 8% progress, workers "Queued") with title
  "aegis-ceo-office.html". This is the product's public face and is defective.

## Defects found (discovery)

D1. Public site = stale fake demo wrapper; no real product info. (Critical,
    user-facing.) → AC1
D2. Site fonts: globals.css uses `--font-geist-sans/-mono` but layout.tsx never
    loads fonts → silent Arial fallback. → AC4
D3. No root README / docs for the suite. → AC5
D4. No tests for build_project_graph.py despite nontrivial logic. → AC6
D5. Wrapper page CSP allows many CDNs + unsafe-eval and pulls scripts from
    unpkg (supply-chain surface) — acceptable only as a Codex-host artifact;
    the real public page must be self-contained. → AC3
D6. Python entrypoints with shebangs lack exec bits (minor).
D7. Deployment path unverified: `.openai/hosting.json` project exists, dist/
    built previously; wrangler auth unknown here. → AC9 (attempt pending)

## Completed so far

- Full repo read (skills, references, assets, site source/configs/git logs).
- Mission files created (this file, MISSION.md, OX_LOG.md).

## Next actions (in order)

1. Rebuild site home page as real premium product page (fix D1, D2, D5);
   keep `/aegis-ceo-office.html` file for host compatibility but stop
   redirecting `/` to it.
2. Root README.md (D3).
3. Unit tests for build_project_graph.py (D4); chmod +x entrypoints (D6).
4. Re-run full check battery; commit coherently.
5. Attempt deploy through existing infra; record truthfully (AC9).

## Blockers

None yet that block code work. Deployment may require credentials not present
in this shell (to be determined via `wrangler whoami` when attempted).
