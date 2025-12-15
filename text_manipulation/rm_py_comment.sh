#!/usr/bin/env bash
set -euo pipefail

SCRIPT="/home/premkr/git/projects/text_manipulation/remove_comments_from_python_file.py"

# Require: path to python file
if [ "$#" -lt 1 ]; then
  echo "Usage: $(basename "$0") <path/to/file.py>" >&2
  exit 1
fi

python3 "$SCRIPT" "$@"
