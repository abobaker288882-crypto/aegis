# Security policy

Aegis runs inside your machine and your agent. Its trust boundaries are the
ones that matter: your files, your git remotes, your vault, and anything your
agent host sends it.

## Supported versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | Yes       |

## How to report

Open a private security advisory via GitHub (Security → Advisories) on the
repository, or contact the maintainer directly. Please include a reproduction
and affected paths. Do not open public issues for exploitable behavior.

## Threat model (what Aegis actually trusts)

| Boundary | Trust stance | Controls in place |
|----------|--------------|-------------------|
| Task input to `route_task.py` | Hostile | Strict schema validation, typed flags, compact JSON errors, exit code 2 on any violation (tested incl. malformed/unicode/oversize inputs) |
| Filesystem walked by `build_project_graph.py` | Semi-trusted (your machine) | Excluded dirs (caches, node_modules, dist…), depth cap, 100k file cap, 4s git subprocess timeout, list-argv subprocess only (no shell), symlink traversal off by default |
| Git remote URLs | Hostile (may embed credentials) | Credential stripping plus query/fragment stripping before anything is written to the vault (regression-tested) |
| Vault writes | Your data | Writes only generated-type-marked notes inside vault folders; `write_if_changed` is idempotent; never copies source files, secrets, `.env`, keys, or build output into the vault |
| Site (GitHub Pages) | Public, static | Zero third-party script/font origins, no forms, no user input, no cookies; HSTS enforced by the platform |
| Installer | Local only | Never follows symlinks into overwrites, refuses non-directory obstructions, backs up before any replacement, no network access |

## What Aegis will never do

- Send your source, secrets, or vault content anywhere on its own.
- Run shell strings built from input.
- Store credentials, tokens, or private URLs in generated notes.

## Known non-goals

The skills themselves are instructions executed by your agent host; their
security depends on the host's own permission model. Aegis adds explicit
rules (probe workers before claiming them, never claim unrun checks, stop
before irreversible actions), but the enforcing sandbox is your agent host's.
