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
| `aegis-ceo-office-site/` | Public product site (Next.js 16 + vinext, Cloudflare Workers target). Self-contained: self-hosted fonts, zero third-party scripts. |

## Installing the skills

Copy the skill folders into your agent host's skills directory (the examples
below assume `~/.agents/skills/`; adjust to your host's convention):

```sh
cp -R aegis-ceo-skills usage-optimizer second-brain-context five-year-old ~/.agents/skills/
```

Skills are plain Markdown plus optional scripts — no daemon, no account, no
telemetry.

## Verifying

From the repository root:

```sh
python3 -m unittest discover usage-optimizer/scripts -p "test_*.py"
python3 -m unittest discover second-brain-context/scripts -p "test_*.py"
```

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

- The main repo has no configured remote; `aegis-ceo-office-site/` is a
  separate nested git repository with its own history.
- Python helpers target the Python 3.9+ standard library only.
