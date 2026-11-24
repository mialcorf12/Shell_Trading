from pathlib import Path

import pytest

from ideas_core import store


@pytest.fixture
def ws(tmp_path):
    for d in ("ideas/draft", "ideas", "estrategias"):
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    return tmp_path


def test_strategy_name_strips_numeric_suffix():
    assert store.strategy_name("ORB_NY_01.md") == "ORB_NY"
    assert store.strategy_name("FVG_12.md") == "FVG"


def test_strategy_name_of_plain_strategy_file_is_its_stem():
    assert store.strategy_name("ORB_NY.md") == "ORB_NY"


def test_list_files_groups_by_folder(ws):
    (ws / "ideas/draft/borrador.md").write_text("x", encoding="utf-8")
    (ws / "ideas/ORB_NY_01.md").write_text("x", encoding="utf-8")
    (ws / "estrategias/ORB_NY.md").write_text("x", encoding="utf-8")

    tree = store.list_files(ws)

    assert tree["draft"] == ["borrador.md"]
    assert tree["ideas"] == ["ORB_NY_01.md"]
    assert tree["strategies"] == ["ORB_NY.md"]


def test_list_files_ignores_non_md_and_hidden_files(ws):
    (ws / "ideas/.gitkeep").write_text("", encoding="utf-8")
    (ws / "ideas/notas.txt").write_text("x", encoding="utf-8")
    assert store.list_files(ws)["ideas"] == []


def test_write_references_appends_section_at_end(ws):
    f = ws / "ideas/ORB_NY_01.md"
    f.write_text("# Idea\n\nCuerpo original.\n", encoding="utf-8")

    store.write_references(f, {"Estrategia": ["ORB_NY"], "Draft": ["borrador"]})

    text = f.read_text(encoding="utf-8")
    assert text.startswith("# Idea\n\nCuerpo original.\n")
    assert text.rstrip().endswith(
        "## Referencias\n- Estrategia: [[ORB_NY]]\n- Draft: [[borrador]]"
    )


def test_write_references_replaces_existing_section_without_duplicating(ws):
    f = ws / "ideas/ORB_NY_01.md"
    f.write_text("# Idea\n", encoding="utf-8")
    store.write_references(f, {"Estrategia": ["ORB_NY"]})
    store.write_references(f, {"Estrategia": ["ORB_NY"], "Draft": ["borrador"]})

    text = f.read_text(encoding="utf-8")
    assert text.count("## Referencias") == 1
    assert store.read_references(f) == {"Estrategia": ["ORB_NY"], "Draft": ["borrador"]}


def test_read_references_returns_empty_when_no_section(ws):
    f = ws / "ideas/ORB_NY_01.md"
    f.write_text("# Idea\n", encoding="utf-8")
    assert store.read_references(f) == {}


def test_write_references_keeps_body_text_below_nothing_else_changed(ws):
    f = ws / "estrategias/ORB_NY.md"
    body = "# ORB NY\n\nReglas.\n\n- punto uno\n"
    f.write_text(body, encoding="utf-8")
    store.write_references(f, {"Ideas": ["ORB_NY_01", "ORB_NY_02"]})
    assert f.read_text(encoding="utf-8").startswith(body)


def test_list_files_includes_context_folder(ws):
    (ws / "contexto").mkdir(exist_ok=True)
    (ws / "contexto/INDICADORES_TOP_7.md").write_text("x", encoding="utf-8")
    tree = store.list_files(ws)
    assert tree["context"] == ["INDICADORES_TOP_7.md"]


def test_list_files_context_folder_missing_is_empty(ws):
    assert store.list_files(ws)["context"] == []
