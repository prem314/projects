#!/usr/bin/env python3
"""
Fetch title and abstract for a list of non-arXiv DOIs (one per line) using
the Semantic Scholar Graph API, and write the results to a text file.

Input:  non_arxiv_doi.txt  (default) - lines of DOIs
Output: non_arxiv_metadata.txt       - blocks of "Title" + "Abstract"

Usage:
    python fetch_non_arxiv_metadata.py               # uses defaults
    python fetch_non_arxiv_metadata.py -i custom.txt -o out.txt
"""
from __future__ import annotations

import argparse
import pathlib
import sys
from typing import Iterable, Tuple

import requests


API_URL = "https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
API_FIELDS = "title,abstract"


def iter_dois(path: pathlib.Path) -> Iterable[str]:
    """Yield non-empty, stripped DOIs from a file."""
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            doi = line.strip()
            if doi:
                yield doi


def fetch_title_abstract(doi: str) -> Tuple[str, str]:
    """Return (title, abstract) for a DOI via Semantic Scholar. Empty strings on failure."""
    paper_id = f"DOI:{doi}"
    url = API_URL.format(paper_id=paper_id)
    try:
        resp = requests.get(url, params={"fields": API_FIELDS}, timeout=15)
        if resp.status_code == 404:
            print(f"[miss] {doi} not found", file=sys.stderr)
            return "", ""
        resp.raise_for_status()
        data = resp.json()
        title = data.get("title") or ""
        abstract = data.get("abstract") or ""
        return title, abstract
    except Exception as e:  # noqa: BLE001 - keep simple for script
        print(f"[error] {doi}: {e}", file=sys.stderr)
        return "", ""


def write_metadata(records: Iterable[Tuple[str, str, str]], out_path: pathlib.Path) -> None:
    """Write entries to the output file."""
    with out_path.open("w", encoding="utf-8") as f:
        for doi, title, abstract in records:
            f.write(f"DOI: {doi}\n")
            f.write(f"Title: {title}\n")
            f.write("Abstract:\n")
            f.write(f"{abstract}\n\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch title/abstract for non-arXiv DOIs.")
    parser.add_argument(
        "-i",
        "--input",
        type=pathlib.Path,
        default=pathlib.Path("non_arxiv_doi.txt"),
        help="Path to file containing non-arXiv DOIs (one per line)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=pathlib.Path,
        default=pathlib.Path("non_arxiv_metadata.txt"),
        help="Where to save fetched metadata",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Input file not found: {args.input}", file=sys.stderr)
        return 1

    records = []
    total = 0
    found = 0
    for doi in iter_dois(args.input):
        total += 1
        title, abstract = fetch_title_abstract(doi)
        if title or abstract:
            found += 1
        records.append((doi, title, abstract))

    write_metadata(records, args.output)

    print(f"Done. {found}/{total} entries contained metadata. Saved to {args.output}")
    return 0 if found else 1


if __name__ == "__main__":
    raise SystemExit(main())
