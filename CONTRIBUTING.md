# Contributing

Thanks for improving Aegis. The product rule is simple: **every claim must be
backed by evidence a stranger can reproduce.**

## Ground rules

1. Skills are Markdown contracts for agents. Edit them only when you can
   state what behavior changes and how you verified it.
2. Python tools stay stdlib-only and Python 3.9-compatible.
3. Every behavior change ships with a test that fails without it.
4. No secrets, prompts, transcripts, or telemetry in code, tests, or docs.
5. Keep the site free of third-party script/style/font origins.

## Workflow

```sh
# run every check (must pass before you commit)
./verify.sh
```

Then:

1. Change the smallest coherent surface.
2. Add or adjust tests for the changed behavior.
3. Update `README.md` / `CHANGELOG.md` when behavior or claims change.
4. Commit with a subject that states the outcome, not the activity.
5. Site changes: follow `aegis-ceo-office-site/DEPLOY.md` and verify the live
   URL afterwards.

## Reporting problems

Security issues: see `SECURITY.md` (private advisories, not public issues).
Everything else: open an issue with reproduction steps and expected vs actual
evidence.
