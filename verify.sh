#!/bin/sh
# Run every check in the Aegis repository. Exit 0 only if all pass.
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
fail=0

echo "== python: usage-optimizer router =="
python3 -m unittest discover usage-optimizer/scripts -p "test_*.py" || fail=1

echo "== python: second-brain-context graph builder =="
python3 -m unittest discover second-brain-context/scripts -p "test_*.py" || fail=1

echo "== installer: clean-environment smoke =="
smoke=$(mktemp -d)
if HOME="$smoke/home" ./install.sh --target "$smoke/home/skills" >/dev/null 2>&1 \
   && [ -f "$smoke/home/skills/aegis-ceo-skills/SKILL.md" ]; then
  echo "installer smoke: OK"
else
  echo "installer smoke: FAILED" >&2
  fail=1
fi
rm -rf "$smoke"

if command -v node >/dev/null 2>&1 && [ -d aegis-ceo-office-site/node_modules ]; then
  echo "== site: lint, types, build =="
  ( cd aegis-ceo-office-site && pnpm lint && npx tsc --noEmit && pnpm build ) || fail=1
else
  echo "== site checks skipped (node or node_modules not present) =="
fi

if [ "$fail" -ne 0 ]; then
  echo "RESULT: FAILURES ABOVE" >&2
  exit 1
fi
echo "RESULT: all checks passed"
