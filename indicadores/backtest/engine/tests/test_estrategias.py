import csv
import json
import random
from array import array

import pytest

from engine import STRATEGIES, notas_for
from engine.cli import build_parser, run
from engine.estrategias import ESTRATEGIAS, POR_ID, POR_NOMBRE, EstrategiaInvalida, cargar
from engine.results_csv import HEADER
from engine.signals import macd_cross_zero

from .test_engine import _args, _data_file, _read, _write_results

NAN = float("nan")
NI = HEADER.index("notas")


# ---------- registro ----------

NOMBRES = ("deberia_1_verde", "deberia_1_amarilla", "deberia_2_verde", "deberia_2_amarilla",
           "deberia_3_verde", "deberia_3_amarilla", "deberia_4_verde", "deberia_4_amarilla",
           "deberia_5_verde", "orb", "vwap_rebote", "barrida_liquidez", "pullback_ema", "gap",
           "premarket_ruptura", "delta_divergencia", "macd_momentum", "power_hour")


def test_registry_loads_all_modules_in_id_order():
    assert [(m.ID, m.NOMBRE) for m in ESTRATEGIAS] == list(enumerate(NOMBRES, 1))
    assert [m.__name__.rsplit(".", 1)[1] for m in ESTRATEGIAS] == [
        "e%02d_%s" % (k, n) for k, n in enumerate(NOMBRES, 1)]
    assert STRATEGIES == NOMBRES
    for m in ESTRATEGIAS:
        assert m.DESCRIPCION and "\n" not in m.REGLA


def test_regla_states_only_its_own_tier():
    for m in ESTRATEGIAS:
        if m.NOMBRE.endswith("_amarilla"):
            assert "(amarillo, sin verde)" in m.REGLA and "(verde)" not in m.REGLA, m.NOMBRE
        elif m.ID <= 8:
            assert "(verde)" in m.REGLA and "amarillo" not in m.REGLA, m.NOMBRE
    assert POR_ID[2].REGLA == ("RSI>50, MACD hist>0, ADX>=20 o VolRel>=0.8 (amarillo, sin verde); "
                               "corto: RSI<50, MACD hist<0, mismo filtro")
    assert POR_ID[1].REGLA == ("RSI>50, MACD hist>0, ADX>=25, VolRel>=1.5 (verde); "
                               "corto: RSI<50, MACD hist<0, mismo filtro")


_MOD = '''ID = {id}
NOMBRE = "{nombre}"
DESCRIPCION = "prueba"
{regla}
def senales(ind, incluir_amarillo=True):
    return bytearray(0), bytearray(0), bytearray(0)
def motivo(ind, i, side):
    return "x"
'''


def _pkg(tmp_path, monkeypatch, name, mods):
    d = tmp_path / name
    d.mkdir()
    (d / "__init__.py").write_text("")
    for fn, id_, nombre, regla in mods:
        (d / fn).write_text(_MOD.format(id=id_, nombre=nombre, regla=regla))
    monkeypatch.syspath_prepend(str(tmp_path))
    return name


def test_registry_rejects_module_missing_regla(tmp_path, monkeypatch):
    pkg = _pkg(tmp_path, monkeypatch, "pkg_sin_regla",
               [("e01_ok.py", 1, "ok", 'REGLA = "a>1"'), ("e02_mala.py", 2, "mala", "")])
    with pytest.raises(EstrategiaInvalida) as e:
        cargar(pkg)
    assert "e02_mala" in str(e.value) and "REGLA" in str(e.value)


def test_registry_picks_up_new_module_by_prefix(tmp_path, monkeypatch):
    pkg = _pkg(tmp_path, monkeypatch, "pkg_nueva",
               [("e06_nueva.py", 6, "nueva", 'REGLA = "b<2"'),
                ("e01_ok.py", 1, "ok", 'REGLA = "a>1"'),
                ("ayuda.py", 9, "no", 'REGLA = "c"')])
    assert [m.ID for m in cargar(pkg)] == [1, 6]


def test_registry_rejects_id_not_matching_prefix(tmp_path, monkeypatch):
    pkg = _pkg(tmp_path, monkeypatch, "pkg_id_malo", [("e03_x.py", 4, "x", 'REGLA = "a"')])
    with pytest.raises(EstrategiaInvalida, match="prefijo e03"):
        cargar(pkg)


# ---------- señales vs regla de referencia (lógica previa del motor) ----------

def _reference(inds, incluir_amarillo=True):
    """Regla combinada previa (5 estrategias, verde o amarillo): buy = buyG o buyY."""
    rsi, adx, ml, mh = inds["rsi"], inds["adx"], inds["macdL"], inds["macdH"]
    vr, vw, tr, close = inds["volRel"], inds["vwapNY"], inds["trend"], inds["close"]
    n = len(rsi)
    out = {"deberia_%d" % k: [bytearray(n), bytearray(n), bytearray(n)] for k in range(1, 6)}
    b1, s1, t1 = out["deberia_1"]
    b2, s2, t2 = out["deberia_2"]
    b3, s3, t3 = out["deberia_3"]
    b4, s4, t4 = out["deberia_4"]
    b5, s5, t5 = out["deberia_5"]
    prev = NAN
    for i in range(n):
        r, a, v = rsi[i], adx[i], vr[i]
        g = a >= 25 and v >= 1.5
        y = a >= 20 or v >= 0.8
        lvl = 1 if g else 2
        if g or (incluir_amarillo and y):
            h, m, t = mh[i], ml[i], tr[i]
            if r > 50:
                if h > 0:
                    b1[i], t1[i] = 1, lvl
                    if t == 1:
                        b3[i], t3[i] = 1, lvl
                if m > 0:
                    b2[i], t2[i] = 1, lvl
                    if t == 1:
                        b4[i], t4[i] = 1, lvl
            elif r < 50:
                if h < 0:
                    s1[i], t1[i] = 1, lvl
                    if t == -1:
                        s3[i], t3[i] = 1, lvl
                if m < 0:
                    s2[i], t2[i] = 1, lvl
                    if t == -1:
                        s4[i], t4[i] = 1, lvl
        m = ml[i]
        if prev <= 0 and m > 0:
            if tr[i] == 1 and close[i] > vw[i]:
                b5[i], t5[i] = 1, 1
        elif prev >= 0 and m < 0:
            if tr[i] == -1 and close[i] < vw[i]:
                s5[i], t5[i] = 1, 1
        prev = m
    return out


def _inds(rows):
    """rows: dicts parciales por vela; faltantes = valores neutros."""
    keys = ("rsi", "adx", "macdL", "macdH", "volRel", "vwapNY", "close")
    d = {k: array("d", [r.get(k, NAN) for r in rows]) for k in keys}
    d["trend"] = array("b", [r.get("trend", 0) for r in rows])
    d["macdCrossUp0"], d["macdCrossDn0"] = macd_cross_zero(d["macdL"])
    return d


def _random_inds(n=4000, seed=7):
    rnd = random.Random(seed)

    def val(choices, lo, hi):
        x = rnd.random()
        if x < 0.05:
            return NAN
        if x < 0.25:
            return rnd.choice(choices)
        return rnd.uniform(lo, hi)
    rows = []
    for _ in range(n):
        rows.append({"rsi": val([50.0, 49.99, 50.01], 30, 70),
                     "adx": val([20.0, 25.0, 19.99, 24.99], 5, 45),
                     "volRel": val([0.8, 1.5, 0.79, 1.49], 0, 3),
                     "macdL": val([0.0, -0.01, 0.01], -2, 2),
                     "macdH": val([0.0, -0.01, 0.01], -1, 1),
                     "vwapNY": val([100.0], 95, 105),
                     "close": rnd.choice([100.0, 99.75, 100.25, 96.0, 104.0]),
                     "trend": rnd.choice([-1, 0, 1])})
    return _inds(rows)


@pytest.mark.parametrize("k", [1, 2, 3, 4])
def test_verde_and_amarilla_are_disjoint_and_union_is_old_rule(k):
    inds = _random_inds()
    rb, rs, rt = _reference(inds)["deberia_%d" % k]
    gb, gs, gt = POR_NOMBRE["deberia_%d_verde" % k].senales(inds)
    yb, ys, yt = POR_NOMBRE["deberia_%d_amarilla" % k].senales(inds)
    n = len(rb)
    for g, y, r in ((gb, yb, rb), (gs, ys, rs)):
        assert not any(g[i] and y[i] for i in range(n))       # disjuntas por lado
        assert bytes(g[i] | y[i] for i in range(n)) == bytes(r)  # union = regla previa
        assert sum(g) and sum(y)
    assert all(gt[i] == (1 if gb[i] or gs[i] else 0) for i in range(n))
    assert all(yt[i] == (2 if yb[i] or ys[i] else 0) for i in range(n))
    assert all(rt[i] == (gt[i] or yt[i]) for i in range(n))
    # verde == regla previa sin amarillo; amarilla sin amarillo no dispara
    ob, os_, ot = _reference(inds, False)["deberia_%d" % k]
    assert (bytes(gb), bytes(gs), bytes(gt)) == (bytes(ob), bytes(os_), bytes(ot))
    eb, es, et = POR_NOMBRE["deberia_%d_amarilla" % k].senales(inds, incluir_amarillo=False)
    assert not (sum(eb) or sum(es) or sum(et))


def test_deberia_5_verde_matches_old_deberia_5():
    inds = _random_inds()
    rb, rs, rt = _reference(inds)["deberia_5"]
    b, s, t = POR_NOMBRE["deberia_5_verde"].senales(inds)
    assert (bytes(b), bytes(s), bytes(t)) == (bytes(rb), bytes(rs), bytes(rt))
    assert sum(b) and sum(s)


VERDE = {"rsi": 60.0, "adx": 30.0, "volRel": 2.0}
AMARILLO = {"rsi": 60.0, "adx": 21.0, "volRel": 0.5}


@pytest.mark.parametrize("nombre,campo", [("deberia_1", "macdH"), ("deberia_2", "macdL"),
                                          ("deberia_3", "macdH"), ("deberia_4", "macdL")])
def test_modules_1_to_4_tiers_and_edges(nombre, campo):
    g = POR_NOMBRE[nombre + "_verde"]
    y = POR_NOMBRE[nombre + "_amarilla"]
    rows = [dict(VERDE, **{campo: 0.5, "trend": 1}),               # verde largo
            dict(AMARILLO, **{campo: 0.5, "trend": 1}),            # amarillo largo
            {"rsi": 40.0, "adx": 30.0, "volRel": 2.0, campo: -0.5, "trend": -1},  # verde corto
            dict(VERDE, **{"rsi": 50.0, campo: 0.5, "trend": 1}),  # borde: RSI == 50
            dict(VERDE, **{campo: 0.0, "trend": 1}),               # borde: MACD == 0
            {"rsi": 60.0, "adx": 19.0, "volRel": 0.79, campo: 0.5, "trend": 1},  # sin filtro
            dict(VERDE, **{campo: 0.5, "trend": 0})]               # sin sesgo
    sesgo = nombre in ("deberia_3", "deberia_4")
    buy, sell, tier = g.senales(_inds(rows))
    assert list(buy) == [1, 0, 0, 0, 0, 0, 0 if sesgo else 1]
    assert list(sell) == [0, 0, 1, 0, 0, 0, 0]
    assert list(tier) == [1, 0, 1, 0, 0, 0, 0 if sesgo else 1]
    buy, sell, tier = y.senales(_inds(rows))
    assert list(buy) == [0, 1, 0, 0, 0, 0, 0]
    assert list(sell) == [0, 0, 0, 0, 0, 0, 0]
    assert list(tier) == [0, 2, 0, 0, 0, 0, 0]


def test_module_5_cross_vwap_and_edges():
    m = POR_ID[9]
    rows = [{"macdL": -0.1, "close": 100.0, "vwapNY": 99.0, "trend": 1},
            {"macdL": 0.3, "close": 100.0, "vwapNY": 99.0, "trend": 1},    # cruce arriba: compra
            {"macdL": 0.4, "close": 100.0, "vwapNY": 99.0, "trend": 1},    # sin cruce
            {"macdL": -0.2, "close": 98.0, "vwapNY": 99.0, "trend": -1},   # cruce abajo: venta
            {"macdL": 0.1, "close": 100.0, "vwapNY": NAN, "trend": 1},     # VWAP NA: nada
            {"macdL": -0.1, "close": 100.0, "vwapNY": 99.0, "trend": -1},  # precio > VWAP: nada
            {"macdL": 0.0, "close": 100.0, "vwapNY": 99.0, "trend": 1},
            {"macdL": 0.2, "close": 99.0, "vwapNY": 99.0, "trend": 1}]     # close == VWAP: nada
    buy, sell, tier = m.senales(_inds(rows))
    assert list(buy) == [0, 1, 0, 0, 0, 0, 0, 0]
    assert list(sell) == [0, 0, 0, 1, 0, 0, 0, 0]
    assert list(tier) == [0, 1, 0, 1, 0, 0, 0, 0]
    assert m.senales(_inds(rows), incluir_amarillo=False)[0] == buy  # sin amarillo


# ---------- motivo ----------

def test_motivo_has_real_values():
    inds = _inds([{"rsi": 61.234, "adx": 27.1, "volRel": 1.83, "macdH": 0.84, "macdL": 1.5,
                   "trend": 1},
                  {"rsi": 42.0, "adx": 21.3, "volRel": 0.92, "macdH": -0.5, "macdL": -1.25,
                   "trend": -1}])
    assert POR_ID[1].motivo(inds, 0, "long") == (
        "RSI 61.23>50; MACD hist 0.84>0; ADX 27.1>=25; VolRel 1.83>=1.5 (verde)")
    assert POR_ID[4].motivo(inds, 1, "short") == (
        "RSI 42<50; MACD linea -1.25<0; ADX 21.3>=20 o VolRel 0.92>=0.8 (amarillo)")
    assert POR_ID[8].motivo(inds, 1, "short").startswith(
        "RSI 42<50; MACD linea -1.25<0; estructura bajista; ADX 21.3>=20")
    i5 = _inds([{"macdL": -0.1, "close": 15640.0, "vwapNY": 15610.0, "trend": 1},
                {"macdL": 0.31, "close": 15640.0, "vwapNY": 15610.0, "trend": 1}])
    assert POR_ID[9].motivo(i5, 1, "long") == (
        "estructura alcista; precio 15640>VWAP NY 15610; cruce MACD linea 0 (+0.31)")


# ---------- CLI: notas, JSON, selección ----------

@pytest.mark.parametrize("id_,tier", [(1, "verde"), (2, "amarillo")])
def test_notas_and_trade_json_motivo_and_tier(tmp_path, id_, tier):
    data = _data_file(tmp_path, amp=200.0, spike=7)
    res = tmp_path / "resultados.csv"
    _write_results(res)
    mod = POR_ID[id_]
    run(_args(tmp_path, data, res, "--estrategias", str(id_), "--contratos", "1,2", "--anos", "6"))
    got = _read(res)
    mine = [r for r in got[1:] if r[1] == "MNQ" and r[0] == mod.NOMBRE]
    assert len(mine) == 12 and len(got) == 1 + 3 + 12 - (id_ == 2)  # 200/600 c1 ya existia
    total = 0
    for r in mine:
        tp, sl, c = (r[HEADER.index(k)] for k in ("tp_usd", "sl_usd", "contratos"))
        js = json.loads((tmp_path / "trades" / ("MNQ_%s_tp%s_sl%s_c%s_a6.json"
                                                % (mod.NOMBRE, tp, sl, c))).read_text())
        assert {t["tier"] for t in js} <= {tier}
        n = len(js)
        total += n
        assert n == int(r[HEADER.index("trades")] or 0)
        v, a = (n, 0) if tier == "verde" else (0, n)
        assert r[NI] == "#e%02d_%s: %s; verdes %d, amarillas %d; %s; %s%s" % (
            id_, mod.NOMBRE, mod.REGLA, v, a, "ventana 6 anos (2024-01-02..2024-01-02)",
            "" if js else "sin trades; ", notas_for(int(c)))
        assert "\n" not in r[NI] and "\r" not in r[NI]
        for t in js:
            assert t["motivo"].startswith("RSI ") and t["motivo"].endswith(" (%s)" % tier)
    assert total, "se esperaban operaciones"
    # el CSV sigue siendo legible con comas dentro de notas
    rows = list(csv.DictReader(open(res, newline="")))
    assert rows[-1]["notas"].startswith("#e%02d_%s: RSI>50, MACD hist>0, " % (id_, mod.NOMBRE))


def test_cli_estrategias_by_id_and_strategies_by_name(tmp_path, capsys):
    data = _data_file(tmp_path)
    res = tmp_path / "resultados.csv"
    _write_results(res)
    ups = run(_args(tmp_path, data, res, "--no-write", "--estrategias", "3,1", "--contratos", "1"))
    assert sorted({u["estrategia"] for u in ups}) == ["deberia_1_verde", "deberia_2_verde"]
    assert [u["estrategia"] for u in ups][0] == "deberia_1_verde"  # orden por ID
    ups = run(_args(tmp_path, data, res, "--no-write", "--strategies", "deberia_5_verde",
                    "--contratos", "1"))
    assert {u["estrategia"] for u in ups} == {"deberia_5_verde"}
    assert all(u["notas"].startswith("#e09_deberia_5_verde: estructura alcista") for u in ups)
    ups = run(_args(tmp_path, data, res, "--no-write", "--contratos", "1", "--anos", "6"))
    assert len(ups) == 18 * 6 and [u["estrategia"] for u in ups[::6]] == list(NOMBRES)
    for bad in (["--estrategias", "19"], ["--estrategias", "0"], ["--strategies", "deberia_1"]):
        with pytest.raises(SystemExit):
            run(_args(tmp_path, data, res, "--no-write", *bad))
    with pytest.raises(SystemExit):
        build_parser().parse_args(["--estrategias", "1", "--strategies", "deberia_1_verde"])
    assert build_parser().parse_args([]).estrategias is None
    assert "432 corridas" in " ".join(build_parser().format_help().split())
