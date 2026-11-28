#!/usr/bin/env python3
"""Compare two versions of a filing section sentence by sentence. Standard library only.

    python section_diff.py older.txt newer.txt            # Markdown: added, removed and reworded passages
    python section_diff.py older.txt newer.txt --json

Each file holds the `text` of one item as the filing-sections call returned it. The script
finds what a reader cannot find by eye in two 80,000-character sections: the sentences that
exist only in the newer filing, the ones that exist only in the older, and the ones that were
reworded. It reports what changed; deciding what matters is the reader's job.
"""
import difflib
import json
import re
import sys

REWORDED = 0.6   # two sentences this alike are one sentence that was edited, not a removal plus an addition
MIN_WORDS = 6    # shorter fragments are headings, page numbers and list markers
PAGE_BREAK = re.compile(r"^\s*(\d{1,3}|table of contents|part [ivx]+.*|item \d+[a-c]?\..*)\s*$", re.I)


def sentences(text):
    """Sentences in reading order, with page furniture removed and line breaks inside a sentence healed."""
    lines = [line for line in text.splitlines() if line.strip() and not PAGE_BREAK.match(line)]
    flat = re.sub(r"\s+", " ", " ".join(lines))
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z“\"(])", flat)
    return [p.strip() for p in parts if len(p.split()) >= MIN_WORDS]


def key(sentence):
    return re.sub(r"[^a-z0-9 ]", "", sentence.lower())


def compare(older, newer):
    old, new = sentences(older), sentences(newer)
    matcher = difflib.SequenceMatcher(a=[key(s) for s in old], b=[key(s) for s in new], autojunk=False)
    added, removed, reworded, same = [], [], [], 0
    for tag, a0, a1, b0, b1 in matcher.get_opcodes():
        if tag == "equal":
            same += a1 - a0
            continue
        gone, come = old[a0:a1], new[b0:b1]
        used = set()
        for before in gone:
            best, score = None, REWORDED
            for index, after in enumerate(come):
                if index in used:
                    continue
                ratio = difflib.SequenceMatcher(a=key(before), b=key(after), autojunk=False).ratio()
                if ratio > score:
                    best, score = index, ratio
            if best is None:
                removed.append(before)
            else:
                used.add(best)
                reworded.append({"before": before, "after": come[best], "similarity": round(score, 2)})
        added += [after for index, after in enumerate(come) if index not in used]
    return {"older_characters": len(older), "newer_characters": len(newer), "older_sentences": len(old), "newer_sentences": len(new),
            "unchanged": same, "added": added, "removed": removed, "reworded": reworded}


def numbers(sentence):
    return set(re.findall(r"\$?\d[\d,.]*%?", sentence))


def markdown(r):
    out = [f"Older section: {r['older_characters']:,} characters, {r['older_sentences']} sentences. "
           f"Newer: {r['newer_characters']:,} characters, {r['newer_sentences']} sentences. "
           f"{r['unchanged']} sentences unchanged, {len(r['added'])} added, {len(r['removed'])} removed, {len(r['reworded'])} reworded.", ""]
    figures = [c for c in r["reworded"] if numbers(c["before"]) != numbers(c["after"])]
    out += [f"## Reworded with a different figure ({len(figures)})", ""]
    out += [f"- BEFORE: {c['before']}\n  AFTER: {c['after']}" for c in figures]
    out += ["", f"## Added in the newer filing ({len(r['added'])})", ""] + [f"- {s}" for s in r["added"]]
    out += ["", f"## Removed from the older filing ({len(r['removed'])})", ""] + [f"- {s}" for s in r["removed"]]
    rest = [c for c in r["reworded"] if c not in figures]
    out += ["", f"## Reworded, same figures ({len(rest)})", ""] + [f"- BEFORE: {c['before']}\n  AFTER: {c['after']}" for c in rest]
    return "\n".join(out)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    with open(sys.argv[1]) as older, open(sys.argv[2]) as newer:
        result = compare(older.read(), newer.read())
    print(json.dumps(result, indent=1) if "--json" in sys.argv else markdown(result))
