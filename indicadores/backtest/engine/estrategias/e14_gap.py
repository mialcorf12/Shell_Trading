"""gap: Gap Fill / Gap and Go en la apertura NY (idea 5 de 00_Nuevas.md).

Gap = (apertura RTH 09:30 - cierre RTH previo) / cierre RTH previo. El cierre
previo es el último cierre con apertura < 16:00 ET de la sesión RTH anterior
(``cierrePrevio``); la apertura es el open de la vela de 09:30 (``aperturaRTH``).
Umbral 0.5% = regla del documento (gaps pequeños se cierran, grandes continúan).

* Gap Fill (0 < |gap| < 0.5%), gap alcista: en los primeros 15 minutos
  (09:30-09:44) el precio intentó continuar (máximo > apertura) y el intento
  falla: entrada CORTA en la primera vela con apertura entre 09:45 y 11:30 ET que
  cierra por debajo de la apertura y todavía por encima del cierre previo (el gap
  sigue abierto). Gap bajista en espejo (largo).
* Gap and Go (|gap| >= 0.5%), gap alcista: entrada LARGA en la primera vela con
  apertura >= 09:45 ET (antes de 10:00) si su cierre está por encima de la
  apertura y ningún cierre de 09:30-09:44 quedó por debajo de la apertura (el
  precio sostiene el lado del gap). Gap bajista en espejo (corto).

Una entrada por fecha como máximo. Solo nivel verde.
"""

from ._comun import evento_en, fmt, hhmm, hora, inicio_dia, senales_eventos

ID = 14
NOMBRE = "gap"
DESCRIPCION = "Gap Fill (<0.5%) tras fallo de continuacion o Gap and Go (>=0.5%) si sostiene la apertura."
REGLA = ("gap=(apertura 09:30-cierre RTH previo)/cierre previo; |gap|<0.5%: intento de continuacion "
         "09:30-09:44 falla y cierre vuelve al otro lado de la apertura sin cerrar el gap, 09:45-11:30, "
         "contra el gap; |gap|>=0.5%: primera vela >=09:45 a favor del gap si ningun cierre 09:30-09:44 "
         "cruzo la apertura (verde)")

UMBRAL = 0.005  # 0.5%, regla del documento
INI = hhmm(9, 30)
FIN_15 = hhmm(9, 45)
FIN_GO = hhmm(10)
FIN_FILL = hhmm(11, 30)


def _eventos(ind, a, b):
    om, h, l, c = ind["om"], ind["high"], ind["low"], ind["close"]
    ap, cp = ind["aperturaRTH"], ind["cierrePrevio"]
    dia = -1
    for i in range(a, b):
        t = om[i]
        m = t % 1440
        d = t // 1440
        if d != dia:
            dia, hecho = d, False
            hi15 = lo15 = cmin = cmax = None
        if hecho or m < INI or m >= FIN_FILL:
            continue
        A, P = ap[i], cp[i]
        if A != A or P != P or P <= 0:
            continue
        if m < FIN_15:
            hi15 = h[i] if hi15 is None else max(hi15, h[i])
            lo15 = l[i] if lo15 is None else min(lo15, l[i])
            cmin = c[i] if cmin is None else min(cmin, c[i])
            cmax = c[i] if cmax is None else max(cmax, c[i])
            continue
        if hi15 is None:
            hecho = True  # sin velas en los primeros 15 minutos
            continue
        gap = (A - P) / P
        ci = c[i]
        info = {"gap": gap, "A": A, "P": P, "hi15": hi15, "lo15": lo15, "cmin": cmin, "cmax": cmax}
        if gap == 0:
            hecho = True
        elif abs(gap) < UMBRAL:
            if gap > 0 and hi15 > A and P < ci < A:
                hecho = True
                yield i, -1, dict(info, tipo="fill")
            elif gap < 0 and lo15 < A and A < ci < P:
                hecho = True
                yield i, 1, dict(info, tipo="fill")
        else:
            hecho = True  # solo la primera vela >= 09:45
            if m >= FIN_GO:
                continue
            if gap > 0 and cmin >= A and ci > A:
                yield i, 1, dict(info, tipo="go")
            elif gap < 0 and cmax <= A and ci < A:
                yield i, -1, dict(info, tipo="go")


def senales(ind, incluir_amarillo=True):
    n = len(ind["close"])
    return senales_eventos(n, _eventos(ind, 0, n))


def motivo(ind, i, side):
    s = evento_en(_eventos(ind, inicio_dia(ind["om"], i), i + 1), i, side)
    if s is None:
        return "sin evento"
    c = fmt(ind["close"][i])
    g = "gap %+.2f%% (apertura %s vs cierre previo %s)" % (s["gap"] * 100, fmt(s["A"]), fmt(s["P"]))
    if s["tipo"] == "fill":
        if side == "short":
            x = "gap fill <0.5%%: maximo 15m %s>apertura y falla; cierre %s<apertura y >cierre previo" % (
                fmt(s["hi15"]), c)
        else:
            x = "gap fill <0.5%%: minimo 15m %s<apertura y falla; cierre %s>apertura y <cierre previo" % (
                fmt(s["lo15"]), c)
    else:
        if side == "long":
            x = "gap and go >=0.5%%: cierre minimo 15m %s>=apertura; cierre %s>apertura" % (
                fmt(s["cmin"]), c)
        else:
            x = "gap and go >=0.5%%: cierre maximo 15m %s<=apertura; cierre %s<apertura" % (
                fmt(s["cmax"]), c)
    return "%s; %s a las %s (verde)" % (g, x, hora(ind["om"][i]))
