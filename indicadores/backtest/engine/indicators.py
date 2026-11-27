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
from collections import deque

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


# ---------------------------------------------------------------------------
# Indicadores de sesión y de las estrategias e10..e18 (ver odd S13).
#
# Todos se calculan vela a vela: el valor en la vela ``i`` usa solo datos hasta
# el CIERRE de ``i``. ``om`` = minuto absoluto de APERTURA (ET); ``om % 1440`` =
# minuto del día; ``om // 1440`` = ordinal de la fecha de apertura.
# ---------------------------------------------------------------------------

RTH_INI = 9 * 60 + 30   # 09:30 ET
RTH_FIN = 16 * 60       # 16:00 ET (apertura < 16:00 = vela de RTH)


def rango_sesion(om, high, low, ini, fin):
    """Máximo y mínimo de la ventana de apertura ``[ini, fin)`` (minutos del día).

    Si ``ini > fin`` la ventana cruza la medianoche (p. ej. Asia 18:00-02:00) y
    pertenece a la fecha en que termina. El valor existe solo DESPUÉS de la
    ventana (vela con apertura >= ``fin``) y en la misma fecha en que terminó;
    dentro de la ventana y en otras fechas es NA. Así nunca hay mirada al futuro.
    """
    n = len(om)
    oh, ol = _nan_array(n), _nan_array(n)
    cruza = ini > fin
    key = None
    h = l = NAN
    for i in range(n):
        t = om[i]
        m = t % 1440
        d = t // 1440
        if cruza:
            dentro = m >= ini or m < fin
        else:
            dentro = ini <= m < fin
        if dentro:
            k = d + 1 if (cruza and m >= ini) else d
            if k != key:
                key = k
                h = high[i]
                l = low[i]
            else:
                if high[i] > h:
                    h = high[i]
                if low[i] < l:
                    l = low[i]
        elif key == d and m >= fin:
            oh[i] = h
            ol[i] = l
    return oh, ol


def _perfil_niveles(prof, paso):
    """POC/VAH/VAL de un perfil ``{bin: volumen}`` con el método del indicador Pine
    (área de valor 70%, se expande hacia el lado con más volumen; empate arriba)."""
    lo = min(prof)
    hi = max(prof)
    vals = [prof.get(k, 0.0) for k in range(lo, hi + 1)]
    total = sum(vals)
    mx = max(vals)
    poc = vals.index(mx)
    va_lo = va_hi = poc
    acc = vals[poc]
    nb = len(vals)
    while acc < 0.7 * total and (va_lo > 0 or va_hi < nb - 1):
        below = vals[va_lo - 1] if va_lo > 0 else -1.0
        above = vals[va_hi + 1] if va_hi < nb - 1 else -1.0
        if above >= below:
            va_hi += 1
            acc += above
        else:
            va_lo -= 1
            acc += below
    return ((lo + poc + 0.5) * paso, (lo + va_hi + 1) * paso, (lo + va_lo) * paso)


def sesion_rth(om, open_, high, low, close, volume, atr_len=14, paso_perfil=1.0):
    """Datos diarios de la sesión regular (velas con apertura en [09:30, 16:00)).

    Devuelve un dict de arrays por vela:

    * ``aperturaRTH``: open de la primera vela RTH de la fecha (solo en velas RTH).
    * ``cierrePrevio``: cierre RTH (último close con apertura < 16:00) de la
      sesión RTH anterior a la fecha de la vela.
    * ``atrD``: media simple del rango verdadero diario RTH de las ``atr_len``
      sesiones anteriores (TR = max(H-L, |H-Cprev|, |L-Cprev|); la primera
      sesión usa H-L). NA con menos de ``atr_len`` sesiones.
    * ``poc``, ``vah``, ``val``: perfil de volumen de la sesión RTH anterior,
      bins de ``paso_perfil`` puntos; el volumen de cada vela se reparte por
      igual entre los bins que toca (como el indicador Pine); área de valor 70%.

    Una sesión se cierra en la primera vela con apertura >= 16:00 o de otra fecha.
    """
    n = len(om)
    ap = _nan_array(n)
    cp = _nan_array(n)
    atr_d = _nan_array(n)
    poc_a, vah_a, val_a = _nan_array(n), _nan_array(n), _nan_array(n)
    cerradas = []  # (fecha, cierre, poc, vah, val)
    trs = []
    abierta = None  # [fecha, open, high, low, close, perfil]
    prev_c = NAN
    ult_atr = NAN

    def cerrar(s):
        nonlocal prev_c, ult_atr
        d, _o, h, l, c, prof = s
        tr = h - l if prev_c != prev_c else max(h - l, abs(h - prev_c), abs(l - prev_c))
        trs.append(tr)
        prev_c = c
        ult_atr = sum(trs[-atr_len:]) / atr_len if len(trs) >= atr_len else NAN
        p = _perfil_niveles(prof, paso_perfil) if prof else (NAN, NAN, NAN)
        cerradas.append((d, c, p[0], p[1], p[2], ult_atr))

    for i in range(n):
        t = om[i]
        m = t % 1440
        d = t // 1440
        rth = RTH_INI <= m < RTH_FIN
        if abierta is not None and (d != abierta[0] or not rth):
            cerrar(abierta)
            abierta = None
        if rth:
            if abierta is None:
                abierta = [d, open_[i], high[i], low[i], close[i], {}]
            else:
                if high[i] > abierta[2]:
                    abierta[2] = high[i]
                if low[i] < abierta[3]:
                    abierta[3] = low[i]
                abierta[4] = close[i]
            prof = abierta[5]
            b1 = int(math.floor(low[i] / paso_perfil))
            b2 = int(math.floor(high[i] / paso_perfil))
            share = volume[i] / (b2 - b1 + 1)
            for b in range(b1, b2 + 1):
                prof[b] = prof.get(b, 0.0) + share
            ap[i] = abierta[1]
        # sesión anterior a la fecha d (si la de hoy ya cerró, es la penúltima)
        prev = None
        for k in (-1, -2):
            if len(cerradas) >= -k and cerradas[k][0] < d:
                prev = cerradas[k]
                break
        if prev is not None:
            cp[i] = prev[1]
            poc_a[i], vah_a[i], val_a[i] = prev[2], prev[3], prev[4]
            atr_d[i] = prev[5]
    return {"aperturaRTH": ap, "cierrePrevio": cp, "atrD": atr_d,
            "poc": poc_a, "vah": vah_a, "val": val_a}


def velas_5m(om, open_, high, low, close, volume):
    """Velas de 5 minutos derivadas de las de 1m por hora de APERTURA
    (bloque = ``om // 5``: :00, :05, ...).

    Una vela de 5m se cierra en la vela de 1m que abre en el último minuto del
    bloque (``om % 5 == 4``) o, si ese minuto falta, en la primera vela de 1m de
    un bloque posterior (antes de sumar esa vela). Devuelve
    ``(o5, h5, l5, c5, v5, idx5, nuevo5)``: series de 5m, el índice de la última
    vela de 5m cerrada en cada vela de 1m (-1 si ninguna) y 1 en la vela de 1m
    donde se cerró una vela de 5m. Sin mirada al futuro.
    """
    n = len(om)
    o5, h5, l5, c5, v5 = array("d"), array("d"), array("d"), array("d"), array("d")
    idx5 = array("q", [-1]) * n
    nuevo5 = bytearray(n)
    cur = None  # [bloque, o, h, l, c, v]
    ult = -1
    for i in range(n):
        b = om[i] // 5
        if cur is not None and cur[0] != b:
            o5.append(cur[1]); h5.append(cur[2]); l5.append(cur[3]); c5.append(cur[4]); v5.append(cur[5])
            ult += 1
            nuevo5[i] = 1
            cur = None
        if cur is None:
            cur = [b, open_[i], high[i], low[i], close[i], volume[i]]
        else:
            if high[i] > cur[2]:
                cur[2] = high[i]
            if low[i] < cur[3]:
                cur[3] = low[i]
            cur[4] = close[i]
            cur[5] += volume[i]
        if om[i] % 5 == 4:
            o5.append(cur[1]); h5.append(cur[2]); l5.append(cur[3]); c5.append(cur[4]); v5.append(cur[5])
            ult += 1
            nuevo5[i] = 1
            cur = None
        idx5[i] = ult
    return o5, h5, l5, c5, v5, idx5, nuevo5


def vwap_ny_sigma(om, high, low, close, volume):
    """Desviación estándar ponderada por volumen del precio típico alrededor del
    VWAP NY (mismo ancla que ``vwap_ny``): sqrt(sum(v*tp^2)/sum(v) - vwap^2).
    Bandas = vwapNY +/- sigma. NA antes del primer ancla."""
    n = len(close)
    out = _nan_array(n)
    pv = pv2 = v = 0.0
    started = False
    prev_anchor = False
    for i in range(n):
        anchor = (om[i] % 1440) == ANCHOR_NY_MINUTE
        if anchor and not prev_anchor:
            pv = pv2 = v = 0.0
            started = True
        prev_anchor = anchor
        if not started:
            continue
        vol = volume[i]
        tp = (high[i] + low[i] + close[i]) / 3.0
        pv += tp * vol
        pv2 += tp * tp * vol
        v += vol
        if v > 0:
            mu = pv / v
            var = pv2 / v - mu * mu
            out[i] = math.sqrt(var) if var > 0 else 0.0
    return out


def delta_acumulado(om, open_, high, low, close, volume):
    """Delta APROXIMADO acumulado desde el ancla 09:30 ET (como el VWAP NY).
    Delta por vela = volumen x (cierre - apertura) / rango (0 si rango 0), la
    misma aproximación del indicador Pine. No es footprint (no hay agresión real)."""
    n = len(close)
    out = _nan_array(n)
    acc = 0.0
    started = False
    prev_anchor = False
    for i in range(n):
        anchor = (om[i] % 1440) == ANCHOR_NY_MINUTE
        if anchor and not prev_anchor:
            acc = 0.0
            started = True
        prev_anchor = anchor
        if not started:
            continue
        rng = high[i] - low[i]
        if rng > 0:
            acc += volume[i] * (close[i] - open_[i]) / rng
        out[i] = acc
    return out


def ultimos_swings(high, low, swing=3):
    """Último swing alto/bajo confirmado en la vela ``i`` (mismos pivotes que
    ``structure_trend``: centro ``i-swing`` en la ventana ``[i-2s, i]``)."""
    n = len(high)
    sh, sl = _nan_array(n), _nan_array(n)
    last_sh = NAN
    last_sl = NAN
    w = 2 * swing
    for i in range(n):
        if i >= w:
            c = i - swing
            if high[c] >= max(high[i - w:i + 1]):
                last_sh = high[c]
            if low[c] <= min(low[i - w:i + 1]):
                last_sl = low[c]
        sh[i] = last_sh
        sl[i] = last_sl
    return sh, sl


def atr(high, low, close, length=14):
    """ta.atr: RMA del rango verdadero; la primera vela usa high - low."""
    n = len(close)
    tr = _nan_array(n)
    for i in range(n):
        if i == 0:
            tr[i] = high[i] - low[i]
        else:
            pc = close[i - 1]
            tr[i] = max(high[i] - low[i], abs(high[i] - pc), abs(low[i] - pc))
    return rma(tr, length)


def sma_valida(src, length):
    """SMA que ignora el NA inicial (empieza en el primer valor válido)."""
    n = len(src)
    out = _nan_array(n)
    acc = 0.0
    vals = deque()
    for i in range(n):
        x = src[i]
        if x != x:
            continue
        vals.append(x)
        acc += x
        if len(vals) > length:
            acc -= vals.popleft()
        if len(vals) == length:
            out[i] = acc / length
    return out


def atr_ratio(high, low, close, length=14, media=50):
    """ATR(14) / SMA(ATR, 50) como el indicador Pine (NA si la media no existe o es 0)."""
    a = atr(high, low, close, length)
    s = sma_valida(a, media)
    out = _nan_array(len(a))
    for i in range(len(a)):
        m = s[i]
        if m == m and m > 0:
            out[i] = a[i] / m
    return out
