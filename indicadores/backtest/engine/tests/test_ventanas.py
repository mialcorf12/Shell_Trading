"""Ventanas de años (``--anos 6,3,1``): inicio, filtro de entrada, periodo, CSV y JSON."""

import csv
import json
import math
from datetime import date

import pytest

from engine import INSTRUMENTS, restar_anos, window_start
from engine.cli import build_parser, run
from engine.data import Bars, load_csv, open_date
from engine.results_csv import HEADER, update_results
from engine.signals import compute_indicators, compute_signals, warmup_index
from engine.estrategias import POR_NOMBRE
from engine.simulate import entry_candidates, simulate

from .test_engine import _args, _read, _write_results

AI = HEADER.index("anos")
PI = HEADER.index("periodo")
NI = HEADER.index("notas")
NOMBRE = "deberia_1_amarilla"


def _segments_file(tmp_path, segments, amp=200.0):
    """``segments``: lista de (fecha ISO, n velas) desde las 09:00; precio senoidal continuo."""
    p = tmp_path / "mnq.csv"
    lines = ["datetime,open,high,low,close,volume"]
    k = 0
    for day, n in segments:
        for j in range(n):
            c = 100 + amp * math.sin(k / 7.0) + k * 0.05 * amp / 10 if amp else 100.0
            c = round(c * 4) / 4
            m = 9 * 60 + 1 + j
            lines.append("%s %02d:%02d:00,%s,%s,%s,%s,%d"
                         % (day, m // 60, m % 60, c, c + 0.5, c - 0.5, c, 10 + k % 5))
            k += 1
    p.write_text("\n".join(lines) + "\n")
    return p


SEGS = [("2022-06-01", 150), ("2024-01-02", 150)]  # anos=1 -> inicio 2023-01-02, vela 150


def _json(tmp_path, anos, tp=100, sl=600, c=1, nombre=NOMBRE):
    return json.loads((tmp_path / "trades" / ("MNQ_%s_tp%d_sl%d_c%d_a%d.json"
                                              % (nombre, tp, sl, c, anos))).read_text())


def _expected(data, start_fn, tp=100, sl=600, nombre=NOMBRE):
    """Operaciones esperadas con indicadores sobre TODA la historia y entradas desde start_fn."""
    bars = load_csv(str(data))
    inds = compute_indicators(bars)
    warm = warmup_index(inds)
    buy, sell, _tier = compute_signals(bars, inds, estrategias=[POR_NOMBRE[nombre]])[nombre]
    start = max(warm, start_fn(bars))
    trades = simulate(bars, buy, sell, tp, sl, start=start,
                      candidates=entry_candidates(buy, sell, start, edge=True), qty=1,
                      instrument=INSTRUMENTS["MNQ"])
    return bars, inds, warm, trades


# ---------- inicio de la ventana ----------

def test_window_start_calendar_years_and_full_history():
    primera, ultima = date(2020, 11, 22), date(2026, 11, 26)
    assert window_start(primera, ultima, 3) == date(2023, 11, 26)
    assert window_start(primera, ultima, 1) == date(2025, 11, 26)
    assert window_start(primera, ultima, 6) == primera  # 6 = historia completa


def test_window_start_leap_day_goes_to_feb_28():
    assert restar_anos(date(2024, 2, 29), 1) == date(2023, 2, 28)
    assert window_start(date(2020, 1, 1), date(2024, 2, 29), 1) == date(2023, 2, 28)
    assert restar_anos(date(2024, 2, 29), 4) == date(2020, 2, 29)


def test_cli_anos_option_defaults_and_rejects_other_values(tmp_path):
    assert build_parser().parse_args([]).anos == "6,3,1"
    data = _segments_file(tmp_path, SEGS)
    res = tmp_path / "resultados.csv"
    _write_results(res)
    before = res.read_bytes()
    for bad in ("2", "0", "6,5", ""):
        with pytest.raises(SystemExit):
            run(_args(tmp_path, data, res, "--anos", bad, "--estrategias", "1"))
    assert res.read_bytes() == before and not (tmp_path / "trades").exists()


# ---------- filtro de entrada y calentamiento ----------

def test_trades_only_from_window_start_with_warm_indicators(tmp_path, capsys):
    data = _segments_file(tmp_path, SEGS)
    res = tmp_path / "resultados.csv"
    _write_results(res)
    run(_args(tmp_path, data, res, "--strategies", NOMBRE, "--contratos", "1", "--anos", "6,1"))
    out = capsys.readouterr().out
    assert "anos=6 ventana=2022-06-01..2024-01-02 vela_inicial=0" in out
    assert "anos=1 ventana=2023-01-02..2024-01-02 vela_inicial=150" in out
    assert "corridas: 12; solapes totales: 0" in out

    a6, a1 = _json(tmp_path, 6), _json(tmp_path, 1)
    assert any(t["open_time"] < "2023-01-02" for t in a6)  # la historia completa opera antes
    assert a1 and all(t["open_time"] >= "2023-01-02" for t in a1)

    # indicadores calientes: mismas operaciones que con indicadores sobre toda la historia
    bars, inds, _warm, exp = _expected(data, lambda b: 150)
    assert [(t["open_time"], t["pnl_usd"]) for t in a1] == [
        (open_date(bars.om[t.entry_index]).isoformat() + " %02d:%02d"
         % ((bars.om[t.entry_index] % 1440) // 60, bars.om[t.entry_index] % 60), round(t.pnl_usd, 2))
        for t in exp]
    # si se reiniciaran en la ventana no habría RSI/MACD en sus primeras velas
    win_bars = Bars()
    for i in range(150, len(bars)):
        win_bars.append(bars.om[i], bars.open[i], bars.high[i], bars.low[i], bars.close[i],
                        bars.volume[i])
    reset_warm = warmup_index(compute_indicators(win_bars))
    assert reset_warm > 0 and all(inds[k][150] == inds[k][150] for k in ("rsi", "adx", "macdL", "macdH", "volRel"))
    assert exp[0].entry_index < 150 + reset_warm  # operación imposible con indicadores reiniciados

    got = _read(res)
    rows = {r[AI]: r for r in got[1:] if r[0] == NOMBRE and r[1] == "MNQ"
            and r[HEADER.index("tp_usd")] == "100" and r[HEADER.index("contratos")] == "1"}
    assert set(rows) == {"6", "1"}
    assert int(rows["1"][HEADER.index("trades")]) == len(a1)
    assert "; ventana 1 anos (2023-01-02..2024-01-02); " in rows["1"][NI]
    assert "; ventana 6 anos (2022-06-01..2024-01-02); " in rows["6"][NI]


def test_anos_6_reproduces_full_history_rule(tmp_path):
    data = _segments_file(tmp_path, SEGS)
    res = tmp_path / "resultados.csv"
    _write_results(res)
    run(_args(tmp_path, data, res, "--strategies", NOMBRE, "--contratos", "1", "--anos", "6"))
    _bars, _inds, warm, exp = _expected(data, lambda b: 0)  # regla previa: desde el warmup
    a6 = _json(tmp_path, 6)
    assert [t["pnl_usd"] for t in a6] == [round(t.pnl_usd, 2) for t in exp] and a6


# ---------- periodo ----------

def test_periodo_is_first_to_last_trade_open_date(tmp_path):
    data = _segments_file(tmp_path, SEGS)
    res = tmp_path / "resultados.csv"
    _write_results(res)
    run(_args(tmp_path, data, res, "--strategies", NOMBRE, "--contratos", "1", "--anos", "6,1"))
    inicio = {"6": "2022-06-01", "1": "2023-01-02"}
    con_trades = 0
    for r in _read(res)[1:]:
        if r[0] != NOMBRE or r[1] != "MNQ" or r[AI] not in ("6", "1"):
            continue
        js = _json(tmp_path, int(r[AI]), int(r[HEADER.index("tp_usd")]), int(r[HEADER.index("sl_usd")]))
        if js:
            con_trades += 1
            assert r[PI] == "%s..%s" % (js[0]["open_time"][:10], js[-1]["open_time"][:10])
        else:
            assert r[PI] == inicio[r[AI]] + "..2024-01-02"
    assert con_trades >= 2
    a6 = [r for r in _read(res)[1:] if r[0] == NOMBRE and r[AI] == "6" and r[1] == "MNQ"]
    assert any(r[PI].startswith("2022-06-01..") for r in a6)


def test_periodo_without_trades_is_window_start_to_last_bar(tmp_path):
    data = _segments_file(tmp_path, SEGS, amp=0)  # precio plano: sin señales
    res = tmp_path / "resultados.csv"
    _write_results(res)
    ups = run(_args(tmp_path, data, res, "--no-write", "--strategies", NOMBRE, "--contratos", "1",
                    "--anos", "3,1"))
    assert len(ups) == 12 and all(u["trades"] == "" for u in ups)
    assert {(u["anos"], u["periodo"]) for u in ups} == {(3, "2021-01-02..2024-01-02"),
                                                         (1, "2023-01-02..2024-01-02")}


def test_default_run_count_is_strategies_configs_contracts_anos(tmp_path):
    data = _segments_file(tmp_path, SEGS)
    ups = run(_args(tmp_path, data, tmp_path / "x.csv", "--no-write"))
    assert len(ups) == 9 * 6 * 4 * 3
    assert {u["anos"] for u in ups} == {6, 3, 1}


# ---------- CSV ----------

def test_csv_key_includes_anos(tmp_path):
    p = tmp_path / "resultados.csv"
    rows = _write_results(p)
    up = {"simbolo": "MNQ", "estrategia": NOMBRE, "tp_usd": 200, "sl_usd": 600, "contratos": 1}
    update_results(str(p), [dict(up, anos=3, trades="5")])
    got = _read(p)
    assert got[2] == rows[2]  # la fila anos=6 no se toca
    assert len(got) == 5 and got[4][AI] == "3" and got[4][HEADER.index("trades")] == "5"
    update_results(str(p), [dict(up, anos=3, trades="8")])
    got = _read(p)
    assert len(got) == 5 and got[4][HEADER.index("trades")] == "8"
    update_results(str(p), [dict(up, trades="9")])  # sin anos = 6
    got = _read(p)
    assert len(got) == 5 and got[2][HEADER.index("trades")] == "9" and got[2][AI] == "6"


def test_migration_inserts_anos_6_and_keeps_values(tmp_path):
    p = tmp_path / "resultados.csv"
    old_header = [h for h in HEADER if h != "anos"]
    old = ["deberia_4_verde", "MNQ", "1m", "2020-11-22..2026-11-26", "1", "1000", "2000", "4572",
           "86.4", "0.16", "1.01", "1.01", "4602.00", "13456.50", "3", "0.12", "0.16", "6.3",
           "#e07: regla, con comas"]
    with open(p, "w", newline="") as f:
        csv.writer(f, lineterminator="\r\n").writerows([old_header, old])
    update_results(str(p), [{"simbolo": "MNQ", "estrategia": "deberia_4_verde", "tp_usd": 1000,
                             "sl_usd": 2000, "contratos": 1, "anos": 1, "trades": "7"}])
    raw = p.read_bytes()
    assert raw.count(b"\r\n") == 3 and raw.count(b"\n") == 3
    got = _read(p)
    assert got[0] == HEADER
    assert got[1] == old[:4] + ["6"] + old[4:]
    assert got[2][AI] == "1" and got[2][HEADER.index("trades")] == "7"
