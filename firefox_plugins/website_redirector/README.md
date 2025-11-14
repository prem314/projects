# Website Redirector (Firefox Add-on)

Lightweight WebExtension that redirects distracting sites to a focus page. Users list the sites (plain domains or full URLs) and a destination URL; every matching page is intercepted via the background script and sent to the configured redirect target.

## Files
- `manifest.json` – extension metadata, permissions, and options page hook.
- `background.js` – listens for outgoing requests and redirects when a match occurs.
- `options.html` / `options.js` – settings UI where users enter domains and the redirect destination.

## Local Testing
1. From this folder run `zip -r website_redirect.zip manifest.json background.js options.html options.js` (or load `manifest.json` directly).
2. In Firefox open `about:debugging#/runtime/this-firefox` → **Load Temporary Add-on…** → choose the zip or manifest.
3. Configure the redirect target and domains via the options page; visit one of those sites to confirm the redirect.

> Note: This project lives inside a larger “projects” repository, so paths above are relative to this subdirectory.
