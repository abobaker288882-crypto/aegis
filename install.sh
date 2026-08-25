#!/bin/sh
# Aegis installer — safe, idempotent, reversible.
# Usage: ./install.sh [--target DIR] [--keep] [--only NAME] [--uninstall] [--help]
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ALL_SKILLS="aegis-ceo-skills usage-optimizer second-brain-context five-year-old"
SKILLS="$ALL_SKILLS"
ENGINE_SRC="$SCRIPT_DIR/aegis-engine"
ENGINE_TARGET="${AEGIS_ENGINE_DIR:-$HOME/.agents/aegis}"
TARGET="${AEGIS_SKILLS_DIR:-$HOME/.agents/skills}"
MODE="install"
KEEP=0

usage() {
  cat <<EOF
Aegis installer

Usage:
  ./install.sh                 Install/upgrade all Aegis skills
  ./install.sh --only NAME     Install a single skill ($ALL_SKILLS)
  ./install.sh --target DIR    Install into DIR instead of ~/.agents/skills
  ./install.sh --keep          On conflict, keep the existing copy (skip)
  ./install.sh --uninstall     Remove the installed Aegis skills (a timestamped
                               backup is kept next to them)

Environment:
  AEGIS_SKILLS_DIR             Default target directory
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --target) [ $# -ge 2 ] || { echo "error: --target needs a value" >&2; exit 2; }
              TARGET=$2; shift 2 ;;
    --only)   [ $# -ge 2 ] || { echo "error: --only needs a skill name" >&2; exit 2; }
              SKILLS=$2; shift 2 ;;
    --keep)   KEEP=1; shift ;;
    --uninstall) MODE="uninstall"; shift ;;
    --help|-h) usage; exit 0 ;;
    *) echo "error: unknown option: $1 (see --help)" >&2; exit 2 ;;
  esac
done

for skill in $SKILLS; do
  case " $ALL_SKILLS " in
    *" $skill "*) ;;
    *) echo "error: unknown skill '$skill' (choose from: $ALL_SKILLS)" >&2; exit 2 ;;
  esac
done

case "$MODE" in
  uninstall)
    removed=0
    for skill in $SKILLS; do
      dest="$TARGET/$skill"
      if [ -d "$dest" ]; then
        backup="$dest.backup-$(date +%Y%m%d-%H%M%S)"
        mv "$dest" "$backup"
        echo "removed $dest (backup: $backup)"
        removed=$((removed + 1))
      fi
    done
    engine_removed=0
    if [ -d "$ENGINE_TARGET" ]; then
      engine_backup="$ENGINE_TARGET.backup-$(date +%Y%m%d-%H%M%S)"
      mv "$ENGINE_TARGET" "$engine_backup"
      echo "removed $ENGINE_TARGET (backup: $engine_backup)"
      engine_removed=1
    fi
    if [ "$removed" -eq 0 ] && [ "$engine_removed" -eq 0 ]; then
      echo "nothing to uninstall in $TARGET"
    else
      echo "uninstalled $removed skill(s). Restore any backup by renaming it back."
    fi
    exit 0
    ;;
esac

for skill in $SKILLS; do
  src="$SCRIPT_DIR/$skill"
  if [ ! -f "$src/SKILL.md" ]; then
    echo "error: $skill not found next to install.sh (run from the repository, or pass an intact checkout)" >&2
    exit 1
  fi
done

mkdir -p "$TARGET"

installed=0
upgraded=0
skipped=0
for skill in $SKILLS; do
  src="$SCRIPT_DIR/$skill"
  dest="$TARGET/$skill"
  if [ -e "$dest" ] && [ ! -d "$dest" ]; then
    echo "error: $dest exists and is not a directory; refusing to touch it" >&2
    exit 1
  fi
  if [ -d "$dest" ]; then
    if diff -rq "$src" "$dest" >/dev/null 2>&1; then
      echo "already installed: $dest"
      skipped=$((skipped + 1))
      continue
    fi
    if [ "$KEEP" -eq 1 ]; then
      echo "kept existing: $dest (differs from this checkout; rerun without --keep to upgrade)"
      skipped=$((skipped + 1))
      continue
    fi
    backup="$dest.backup-$(date +%Y%m%d-%H%M%S)"
    mv "$dest" "$backup"
    cp -R "$src" "$dest"
    echo "upgraded $dest (previous copy backed up: $backup)"
    upgraded=$((upgraded + 1))
  else
    cp -R "$src" "$dest"
    echo "installed $dest"
    installed=$((installed + 1))
  fi
done

# Mission engine (used per-project; not an agent skill folder)
if [ -d "$ENGINE_SRC" ]; then
  if [ -d "$ENGINE_TARGET" ]; then
    if diff -rq "$ENGINE_SRC" "$ENGINE_TARGET" >/dev/null 2>&1; then
      echo "engine already installed: $ENGINE_TARGET"
    elif [ "$KEEP" -eq 1 ]; then
      echo "kept existing engine: $ENGINE_TARGET"
    else
      engine_backup="$ENGINE_TARGET.backup-$(date +%Y%m%d-%H%M%S)"
      mv "$ENGINE_TARGET" "$engine_backup"
      cp -R "$ENGINE_SRC" "$ENGINE_TARGET"
      echo "upgraded engine $ENGINE_TARGET (previous: $engine_backup)"
    fi
  else
    mkdir -p "$(dirname "$ENGINE_TARGET")"
    cp -R "$ENGINE_SRC" "$ENGINE_TARGET"
    echo "installed mission engine: $ENGINE_TARGET"
  fi
  echo "engine usage: python3 \"$ENGINE_TARGET/aegis.py\" init --goal \"...\"   (run inside any project)"
fi

echo "done: $installed installed, $upgraded upgraded, $skipped unchanged (target: $TARGET)"

router="$TARGET/usage-optimizer/scripts/route_task.py"
if [ -f "$router" ] && command -v python3 >/dev/null 2>&1; then
  if python3 "$router" --task "format a README" --kind formatting --complexity low --risk low \
      | grep -q '"route":"luna"'; then
    echo "verified: installed router answers correctly"
  else
    echo "warning: router smoke check failed; inspect $router" >&2
    exit 1
  fi
else
  echo "note: python3 not found; skipped the router smoke check"
fi

cat <<EOF

Next step: point your agent host at $TARGET
(e.g. ~/.agents/skills, ~/.codex/skills, or your host's equivalent) and ask it
to run a skill, e.g. "Use \$usage-optimizer to reduce the usage of this task."
EOF
