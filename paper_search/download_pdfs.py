#!/usr/bin/env python3
"""
Download PDFs for a list of arXiv DOIs found in doi.txt (one per line).

Assumes DOIs look like:
  - 10.48550/arXiv.2401.11595
  - https://doi.org/10.48550/arXiv:2401.11595
  - arXiv:2401.11595
The script extracts the arXiv identifier and fetches https://arxiv.org/pdf/<id>.pdf.
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request
from typing import Iterable, Optional


ARXIV_ID_RE = re.compile(
    r"arXiv[:\.]?"  # prefix
    r"("  # begin capture
    r"[0-9]{4}\.[0-9]{4,5}(?:v[0-9]+)?"  # post-2007 ids
    r"|"
    r"[a-z\-]+\/[0-9]{7}(?:v[0-9]+)?"  # legacy ids like math/0601001
    r")",
    re.IGNORECASE,
)


def extract_arxiv_id(doi: str) -> Optional[str]:
    """Return bare arXiv id (without version) from a DOI/URL/identifier string."""
    text = doi.strip()
    if not text:
        return None
    # Trim URL prefix if present
    if text.startswith(("http://", "https://")):
        text = text.split("://", 1)[1]
    if text.startswith("doi.org/"):
        text = text[len("doi.org/") :]
    # Match arXiv pattern
    m = ARXIV_ID_RE.search(text)
    if not m:
        return None
    arxiv_id = m.group(1)
    # Drop version suffix (v#) to get stable PDF URL
    return arxiv_id.split("v", 1)[0]


def iter_dois(path: pathlib.Path) -> Iterable[str]:
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield line


def download_pdf(arxiv_id: str, dest: pathlib.Path, retries: int = 2, delay: float = 1.5) -> bool:
    """Download a single arXiv PDF; returns True on success."""
    url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    tmp_path = dest.with_suffix(".part")
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=30) as resp, tmp_path.open("wb") as out:
                while True:
                    chunk = resp.read(1024 * 64)
                    if not chunk:
                        break
                    out.write(chunk)
            tmp_path.rename(dest)
            return True
        except urllib.error.HTTPError as e:
            print(f"[{arxiv_id}] HTTP {e.code} when fetching {url}", file=sys.stderr)
            break  # HTTP errors are unlikely to succeed on retry
        except Exception as e:
            if tmp_path.exists():
                tmp_path.unlink(missing_ok=True)
            if attempt < retries:
                print(f"[{arxiv_id}] error: {e}; retrying in {delay}s...", file=sys.stderr)
                time.sleep(delay)
                continue
            print(f"[{arxiv_id}] failed after {retries + 1} attempts: {e}", file=sys.stderr)
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="Download PDFs from arXiv DOIs listed in a file.")
    parser.add_argument("-i", "--input", type=pathlib.Path, default=pathlib.Path("doi.txt"), help="path to DOI list")
    parser.add_argument("-o", "--out-dir", type=pathlib.Path, default=pathlib.Path("pdfs"), help="where to save PDFs")
    parser.add_argument("--overwrite", action="store_true", help="re-download existing PDFs")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Input file not found: {args.input}", file=sys.stderr)
        return 1

    args.out_dir.mkdir(parents=True, exist_ok=True)

    successes = 0
    total = 0
    for raw in iter_dois(args.input):
        total += 1
        arxiv_id = extract_arxiv_id(raw)
        if not arxiv_id:
            print(f"[skip] could not parse arXiv id from line: {raw.strip()}", file=sys.stderr)
            continue

        dest = args.out_dir / f"{arxiv_id}.pdf"
        if dest.exists() and not args.overwrite:
            print(f"[skip] already downloaded: {dest}")
            successes += 1
            continue

        ok = download_pdf(arxiv_id, dest)
        if ok:
            print(f"[ok] {arxiv_id} -> {dest}")
            successes += 1
    print(f"Done: {successes}/{total} PDFs downloaded.")
    return 0 if successes else 1


if __name__ == "__main__":
    raise SystemExit(main())
