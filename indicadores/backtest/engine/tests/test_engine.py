import csv
import json
import math
import os

import pytest

from engine import INSTRUMENTS, INVALIDO_PREFIX, NOTAS, notas_base, notas_for
from engine.cli import build_parser, default_data_path, run
from engine.data import Bars, format_open, load_csv, stamp_to_open_minute
from engine.indicators import vwap_ny
from engine.metrics import compute_metrics, format_metrics
from engine.results_csv import HEADER, trades_json_path, update_results
from engine.simulate import (OverlapError, Trade, check_no_overlap, count_overlaps, points_for,
                             simulate)

NQ = INSTRUMENTS["NQ"]
MNQ = INSTRUMENTS["MNQ"]


def make_bars(rows, start="2024-01-02 10:00:00"):
    """rows: lista de (high, low, close); open = close; volumen 1."""
    b = Bars()
    om0 = stamp_to_open_minute(start)
    for k, (h, l, c) in enumerate(rows):
        b.append(om0 + k, c, h, l, c, 1.0)
    return b


def flags(n, idx):
    a = bytearray(n)
    for i in idx:
        a[i] = 1
    return a


# ---------- tiempo ----------

def test_open_time_is_stamp_minus_one_minute(tmp_path):
    p = tmp_path / "d.csv"
    p.write_text("datetime,open,high,low,close,volume\n"
                 "2020-11-22 18:01:00,1,2,0.5,1.5,10\n"
                 "2020-11-23 00:00:00,1,2,0.5,1.5,10\n")
    b = load_csv(str(p))
    assert format_open(b.om[0]) == "2020-11-22 18:00"
    assert format_open(b.om[1]) == "2020-11-22 23:59"


def test_vwap_anchor_on_bar_opening_at_0930():
    # marcas 09:30, 09:31, 09:32 -> aperturas 09:29, 09:30, 09:31
    b = Bars()
    for stamp, px, vol in (("2024-01-02 09:30:00", 100.0, 5.0),
                           ("2024-01-02 09:31:00", 200.0, 1.0),
                           ("2024-01-02 09:32:00", 300.0, 1.0)):
        b.append(stamp_to_open_minute(stamp), px, px, px, px, vol)
    v = vwap_ny(b.om, b.high, b.low, b.close, b.volume)
    assert math.isnan(v[0])  # antes del primer ancla
    assert v[1] == 200.0  # reinicio en la vela con apertura 09:30
    assert v[2] == 250.0


# ---------- ejecución ----------

def test_edge_entry_single_entry_for_consecutive_signal():
    # señal en 0 y 1; TP en vela 1 deja la cuenta plana, pero el flanco impide reentrar
    b = make_bars([(100, 100, 100), (106, 100, 101), (101, 100, 100), (101, 100, 100)])
    t = simulate(b, flags(4, [0, 1]), flags(4, []), 100, 600, instrument=NQ)
    assert len(t) == 1
    assert t[0].entry_index == 0 and t[0].entry == 100.25


def test_long_tp_exact_fill_and_pnl():
    b = make_bars([(100, 100, 100), (105.25, 100, 104)])
    (t,) = simulate(b, flags(2, [0]), flags(2, []), 100, 600, instrument=NQ)
    assert t.reason == "TP" and t.exit == 100.25 + 5.0
    assert t.pnl_usd == 5.0 * 20 - 4


def test_long_sl_with_slippage():
    b = make_bars([(100, 100, 100), (100.5, 70.0, 75)])
    (t,) = simulate(b, flags(2, [0]), flags(2, []), 100, 600, instrument=NQ)
    assert t.reason == "SL" and t.exit == 100.25 - 30.0 - 0.25
    assert t.pnl_usd == (-30.25) * 20 - 4 == -609.0


def test_both_tp_and_sl_in_same_bar_takes_sl():
    b = make_bars([(100, 100, 100), (200, 0, 100)])
    (t,) = simulate(b, flags(2, [0]), flags(2, []), 100, 600, instrument=NQ)
    assert t.reason == "SL"
    b2 = make_bars([(100, 100, 100), (200, 0, 100)])
    (s,) = simulate(b2, flags(2, []), flags(2, [0]), 100, 600, instrument=NQ)
    assert s.reason == "SL" and s.exit == 99.75 + 30 + 0.25


def test_entry_fill_and_no_exit_on_entry_bar():
    # la vela de entrada cubre TP y SL, pero no se revisa; sale en la siguiente
    b = make_bars([(200, 0, 100), (100, 100, 100), (106, 100, 100)])
    (t,) = simulate(b, flags(3, [0]), flags(3, []), 100, 600, instrument=NQ)
    assert t.entry == 100.25 and t.exit_index == 2 and t.reason == "TP"
    b2 = make_bars([(200, 0, 100), (100, 100, 100), (100, 94, 100)])
    (s,) = simulate(b2, flags(3, []), flags(3, [0]), 100, 600, instrument=NQ)
    assert s.entry == 99.75 and s.exit_index == 2 and s.exit == 94.75
    assert s.pnl_usd == 5 * 20 - 4


def test_one_position_at_a_time():
    # señal larga en 0, corta en 1 y larga en 3 mientras la posición sigue abierta
    rows = [(100, 100, 100)] * 5 + [(106, 100, 100)]
    b = make_bars(rows)
    t = simulate(b, flags(6, [0, 3]), flags(6, [1]), 100, 600, instrument=NQ)
    assert len(t) == 1 and t[0].entry_index == 0 and t[0].exit_index == 5


def test_reentry_allowed_on_exit_bar_with_new_edge():
    b = make_bars([(100, 100, 100), (106, 100, 100), (100, 100, 100), (106, 100, 100)])
    t = simulate(b, flags(4, [0, 2]), flags(4, []), 100, 600, instrument=NQ)
    assert [(x.entry_index, x.exit_index) for x in t] == [(0, 1), (2, 3)]
    assert count_overlaps(t) == 0  # salida y nueva entrada en la misma vela no es solape


def test_signal_every_bar_during_open_trade_no_second_entry():
    # cada vela tiene señal (sin flanco) y la posición sigue abierta hasta la vela 5
    rows = [(100, 100, 100)] * 5 + [(106, 100, 100)] + [(100, 100, 100)] * 2
    b = make_bars(rows)
    t = simulate(b, flags(8, range(8)), flags(8, []), 100, 600, edge=False, qty=3, instrument=NQ)
    assert [(x.entry_index, x.exit_index) for x in t] == [(0, 5)]
    assert count_overlaps(t) == 0
    check_no_overlap(t)


def test_overlap_check_raises_when_two_trades_overlap():
    a = Trade(0, 5, 1, 100.0, 105.0, 96.0, "TP")
    b = Trade(3, 7, -1, 100.0, 95.0, 96.0, "TP")
    c = Trade(7, 9, 1, 100.0, 105.0, 96.0, "TP")
    assert count_overlaps([a, b, c]) == 1
    with pytest.raises(OverlapError):
        check_no_overlap([a, b, c])
    check_no_overlap([b, c])  # b sale en 7 y c entra en 7: permitido


# ---------- contratos ----------
# Regla decidida: TP/SL son USD TOTALES de la operación. Con N contratos la
# distancia en puntos = usd / (point_value x N). PnL y comisión escalan por N.

def test_points_distance_total_usd_split_across_contracts():
    assert points_for(600, MNQ, 1) == 300.0
    assert points_for(600, MNQ, 4) == 75.0
    assert points_for(100, MNQ, 4) == 12.5
    assert points_for(600, NQ, 2) == 15.0


def test_mnq_four_contracts_tp_exact_gross_equals_tp_usd():
    # entrada 100.25; TP 100 USD / (2 x 4) = 12.5 puntos -> 112.75
    b = make_bars([(100, 100, 100), (112.75, 100, 104)])
    (t,) = simulate(b, flags(2, [0]), flags(2, []), 100, 600, qty=4, instrument=MNQ)
    assert t.reason == "TP" and t.entry == 100.25 and t.exit == 112.75
    assert t.pnl_usd == 100 - 16 == 84.0


def test_mnq_four_contracts_sl_75_points_with_slippage():
    # SL 600 USD / (2 x 4) = 75 puntos: nivel 25.25, fill 25.0 (1 tick adverso)
    b = make_bars([(100, 100, 100), (100.5, 20.0, 30)])
    (t,) = simulate(b, flags(2, [0]), flags(2, []), 100, 600, qty=4, instrument=MNQ)
    assert t.reason == "SL" and t.entry == 100.25 and t.exit == 25.0
    # -(600) - 0.25 x 2 x 4 - 4 x 4 = -600 - 2 - 16
    assert t.pnl_usd == (25.0 - 100.25) * 2 * 4 - 16 == -618.0


def test_contracts_short_sl_nq_distance_divided_by_n():
    # NQ, N=2: SL 600 / (20 x 2) = 15 puntos; corto en 99.75 -> SL 114.75, fill 115.0
    b = make_bars([(100, 100, 100), (140, 99, 120)])
    (t,) = simulate(b, flags(2, []), flags(2, [0]), 100, 600, qty=2, instrument=NQ)
    assert t.reason == "SL" and t.entry == 99.75 and t.exit == 115.0
    assert t.pnl_usd == (99.75 - 115.0) * 20 * 2 - 8 == -618.0


def test_notas_total_usd_text_and_no_contract_risk_sentence():
    assert notas_for(1) == NOTAS
    n = notas_for(3)
    assert n == ("3 contratos; TP/SL en USD totales de la operacion; "
                 "N contratos dividen la distancia en puntos; " + NOTAS)
    for k in (1, 2, 3, 4):
        assert "riesgo" not in notas_for(k).lower() and "por contrato" not in notas_for(k)


# ---------- instrumentos ----------

def test_instrument_table_mnq_and_nq():
    assert (MNQ.point_value, MNQ.tick, MNQ.commission_side, MNQ.commission_rt) == (2.0, 0.25, 2.0, 4.0)
    assert (NQ.point_value, NQ.tick, NQ.commission_side, NQ.commission_rt) == (20.0, 0.25, 2.0, 4.0)


def test_mnq_notas_text():
    assert NOTAS == ("motor python; MNQ 2 USD/punto; fills en cierre; SL prioridad si ambos; "
                     "comision 2/lado (supuesto); slippage 1 tick")
    assert notas_base("NQ").startswith("motor python; NQ 20 USD/punto; ")
    assert notas_for(2, "MNQ").endswith(NOTAS) and notas_for(2, "MNQ").startswith("2 contratos; ")


def test_mnq_is_default_and_tp_points_from_point_value():
    # TP 100 USD en MNQ = 50 puntos; el mismo movimiento de 5 puntos no alcanza
    b = make_bars([(100, 100, 100), (105.25, 100, 104), (150.25, 100, 150)])
    (t,) = simulate(b, flags(3, [0]), flags(3, []), 100, 600)
    assert t.reason == "TP" and t.entry == 100.25 and t.exit == 150.25 and t.exit_index == 2
    assert t.pnl_usd == 50.0 * 2 - 4 == 96.0


def test_mnq_tp_gross_is_tp_usd_for_every_n():
    b = make_bars([(100, 100, 100), (150.25, 100, 150)])
    for n in (1, 2, 3, 4):
        (t,) = simulate(b, flags(2, [0]), flags(2, []), 100, 600, qty=n, instrument=MNQ)
        assert t.reason == "TP" and t.exit == pytest.approx(100.25 + 50.0 / n)
        assert t.pnl_usd == pytest.approx((t.exit - t.entry) * 2 * n - 4 * n)
        assert t.pnl_usd == pytest.approx(100 - 4 * n)


def test_mnq_short_sl_slippage_one_tick():
    # SL 600 USD en MNQ con N=2 = 150 puntos; corto en 99.75 -> SL 249.75, fill 250.0
    b = make_bars([(100, 100, 100), (450, 99, 420)])
    (t,) = simulate(b, flags(2, []), flags(2, [0]), 100, 600, qty=2, instrument=MNQ)
    assert t.reason == "SL" and t.entry == 99.75 and t.exit == 250.0
    assert t.pnl_usd == (99.75 - 250.0) * 2 * 2 - 4 * 2 == -609.0


def test_nq_still_works_with_twenty_usd_per_point():
    # NQ, N=2: TP 100 / (20 x 2) = 2.5 puntos
    b = make_bars([(100, 100, 100), (105.25, 100, 104)])
    (t,) = simulate(b, flags(2, [0]), flags(2, []), 100, 600, qty=2, instrument=NQ)
    assert t.exit == 102.75 and t.pnl_usd == 2.5 * 20 * 2 - 4 * 2 == 92.0


# ---------- métricas ----------

def test_metrics_hand_computed():
    pnls = [100, -50, -50, 200, -30, 10]
    m = compute_metrics(pnls, [1, 1, 2, 2, 3, 3])
    assert m["trades"] == 6
    assert m["win_rate_pct"] == 50.0
    assert m["net_profit_usd"] == 180
    assert m["profit_factor"] == pytest.approx(310 / 130)
    assert m["payoff"] == pytest.approx((310 / 3) / (130 / 3))
    assert m["expectancy_usd"] == pytest.approx(30)
    assert m["max_dd_usd"] == 100  # 100 -> 0
    assert m["max_consec_losses"] == 2
    assert m["top3_pct"] == pytest.approx(310 / 180 * 100)
    daily = [50, 150, -20]
    mu = sum(daily) / 3
    sd = math.sqrt(sum((x - mu) ** 2 for x in daily) / 3)
    assert m["sharpe"] == pytest.approx(mu / sd * math.sqrt(252))
    f = format_metrics(m)
    assert f["trades"] == "6" and f["win_rate_pct"] == "50.0" and f["profit_factor"] == "2.38"


def test_metrics_top3_empty_when_net_not_positive_and_no_trades():
    m = compute_metrics([100, -150], [1, 2])
    assert m["top3_pct"] is None and format_metrics(m)["top3_pct"] == ""
    empty = format_metrics(compute_metrics([], []))
    assert all(v == "" for v in empty.values())


# ---------- CSV ----------

LEGACY_NQ_NOTAS = "motor python; fills en cierre; SL prioridad si ambos; comision 2/lado; slippage 1 tick"


def _write_results(path):
    rows = [HEADER,
            ["deberia_1_amarilla", "NQ", "1m", "a..b", "6", "1", "100", "600"] + ["5"] * 11
            + [LEGACY_NQ_NOTAS],
            ["deberia_1_amarilla", "MNQ", "", "", "6", "1", "200", "600"] + [""] * 11 + ["pendiente"],
            ["otra", "ES", "5m", "x", "6", "1", "1", "2"] + ["7"] * 11 + ["no tocar"]]
    with open(path, "w", newline="") as f:
        csv.writer(f, lineterminator="\r\n").writerows(rows)
    return rows


def _read(path):
    return list(csv.reader(open(path, newline="")))


NI = HEADER.index("notas")


def test_header_has_anos_after_periodo():
    assert HEADER == ["estrategia", "simbolo", "timeframe", "periodo", "anos", "contratos", "tp_usd",
                      "sl_usd", "trades", "win_rate_pct", "payoff", "profit_factor",
                      "expectancy_usd", "net_profit_usd", "max_dd_usd", "max_consec_losses",
                      "sharpe", "sortino", "top3_pct", "notas"]


def test_update_results_only_matching_row_and_marks_legacy_nq(tmp_path):
    p = tmp_path / "resultados.csv"
    rows = _write_results(p)
    update_results(str(p), [{"simbolo": "MNQ", "estrategia": "deberia_1_amarilla", "tp_usd": 200.0,
                             "sl_usd": 600, "trades": "12", "notas": "hecho", "periodo": "a..b"}])
    raw = p.read_bytes()
    assert raw.count(b"\r\n") == 4
    got = _read(p)
    assert got[0] == HEADER and len(got) == 4
    # NQ heredada: conservada, solo cambia notas con el prefijo INVALIDO
    assert got[1][:NI] == rows[1][:NI]
    assert got[1][NI] == INVALIDO_PREFIX + LEGACY_NQ_NOTAS
    assert got[3] == rows[3]
    assert got[2][HEADER.index("trades")] == "12" and got[2][NI] == "hecho"
    assert got[2][HEADER.index("tp_usd")] == "200" and got[2][1] == "MNQ"
    assert [x.name for x in tmp_path.iterdir()] == ["resultados.csv"]


def test_invalido_prefix_applied_once(tmp_path):
    p = tmp_path / "resultados.csv"
    _write_results(p)
    up = [{"simbolo": "MNQ", "estrategia": "deberia_1_amarilla", "tp_usd": 200, "sl_usd": 600}]
    update_results(str(p), up)
    update_results(str(p), up)
    assert _read(p)[1][NI] == INVALIDO_PREFIX + LEGACY_NQ_NOTAS


def test_new_format_nq_row_is_not_marked_invalid(tmp_path):
    p = tmp_path / "resultados.csv"
    with open(p, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\r\n")
        w.writerow(HEADER)
        w.writerow(["deberia_2_verde", "NQ", "1m", "a..b", "6", "1", "100", "600"] + ["5"] * 11
                   + [notas_base("NQ")])
    update_results(str(p), [{"simbolo": "MNQ", "estrategia": "deberia_2_verde", "tp_usd": 100,
                             "sl_usd": 600, "trades": "3"}])
    got = _read(p)
    assert got[1][NI] == notas_base("NQ") and len(got) == 3


def test_same_key_different_simbolo_appends_new_row(tmp_path):
    p = tmp_path / "resultados.csv"
    rows = _write_results(p)
    update_results(str(p), [{"simbolo": "MNQ", "estrategia": "deberia_1_amarilla", "tp_usd": 100,
                             "sl_usd": 600, "contratos": 1, "trades": "9"}])
    got = _read(p)
    assert len(got) == 5
    assert got[1][:NI] == rows[1][:NI]  # la fila NQ no se pisa
    new = got[4]
    assert (new[0], new[1], new[HEADER.index("contratos")], new[HEADER.index("tp_usd")],
            new[HEADER.index("trades")]) == ("deberia_1_amarilla", "MNQ", "1", "100", "9")


def test_update_results_appends_missing_row(tmp_path):
    p = tmp_path / "resultados.csv"
    _write_results(p)
    update_results(str(p), [{"simbolo": "MNQ", "estrategia": "deberia_9", "tp_usd": 5,
                             "sl_usd": 6, "trades": "1"}])
    got = _read(p)
    assert len(got) == 5 and got[4][0] == "deberia_9" and got[4][HEADER.index("trades")] == "1"
    assert got[4][HEADER.index("contratos")] == "1" and got[4][1] == "MNQ"


def test_update_results_matches_by_contratos(tmp_path):
    p = tmp_path / "resultados.csv"
    _write_results(p)
    update_results(str(p), [{"simbolo": "MNQ", "estrategia": "deberia_1_amarilla", "tp_usd": 200,
                             "sl_usd": 600, "contratos": 2, "trades": "9"}])
    got = _read(p)
    assert got[2][HEADER.index("trades")] == ""  # la fila de 1 contrato no se toca
    new = got[4]
    assert (new[0], new[1], new[HEADER.index("contratos")], new[HEADER.index("trades")]) == (
        "deberia_1_amarilla", "MNQ", "2", "9")


def test_update_results_requires_simbolo_and_leaves_file_unchanged(tmp_path):
    p = tmp_path / "resultados.csv"
    _write_results(p)
    before = p.read_bytes()
    with pytest.raises(ValueError):
        update_results(str(p), [{"estrategia": "deberia_1_amarilla", "tp_usd": 200, "sl_usd": 600}])
    assert p.read_bytes() == before


def test_update_results_migrates_legacy_header_to_contratos_1(tmp_path):
    p = tmp_path / "resultados.csv"
    legacy = [h for h in HEADER if h not in ("contratos", "anos")]
    with open(p, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\r\n")
        w.writerow(legacy)
        w.writerow(["deberia_1_amarilla", "NQ", "1m", "a..b", "100", "600"] + ["5"] * 11 + ["vieja"])
    update_results(str(p), [{"simbolo": "NQ", "estrategia": "deberia_1_amarilla", "tp_usd": 100,
                             "sl_usd": 600, "contratos": 1, "trades": "42"}])
    raw = p.read_bytes()
    assert raw.count(b"\r\n") == 2
    got = _read(p)
    assert got[0] == HEADER and len(got) == 2
    assert got[1][:6] == ["deberia_1_amarilla", "NQ", "1m", "a..b", "6", "1"]
    assert got[1][HEADER.index("trades")] == "42" and got[1][-1] == INVALIDO_PREFIX + "vieja"


# ---------- CLI ----------

def _data_file(tmp_path, n=300, amp=10.0, spike=0):
    """``spike`` > 0: volumen x10 cada ``spike`` velas (VolRel alto: velas verdes)."""
    p = tmp_path / "mnq.csv"
    lines = ["datetime,open,high,low,close,volume"]
    om = stamp_to_open_minute("2024-01-02 09:00:00")
    for k in range(n):
        c = 100 + amp * math.sin(k / 7.0) + k * 0.05 * amp / 10
        c = round(c * 4) / 4
        m = om + 1 + k
        stamp = "2024-01-02 %02d:%02d:00" % ((m % 1440) // 60, m % 60)
        vol = 10 + k % 5
        if spike and k % spike == 0:
            vol *= 10
        lines.append("%s,%s,%s,%s,%s,%d" % (stamp, c, c + 0.5, c - 0.5, c, vol))
    p.write_text("\n".join(lines) + "\n")
    return p


def _args(tmp_path, data, res, *extra):
    return build_parser().parse_args(["--data", str(data), "--results", str(res),
                                      "--trades-dir", str(tmp_path / "trades")] + list(extra))


def test_cli_defaults_mnq_and_mnq_data_file():
    a = build_parser().parse_args([])
    assert a.simbolo == "MNQ" and a.data is None and a.contratos == "1,2,3,4"
    assert a.anos == "6,3,1"
    assert default_data_path("MNQ").endswith(os.path.join("data", "mnq_1m.csv"))
    assert default_data_path("NQ").endswith(os.path.join("data", "nq_1m.csv"))
    with pytest.raises(SystemExit):
        build_parser().parse_args(["--simbolo", "ES"])


def test_cli_limit_bars_does_not_write_without_flag(tmp_path, capsys):
    data = _data_file(tmp_path)
    res = tmp_path / "resultados.csv"
    _write_results(res)
    before = res.read_bytes()
    run(_args(tmp_path, data, res, "--limit-bars", "200", "--strategies", "deberia_1_amarilla"))
    assert res.read_bytes() == before
    assert not (tmp_path / "trades").exists()
    out = capsys.readouterr().out
    assert "corrida en seco" in out
    assert "instrumento=MNQ point_value=2 USD/punto" in out


def test_cli_write_mnq_rows_and_trades_json(tmp_path):
    data = _data_file(tmp_path, amp=200.0)  # movimientos grandes: hay TP/SL en MNQ
    res = tmp_path / "resultados.csv"
    rows = _write_results(res)
    run(_args(tmp_path, data, res, "--strategies", "deberia_1_amarilla", "--contratos", "1",
              "--anos", "6"))
    got = _read(res)
    assert got[0] == HEADER and got[3] == rows[3]
    assert got[1][:NI] == rows[1][:NI] and got[1][NI] == INVALIDO_PREFIX + LEGACY_NQ_NOTAS
    assert len(got) == 1 + 3 + 5  # MNQ 200/600 c1 existia; las otras 5 se agregan
    mnq = [r for r in got[1:] if r[1] == "MNQ"]
    assert len(mnq) == 6
    for r in mnq:
        assert r[HEADER.index("timeframe")] == "1m"
        assert r[HEADER.index("periodo")] == "2024-01-02..2024-01-02"
        assert r[NI].endswith(NOTAS)
        assert r[HEADER.index("anos")] == "6"
    js = json.loads((tmp_path / "trades" / "MNQ_deberia_1_amarilla_tp100_sl600_c1_a6.json").read_text())
    assert js, "se esperaban operaciones"
    for t in js:
        assert set(t) == {"open_time", "exit_time", "side", "entry", "exit", "pnl_usd",
                          "reason", "motivo", "tier"}
        sign = 1 if t["side"] == "long" else -1
        assert t["pnl_usd"] == pytest.approx((t["exit"] - t["entry"]) * sign * 2 - 4)


def test_cli_nq_reference_still_works(tmp_path, capsys):
    data = _data_file(tmp_path)
    res = tmp_path / "resultados.csv"
    _write_results(res)
    run(_args(tmp_path, data, res, "--simbolo", "NQ", "--strategies", "deberia_1_amarilla",
              "--contratos", "1", "--anos", "6"))
    assert "instrumento=NQ point_value=20 USD/punto" in capsys.readouterr().out
    got = _read(res)
    nq = [r for r in got[1:] if r[1] == "NQ"]
    assert len(nq) == 6
    assert sum(1 for r in nq if r[NI].startswith(INVALIDO_PREFIX)) == 0  # recalculada, notas nuevas
    assert all(notas_base("NQ") in r[NI] for r in nq)
    js = json.loads((tmp_path / "trades" / "NQ_deberia_1_amarilla_tp100_sl600_c1_a6.json").read_text())
    for t in js:
        sign = 1 if t["side"] == "long" else -1
        assert t["pnl_usd"] == pytest.approx((t["exit"] - t["entry"]) * sign * 20 - 4)


def test_cli_contratos_writes_one_row_and_json_per_contract(tmp_path, capsys):
    data = _data_file(tmp_path, amp=200.0)
    res = tmp_path / "resultados.csv"
    _write_results(res)
    run(_args(tmp_path, data, res, "--strategies", "deberia_1_amarilla", "--contratos", "1,3",
              "--anos", "6"))
    out = capsys.readouterr().out
    got = _read(res)
    ci = HEADER.index("contratos")
    mine = [r for r in got[1:] if r[0] == "deberia_1_amarilla" and r[1] == "MNQ"]
    assert sorted((r[ci], r[HEADER.index("tp_usd")]) for r in mine) == sorted(
        (str(c), str(tp)) for c in (1, 3) for tp in (100, 200, 300, 600, 1000, 1500))
    assert "solapes totales: 0" in out
    j3 = json.loads((tmp_path / "trades" / "MNQ_deberia_1_amarilla_tp100_sl600_c3_a6.json").read_text())
    assert j3
    for t in j3:
        sign = 1 if t["side"] == "long" else -1
        assert t["pnl_usd"] == pytest.approx((t["exit"] - t["entry"]) * sign * 2 * 3 - 12, abs=0.01)
        if t["reason"] == "TP":  # bruto = TP total: 100 / (2 x 3) puntos x 2 x 3
            assert t["pnl_usd"] == pytest.approx(100 - 12, abs=0.01)
    for prev, nxt in zip(j3, j3[1:]):
        assert prev["exit_time"] <= nxt["open_time"]
    r3 = [r for r in mine if r[ci] == "3" and r[HEADER.index("tp_usd")] == "100"][0]
    assert r3[NI].startswith("#e02_deberia_1_amarilla: ") and r3[NI].endswith("; " + notas_for(3))
    assert "; ventana 6 anos (2024-01-02..2024-01-02); " in r3[NI]


def test_cli_rejects_contratos_out_of_range(tmp_path):
    data = _data_file(tmp_path)
    args = build_parser().parse_args(["--data", str(data), "--no-write", "--contratos", "5"])
    with pytest.raises(SystemExit):
        run(args)


def test_trades_json_name_has_simbolo_prefix_contracts_and_anos_suffix():
    assert trades_json_path("d", "MNQ", "deberia_2_verde", 1000.0, 2000, 4, 3).endswith(
        os.path.join("d", "MNQ_deberia_2_verde_tp1000_sl2000_c4_a3.json"))
    assert trades_json_path("d", "MNQ", "deberia_2_verde", 100, 600, 1).endswith(
        os.path.join("d", "MNQ_deberia_2_verde_tp100_sl600_c1_a6.json"))
