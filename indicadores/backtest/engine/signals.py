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

Las claves de e10..e18 (sesiones, RTH diario, 5m, EMA, sigma del VWAP, delta
aproximado, swings, ATR ratio) son perezosas: ver ``Indicadores``. Las claves
base no cambian, así que e01..e09 dan los mismos números.
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


import re

_ORB = re.compile(r"^orb([HL])(\d+)$")


def _extra_sesiones(bars, inds):
    om, h, l = bars.om, bars.high, bars.low
    out = {}
    for pref, ini, fin in (("asia", 18 * 60, 2 * 60), ("londres", 2 * 60, 8 * 60 + 30),
                           ("pm", 8 * 60, 9 * 60 + 30), ("md", 12 * 60, 15 * 60)):
        out[pref + "H"], out[pref + "L"] = ind.rango_sesion(om, h, l, ini, fin)
    return out


def _extra_rth(bars, inds):
    return ind.sesion_rth(bars.om, bars.open, bars.high, bars.low, bars.close, bars.volume)


def _extra_5m(bars, inds):
    o5, h5, l5, c5, v5, idx5, nuevo5 = ind.velas_5m(bars.om, bars.open, bars.high, bars.low,
                                                    bars.close, bars.volume)
    return {"open5m": o5, "high5m": h5, "low5m": l5, "close5m": c5, "volume5m": v5,
            "idx5": idx5, "nuevo5": nuevo5,
            "ema9_5m": ind.ema(c5, 9), "ema21_5m": ind.ema(c5, 21),
            "adx5m": ind.adx(h5, l5, c5), "rsi5m": ind.rsi(c5)}


def _extra_swings(bars, inds):
    sh, sl = ind.ultimos_swings(bars.high, bars.low, inds._swing)
    return {"ultSH": sh, "ultSL": sl}


# clave -> constructor (devuelve un dict con esa clave y sus hermanas)
_EXTRAS = {
    "om": lambda b, d: {"om": b.om}, "open": lambda b, d: {"open": b.open},
    "high": lambda b, d: {"high": b.high}, "low": lambda b, d: {"low": b.low},
    "volume": lambda b, d: {"volume": b.volume},
    "ema9": lambda b, d: {"ema9": ind.ema(b.close, 9)},
    "ema21": lambda b, d: {"ema21": ind.ema(b.close, 21)},
    "sigmaNY": lambda b, d: {"sigmaNY": ind.vwap_ny_sigma(b.om, b.high, b.low, b.close, b.volume)},
    "cvd": lambda b, d: {"cvd": ind.delta_acumulado(b.om, b.open, b.high, b.low, b.close, b.volume)},
    "atrRatio": lambda b, d: {"atrRatio": ind.atr_ratio(b.high, b.low, b.close)},
}
for _k in ("asiaH", "asiaL", "londresH", "londresL", "pmH", "pmL", "mdH", "mdL"):
    _EXTRAS[_k] = _extra_sesiones
for _k in ("aperturaRTH", "cierrePrevio", "atrD", "poc", "vah", "val"):
    _EXTRAS[_k] = _extra_rth
for _k in ("open5m", "high5m", "low5m", "close5m", "volume5m", "idx5", "nuevo5", "ema9_5m",
           "ema21_5m", "adx5m", "rsi5m"):
    _EXTRAS[_k] = _extra_5m
for _k in ("ultSH", "ultSL"):
    _EXTRAS[_k] = _extra_swings


class Indicadores(dict):
    """Dict de indicadores. Las claves base (las de e01..e09) se calculan al crear;
    las de e10..e18 se calculan la primera vez que alguna estrategia las pide y
    quedan guardadas (una sola vez para todas). Claves perezosas:

    * velas: ``om``, ``open``, ``high``, ``low``, ``volume``.
    * rangos de sesión (NA hasta que la ventana termina, solo esa fecha):
      ``asiaH/L`` 18:00-02:00, ``londresH/L`` 02:00-08:30, ``pmH/L`` 08:00-09:30,
      ``mdH/L`` 12:00-15:00, ``orbH<N>``/``orbL<N>`` 09:30-09:30+N min.
    * RTH diario: ``aperturaRTH``, ``cierrePrevio``, ``atrD``, ``poc``, ``vah``, ``val``.
    * 1m: ``ema9``, ``ema21``, ``sigmaNY``, ``cvd``, ``atrRatio``, ``ultSH``, ``ultSL``.
    * 5m (índice de 5m; ``idx5``/``nuevo5`` por vela de 1m): ``open5m`` .. ``volume5m``,
      ``ema9_5m``, ``ema21_5m``, ``adx5m``, ``rsi5m``.
    """

    def __init__(self, bars, base, swing=3):
        super().__init__(base)
        self._bars = bars
        self._swing = swing

    def __missing__(self, key):
        m = _ORB.match(key) if isinstance(key, str) else None
        if m:
            mins = int(m.group(2))
            hh, ll = ind.rango_sesion(self._bars.om, self._bars.high, self._bars.low,
                                      ind.RTH_INI, ind.RTH_INI + mins)
            self["orbH%d" % mins], self["orbL%d" % mins] = hh, ll
            return self[key]
        f = _EXTRAS.get(key)
        if f is None:
            raise KeyError(key)
        self.update(f(self._bars, self))
        return self[key]


def compute_indicators(bars, swing=3):
    h, l, c, v = bars.high, bars.low, bars.close, bars.volume
    macd_l, _macd_s, macd_h = ind.macd(c)
    up, dn = macd_cross_zero(macd_l)
    return Indicadores(bars, {
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
    }, swing)


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
