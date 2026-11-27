"""Indicadores compartidos y orquestación de las señales por vela.

Los indicadores se calculan una sola vez aquí (``compute_indicators``); las
reglas de cada estrategia viven en ``engine/estrategias/eNN_<nombre>.py`` y
reciben estos arrays ya calculados. ``compute_signals`` llama al registro y
devuelve, por estrategia, (buySig, sellSig, tier) como ``bytearray`` por vela.

Banderas de cruce precalculadas (``ta.crossover/crossunder(macdL, 0)``):
``macdCrossUp0[i] = macdL[i-1] <= 0 and macdL[i] > 0`` y
``macdCrossDn0[i] = macdL[i-1] >= 0 and macdL[i] < 0`` (NaN -> falso).

Calentamiento: no se opera antes de ``warmup``, la primera vela en la que RSI,
ADX, macdL, macdH y volRel existen a la vez (unas 33 velas en la práctica:
lo que tarde la señal del MACD). Antes de ese punto las señales son falsas
por NA de todas formas. El VWAP NY no entra en el calentamiento: si es NA,
``close > vwapNY`` es falso y deberia_5_verde no dispara.
"""

from . import indicators as ind
from .estrategias import ESTRATEGIAS


def macd_cross_zero(macd_line):
    n = len(macd_line)
    up, dn = bytearray(n), bytearray(n)
    prev = float("nan")
    for i in range(n):
        m = macd_line[i]
        if prev <= 0 and m > 0:
            up[i] = 1
        elif prev >= 0 and m < 0:
            dn[i] = 1
        prev = m
    return up, dn


def compute_indicators(bars, swing=3):
    h, l, c, v = bars.high, bars.low, bars.close, bars.volume
    macd_l, _macd_s, macd_h = ind.macd(c)
    up, dn = macd_cross_zero(macd_l)
    return {
        "rsi": ind.rsi(c),
        "adx": ind.adx(h, l, c),
        "macdL": macd_l,
        "macdH": macd_h,
        "volRel": ind.vol_rel(v),
        "vwapNY": ind.vwap_ny(bars.om, h, l, c, v),
        "trend": ind.structure_trend(h, l, c, swing),
        "close": c,
        "macdCrossUp0": up,
        "macdCrossDn0": dn,
    }


def warmup_index(inds):
    keys = ("rsi", "adx", "macdL", "macdH", "volRel")
    n = len(inds["rsi"])
    for i in range(n):
        if all(inds[k][i] == inds[k][i] for k in keys):
            return i
    return n


def compute_signals(bars, inds, incluir_amarillo=True, estrategias=None):
    """Devuelve {NOMBRE: (buy, sell, tier)} para ``estrategias`` (por defecto todas)."""
    mods = ESTRATEGIAS if estrategias is None else estrategias
    return {m.NOMBRE: m.senales(inds, incluir_amarillo) for m in mods}
