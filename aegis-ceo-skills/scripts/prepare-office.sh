#!/bin/sh
set -eu

if [ "$#" -ne 1 ]; then
  echo "usage: prepare-office.sh <writable-visualization-directory>" >&2
  exit 2
fi

case "$1" in
  /*) ;;
  *) echo "destination must be an absolute path" >&2; exit 2 ;;
esac

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
source_file="$script_dir/../assets/ceo-office-game.html"
destination="$1/aegis-ceo-office-game.html"

test -f "$source_file"
mkdir -p -- "$1"
cp -- "$source_file" "$destination"
printf '%s\n' "$destination"
