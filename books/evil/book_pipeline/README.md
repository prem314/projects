# Book Pipeline

This folder is for code used to build the puzzle book: fetching person
metadata, finding reusable images, recording license/source evidence, and
preparing structured inputs for the TeX profile files.

Prefer APIs and archives with machine-readable rights metadata. Store raw
downloaded images and generated build output outside this folder unless a
specific asset or fixture needs to be versioned.

Current helper:

- `fetch_commons_file.py`: fetches a Wikimedia Commons file, writes API
  metadata/license evidence to JSON, and downloads the original image.
