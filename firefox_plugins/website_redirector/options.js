const DEFAULT_REDIRECT = "https://breakfreefromaddictions.blogspot.com/p/addiction-free.html";

const form = document.getElementById("settings-form");
const redirectInput = document.getElementById("redirectUrl");
const blockedTextarea = document.getElementById("blockedUrls");
const statusEl = document.getElementById("status");

function textToList(text) {
    return text
        .split(/[\n,]/)
        .map((entry) => entry.trim())
        .filter((entry) => entry.length);
}

function listToText(list = []) {
    return list.join("\n");
}

async function loadSettings() {
    const stored = await browser.storage.local.get({
        redirectUrl: DEFAULT_REDIRECT,
        blockedEntries: null,
        blockedUrls: []
    });

    redirectInput.value = stored.redirectUrl || DEFAULT_REDIRECT;

    const entries = Array.isArray(stored.blockedEntries) ? stored.blockedEntries : stored.blockedUrls;
    blockedTextarea.value = listToText(entries);
}

async function saveSettings(event) {
    event.preventDefault();
    const redirectUrl = redirectInput.value.trim() || DEFAULT_REDIRECT;
    const blockedEntries = textToList(blockedTextarea.value);

    await browser.storage.local.set({ redirectUrl, blockedEntries });

    statusEl.textContent = "Settings saved.";
    setTimeout(() => {
        statusEl.textContent = "";
    }, 3000);
}

form.addEventListener("submit", saveSettings);

loadSettings();
