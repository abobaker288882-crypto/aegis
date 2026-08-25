# Quickstart: first success in five minutes

Goal: install Aegis, prove it works on your machine, and see one skill do its
job. Every step below is observable — you will see real output, not promises.

## 0. What you need

- A terminal (macOS or Linux).
- Python 3.9+ (`python3 --version`) — only for the deterministic helpers.
- An agent host that loads skill folders (Codex, opencode, or similar). If
  you only want the tools and site, steps 1–2 work without any agent host.

## 1. Get and install

```sh
git clone https://github.com/abobaker288882-crypto/aegis.git
cd aegis
./install.sh
```

You should see four `installed …` lines, a `done:` summary, and
`verified: installed router answers correctly`. That last line is your first
proof: the installed code just answered a real routing question.

Nothing outside the target directory (default `~/.agents/skills`) is touched.
Existing copies are backed up before any upgrade; `./install.sh --uninstall`
removes everything cleanly.

## 2. Use a tool directly

```sh
python3 ~/.agents/skills/usage-optimizer/scripts/route_task.py \
  --task "review authentication vulnerability" --kind security --risk high
# → {"reason":"high-risk or consequential work needs strongest judgment","route":"sol"}
```

Change the flags and watch the route change — the router is a real, tested
policy engine, not a mock.

## 3. Verify everything

```sh
./verify.sh
```

Runs both test suites (20 router tests, 10 graph-builder tests), an
installer smoke test in a clean temp directory, and — if Node is present —
the site lint/typecheck/build. Ends with `RESULT: all checks passed`.

## 4. Hand the skills to your agent

Point your agent host at the skills directory from step 1 (for example
`~/.agents/skills`), restart it if needed, and invoke one:

> Use $usage-optimizer to find the lowest-usage way to complete this request
> well: [your task]

Expected observable behavior: the agent states its quality floor, chooses the
lean route, and finishes with result + verification status — per
`usage-optimizer/SKILL.md`. If it instead rambles or invents usage numbers,
your host did not load the skill; check the directory path.

## 5. Where to go next

- What each component does: `README.md`
- Safety guarantees and limits: `SECURITY.md`
- The full delivery playbook: `aegis-ceo-skills/SKILL.md`
