"""Cleanup of a draft into a new idea, via an injected LLM client (S7, S8).

Order matters: persona and LLM call happen BEFORE the draft is moved, so any
failure leaves Ideas/Draft untouched.
"""
from __future__ import annotations

from pathlib import Path

from . import store

PERSONA_RELATIVE = "Jira/trading_agent_persona.md"


def clean_draft(root: Path, draft_name: str, strategy: str, client) -> Path:
    root = Path(root)
    persona = (root / PERSONA_RELATIVE).read_text(encoding="utf-8")
    source = root / store.FOLDERS["draft"] / draft_name
    if not source.is_file():
        raise FileNotFoundError(str(source))
    rewritten = client.rewrite(system=persona, user=source.read_text(encoding="utf-8"))

    target = store.promote_draft(root, draft_name, strategy)
    refs = store.read_references(target)
    target.write_text(rewritten.rstrip() + "\n", encoding="utf-8")
    store.write_references(target, refs)
    return target
