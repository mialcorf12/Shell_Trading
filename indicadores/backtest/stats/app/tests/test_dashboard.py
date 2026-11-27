import csv
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP_DIR))

from server import DEFAULT_PORT, check_row, create_app, load_rows  # noqa: E402

COLS = [
    "estrategia", "simbolo", "timeframe", "periodo", "anos", "contratos", "tp_usd", "sl_usd", "trades",
    "win_rate_pct", "payoff", "profit_factor", "expectancy_usd", "net_profit_usd",
    "max_dd_usd", "max_consec_losses", "sharpe", "sortino", "top3_pct", "notas",
]


def write_csv(path: Path, rows: list[dict]) -> Path:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            full = {c: "" for c in COLS}
            full.update(r)
            w.writerow(full)
    return path


GOOD = {
    "estrategia": "deberia_1", "anos": "6", "contratos": "1", "tp_usd": "600", "sl_usd": "600", "trades": "150",
    "win_rate_pct": "45", "payoff": "1.8", "profit_factor": "1.6", "expectancy_usd": "35",
    "net_profit_usd": "5200", "max_dd_usd": "1800", "max_consec_losses": "5",
    "sharpe": "1.3", "sortino": "1.9", "top3_pct": "30", "notas": "buena",
}
BAD = dict(GOOD, estrategia="deberia_2", profit_factor="0.9", net_profit_usd="-400",
           expectancy_usd="-3", sharpe="0.2", top3_pct="80", notas="mala")
PENDING = {"estrategia": "deberia_3", "contratos": "1", "tp_usd": "100", "sl_usd": "600",
           "notas": "pendiente"}


def test_pending_row_has_no_data(tmp_path):
    rows = load_rows(write_csv(tmp_path / "r.csv", [PENDING]))
    assert rows[0]["veredicto"] == "pendiente"
    assert rows[0]["trades"] is None


def test_good_row_is_approved(tmp_path):
    rows = load_rows(write_csv(tmp_path / "r.csv", [GOOD]))
    assert rows[0]["veredicto"] == "aprueba"
    assert all(v is True for v in rows[0]["checks"].values())


def test_bad_row_is_discarded(tmp_path):
    rows = load_rows(write_csv(tmp_path / "r.csv", [BAD]))
    assert rows[0]["veredicto"] == "descarta"
    assert rows[0]["checks"]["profit_factor"] is False
    assert rows[0]["checks"]["top3_pct"] is False


def test_threshold_boundaries():
    # PF exacto 1.25 cumple (piso); trades 99 no cumple (mínimo 100)
    assert check_row({"trades": 99, "profit_factor": 1.25, "net_profit_usd": 1,
                      "expectancy_usd": 1, "sharpe": 1.0, "top3_pct": 50})["trades"] is False
    checks = check_row({"trades": 100, "profit_factor": 1.25, "net_profit_usd": 1,
                        "expectancy_usd": 1, "sharpe": 1.0, "top3_pct": 50})
    assert all(v is True for v in checks.values())


def test_net_profit_zero_is_not_positive():
    assert check_row({"net_profit_usd": 0})["net_profit_usd"] is False


def test_incomplete_when_metric_missing(tmp_path):
    partial = dict(GOOD, estrategia="deberia_4", sharpe="")
    rows = load_rows(write_csv(tmp_path / "r.csv", [partial]))
    assert rows[0]["veredicto"] == "incompleto"


def test_missing_csv_gives_empty_list(tmp_path):
    assert load_rows(tmp_path / "no_existe.csv") == []


def test_api_results_returns_rows_and_thresholds(tmp_path):
    csv_path = write_csv(tmp_path / "r.csv", [GOOD, PENDING])
    client = create_app(csv_path).test_client()
    data = client.get("/api/results").get_json()
    assert [r["veredicto"] for r in data["rows"]] == ["aprueba", "pendiente"]
    assert data["thresholds"]["trades"] == ["min", 100]


def test_index_serves_table(tmp_path):
    client = create_app(write_csv(tmp_path / "r.csv", [GOOD])).test_client()
    res = client.get("/")
    assert res.status_code == 200
    assert b'id="results"' in res.data
    assert b"/static/app.js" in res.data


def test_default_port_is_5002():
    assert DEFAULT_PORT == 5002


def test_loader_parses_contratos_as_int(tmp_path):
    rows = load_rows(write_csv(tmp_path / "r.csv", [GOOD, dict(GOOD, contratos="3")]))
    assert [r["contratos"] for r in rows] == [1, 3]
    assert all(type(r["contratos"]) is int for r in rows)


def test_api_returns_contratos_as_number_and_honors_filter(tmp_path):
    csv_path = write_csv(tmp_path / "r.csv", [GOOD, dict(GOOD, contratos="2", notas="dos"),
                                              dict(BAD, contratos="2")])
    client = create_app(csv_path).test_client()
    every = client.get("/api/results").get_json()["rows"]
    assert [r["contratos"] for r in every] == [1, 2, 2]
    two = client.get("/api/results?contratos=2").get_json()["rows"]
    assert [(r["contratos"], r["notas"]) for r in two] == [(2, "dos"), (2, "mala")]
    # la verdad del veredicto no cambia con contratos
    assert [r["veredicto"] for r in two] == ["aprueba", "descarta"]


def test_index_has_contratos_column_and_filter(tmp_path):
    client = create_app(write_csv(tmp_path / "r.csv", [GOOD])).test_client()
    html = client.get("/").get_data(as_text=True)
    assert 'id="f-contracts"' in html and '>Contratos</th>' in html
    for v in ("1", "2", "3", "4"):
        assert '<option value="%s">%s</option>' % (v, v) in html


def test_index_note_says_tp_sl_are_total_usd(tmp_path):
    client = create_app(write_csv(tmp_path / "r.csv", [GOOD])).test_client()
    html = client.get("/").get_data(as_text=True)
    assert ("TP/SL en USD totales de la operacion; con N contratos la distancia en puntos se "
            "divide entre N y el PnL y la comision escalan por N.") in html
    assert "por contrato" not in html and "x N" not in html


NQ_ROW = dict(GOOD, simbolo="NQ", contratos="1", notas="motor python; NQ 20 USD/punto")
MNQ_ROW = dict(BAD, simbolo="MNQ", notas="motor python; MNQ 2 USD/punto")


def test_api_hides_nq_rows(tmp_path):
    csv_path = write_csv(tmp_path / "r.csv", [NQ_ROW, MNQ_ROW])
    rows = create_app(csv_path).test_client().get("/api/results").get_json()["rows"]
    assert [r["simbolo"] for r in rows] == ["MNQ"]
    assert "invalido" not in rows[0]
    assert [r["veredicto"] for r in rows] == ["descarta"]


def test_api_simbolo_filter_and_default_all(tmp_path):
    csv_path = write_csv(tmp_path / "r.csv", [NQ_ROW, MNQ_ROW, dict(MNQ_ROW, contratos="2")])
    client = create_app(csv_path).test_client()
    assert len(client.get("/api/results").get_json()["rows"]) == 2
    mnq = client.get("/api/results?simbolo=MNQ").get_json()["rows"]
    assert [(r["simbolo"], r["contratos"]) for r in mnq] == [("MNQ", 1), ("MNQ", 2)]
    assert client.get("/api/results?simbolo=NQ").get_json()["rows"] == []
    both = client.get("/api/results?simbolo=MNQ&contratos=2").get_json()["rows"]
    assert [(r["simbolo"], r["contratos"]) for r in both] == [("MNQ", 2)]
    assert client.get("/api/results?simbolo=ES").get_json()["rows"] == []


def test_index_has_only_mnq_symbol_filter(tmp_path):
    client = create_app(write_csv(tmp_path / "r.csv", [GOOD])).test_client()
    html = client.get("/").get_data(as_text=True)
    assert 'id="f-symbol"' in html and '>Símbolo</th>' in html
    assert '<option value="MNQ">MNQ</option>' in html
    assert '<option value="NQ">NQ</option>' not in html
    assert '<option value="">todos</option>' in html

def test_api_tp_filter(tmp_path):
    rows_in = [dict(GOOD, tp_usd="600"), dict(GOOD, tp_usd="1000", sl_usd="2000"), dict(GOOD, tp_usd="100", estrategia="deberia_2")]
    client = create_app(write_csv(tmp_path / "r.csv", rows_in)).test_client()
    tp600 = client.get("/api/results?tp_usd=600").get_json()["rows"]
    assert [r["tp_usd"] for r in tp600] == [600]
    tp1000 = client.get("/api/results?tp_usd=1000&contratos=1").get_json()["rows"]
    assert [(r["tp_usd"], r["sl_usd"]) for r in tp1000] == [(1000, 2000)]
    assert client.get("/api/results?tp_usd=1500").get_json()["rows"] == []


def test_index_has_tp_filter(tmp_path):
    client = create_app(write_csv(tmp_path / "r.csv", [GOOD])).test_client()
    html = client.get("/").get_data(as_text=True)
    assert 'id="f-tp"' in html and '<option value="1500">$1500</option>' in html


def test_index_headers_sortable_from_contratos_to_veredicto(tmp_path):
    client = create_app(write_csv(tmp_path / "r.csv", [GOOD])).test_client()
    html = client.get("/").get_data(as_text=True)
    for key in ("anos", "contratos", "tp_usd", "sl_usd", "trades", "win_rate_pct", "payoff",
                "profit_factor", "expectancy_usd", "net_profit_usd", "max_dd_usd",
                "max_consec_losses", "sharpe", "sortino", "top3_pct", "veredicto"):
        assert 'data-key="%s"' % key in html, key
    assert 'data-key="simbolo"' not in html and 'data-key="notas"' not in html


def test_every_header_has_tooltip_text(tmp_path):
    import re
    client = create_app(write_csv(tmp_path / "r.csv", [GOOD])).test_client()
    html = client.get("/").get_data(as_text=True)
    thead = html[html.index("<thead>"):html.index("</thead>")]
    headers = re.findall(r'<th[^>]*data-tip="([^"]+)"[^>]*>([^<]+)</th>', thead)
    assert len(headers) == 19
    assert all(len(tip) > 20 for tip, _ in headers)
    assert "1 / (1 + payoff)" in dict((t, n) for t, n in headers) or any("1 / (1 + payoff)" in t for t, _ in headers)
    assert "th[data-tip]::after" in html or "th[data-tip]::after" in client.get("/").get_data(as_text=True)


ANOS_TIP = ("Años de historial usados en la corrida: 6 = completo, 3 y 1 = últimos años hasta la "
            "última vela. Los indicadores usan toda la historia para calentarse.")


def test_loader_parses_anos_as_int(tmp_path):
    rows = load_rows(write_csv(tmp_path / "r.csv", [GOOD, dict(GOOD, anos="3"), dict(GOOD, anos="1")]))
    assert [r["anos"] for r in rows] == [6, 3, 1]
    assert all(type(r["anos"]) is int for r in rows)


def test_api_anos_filter_and_verdict_unchanged(tmp_path):
    csv_path = write_csv(tmp_path / "r.csv", [GOOD, dict(GOOD, anos="3", notas="tres"),
                                              dict(BAD, anos="3"), dict(GOOD, anos="1", contratos="2")])
    client = create_app(csv_path).test_client()
    assert [r["anos"] for r in client.get("/api/results").get_json()["rows"]] == [6, 3, 3, 1]
    three = client.get("/api/results?anos=3").get_json()["rows"]
    assert [(r["anos"], r["notas"], r["veredicto"]) for r in three] == [
        (3, "tres", "aprueba"), (3, "mala", "descarta")]
    assert [(r["anos"], r["contratos"]) for r in
            client.get("/api/results?anos=1&contratos=2").get_json()["rows"]] == [(1, 2)]
    assert client.get("/api/results?anos=1&contratos=1").get_json()["rows"] == []


def test_index_has_anos_column_after_simbolo_filter_and_tooltip(tmp_path):
    client = create_app(write_csv(tmp_path / "r.csv", [GOOD])).test_client()
    html = client.get("/").get_data(as_text=True)
    thead = html[html.index("<thead>"):html.index("</thead>")]
    assert thead.index(">Símbolo</th>") < thead.index(">Años</th>") < thead.index(">Contratos</th>")
    assert 'data-tip="%s">Años</th>' % ANOS_TIP in thead
    sel = html[html.index('id="f-anos"'):]
    sel = sel[:sel.index("</select>")]
    assert ['<option value="">todos</option>', '<option value="1">1</option>',
            '<option value="3">3</option>', '<option value="6">6</option>'] == [
        line.strip() for line in sel.splitlines()[1:] if line.strip()]


# --- Estrategias recomendadas (acordeón) ---

def _windows(base: dict, nets=("100", "100", "100"), pfs=("1.6", "1.6", "1.6"),
             sharpes=("1.3", "1.3", "1.3")) -> list[dict]:
    """Tres filas (anos 6, 3, 1) del mismo grupo (estrategia, sl, contratos)."""
    out = []
    for anos, net, pf, sh in zip(("6", "3", "1"), nets, pfs, sharpes):
        out.append(dict(base, anos=anos, net_profit_usd=net, profit_factor=pf, sharpe=sh))
    return out


def test_recommend_ranking_order_with_tie_breaks(tmp_path):
    from server import recommend
    base = dict(GOOD, simbolo="MNQ", tp_usd="600", sl_usd="600", contratos="1")
    rows_in = (
        # e_low: 0 aprueba (PF < 1.25 en todas), 3 netos positivos
        _windows(dict(base, estrategia="e_low"), pfs=("1.1", "1.1", "1.1"))
        # e_top: 3 aprueba
        + _windows(dict(base, estrategia="e_top"))
        # e_two_a/b/c: 2 aprueba, 2 netos positivos; desempate por PF mínimo y luego Sharpe mínimo
        + _windows(dict(base, estrategia="e_two_a"), nets=("100", "100", "-50"), pfs=("1.6", "1.6", "0.9"))
        + _windows(dict(base, estrategia="e_two_b"), nets=("100", "100", "-50"), pfs=("1.6", "1.6", "0.95"),
                   sharpes=("1.3", "1.3", "0.2"))
        + _windows(dict(base, estrategia="e_two_c"), nets=("100", "100", "-50"), pfs=("1.6", "1.6", "0.95"),
                   sharpes=("1.3", "1.3", "0.5"))
        # e_two_d: 2 aprueba pero 3 netos positivos -> va antes de e_two_a/b/c
        + _windows(dict(base, estrategia="e_two_d"), nets=("100", "100", "20"), pfs=("1.6", "1.6", "1.1"))
    )
    rows = load_rows(write_csv(tmp_path / "r.csv", rows_in))
    out = recommend(rows, top_n=10)
    names = [c["estrategia"] for c in out["600"]]
    assert names == ["e_top", "e_two_d", "e_two_c", "e_two_b", "e_two_a", "e_low"]
    assert [c["aprueba"] for c in out["600"]] == [3, 2, 2, 2, 2, 0]
    top = out["600"][0]
    assert top["sl_usd"] == 600 and top["contratos"] == 1


def test_recommend_skips_groups_with_missing_window(tmp_path):
    from server import recommend
    base = dict(GOOD, simbolo="MNQ", tp_usd="200", sl_usd="600", contratos="1")
    full = _windows(dict(base, estrategia="completa"), pfs=("1.1", "1.1", "1.1"))
    partial = _windows(dict(base, estrategia="falta_1"))[:2]  # solo 6 y 3
    rows = load_rows(write_csv(tmp_path / "r.csv", full + partial))
    assert [c["estrategia"] for c in recommend(rows)["200"]] == ["completa"]


def test_recommend_group_key_separates_sl_and_contratos(tmp_path):
    from server import recommend
    base = dict(GOOD, simbolo="MNQ", tp_usd="100", estrategia="x")
    rows_in = (_windows(dict(base, sl_usd="600", contratos="1"))
               + _windows(dict(base, sl_usd="100", contratos="1"))
               + _windows(dict(base, sl_usd="600", contratos="2")))
    rows = load_rows(write_csv(tmp_path / "r.csv", rows_in))
    keys = [(c["sl_usd"], c["contratos"]) for c in recommend(rows)["100"]]
    assert sorted(keys) == [(100, 1), (600, 1), (600, 2)]


def test_recommend_respects_top_n_and_ascending_tp_order(tmp_path):
    from server import recommend
    rows_in = []
    for tp, sl in (("1500", "2000"), ("100", "600"), ("1000", "2000"), ("300", "600")):
        for i in range(7):
            rows_in += _windows(dict(GOOD, simbolo="MNQ", tp_usd=tp, sl_usd=sl, contratos="1",
                                     estrategia="s%d" % i))
    rows = load_rows(write_csv(tmp_path / "r.csv", rows_in))
    out = recommend(rows)
    assert list(out.keys()) == ["100", "300", "1000", "1500"]
    assert all(len(v) == 5 for v in out.values())
    assert len(recommend(rows, top_n=2)["300"]) == 2


def test_recommend_fields_and_no_mdd(tmp_path):
    from server import recommend
    rows_in = _windows(dict(GOOD, simbolo="MNQ", tp_usd="600", sl_usd="600", contratos="1"),
                       nets=("5200", "-30", "800"))
    rows = load_rows(write_csv(tmp_path / "r.csv", rows_in))
    cand = recommend(rows)["600"][0]
    assert cand["neto_by_anos"] == {"6": 5200, "3": -30, "1": 800}
    assert cand["aprueba"] == 2
    assert set(cand["detalle"].keys()) == {"6", "3", "1"}
    det = cand["detalle"]["3"]
    assert set(det.keys()) == {"win_rate_pct", "profit_factor", "expectancy_usd", "net_profit_usd",
                               "max_consec_losses", "sharpe", "top3_pct", "veredicto"}
    assert det["net_profit_usd"] == -30 and det["veredicto"] == "descarta"
    import json
    assert "max_dd" not in json.dumps(recommend(rows))


def test_api_recommended_shape(tmp_path):
    rows_in = []
    for tp, sl in (("1000", "2000"), ("200", "600")):
        rows_in += _windows(dict(GOOD, simbolo="MNQ", tp_usd=tp, sl_usd=sl, contratos="1"))
    rows_in += _windows(dict(GOOD, simbolo="MNQ", tp_usd="200", sl_usd="600", contratos="2",
                             top3_pct=""))
    client = create_app(write_csv(tmp_path / "r.csv", rows_in)).test_client()
    res = client.get("/api/recommended")
    assert res.status_code == 200
    body = res.get_data(as_text=True)
    assert body.index('"200"') < body.index('"1000"')
    data = res.get_json()
    assert list(data.keys()) == ["por_tp"]
    assert list(data["por_tp"].keys()) == ["200", "1000"]
    first = data["por_tp"]["200"][0]
    assert first["neto_by_anos"] == {"6": 100, "3": 100, "1": 100}
    assert isinstance(first["sl_usd"], (int, float)) and first["contratos"] == 1
    missing = [c for c in data["por_tp"]["200"] if c["contratos"] == 2][0]
    assert missing["detalle"]["6"]["top3_pct"] is None


def test_index_has_closed_recommended_accordion(tmp_path):
    import re
    client = create_app(write_csv(tmp_path / "r.csv", [GOOD])).test_client()
    html = client.get("/").get_data(as_text=True)
    tag = re.search(r'<details[^>]*id="recomendadas"[^>]*>', html).group(0)
    assert "open" not in tag
    assert "<summary>Estrategias recomendadas</summary>" in html
    sel = html[html.index('id="rec-anos"'):]
    sel = sel[:sel.index("</select>")]
    assert re.findall(r'<option value="(\d)"', sel) == ["1", "3", "6"]
    assert "Años para detalle" in html
    rec = html[html.index('id="recomendadas"'):html.index("</details>")]
    rec += html[html.index('<template id="rec-table">'):html.index("</template>")]
    assert "MDD" not in rec and "max_dd" not in rec
    assert ('data-tip="Número de ventanas (6, 3 y 1 años) donde el veredicto es aprueba">'
            'Aprueba (de 3años)</th>') in rec
    heads = re.findall(r'<th[^>]*data-tip="[^"]+"[^>]*>([^<]+)</th>', rec)
    assert heads == ["Estrategia", "SL $", "Contratos", "Aprueba (de 3años)", "Neto 6a $", "Neto 3a $",
                     "Neto 1a $", "PF", "Expectancy $", "Net $", "Racha pérd.", "Sharpe",
                     "Top3 %", "Veredicto", "Win %"]
