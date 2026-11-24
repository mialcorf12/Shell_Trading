import pytest

from server import create_app


@pytest.fixture
def client(tmp_path):
    for d in ("ideas/draft", "ideas", "estrategias"):
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    app = create_app(tmp_path)
    app.config["TESTING"] = True
    return app.test_client()


def test_tree_lists_all_three_folders(client, tmp_path):
    (tmp_path / "ideas/draft/borrador.md").write_text("x", encoding="utf-8")
    res = client.get("/api/tree")
    assert res.status_code == 200
    assert res.get_json()["draft"] == ["borrador.md"]
    assert res.get_json()["ideas"] == []
    assert res.get_json()["strategies"] == []


def test_create_strategy_endpoint(client, tmp_path):
    res = client.post("/api/strategy", json={"name": "ORB_NY"})
    assert res.status_code == 201
    assert (tmp_path / "estrategias/ORB_NY.md").exists()


def test_create_strategy_duplicate_is_409(client):
    client.post("/api/strategy", json={"name": "ORB_NY"})
    res = client.post("/api/strategy", json={"name": "ORB_NY"})
    assert res.status_code == 409


def test_create_strategy_rejects_path_traversal(client, tmp_path):
    res = client.post("/api/strategy", json={"name": "../evil"})
    assert res.status_code == 400
    assert not (tmp_path / "evil.md").exists()


def test_promote_endpoint_moves_draft_to_ideas(client, tmp_path):
    (tmp_path / "ideas/draft/fvg.md").write_text("# FVG\n", encoding="utf-8")
    res = client.post("/api/promote", json={"draft": "fvg.md", "strategy": "FVG"})
    assert res.status_code == 201
    assert res.get_json()["idea"] == "FVG_01.md"
    assert (tmp_path / "ideas/FVG_01.md").exists()


def test_promote_missing_draft_is_404(client):
    res = client.post("/api/promote", json={"draft": "nope.md", "strategy": "FVG"})
    assert res.status_code == 404


def test_promote_rejects_path_traversal_in_draft(client, tmp_path):
    (tmp_path / "secreto.md").write_text("x", encoding="utf-8")
    res = client.post("/api/promote", json={"draft": "../../secreto.md", "strategy": "FVG"})
    assert res.status_code == 400
    assert (tmp_path / "secreto.md").exists()


def test_index_serves_mindmap_page(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"cytoscape" in res.data.lower()
    assert b'id="graph"' in res.data


def test_clean_endpoint_uses_injected_client(tmp_path):
    from tests.test_cleanup import FakeClient

    for d in ("ideas/draft", "ideas", "estrategias", "jira"):
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    (tmp_path / "jira/trading_agent_persona.md").write_text("P", encoding="utf-8")
    (tmp_path / "ideas/draft/fvg.md").write_text("x", encoding="utf-8")
    app = create_app(tmp_path, llm_client=FakeClient())
    app.config["TESTING"] = True
    res = app.test_client().post("/api/clean", json={"draft": "fvg.md", "strategy": "FVG"})
    assert res.status_code == 201
    assert res.get_json()["idea"] == "FVG_01.md"


def test_clean_endpoint_maps_llm_failure_to_502(tmp_path):
    from tests.test_cleanup import FakeClient

    for d in ("ideas/draft", "ideas", "estrategias", "jira"):
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    (tmp_path / "jira/trading_agent_persona.md").write_text("P", encoding="utf-8")
    (tmp_path / "ideas/draft/fvg.md").write_text("x", encoding="utf-8")
    app = create_app(tmp_path, llm_client=FakeClient(error=RuntimeError("down")))
    app.config["TESTING"] = True
    res = app.test_client().post("/api/clean", json={"draft": "fvg.md", "strategy": "FVG"})
    assert res.status_code == 502
    assert (tmp_path / "ideas/draft/fvg.md").exists()


def test_default_port_is_5001():
    import server

    assert server.DEFAULT_PORT == 5001


def test_app_url_points_to_default_port():
    import server

    assert server.app_url() == "http://127.0.0.1:5001/"


def test_index_has_helptext_for_promote_and_clean(tmp_path):
    app = create_app(tmp_path)
    html = app.test_client().get("/").get_data(as_text=True)
    assert "Tomás un borrador de ideas/draft/" in html
    assert "Hace lo mismo que promover" in html
