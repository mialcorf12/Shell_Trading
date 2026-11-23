import pytest

from ideas_core import cleanup, store


class FakeClient:
    def __init__(self, reply="# FVG depurada\n\nRegla clara.\n", error=None):
        self.reply = reply
        self.error = error
        self.calls = []

    def rewrite(self, system, user):
        self.calls.append((system, user))
        if self.error:
            raise self.error
        return self.reply


@pytest.fixture
def ws(tmp_path):
    for d in ("Ideas/Draft", "Ideas", "Estrategias", "Jira"):
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    (tmp_path / "Jira/trading_agent_persona.md").write_text("PERSONA", encoding="utf-8")
    (tmp_path / "Ideas/Draft/fvg.md").write_text("# FVG reel\nidea sucia\n", encoding="utf-8")
    return tmp_path


def test_clean_sends_persona_as_system_and_draft_as_user(ws):
    client = FakeClient()
    cleanup.clean_draft(ws, "fvg.md", "FVG", client)
    system, user = client.calls[0]
    assert system == "PERSONA"
    assert "idea sucia" in user


def test_clean_writes_rewritten_text_into_new_idea(ws):
    cleanup.clean_draft(ws, "fvg.md", "FVG", FakeClient())
    idea = ws / "Ideas/FVG_01.md"
    assert idea.read_text(encoding="utf-8").startswith("# FVG depurada\n\nRegla clara.\n")
    assert not (ws / "Ideas/Draft/fvg.md").exists()


def test_clean_keeps_both_reference_sides(ws):
    cleanup.clean_draft(ws, "fvg.md", "FVG", FakeClient())
    assert store.read_references(ws / "Ideas/FVG_01.md") == {"Estrategia": ["FVG"], "Draft": ["fvg"]}
    assert store.read_references(ws / "Estrategias/FVG.md") == {"Ideas": ["FVG_01"]}


def test_llm_failure_leaves_draft_untouched(ws):
    with pytest.raises(RuntimeError):
        cleanup.clean_draft(ws, "fvg.md", "FVG", FakeClient(error=RuntimeError("api down")))
    assert (ws / "Ideas/Draft/fvg.md").exists()
    assert not (ws / "Ideas/FVG_01.md").exists()


def test_missing_persona_fails_before_moving_draft(ws):
    (ws / "Jira/trading_agent_persona.md").unlink()
    with pytest.raises(FileNotFoundError):
        cleanup.clean_draft(ws, "fvg.md", "FVG", FakeClient())
    assert (ws / "Ideas/Draft/fvg.md").exists()
