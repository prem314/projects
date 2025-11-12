const DEFAULT_REDIRECT = "https://breakfreefromaddictions.blogspot.com/p/addiction-free.html";

let redirectTarget = DEFAULT_REDIRECT;
let blockedSites = [];

const redirect = () => ({ redirectUrl: redirectTarget });

function hasListener() {
    return browser.webRequest.onBeforeRequest.hasListener(redirect);
}

function updateListener() {
    if (hasListener()) {
        browser.webRequest.onBeforeRequest.removeListener(redirect);
    }

    if (blockedSites.length > 0) {
        browser.webRequest.onBeforeRequest.addListener(
            redirect,
            { urls: blockedSites, types: ["main_frame"] },
            ["blocking"]
        );
    }
}

function sanitizeEntries(entries = []) {
    return entries
        .map((entry) => (typeof entry === "string" ? entry.trim() : ""))
        .filter((entry) => entry.length > 0);
}

function toUrl(value) {
    try {
        return new URL(value);
    } catch (error) {
        try {
            return new URL(`https://${value}`);
        } catch (innerError) {
            return null;
        }
    }
}

function entryToPattern(entry) {
    if (!entry) {
        return null;
    }

    if (entry.includes("*")) {
        return entry;
    }

    const url = toUrl(entry);
    if (!url || !url.hostname) {
        return null;
    }

    const host = url.hostname.replace(/^www\./i, "");
    if (!host) {
        return null;
    }

    return `*://*.${host}/*`;
}

function entriesToPatterns(entries = []) {
    const sanitized = sanitizeEntries(entries);
    const unique = new Set();

    sanitized.forEach((entry) => {
        const pattern = entryToPattern(entry);
        if (pattern) {
            unique.add(pattern);
        }
    });

    return Array.from(unique);
}

async function loadSettings() {
    const stored = await browser.storage.local.get({
        redirectUrl: DEFAULT_REDIRECT,
        blockedEntries: null,
        blockedUrls: []
    });

    redirectTarget = stored.redirectUrl || DEFAULT_REDIRECT;

    const entries = Array.isArray(stored.blockedEntries) ? stored.blockedEntries : stored.blockedUrls;

    blockedSites = entriesToPatterns(entries);
    updateListener();
}

browser.storage.onChanged.addListener((changes, areaName) => {
    if (areaName !== "local") {
        return;
    }

    if (changes.redirectUrl) {
        redirectTarget = changes.redirectUrl.newValue || DEFAULT_REDIRECT;
    }

    if (changes.blockedEntries) {
        blockedSites = entriesToPatterns(changes.blockedEntries.newValue);
    } else if (changes.blockedUrls) {
        blockedSites = entriesToPatterns(changes.blockedUrls.newValue);
    }

    updateListener();
});

browser.runtime.onInstalled.addListener(() => {
    browser.runtime.openOptionsPage().catch(() => {});
});

loadSettings();
