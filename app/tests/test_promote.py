import pytest

from ideas_core import store


@pytest.fixture
def ws(tmp_path):
    for d in ("Ideas/Draft", "Ideas", "Estrategias"):
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    return tmp_path


def test_next_idea_name_starts_at_01_for_new_strategy(ws):
    assert store.next_idea_name(ws, "ORB_NY") == "ORB_NY_01.md"


def test_next_idea_name_increments_past_existing_ideas(ws):
    (ws / "Ideas/ORB_NY_01.md").write_text("x", encoding="utf-8")
    (ws / "Ideas/ORB_NY_02.md").write_text("x", encoding="utf-8")
    assert store.next_idea_name(ws, "ORB_NY") == "ORB_NY_03.md"


def test_create_strategy_writes_file_with_heading(ws):
    path = store.create_strategy(ws, "ORB_NY")
    assert path == ws / "Estrategias/ORB_NY.md"
    assert path.read_text(encoding="utf-8").startswith("# ORB_NY\n")


def test_create_strategy_refuses_to_overwrite(ws):
    store.create_strategy(ws, "ORB_NY")
    with pytest.raises(FileExistsError):
        store.create_strategy(ws, "ORB_NY")


def test_promote_draft_moves_it_to_ideas_with_strategy_name(ws):
    (ws / "Ideas/Draft/fvg borrador.md").write_text("# FVG reel\n\nIdea sucia.\n", encoding="utf-8")

    new = store.promote_draft(ws, "fvg borrador.md", "FVG")

    assert new == ws / "Ideas/FVG_01.md"
    assert not (ws / "Ideas/Draft/fvg borrador.md").exists()
    assert new.read_text(encoding="utf-8").startswith("# FVG reel\n\nIdea sucia.\n")


def test_promote_draft_links_idea_and_strategy_both_ways(ws):
    (ws / "Ideas/Draft/fvg borrador.md").write_text("# FVG\n", encoding="utf-8")

    store.promote_draft(ws, "fvg borrador.md", "FVG")

    assert store.read_references(ws / "Ideas/FVG_01.md") == {
        "Estrategia": ["FVG"],
        "Draft": ["fvg borrador"],
    }
    assert store.read_references(ws / "Estrategias/FVG.md") == {"Ideas": ["FVG_01"]}


def test_promote_draft_keeps_existing_strategy_body_and_adds_idea(ws):
    strategy = ws / "Estrategias/FVG.md"
    strategy.write_text("# FVG\n\nReglas base.\n", encoding="utf-8")
    (ws / "Ideas/FVG_01.md").write_text("# previa\n", encoding="utf-8")
    store.write_references(strategy, {"Ideas": ["FVG_01"]})
    (ws / "Ideas/Draft/nueva.md").write_text("# nueva\n", encoding="utf-8")

    new = store.promote_draft(ws, "nueva.md", "FVG")

    assert new.name == "FVG_02.md"
    text = strategy.read_text(encoding="utf-8")
    assert text.startswith("# FVG\n\nReglas base.\n")
    assert store.read_references(strategy) == {"Ideas": ["FVG_01", "FVG_02"]}


def test_promote_draft_fails_when_draft_missing(ws):
    with pytest.raises(FileNotFoundError):
        store.promote_draft(ws, "no_existe.md", "FVG")
