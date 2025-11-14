#!/usr/bin/env bash

# Automatically generate and append a table of contents for the first PDF in the current directory.
# 1. Uses Codex to ask a model for a structured TOC and saves it to toc.txt
# 2. Runs toc_append.py to embed the TOC into the PDF

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
SCRATCH_DIR="${SCRIPT_DIR}/codex_scratch"
mkdir -p "${SCRATCH_DIR}"

# Allow callers to override the Codex model via TOC_MODEL, default to a generally available model.
MODEL="${TOC_MODEL:-gpt-5-codex}"

# Prefer using the user's conda environment for PyMuPDF; fall back to python3 if unavailable.
PYTHON_CMD=("python3")
CONDA_ENV="${TOC_CONDA_ENV:-pdf}"
CONDA_BIN="${TOC_CONDA_BIN:-}"
if [[ -z "${CONDA_BIN}" ]]; then
  if command -v conda >/dev/null 2>&1; then
    CONDA_BIN="$(command -v conda)"
  elif [[ -x "${HOME}/anaconda3/bin/conda" ]]; then
    CONDA_BIN="${HOME}/anaconda3/bin/conda"
  fi
fi
if [[ -n "${CONDA_BIN}" && -n "${CONDA_ENV}" ]]; then
  PYTHON_CMD=("${CONDA_BIN}" run -n "${CONDA_ENV}" python)
fi

# Find the first PDF (case-insensitive) in the current directory.
mapfile -t PDF_FILES < <(find . -maxdepth 1 -type f \( -iname '*.pdf' \) | sort)
if [[ ${#PDF_FILES[@]} -eq 0 ]]; then
  echo "Error: No PDF files found in ${SCRIPT_DIR}."
  exit 1
fi

PDF_PATH="${PDF_FILES[0]}"
PDF_PATH_ABS="$(realpath "${PDF_PATH}")"
PDF_BASENAME="$(basename "${PDF_PATH_ABS}")"
PDF_STEM="${PDF_BASENAME%.*}"

echo "Using PDF: ${PDF_BASENAME}"
echo "Requesting TOC from Codex model: ${MODEL}"

PROMPT=$(cat <<EOF
You are given a PDF attachment. Carefully read it and produce a detailed table of contents with accurate page numbers.

All scratch or helper files you create must stay inside the current working directory (${SCRATCH_DIR}). Do not modify files outside it; leave toc.txt alone because it is managed externally.

Formatting rules:
- Output plain text only (no Markdown fences).
- One entry per line in the form 'Title - Page N'.
- Use 4 leading spaces per hierarchy level (top-level entries have no leading spaces).
- Page numbering is 1-indexed and must match the PDF.
- Include all major sections and meaningful subsections; skip boilerplate like copyright notices.

Double-check that every page number exists and that indentation reflects the section hierarchy.
EOF
)

TMP_OUTPUT="$(mktemp)"
cleanup() {
  rm -f "${TMP_OUTPUT}"
}
trap cleanup EXIT

if ! printf '%s\n' "${PROMPT}" | codex exec -m "${MODEL}" --output-last-message "${TMP_OUTPUT}" -i "${PDF_PATH_ABS}" -C "${SCRATCH_DIR}"; then
  echo "Error: Codex request failed."
  exit 1
fi

if [[ ! -s "${TMP_OUTPUT}" ]]; then
  echo "Error: Codex response was empty."
  exit 1
fi

# Some models wrap the response in Markdown fences; strip them if present.
if grep -q '^```' "${TMP_OUTPUT}"; then
  awk '
    /^```/ {fence = !fence; next}
    fence {print}
  ' "${TMP_OUTPUT}" > toc.txt
else
  cp "${TMP_OUTPUT}" toc.txt
fi

if [[ ! -s toc.txt ]]; then
  echo "Error: toc.txt is empty after processing Codex output."
  exit 1
fi

echo "Structured TOC saved to toc.txt"

# Use toc_append's helper directly to avoid interactive prompts.
PAGE_OFFSET="${TOC_PAGE_OFFSET:-0}"
PYTHON_SNIPPET=$(
  cat <<PYCODE
from toc_append import create_bookmarks_from_toc
create_bookmarks_from_toc("${PDF_STEM}", "toc.txt", offset=${PAGE_OFFSET})
PYCODE
)
"${PYTHON_CMD[@]}" -c "${PYTHON_SNIPPET}"
