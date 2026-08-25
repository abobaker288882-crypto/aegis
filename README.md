# Aegis

Agent skills plus deterministic tools that turn an AI coding agent into an
accountable, usage-efficient product team: from a short brief through design,
build, security, tests, commit, deployment, and live verification — with
explicit rules against faking any step.

## Components

| Path | Role |
|------|------|
| `aegis-ceo-skills/` | Flagship skill: autonomous end-to-end delivery with a mission-graph status surface, worker activation gates (real capability probes, never simulated workers), a usage governor, and release gates. |
| `usage-optimizer/` | Skill + `scripts/route_task.py`, a stdlib-only deterministic router that picks the cheapest capable route for a task. Ships with unit tests. |
| `second-brain-context/` | Skill + `scripts/build_project_graph.py`, which indexes local projects into an Obsidian vault graph (paths and metadata only; sanitizes git credentials; never copies source into the vault). |
| `five-year-old/` | Skill for plain-language end-to-end ownership: simple progress updates, complete delivery, honest final report. |
| `aegis-ceo-office-site/` | Public product site (Next.js 16 + vinext), live at `https://abobaker288882-crypto.github.io/` via GitHub Pages. Self-contained: self-hosted fonts, zero third-party scripts. See its `DEPLOY.md`. |

## Installing the skills

```sh
git clone https://github.com/abobaker288882-crypto/aegis.git
cd aegis
./install.sh
```

Safe and reversible by design: idempotent, backs up existing copies before
any upgrade (`--keep` skips instead), refuses to touch non-directory
obstructions, and ends with a live smoke check of the installed router.
`./install.sh --uninstall` removes the skills (keeping timestamped backups).
`--target DIR` or `AEGIS_SKILLS_DIR` chooses another skills directory
(default `~/.agents/skills`; use your host's equivalent).

Skills are plain Markdown plus optional scripts — no daemon, no account, no
telemetry. New here? Follow `QUICKSTART.md` for a five-minute verified first
success.

## Verifying

```sh
./verify.sh
```

Runs both Python test suites (30 tests), an installer smoke test in a clean
temp directory, and — when Node is available — the site checks below.

Site checks (requires Node 22+ and pnpm):

```sh
cd aegis-ceo-office-site
pnpm install
pnpm lint && npx tsc --noEmit && pnpm build
node scripts/screenshot.mjs http://localhost:4173/ shots   # after `pnpm start` or `vinext start -p 4173`
```

## Mission files

`MISSION.md`, `OX_STATE.md`, and `OX_LOG.md` record the current product
mission, verified state, and chronological decisions/evidence. Keep them
accurate when you change the product.

## Repository notes

- Suite source: https://github.com/abobaker288882-crypto/aegis
- Site source: https://github.com/abobaker288882-crypto/aegis-site
- Live site: https://abobaker288882-crypto.github.io/
- `aegis-ceo-office-site/` is a separate nested git repository with its own
  history and remote.
- Python helpers target the Python 3.9+ standard library only.

## License

MIT — see `LICENSE`. Security concerns: `SECURITY.md`. Contributions:
`CONTRIBUTING.md`.
