"""Queue of reel links in Ideas/Draft/reels.md.

Section A: new links.
Section B: processed links, each mapped to its idea or draft.
Section C: discarded links, each with its draft file (or "-") and a reason.

Rules:
- A link already in B is dropped from A.
- A link already in C is dropped from A, and its draft in Ideas/Draft is deleted.
- Sections stay sorted by URL.
Processing a link (reading the video, writing the draft) is not done here.
"""
from __future__ import annotations

from pathlib import Path

NEW_HEADING = "## A) Links nuevos"
DONE_HEADING = "## B) Links procesados"
DISCARD_HEADING = "## C) Links descartados"
EMPTY = "(vacío)"
_ARROW = " → "
_BAR = " | "


def _section(line: str):
    if line.startswith(NEW_HEADING):
        return "new"
    if line.startswith(DONE_HEADING):
        return "done"
    if line.startswith(DISCARD_HEADING):
        return "discard"
    return None


def _items(text: str):
    """Yield (section, item) for every list item or bare URL line."""
    section = None
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("## "):
            section = _section(line)
            continue
        if line.startswith("- "):
            item = line[2:].strip()
        elif line.startswith("http"):
            item = line
        else:
            continue
        if item:
            yield section, item


def parse(text: str):
    """Return (new_urls, {url: idea}) from the reels.md text."""
    new, done = [], {}
    for section, item in _items(text):
        if section == "new":
            new.append(item)
        elif section == "done":
            url, _, idea = item.partition(_ARROW)
            done[url.strip()] = idea.strip()
    return new, done


def parse_discarded(text: str):
    """Return {url: (draft_or_dash, reason)} from section C."""
    discarded = {}
    for section, item in _items(text):
        if section != "discard":
            continue
        url, _, rest = item.partition(_ARROW)
        draft, _, reason = rest.partition(_BAR)
        discarded[url.strip()] = (draft.strip() or "-", reason.strip())
    return discarded


def check(new: list, done: dict, discarded: dict):
    """Split new links into (pending, removed_processed, discarded_hit)."""
    pending, removed, discarded_hit, seen = [], [], [], set()
    for url in new:
        if url in seen:
            continue
        seen.add(url)
        if url in discarded:
            discarded_hit.append(url)
        elif url in done:
            removed.append(url)
        else:
            pending.append(url)
    return pending, removed, discarded_hit


def mark_done(new: list, done: dict, url: str, idea: str):
    """Move url from A to B with its idea. Returns (new, done) with B sorted."""
    if url in done:
        raise ValueError(f"already processed: {url}")
    new = [u for u in new if u != url]
    done = dict(done)
    done[url] = idea
    return new, dict(sorted(done.items()))


def mark_discarded(new: list, done: dict, discarded: dict, url: str, reason: str):
    """Move url from A or B to C. Its draft (if any) is recorded for deletion."""
    if url in discarded:
        raise ValueError(f"already discarded: {url}")
    if url not in done and url not in new:
        raise ValueError(f"not in A or B: {url}")
    draft = _draft_name(done.get(url, "-"))
    new = [u for u in new if u != url]
    done = {u: v for u, v in done.items() if u != url}
    discarded = dict(discarded)
    discarded[url] = (draft, reason)
    return new, done, dict(sorted(discarded.items()))


def _draft_name(value: str) -> str:
    """Only reel_*.md and post_*.md drafts count; promoted ideas (FVG_01.md) are never deleted."""
    is_draft = value.startswith(("reel_", "post_")) and value.endswith(".md")
    return value if is_draft else "-"


def delete_draft(folder: Path, name: str) -> bool:
    """Delete Ideas/Draft/<name> if it is a reel draft. Returns True if deleted."""
    if _draft_name(name) == "-":
        return False
    target = Path(folder) / name
    if target.is_file():
        target.unlink()
        return True
    return False


def render(header: str, new: list, done: dict, discarded: dict | None = None) -> str:
    discarded = discarded or {}
    out = header.rstrip() + "\n\n" + NEW_HEADING + "\n\n"
    out += "\n".join(f"- {u}" for u in sorted(set(new))) + "\n" if new else EMPTY + "\n"
    out += "\n" + DONE_HEADING + "\n\n"
    out += "\n".join(f"- {u}{_ARROW}{idea}" for u, idea in sorted(done.items())) + "\n" if done else ""
    out += "\n" + DISCARD_HEADING + "\n\n"
    out += (
        "\n".join(f"- {u}{_ARROW}{draft}{_BAR}{reason}" for u, (draft, reason) in sorted(discarded.items())) + "\n"
        if discarded else ""
    )
    return out


def header_of(text: str) -> str:
    """Everything before the section A heading (the processing rules)."""
    return text.split(NEW_HEADING, 1)[0]


def run_check(path: Path) -> dict:
    """Apply the A-vs-B and A-vs-C rules to the file in place."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    new, done = parse(text)
    discarded = parse_discarded(text)
    pending, removed, discarded_hit = check(new, done, discarded)
    for url in discarded_hit:
        delete_draft(path.parent, discarded[url][0])
    path.write_text(render(header_of(text), pending, done, discarded), encoding="utf-8")
    return {"pending": pending, "removed": removed, "discarded_hit": discarded_hit}


def run_mark_done(path: Path, url: str, idea: str) -> None:
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    new, done = parse(text)
    new, done = mark_done(new, done, url, idea)
    path.write_text(render(header_of(text), new, done, parse_discarded(text)), encoding="utf-8")


def run_discard(path: Path, url: str, reason: str) -> None:
    """Discard a link: move it to C and delete its reel draft from the folder."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    new, done = parse(text)
    new, done, discarded = mark_discarded(new, done, parse_discarded(text), url, reason)
    delete_draft(path.parent, discarded[url][0])
    path.write_text(render(header_of(text), new, done, discarded), encoding="utf-8")
