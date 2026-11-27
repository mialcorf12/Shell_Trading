"""Conjuntos de TP/SL (``--configs base|1a1|all``): base sin cambios y relación 1:1."""

import json

import pytest

from engine import (CONFIGS, CONFIGS_1A1, CONFIGS_BASE, CONJUNTO_1A1, CONJUNTO_BASE, CONJUNTOS,
                    INSTRUMENTS, notas_estrategia, notas_for)
from engine.cli import build_parser, parse_configs, run
from engine.results_csv import HEADER
from engine.simulate import points_for

from .test_engine import NI, _args, _data_file, _read, _write_results

MNQ = INSTRUMENTS["MNQ"]
TI, SI, CI = HEADER.index("tp_usd"), HEADER.index("sl_usd"), HEADER.index("contratos")
NOMBRE = "deberia_1_amarilla"


def test_1a1_set_has_exactly_three_configs():
    assert CONFIGS_1A1 == ((100, 100), (200, 200), (300, 300))
    assert CONJUNTO_1A1.clave == "1a1" and CONJUNTO_1A1.nombre == "1:1"
    assert all(tp == sl for tp, sl in CONJUNTO_1A1.configs)


def test_base_set_unchanged_and_default():
    assert CONFIGS == CONFIGS_BASE == ((100, 600), (200, 600), (300, 600), (600, 600),
                                       (1000, 2000), (1500, 2000))
    assert CONJUNTO_BASE.configs == CONFIGS_BASE and len(CONJUNTO_BASE.configs) == 6
    assert [c.clave for c in CONJUNTOS] == ["base", "1a1"]
    assert build_parser().parse_args([]).configs == "base"
    assert [(tp, sl) for _c, tp, sl in parse_configs("base")] == list(CONFIGS_BASE)


def test_configs_option_selects_sets():
    assert [(tp, sl) for _c, tp, sl in parse_configs("1a1")] == list(CONFIGS_1A1)
    assert [(tp, sl) for _c, tp, sl in parse_configs("all")] == list(CONFIGS_BASE) + list(CONFIGS_1A1)
    assert build_parser().parse_args(["--configs", "1a1"]).configs == "1a1"
    with pytest.raises(SystemExit):
        build_parser().parse_args(["--configs", "2a1"])


def test_1a1_two_contracts_point_distance_rule():
    # puntos = usd / (2 x N) en MNQ
    for usd in (100, 200, 300):
        assert points_for(usd, MNQ, 2) == usd / (2 * 2)
    assert points_for(100, MNQ, 2) == 25.0 and points_for(300, MNQ, 2) == 75.0


def test_notas_1a1_text_and_base_unchanged():
    args = ("e02_x", "regla", 3, 0, 2)
    plain = notas_estrategia(*args, ventana="ventana 6 anos (a..b)")
    assert notas_estrategia(*args, ventana="ventana 6 anos (a..b)", conjunto=CONJUNTO_BASE) == plain
    uno = notas_estrategia(*args, ventana="ventana 6 anos (a..b)", conjunto=CONJUNTO_1A1)
    assert uno == ("#e02_x: regla; verdes 3, amarillas 0; config 1:1 (TP = SL); "
                   "ventana 6 anos (a..b); " + notas_for(2))


def test_cli_1a1_two_contracts_adds_rows_without_changing_existing(tmp_path, capsys):
    data = _data_file(tmp_path, amp=200.0)
    res = tmp_path / "resultados.csv"
    _write_results(res)
    # fila base existente (calculada con el conjunto por defecto)
    run(_args(tmp_path, data, res, "--strategies", NOMBRE, "--contratos", "2", "--anos", "6"))
    before = _read(res)
    trades_before = {p.name: p.read_bytes() for p in (tmp_path / "trades").iterdir()}
    run(_args(tmp_path, data, res, "--strategies", NOMBRE, "--contratos", "2", "--anos", "6",
              "--configs", "1a1"))
    out = capsys.readouterr().out
    assert "corridas: 3; solapes totales: 0" in out
    got = _read(res)
    assert got[:len(before)] == before  # filas existentes intactas
    new = got[len(before):]
    assert sorted((r[TI], r[SI], r[CI]) for r in new) == [("100", "100", "2"), ("200", "200", "2"),
                                                          ("300", "300", "2")]
    for r in new:
        assert "; config 1:1 (TP = SL); ventana 6 anos (2024-01-02..2024-01-02); " in r[NI]
        assert r[NI].endswith("; " + notas_for(2))
    assert raw_crlf(res)
    for name, data_bytes in trades_before.items():
        assert (tmp_path / "trades" / name).read_bytes() == data_bytes
    js = json.loads((tmp_path / "trades" / ("MNQ_%s_tp100_sl100_c2_a6.json" % NOMBRE)).read_text())
    assert js
    for t in js:  # distancia 100 / (2 x 2) = 25 puntos para TP y SL
        sign = 1 if t["side"] == "long" else -1
        moved = (t["exit"] - t["entry"]) * sign
        if t["reason"] == "TP":
            assert moved == pytest.approx(25.0)
            assert t["pnl_usd"] == pytest.approx(100 - 8, abs=0.01)
        else:  # SL: 25 puntos + 1 tick de slippage
            assert moved == pytest.approx(-25.25)


def raw_crlf(path):
    raw = path.read_bytes()
    return raw.count(b"\r\n") == raw.count(b"\n")
