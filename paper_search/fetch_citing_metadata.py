#!/usr/bin/env python3
"""
Given a DOI or arXiv ID, fetch the title and abstract of all papers that cite it
using the Semantic Scholar Graph API. Works for arXiv and non-arXiv inputs.

Output: citing_metadata.txt (default) containing one block per citing paper.

Usage:
    python fetch_citing_metadata.py                     # prompts for ID
    python fetch_citing_metadata.py -i 10.1145/3368089.3409697
    python fetch_citing_metadata.py -i 2106.15928 -o my_output.txt
"""
from __future__ import annotations

import argparse
import os
import pathlib
import sys
import time
from typing import Iterable, Tuple

import requests


API_URL = "https://api.semanticscholar.org/graph/v1/paper/{paper_id}"
API_FIELDS = "citations.title,citations.abstract,citations.externalIds,citations.authors"


def normalize_paper_id(raw: str) -> str:
    """Return Semantic Scholar paper_id string for DOI or arXiv ID."""
    text = raw.strip()
    if not text:
        return ""
    if text.lower().startswith("arxiv:"):
        text = text.split(":", 1)[1]
    # arXiv identifiers have a dot pattern 4 digits dot 4/5 digits or legacy slash
    if text.startswith("10."):
        return f"DOI:{text}"
    return f"ARXIV:{text}"


def fetch_citations(paper_id: str, retries: int = 3, backoff: float = 3.0):
    """Fetch citing papers with retries on rate-limit; return JSON or None."""
    url = API_URL.format(paper_id=paper_id)
    headers = {"User-Agent": "paper-search/1.0 (contact: user@example.com)"}
    api_key = os.getenv("S2_API_KEY") or os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        headers["x-api-key"] = api_key
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, params={"fields": API_FIELDS}, headers=headers, timeout=30)
            if resp.status_code == 404:
                print("Paper not found. Check the DOI/arXiv ID.", file=sys.stderr)
                return None
            if resp.status_code == 429:
                retry_after = float(resp.headers.get("Retry-After", backoff))
                if attempt == retries:
                    print("Rate limited and retries exhausted.", file=sys.stderr)
                    return None
                wait = retry_after * (attempt + 1)
                print(f"Rate limited (429). Waiting {wait:.1f}s before retry {attempt+1}/{retries}...", file=sys.stderr)
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.json()
        except Exception as e:  # noqa: BLE001
            if attempt == retries:
                print(f"Error fetching paper after retries: {e}", file=sys.stderr)
                return None
            wait = backoff * (attempt + 1)
            print(f"Error fetching paper: {e}; retrying in {wait:.1f}s", file=sys.stderr)
            time.sleep(wait)
    return None


def iter_citing_metadata(data) -> Iterable[Tuple[str, str, str, str]]:
    """Yield (label, title, authors, abstract) for each citing paper."""
    for citation in data.get("citations", []) or []:
        external = citation.get("externalIds", {}) or {}
        doi = external.get("DOI")
        arxiv = external.get("ArXiv")
        label = doi or (f"arXiv:{arxiv}" if arxiv else "(no id)")
        title = citation.get("title") or ""
        authors = ", ".join(a.get("name", "") for a in citation.get("authors", []) if a.get("name"))
        abstract = citation.get("abstract") or ""
        yield label, title, authors, abstract


def write_metadata(records: Iterable[Tuple[str, str, str, str]], out_path: pathlib.Path) -> int:
    count = 0
    with out_path.open("w", encoding="utf-8") as f:
        for idx, (label, title, authors, abstract) in enumerate(records, start=1):
            f.write(f"## Citing Paper {idx}\n")
            f.write(f"ID: {label}\n")
            f.write(f"Title: {title}\n")
            f.write(f"Authors: {authors}\n")
            f.write("Abstract:\n")
            f.write(f"{abstract}\n\n")
            count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch citing paper metadata for a DOI/arXiv ID.")
    parser.add_argument("-i", "--id", help="Input DOI or arXiv ID. If omitted, prompts interactively.")
    parser.add_argument("-o", "--output", type=pathlib.Path, default=pathlib.Path("citing_metadata.txt"))
    args = parser.parse_args()

    raw_id = args.id or input("Enter DOI or arXiv ID: ").strip()
    paper_id = normalize_paper_id(raw_id)
    if not paper_id:
        print("No ID provided. Exiting.")
        return 1

    data = fetch_citations(paper_id)
    if not data:
        return 1

    citations = list(iter_citing_metadata(data))
    if not citations:
        print("No citations found.")
        return 1

    written = write_metadata(citations, args.output)
    print(f"Saved {written} citing papers to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
