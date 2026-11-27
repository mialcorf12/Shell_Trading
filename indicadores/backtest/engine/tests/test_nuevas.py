"""Estrategias e10..e18 (ideas de 00_Nuevas.md) e indicadores de sesión."""

import math
import random
from array import array
from datetime import date

import pytest

from engine import indicators as I
from engine.data import Bars
from engine.estrategias import ESTRATEGIAS, POR_ID
from engine.signals import compute_indicators

NAN = float("nan")
D0 = date(2024, 3, 5).toordinal()  # martes


def om_at(hhmm, day=0):
    h, m = hhmm.split(":")
    return (D0 + day) * 1440 + int(h) * 60 + int(m)


def _ind(rows, **series):
    """rows: dicts por vela con 't' ('HH:MM' o (HH:MM, dia)) y valores; faltantes NaN.
    ``series``: arrays completos (p. ej. series de 5m)."""
    keys = set()
    for r in rows:
        keys.update(k for k in r if k != "t")
    d = {}
    for k in keys:
        if k in ("trend",):
            d[k] = array("b", [r.get(k, 0) for r in rows])
        elif k in ("nuevo5",):
            d[k] = bytearray(r.get(k, 0) for r in rows)
        elif k in ("idx5",):
            d[k] = array("q", [r.get(k, -1) for r in rows])
        else:
            d[k] = array("d", [r.get(k, NAN) for r in rows])
    d["om"] = array("q", [om_at(*(r["t"] if isinstance(r["t"], tuple) else (r["t"],)))
                          for r in rows])
    for k in ("open", "high", "low"):
        if k not in d and "close" in d:
            d[k] = array("d", d["close"])
    d.update(series)
    return d


def _sig(mod, ind):
    b, s, t = mod.senales(ind)
    return list(b), list(s), list(t)


# ---------- registro ----------

NUEVAS = ("orb", "vwap_rebote", "barrida_liquidez", "pullback_ema", "gap", "premarket_ruptura",
          "delta_divergencia", "macd_momentum", "power_hour")


def test_registry_loads_new_modules_in_order():
    nuevas = [m for m in ESTRATEGIAS if m.ID >= 10]
    assert [(m.ID, m.NOMBRE) for m in nuevas] == list(enumerate(NUEVAS, 10))
    assert [m.__name__.rsplit(".", 1)[1] for m in nuevas] == [
        "e%02d_%s" % (k, n) for k, n in enumerate(NUEVAS, 10)]
    for m in nuevas:
        assert "(verde)" in m.REGLA and "amarillo" not in m.REGLA


# ---------- e10 orb ----------

def _orb_rows(atr=40.0, vr=2.0):
    base = {"orbH15": 100.0, "orbL15": 90.0, "atrD": atr}
    return [{"t": "09:44", "close": 95.0, "atrD": atr, "volRel": 1.0},
            dict(base, t="09:45", close=101.0, volRel=vr),   # ruptura arriba: compra
            dict(base, t="09:46", close=102.0, volRel=vr),   # sin cruce
            dict(base, t="09:47", close=95.0, volRel=vr),
            dict(base, t="09:48", close=89.0, volRel=vr),    # ruptura abajo: venta
            dict(base, t="09:49", close=95.0, volRel=vr),
            dict(base, t="09:50", close=101.0, volRel=vr)]   # segundo cruce: no


def test_e10_orb_first_break_with_filters():
    m = POR_ID[10]
    b, s, t = _sig(m, _ind(_orb_rows()))
    assert b == [0, 1, 0, 0, 0, 0, 0] and s == [0, 0, 0, 0, 1, 0, 0]
    assert t == [0, 1, 0, 0, 1, 0, 0]
    assert m.motivo(_ind(_orb_rows()), 1, "long") == (
        "cierre 101>max ORB 15m 100 a las 09:45; VolRel 2>1.5; rango 10<0.5 x ATR diario 40 (verde)")


@pytest.mark.parametrize("atr,vr", [(20.0, 2.0), (40.0, 1.5)])
def test_e10_orb_filter_negative(atr, vr):
    b, s, _ = _sig(POR_ID[10], _ind(_orb_rows(atr, vr)))  # rango 10 >= 0.5 x 20; VolRel no > 1.5
    assert sum(b) == sum(s) == 0


# ---------- e11 vwap_rebote ----------

def _e11(wick_open=101.0, t0="10:30"):
    h0, m0 = map(int, t0.split(":"))
    t1 = "%02d:%02d" % (h0, m0 + 1)
    rows = [{"t": t0, "open": wick_open, "high": 101.5, "low": 99.5, "close": 101.25,
             "vwapNY": 100.0, "sigmaNY": 2.0, "trend": 1},
            {"t": t1, "open": 101.5, "high": 101.5, "low": 101.5, "close": 101.5,
             "vwapNY": 100.0, "sigmaNY": 2.0, "trend": 1, "nuevo5": 1, "idx5": 1}]
    return _ind(rows, rsi5m=array("d", [45.0, 55.0]))


def test_e11_vwap_rejection_then_rsi5m_cross():
    m = POR_ID[11]
    b, s, t = _sig(m, _e11())
    assert b == [0, 1] and s == [0, 0] and t == [0, 1]
    assert m.motivo(_e11(), 1, "long") == (
        "estructura alcista; rechazo en VWAP NY 100 a las 10:30 (min 99.5, max 101.5, cierre 101.25); "
        "RSI14 5m 45->55 cruza 50; cierre 101.5>VWAP NY 100 (verde)")


@pytest.mark.parametrize("kw", [{"wick_open": 99.6}, {"t0": "10:00"}])
def test_e11_filter_negative(kw):
    b, s, _ = _sig(POR_ID[11], _e11(**kw))  # mecha corta / antes de 10:30
    assert sum(b) == sum(s) == 0


# ---------- e12 barrida_liquidez ----------

def _e12(invalida=False):
    lv = {"asiaL": 95.0, "londresL": 97.0, "asiaH": 200.0, "londresH": 200.0, "ultSH": 99.75,
          "ultSL": 50.0}
    rows = [dict(lv, t="09:30", high=100.0, low=99.0, close=99.5),
            dict(lv, t="09:31", high=98.5, low=96.0, close=98.0),     # barre min Londres 97
            dict(lv, t="09:32", high=99.0, low=97.5, close=98.5),
            dict(lv, t="09:33", high=101.0, low=99.5, close=100.5),   # FVG + MSS (>99.75)
            dict(lv, t="09:34", high=101.5, low=95.5 if invalida else 100.25, close=101.0),
            dict(lv, t="09:35", high=100.5, low=99.5, close=100.0)]   # retroceso al medio FVG
    return _ind(rows)


def test_e12_sweep_mss_fvg_entry():
    m = POR_ID[12]
    b, s, t = _sig(m, _e12())
    assert b == [0, 0, 0, 0, 0, 1] and s == [0] * 6 and t[5] == 1
    assert m.motivo(_e12(), 5, "long") == (
        "barrida min Londres 97 (min 96) a las 09:31 y cierre dentro; MSS cierre>swing alto 99.75 "
        "a las 09:33; FVG alcista 99-100.25, medio 99.62; minimo 99.5<=medio; cierre 100>99 (verde)")


def test_e12_negative_new_extreme_cancels():
    b, s, _ = _sig(POR_ID[12], _e12(invalida=True))  # minimo 95.5 < extremo 96: se reinicia
    assert sum(b) == sum(s) == 0


# ---------- e13 pullback_ema ----------

def _e13(adx=30.0, t="09:59"):
    k = 6
    return _ind([{"t": t, "close": 100.0, "nuevo5": 1, "idx5": k}],
                ema9_5m=array("d", [10, 11, 12, 13, 14, 15, 16]),
                ema21_5m=array("d", [14.0] * 7), adx5m=array("d", [adx] * 7),
                low5m=array("d", [20, 20, 20, 20, 20, 17, 15.5]),
                high5m=array("d", [20.0] * 7),
                close5m=array("d", [20, 20, 20, 20, 20, 17, 16.5]))


def test_e13_pullback_to_ema_zone():
    m = POR_ID[13]
    assert _sig(m, _e13()) == ([1], [0], [1])
    assert m.motivo(_e13(), 0, "long") == (
        "5m cerrada a las 10:00: EMA9 16>EMA21 14; EMA9 sube desde 11; ADX 5m 30>=25; "
        "minimo 15.5<=EMA9; cierre 16.5>EMA9 (verde)")


@pytest.mark.parametrize("kw", [{"adx": 24.9}, {"t": "08:59"}])
def test_e13_filter_negative(kw):
    assert _sig(POR_ID[13], _e13(**kw)) == ([0], [0], [0])


# ---------- e14 gap ----------

def _e14(A, closes15, c45, hi15=None):
    rows = []
    for k, c in enumerate(closes15):
        rows.append({"t": "09:%02d" % (30 + k), "close": c, "high": hi15 if hi15 and k == 3 else c,
                     "aperturaRTH": A, "cierrePrevio": 10000.0})
    rows.append({"t": "09:45", "close": c45, "aperturaRTH": A, "cierrePrevio": 10000.0})
    return _ind(rows)


def test_e14_gap_fill_small_gap_short():
    m = POR_ID[14]
    ind = _e14(10020.0, [10022.0] * 15, 10010.0, hi15=10030.0)  # gap +0.2%
    b, s, t = _sig(m, ind)
    assert s == [0] * 15 + [1] and sum(b) == 0 and t[15] == 1
    assert m.motivo(ind, 15, "short") == (
        "gap +0.20% (apertura 10020 vs cierre previo 10000); gap fill <0.5%: maximo 15m 10030>apertura "
        "y falla; cierre 10010<apertura y >cierre previo a las 09:45 (verde)")


def test_e14_gap_and_go_and_negative():
    m = POR_ID[14]
    ind = _e14(10100.0, [10105.0] * 15, 10110.0)  # gap +1%
    b, s, _ = _sig(m, ind)
    assert b == [0] * 15 + [1] and sum(s) == 0
    assert "gap and go >=0.5%: cierre minimo 15m 10105>=apertura; cierre 10110>apertura" in \
        m.motivo(ind, 15, "long")
    neg = _e14(10100.0, [10105.0] * 7 + [10090.0] + [10105.0] * 7, 10110.0)  # no sostiene
    assert _sig(m, neg)[0] == [0] * 16


# ---------- e15 premarket_ruptura ----------

def _e15(retest_close=100.5, retest_t="09:32"):
    lv = {"pmH": 100.0, "pmL": 90.0}
    return _ind([{"t": "09:29", "close": 99.0},
                 dict(lv, t="09:30", close=101.0),                         # ruptura
                 dict(lv, t="09:31", close=101.5, low=100.5),
                 dict(lv, t=retest_t, close=retest_close, low=99.75)])     # retesteo


def test_e15_break_and_retest_holds():
    m = POR_ID[15]
    b, s, t = _sig(m, _e15())
    assert b == [0, 0, 0, 1] and sum(s) == 0 and t[3] == 1
    assert m.motivo(_e15(), 3, "long") == (
        "ruptura max pre-market 100 (cierre 101 a las 09:30); retesteo a las 09:32: minimo 99.75<=nivel, "
        "cierre 100.5>nivel (verde)")


@pytest.mark.parametrize("kw", [{"retest_close": 99.5}, {"retest_t": "09:46"}])
def test_e15_filter_negative(kw):
    b, s, _ = _sig(POR_ID[15], _e15(**kw))  # cierra dentro / retesteo tras 15 min
    assert sum(b) == sum(s) == 0


# ---------- e16 delta_divergencia ----------

def _e16(cvd7=-40.0, val=100.5):
    lows = [105, 104, 103, 100, 103, 104, 105, 99]
    cvd = [0, -10, -20, -50, -40, -30, -20, cvd7]
    return _ind([{"t": "09:%02d" % (30 + k), "close": lows[k] + 1, "low": lows[k], "high": 110.0,
                  "cvd": cvd[k], "poc": 120.0, "vah": 125.0, "val": val} for k in range(8)])


def test_e16_lower_low_with_higher_delta_at_val():
    m = POR_ID[16]
    b, s, t = _sig(m, _e16())
    assert b == [0] * 7 + [1] and sum(s) == 0 and t[7] == 1
    assert m.motivo(_e16(), 7, "long") == (
        "minimo 99<swing bajo 100; delta acum. aprox. -40>-50; a 1.5 pts de VAL 100.5 (sesion previa) "
        "(verde)")


@pytest.mark.parametrize("kw", [{"cvd7": -60.0}, {"val": 102.0}])
def test_e16_filter_negative(kw):
    b, s, _ = _sig(POR_ID[16], _e16(**kw))  # sin divergencia / lejos del nivel (>2 pts)
    assert sum(b) == sum(s) == 0


# ---------- e17 macd_momentum ----------

def _e17(t="09:35", ar=1.0):
    return _ind([{"t": t, "macdH": 0.1, "close": 1.0},
                 {"t": t[:3] + "%02d" % (int(t[3:]) + 1), "macdH": 0.3, "trend": 1, "atrRatio": ar,
                  "volRel": 2.0, "close": 1.0}])


def test_e17_hist_expansion_in_window():
    m = POR_ID[17]
    assert _sig(m, _e17()) == ([0, 1], [0, 0], [0, 1])
    assert m.motivo(_e17(), 1, "long") == (
        "hora 09:36; MACD hist 0.3>0 y > previa 0.1; estructura alcista; ATR ratio 1 en 0.8-1.5; "
        "VolRel 2>=1.5 (verde)")


@pytest.mark.parametrize("kw", [{"t": "12:30"}, {"ar": 1.6}])
def test_e17_filter_negative(kw):
    assert _sig(POR_ID[17], _e17(**kw))[0] == [0, 0]  # mediodía / ATR ratio alto


# ---------- e18 power_hour ----------

def _e18(c1129=105.0):
    lv = {"mdH": 110.0, "mdL": 100.0, "vwapNY": 100.0}
    return _ind([{"t": "11:29", "close": c1129, "vwapNY": 100.0},
                 {"t": "14:59", "close": 104.0, "vwapNY": 100.0},
                 dict(lv, t="15:00", close=111.0)])


def test_e18_break_with_morning_bias():
    m = POR_ID[18]
    assert _sig(m, _e18()) == ([0, 0, 1], [0, 0, 0], [0, 0, 1])
    assert m.motivo(_e18(), 2, "long") == (
        "hora 15:00; cierre 111>max 12:00-15:00 110; sesgo alcista (cierre 105>VWAP NY 100 a las "
        "11:30) (verde)")


def test_e18_negative_against_bias():
    assert _sig(POR_ID[18], _e18(95.0)) == ([0, 0, 0], [0, 0, 0], [0, 0, 0])


# ---------- indicadores de sesión ----------

def _bars(rows):
    b = Bars()
    for om, o, h, l, c, v in rows:
        b.append(om, o, h, l, c, v)
    return b


def test_rango_sesion_asia_crosses_midnight_and_is_na_inside():
    oms = [om_at("18:00", -1), om_at("23:00", -1), om_at("01:59"), om_at("02:00"), om_at("09:00"),
           om_at("18:00")]
    hi = array("d", [10, 12, 11, 50, 50, 50])
    lo = array("d", [5, 6, 4, 1, 1, 1])
    h, l = I.rango_sesion(array("q", oms), hi, lo, 18 * 60, 2 * 60)
    assert all(math.isnan(x) for x in h[:3]) and math.isnan(h[5])
    assert (h[3], l[3], h[4], l[4]) == (12, 4, 12, 4)


def test_sesion_rth_prev_close_open_atr_and_profile():
    rows = []
    for d, (o, h, l, c) in enumerate(((100, 110, 90, 105), (106, 120, 104, 118), (117, 119, 100, 101))):
        rows.append((om_at("09:30", d), o, h, l, c, 10.0))
        rows.append((om_at("16:00", d), c, c, c, c, 1.0))
    b = _bars(rows)
    r = I.sesion_rth(b.om, b.open, b.high, b.low, b.close, b.volume, atr_len=2)
    assert r["aperturaRTH"][2] == 106 and math.isnan(r["aperturaRTH"][3])
    assert math.isnan(r["cierrePrevio"][1]) and r["cierrePrevio"][2] == 105
    assert r["cierrePrevio"][3] == 105  # 16:00 del día 1: la previa sigue siendo la del día 0
    assert math.isnan(r["atrD"][2]) and r["atrD"][4] == (20 + 16) / 2.0  # TR d0=20, d1=max(16,15,1)
    # perfil del día 0: una vela 90-110, bins de 1 punto, volumen uniforme
    assert r["poc"][2] == 90.5 and r["val"][2] == 90 and r["vah"][2] == 105


def test_velas_5m_from_open_time_without_lookahead():
    oms = [om_at("09:30") + k for k in range(5)] + [om_at("09:35"), om_at("09:36"), om_at("09:41")]
    c = [1, 2, 3, 4, 5, 6, 7, 8]
    b = _bars([(om, x, x + 1, x - 1, x, 1.0) for om, x in zip(oms, c)])
    o5, h5, l5, c5, v5, idx5, nuevo5 = I.velas_5m(b.om, b.open, b.high, b.low, b.close, b.volume)
    assert list(nuevo5) == [0, 0, 0, 0, 1, 0, 0, 1]   # 09:35-09:39 se cierra al llegar 09:41
    assert list(idx5) == [-1, -1, -1, -1, 0, 0, 0, 1]
    assert (o5[0], h5[0], l5[0], c5[0], v5[0]) == (1, 6, 0, 5, 5)
    assert (o5[1], h5[1], l5[1], c5[1]) == (6, 8, 5, 7)


def test_vwap_sigma_and_cumulative_delta_reset_at_0930():
    b = _bars([(om_at("09:29"), 0, 0, 0, 0, 5.0), (om_at("09:30"), 100, 100, 100, 100, 1.0),
               (om_at("09:31"), 190, 200, 190, 200, 1.0)])
    s = I.vwap_ny_sigma(b.om, b.high, b.low, b.close, b.volume)
    assert math.isnan(s[0]) and s[1] == 0  # antes del ancla NA; una vela: sigma 0
    tp2 = (200 + 190 + 200) / 3.0
    assert abs(s[2] - abs(tp2 - 100) / 2) < 1e-9
    cv = I.delta_acumulado(b.om, b.open, b.high, b.low, b.close, b.volume)
    assert math.isnan(cv[0]) and cv[1] == 0 and cv[2] == 1.0  # 1 x (200-190)/10


# ---------- sin mirada al futuro ----------

def _synth(dias=18, seed=3):
    rnd = random.Random(seed)
    b = Bars()
    px = 20000.0
    for d in range(dias):
        for m in range(1440):
            if 17 * 60 <= m < 18 * 60:
                continue
            o = px
            px = round((px + rnd.gauss(0, 3.0 if 570 <= m < 960 else 1.2)) * 4) / 4
            h = max(o, px) + rnd.choice([0, 0.25, 0.5, 1.0, 2.0])
            l = min(o, px) - rnd.choice([0, 0.25, 0.5, 1.0, 2.0])
            v = rnd.randint(50, 150) * (5 if rnd.random() < 0.08 else 1)
            b.append((D0 + d) * 1440 + m, o, h, l, px, float(v))
    return b


def _prefix(b, n):
    p = Bars()
    for k in ("om", "open", "high", "low", "close", "volume"):
        setattr(p, k, getattr(b, k)[:n])
    return p


def test_new_modules_have_no_lookahead():
    bars = _synth()
    full = compute_indicators(bars)
    mods = [POR_ID[k] for k in range(10, 19)]
    sig = {m.ID: m.senales(full) for m in mods}
    cortes = set()
    for m in mods:
        b, s, _ = sig[m.ID]
        idx = [i for i in range(len(b)) if b[i] or s[i]]
        assert idx, "%s sin senales en la serie sintetica" % m.NOMBRE
        cortes.add(idx[len(idx) // 2])
    for i in sorted(cortes):
        pre = compute_indicators(_prefix(bars, i + 1))  # datos hasta el cierre de la vela i
        for m in mods:
            b, s, t = m.senales(pre)
            fb, fs, ft = sig[m.ID]
            assert (bytes(b), bytes(s), bytes(t)) == (bytes(fb[:i + 1]), bytes(fs[:i + 1]),
                                                      bytes(ft[:i + 1])), (m.NOMBRE, i)
            if fb[i] or fs[i]:
                side = "long" if fb[i] else "short"
                assert m.motivo(pre, i, side) == m.motivo(full, i, side) != "sin evento"
