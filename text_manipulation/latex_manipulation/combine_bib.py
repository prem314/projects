# Paste this entire cell in Google Colab and run it.
# Make sure a.bib and b.bib are in the current working directory (e.g., upload via the Files sidebar).
# Optional: set DRY_RUN = True to preview without writing.

import os, shutil, re

DRY_RUN = False        # Set to True to preview missing keys without writing
MAKE_BACKUP = True     # Set to False to skip making b.bib.bak backup if b.bib exists

SRC = "a.bib"
DST = "b.bib"

def _read_with_fallback(path, encodings=("utf-8", "utf-8-sig", "latin-1", "cp1252")):
    last_err = None
    for enc in encodings:
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read(), enc
        except UnicodeDecodeError as e:
            last_err = e
        except FileNotFoundError:
            raise
    raise UnicodeDecodeError(f"Could not decode {path} with tried encodings", "", 0, 0, str(last_err))

def _balanced_end(text, start_idx, open_ch, close_ch):
    """Return index (exclusive) of the matching close for text[start_idx]==open_ch."""
    depth = 0
    in_quotes = False
    quote_esc = False
    escaped = False  # Tracks backslash escapes outside quote strings (e.g., TeX accents like \")
    i = start_idx
    n = len(text)
    while i < n:
        ch = text[i]
        if in_quotes:
            if quote_esc:
                quote_esc = False
            elif ch == "\\":
                quote_esc = True
            elif ch == '"':
                in_quotes = False
        else:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_quotes = True
            elif ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth == 0:
                    return i + 1
        i += 1
    raise ValueError("Unbalanced BibTeX entry delimiters")

META_TYPES = {"string", "preamble", "comment"}

def iter_bib_entries(text):
    """Yield dicts: {'type': str, 'key': str|None, 'text': full_entry}."""
    i = 0
    n = len(text)
    while True:
        at = text.find("@", i)
        if at == -1:
            break
        j = at + 1
        while j < n and text[j].isalpha():
            j += 1
        etype = text[at+1:j].strip()
        if not etype:
            i = at + 1
            continue
        # skip whitespace to opening delimiter
        while j < n and text[j].isspace():
            j += 1
        if j >= n or text[j] not in "{(":
            i = at + 1
            continue
        open_ch = text[j]
        close_ch = "}" if open_ch == "{" else ")"
        end = _balanced_end(text, j, open_ch, close_ch)
        full = text[at:end]

        key = None
        if etype.lower() not in META_TYPES:
            # Extract key: first top-level comma after opening delimiter
            pos = j + 1
            brace_depth = 0
            in_q = False
            esc = False
            key_buf = []
            while pos < end:
                ch = text[pos]
                if in_q:
                    if esc:
                        esc = False
                    elif ch == "\\":
                        esc = True
                    elif ch == '"':
                        in_q = False
                    key_buf.append(ch)
                else:
                    if ch == '"':
                        in_q = True
                        key_buf.append(ch)
                    elif ch == "{":
                        brace_depth += 1
                        key_buf.append(ch)
                    elif ch == "}":
                        if brace_depth > 0:
                            brace_depth -= 1
                        key_buf.append(ch)
                    elif ch == "," and brace_depth == 0:
                        break
                    else:
                        key_buf.append(ch)
                pos += 1
            raw_key = "".join(key_buf).strip().strip("{}\"").strip()
            if raw_key:
                key = re.split(r"\s|=", raw_key)[0].strip()

        yield {"type": etype, "key": key, "text": full}
        i = end

def parse_bib(text):
    """Return (ordered_keys, key->entry_text) for citation entries (ignores meta)."""
    order = []
    m = {}
    for ent in iter_bib_entries(text):
        k = ent["key"]
        t = ent["type"].lower()
        if k and t not in META_TYPES and k not in m:
            m[k] = ent["text"]
            order.append(k)
    return order, m

def ensure_trailing_newlines(s, min_newlines=2):
    tail = len(s) - len(s.rstrip("\n"))
    if tail >= min_newlines:
        return s
    return s.rstrip("\n") + ("\n" * min_newlines)

# --- main ---
if not os.path.exists(SRC):
    raise FileNotFoundError(f"'{SRC}' not found in working directory. Upload it first.")

a_text, _ = _read_with_fallback(SRC)
try:
    b_text, _ = _read_with_fallback(DST)
except FileNotFoundError:
    b_text = ""

a_order, a_map = parse_bib(a_text)
_, b_map = parse_bib(b_text)

missing = [k for k in a_order if k not in b_map]

if not missing:
    print("No missing entries. b.bib already contains all keys from a.bib.")
else:
    print(f"Found {len(missing)} missing entr{'y' if len(missing)==1 else 'ies'}:")
    for k in missing:
        print("  -", k)

    if DRY_RUN:
        print("\nDRY RUN: No changes written to b.bib.")
    else:
        if MAKE_BACKUP and os.path.exists(DST):
            shutil.copyfile(DST, DST + ".bak")
            print(f"\nBackup created: {DST}.bak")
        append_blob = "\n\n".join(a_map[k].rstrip() for k in missing) + "\n"
        out_text = ensure_trailing_newlines(b_text, 2) + append_blob
        with open(DST, "w", encoding="utf-8", newline="\n") as f:
            f.write(out_text)
        print(f"\nAppended {len(missing)} entr{'y' if len(missing)==1 else 'ies'} to {DST}.")
