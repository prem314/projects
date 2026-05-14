#!/usr/bin/env python3
"""Fetch a Wikimedia Commons file and its reuse metadata.

The script intentionally uses only the Python standard library so the book
pipeline can run in a fresh checkout without dependency setup.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path


API_URL = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "evil-puzzle-book-pipeline/0.1 (local research build)"


def request_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        destination.write_bytes(response.read())


def text_from_html(value: str) -> str:
    value = re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE)
    value = re.sub(r"<[^>]+>", "", value)
    value = html.unescape(value)
    return re.sub(r"\s+", " ", value).strip()


def simplify_extmetadata(extmetadata: dict) -> dict:
    simplified = {}
    for key, payload in sorted(extmetadata.items()):
        value = payload.get("value")
        simplified[key] = text_from_html(str(value)) if value is not None else ""
    return simplified


def commons_metadata(title: str) -> dict:
    query = {
        "action": "query",
        "format": "json",
        "titles": title,
        "prop": "imageinfo",
        "iiprop": "url|size|mime|sha1|extmetadata",
        "iiextmetadatalanguage": "en",
    }
    url = f"{API_URL}?{urllib.parse.urlencode(query)}"
    data = request_json(url)
    pages = data.get("query", {}).get("pages", {})
    if not pages:
        raise RuntimeError(f"No Commons page returned for {title!r}")

    page = next(iter(pages.values()))
    if "missing" in page:
        raise RuntimeError(f"Commons file not found: {title}")

    imageinfo = page.get("imageinfo", [])
    if not imageinfo:
        raise RuntimeError(f"No imageinfo returned for {title!r}")

    info = imageinfo[0]
    return {
        "commons_title": page.get("title", title),
        "description_url": info.get("descriptionurl"),
        "file_url": info.get("url"),
        "mime": info.get("mime"),
        "size": info.get("size"),
        "width": info.get("width"),
        "height": info.get("height"),
        "sha1": info.get("sha1"),
        "extmetadata": info.get("extmetadata", {}),
        "extmetadata_text": simplify_extmetadata(info.get("extmetadata", {})),
        "api_url": url,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True, help="Commons file title, e.g. File:Example.jpg")
    parser.add_argument("--image-out", required=True, type=Path)
    parser.add_argument("--metadata-out", required=True, type=Path)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    metadata = commons_metadata(args.title)
    file_url = metadata.get("file_url")
    if not file_url:
        raise RuntimeError(f"No file URL returned for {args.title!r}")

    args.metadata_out.parent.mkdir(parents=True, exist_ok=True)
    args.metadata_out.write_text(json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8")
    download(file_url, args.image_out)

    print(f"Wrote {args.metadata_out}")
    print(f"Wrote {args.image_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
