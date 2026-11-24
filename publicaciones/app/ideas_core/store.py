"""File-system store for ideas/draft, ideas and estrategias (under publicaciones/).

Relations are by strategy name only (S3): an idea file ``ORB_NY_01.md``
belongs to the strategy ``ORB_NY``, whose file is ``ORB_NY.md``.
"""
from __future__ import annotations

import re
from pathlib import Path

FOLDERS = {
    "draft": "ideas/draft",
    "ideas": "ideas",
    "strategies": "estrategias",
    "context": "contexto",
}

REFERENCES_HEADING = "## Referencias"
_IDEA_RE = re.compile(r"^(?P<strategy>.+)_(?P<num>\d+)\.md$")
_LINK_RE = re.compile(r"^- (?P<label>[^:]+): \[\[(?P<target>.+)\]\]$")


def strategy_name(file_name: str) -> str:
    """Return the strategy a file belongs to, from its file name."""
    match = _IDEA_RE.match(file_name)
    if match:
        return match.group("strategy")
    return file_name[: -len(".md")] if file_name.endswith(".md") else file_name


def list_files(root: Path) -> dict:
    """Return the markdown file names in each managed folder, sorted."""
    tree = {}
    for key, rel in FOLDERS.items():
        folder = Path(root) / rel
        names = []
        if folder.is_dir():
            names = sorted(
                p.name
                for p in folder.iterdir()
                if p.is_file() and p.suffix == ".md" and not p.name.startswith(".")
            )
        tree[key] = names
    return tree


def read_references(path: Path) -> dict:
    """Parse the trailing ``## Referencias`` section into {label: [targets]}."""
    text = Path(path).read_text(encoding="utf-8")
    if REFERENCES_HEADING not in text:
        return {}
    section = text.split(REFERENCES_HEADING, 1)[1]
    refs = {}
    for line in section.splitlines():
        match = _LINK_RE.match(line.strip())
        if match:
            refs.setdefault(match.group("label"), []).append(match.group("target"))
    return refs


def next_idea_name(root: Path, strategy: str) -> str:
    """Return the next free idea file name, e.g. ORB_NY_03.md."""
    folder = Path(root) / FOLDERS["ideas"]
    taken = []
    for p in folder.glob(f"{strategy}_*.md"):
        match = _IDEA_RE.match(p.name)
        if match and match.group("strategy") == strategy:
            taken.append(int(match.group("num")))
    return f"{strategy}_{(max(taken) if taken else 0) + 1:02d}.md"


def create_strategy(root: Path, strategy: str) -> Path:
    """Create estrategias/<strategy>.md. Refuses to overwrite an existing file."""
    path = Path(root) / FOLDERS["strategies"] / f"{strategy}.md"
    if path.exists():
        raise FileExistsError(str(path))
    path.write_text(f"# {strategy}\n", encoding="utf-8")
    return path


def promote_draft(root: Path, draft_name: str, strategy: str) -> Path:
    """Move ideas/draft/<draft_name> to ideas/<STRATEGY>_<NN>.md and link both sides.

    The idea records its strategy and its draft origin; the strategy records the
    new idea. The strategy file is created when missing (S3: one per strategy).
    """
    root = Path(root)
    source = root / FOLDERS["draft"] / draft_name
    if not source.is_file():
        raise FileNotFoundError(str(source))

    strategy_path = root / FOLDERS["strategies"] / f"{strategy}.md"
    if not strategy_path.exists():
        create_strategy(root, strategy)

    idea_name = next_idea_name(root, strategy)
    target = root / FOLDERS["ideas"] / idea_name
    origin = draft_name[: -len(".md")] if draft_name.endswith(".md") else draft_name
    source.replace(target)
    write_references(target, {"Estrategia": [strategy], "Draft": [origin]})

    strategy_refs = read_references(strategy_path)
    ideas = strategy_refs.get("Ideas", [])
    stem = idea_name[: -len(".md")]
    if stem not in ideas:
        ideas.append(stem)
    strategy_refs["Ideas"] = ideas
    write_references(strategy_path, strategy_refs)
    return target


def write_references(path: Path, refs: dict) -> None:
    """Replace (or append) the ``## Referencias`` section, keeping the body intact."""
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    if REFERENCES_HEADING in text:
        text = text.split(REFERENCES_HEADING, 1)[0]
    body = text.rstrip() + "\n"
    lines = [REFERENCES_HEADING]
    for label, targets in refs.items():
        for target in targets:
            lines.append(f"- {label}: [[{target}]]")
    path.write_text(body + "\n" + "\n".join(lines) + "\n", encoding="utf-8")
