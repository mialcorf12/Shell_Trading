"""Cleanup of a draft into a new idea, via an injected LLM client (S7, S8).

Order matters: persona and LLM call happen BEFORE the draft is moved, so any
failure leaves ideas/draft untouched.
"""
from __future__ import annotations

from pathlib import Path

from . import store

# jira/ stays at the project root (parents[3] of this file: ideas_core -> app -> publicaciones -> root).
PERSONA_PATH = Path(__file__).resolve().parents[3] / "jira" / "trading_agent_persona.md"


def clean_draft(root: Path, draft_name: str, strategy: str, client, persona_path: Path = PERSONA_PATH) -> Path:
    root = Path(root)
    persona = Path(persona_path).read_text(encoding="utf-8")
    source = root / store.FOLDERS["draft"] / draft_name
    if not source.is_file():
        raise FileNotFoundError(str(source))
    rewritten = client.rewrite(system=persona, user=source.read_text(encoding="utf-8"))
    # Validate BEFORE moving anything: an empty reply must leave the draft where it is.
    if not isinstance(rewritten, str) or not rewritten.strip():
        raise ValueError("la IA devolvió una respuesta vacía; el borrador queda intacto")

    target = store.promote_draft(root, draft_name, strategy)
    refs = store.read_references(target)
    target.write_text(rewritten.rstrip() + "\n", encoding="utf-8")
    store.write_references(target, refs)
    return target
