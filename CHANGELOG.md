# Changelog

All notable changes to Aegis. Format follows Keep a Changelog; versioning is
semantic (MAJOR.MINOR.PATCH).

## [1.1.0] — 2026-08-25

### Added
- `install.sh`: safe, idempotent installer with `--target`, `--keep`,
  `--uninstall`, timestamped backups before any replacement, refusal to touch
  non-directory obstructions, and a post-install router smoke check.
  Verified from a clean environment including paths with spaces.
- `QUICKSTART.md`: first-success path from install to observable verification.
- `verify.sh`: one command that runs every check in the repository.
- Security hardening: `build_project_graph.py` now strips query strings and
  fragments from git remote URLs (delegated-token leak path), with regression
  tests; 13 new boundary/adversarial tests for `route_task.py` (empty and
  whitespace tasks, unicode, oversize tasks, malformed JSON, conflicting
  input modes, non-boolean flags, keyword inference, override precedence).
- Trust set: LICENSE (MIT), SECURITY.md with explicit threat model,
  CONTRIBUTING.md, this changelog, and git tags for releases.

### Changed
- Site: install instructions now match the tested installer; added
  host-directory hints; social share image and metadata; branded 404.

## [1.0.0] — 2026-08-25

### Added
- `aegis-ceo-skills`: autonomous end-to-end delivery skill with mission
  graph, worker activation gates, usage governor, and release gates.
- `usage-optimizer`: usage-minimizing skill with tested deterministic router.
- `second-brain-context`: Obsidian vault context skill with project-graph
  builder (credential-sanitizing, idempotent).
- `five-year-old`: plain-language end-to-end ownership skill.
- `aegis-ceo-office-site`: product site, live at
  https://abobaker288882-crypto.github.io/ (GitHub Pages), self-contained
  with self-hosted fonts and zero third-party origins.
