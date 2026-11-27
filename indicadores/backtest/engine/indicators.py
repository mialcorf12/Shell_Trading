"""Indicadores vela a vela, con las definiciones del indicador Pine.

NA se representa con ``float('nan')``: toda comparación con NaN es falsa, igual
que en Pine (``na > 50`` -> false).

Supuestos de semilla (Pine no los documenta con detalle; se eligen los usuales):

* ``rma`` (Wilder): primera salida = SMA de los primeros ``length`` valores
  válidos; luego ``rma = (rma_prev * (length - 1) + x) / length``.
* ``ema``: primera salida = SMA de los primeros ``length`` valores válidos;
  luego ``ema = alpha * x + (1 - alpha) * ema_prev`` con ``alpha = 2/(length+1)``.
* RSI(14): RMA de subidas y bajadas de ``close`` (los cambios empiezan en la
  vela 1, así que el RSI existe desde la vela 14).
* DMI(14,14): +DM/-DM/TR desde la vela 1, suavizados con RMA(14); DX con
  ``sum == 0 -> 1`` como Pine; ADX = RMA(DX, 14).
* MACD(12,26,9): ``macdL = EMA12 - EMA26``; ``macdS = EMA9(macdL)``;
  ``macdH = macdL - macdS``.
* volRel = volume / SMA(volume, 20) (NA si la SMA no existe o es 0).
* VWAP NY: se reinicia en la vela cuya APERTURA es 09:30 ET; NA antes del
  primer ancla.
* Estructura: pivotes con ventana ``[i-2s, i]`` y centro ``i-s`` (empates
  permitidos); ruptura con ``lastSH``/``lastSL`` de la vela previa.
"""

import math
from array import array

NAN = float("nan")


def _nan_array(n):
    return array("d", [NAN]) * n


def rma(src, length):
    out = _nan_array(len(src))
    acc = 0.0
    cnt = 0
    prev = NAN
    for i, x in enumerate(src):
        if x != x:  # NaN
            continue
        if cnt < length:
            acc += x
            cnt += 1
            if cnt == length:
                prev = acc / length
                out[i] = prev
            continue
        prev = (prev * (length - 1) + x) / length
        out[i] = prev
    return out


def ema(src, length):
    out = _nan_array(len(src))
    alpha = 2.0 / (length + 1)
    acc = 0.0
    cnt = 0
    prev = NAN
    for i, x in enumerate(src):
        if x != x:
            continue
        if cnt < length:
            acc += x
            cnt += 1
            if cnt == length:
                prev = acc / length
                out[i] = prev
            continue
        prev = alpha * x + (1.0 - alpha) * prev
        out[i] = prev
    return out


def sma(src, length):
    out = _nan_array(len(src))
    acc = 0.0
    for i, x in enumerate(src):
        acc += x
        if i >= length:
            acc -= src[i - length]
        if i >= length - 1:
            out[i] = acc / length
    return out


def rsi(close, length=14):
    n = len(close)
    up = _nan_array(n)
    dn = _nan_array(n)
    for i in range(1, n):
        ch = close[i] - close[i - 1]
        up[i] = ch if ch > 0 else 0.0
        dn[i] = -ch if ch < 0 else 0.0
    ru = rma(up, length)
    rd = rma(dn, length)
    out = _nan_array(n)
    for i in range(n):
        u = ru[i]
        d = rd[i]
        if u != u or d != d:
            continue
        if d == 0:
            out[i] = 100.0
        elif u == 0:
            out[i] = 0.0
        else:
            out[i] = 100.0 - 100.0 / (1.0 + u / d)
    return out


def adx(high, low, close, di_len=14, adx_len=14):
    n = len(close)
    pdm = _nan_array(n)
    mdm = _nan_array(n)
    tr = _nan_array(n)
    for i in range(1, n):
        up = high[i] - high[i - 1]
        down = low[i - 1] - low[i]
        pdm[i] = up if (up > down and up > 0) else 0.0
        mdm[i] = down if (down > up and down > 0) else 0.0
        pc = close[i - 1]
        tr[i] = max(high[i] - low[i], abs(high[i] - pc), abs(low[i] - pc))
    trur = rma(tr, di_len)
    rp = rma(pdm, di_len)
    rm = rma(mdm, di_len)
    dx = _nan_array(n)
    for i in range(n):
        t = trur[i]
        if t != t or rp[i] != rp[i]:
            continue
        if t == 0:
            continue  # Pine: fixnan; se deja NA (solo ocurre con velas planas)
        plus = 100.0 * rp[i] / t
        minus = 100.0 * rm[i] / t
        s = plus + minus
        dx[i] = abs(plus - minus) / (s if s != 0 else 1.0)
    out = rma(dx, adx_len)
    for i in range(n):
        out[i] = out[i] * 100.0
    return out


def macd(close, fast=12, slow=26, signal=9):
    ef = ema(close, fast)
    es = ema(close, slow)
    n = len(close)
    line = _nan_array(n)
    for i in range(n):
        line[i] = ef[i] - es[i]  # NaN se propaga
    sig = ema(line, signal)
    hist = _nan_array(n)
    for i in range(n):
        hist[i] = line[i] - sig[i]
    return line, sig, hist


def vol_rel(volume, length=20):
    s = sma(volume, length)
    out = _nan_array(len(volume))
    for i, v in enumerate(volume):
        m = s[i]
        if m == m and m > 0:
            out[i] = v / m
    return out


ANCHOR_NY_MINUTE = 9 * 60 + 30  # apertura 09:30 ET


def vwap_ny(om, high, low, close, volume):
    """VWAP anclado a la vela cuya APERTURA (``om``) es 09:30 ET."""
    n = len(close)
    out = _nan_array(n)
    pv = 0.0
    v = 0.0
    started = False
    prev_anchor = False
    for i in range(n):
        anchor = (om[i] % 1440) == ANCHOR_NY_MINUTE
        if anchor and not prev_anchor:
            pv = 0.0
            v = 0.0
            started = True
        prev_anchor = anchor
        if not started:
            continue
        vol = volume[i]
        pv += (high[i] + low[i] + close[i]) / 3.0 * vol
        v += vol
        if v > 0:
            out[i] = pv / v
    return out


def structure_trend(high, low, close, swing=3):
    """Sesgo de estructura: 1 alcista, -1 bajista, 0 sin definir."""
    n = len(close)
    trend = array("b", bytes(n))
    last_sh = NAN
    last_sl = NAN
    t = 0
    w = 2 * swing
    for i in range(n):
        if i > 0:
            c0 = close[i - 1]
            c1 = close[i]
            if c0 <= last_sh and c1 > last_sh:
                t = 1
            if c0 >= last_sl and c1 < last_sl:
                t = -1
        if i >= w:
            c = i - swing
            hc = high[c]
            if hc >= max(high[i - w:i + 1]):
                last_sh = hc
            lc = low[c]
            if lc <= min(low[i - w:i + 1]):
                last_sl = lc
        trend[i] = t
    return trend
