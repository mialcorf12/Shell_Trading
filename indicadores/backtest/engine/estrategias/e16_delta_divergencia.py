"""delta_divergencia: absorción por divergencia de delta en niveles del perfil (idea 7 de 00_Nuevas.md).

Delta APROXIMADO (no footprint): delta por vela = volumen x (cierre - apertura) /
rango, acumulado desde el ancla 09:30 ET (``cvd``). Es la aproximación del
indicador Pine; los datos de NT8 no traen agresión comprador/vendedor.

Niveles: POC, VAH y VAL del perfil de volumen de la sesión RTH anterior
(``poc``/``vah``/``val``; bins de 1 punto, área de valor 70%, método del
indicador Pine).

Solo velas con apertura entre 09:30 y 16:00 ET. Swings = pivotes de 1m de 3
velas a cada lado dentro de la sesión del día (confirmados 3 velas después).
Largo en la vela ``i``: su mínimo marca un nuevo mínimo contra el último swing
bajo confirmado (``low < swing``) mientras el delta acumulado al cierre de
``i`` es mayor que el delta acumulado en la vela del swing (mínimo más alto del
delta), y el mínimo está a <= 2 puntos de POC, VAH o VAL. Corto en espejo con
máximos. Solo nivel verde.
"""

from ._comun import evento_en, fmt, hhmm, inicio_dia, senales_eventos

ID = 16
NOMBRE = "delta_divergencia"
DESCRIPCION = ("Nuevo minimo/maximo contra el ultimo swing con delta acumulado aproximado divergente, "
               "a <=2 puntos de POC/VAH/VAL de la sesion anterior.")
REGLA = ("09:30-16:00 ET minimo<ultimo swing bajo y delta acumulado aprox.>delta del swing, minimo a "
         "<=2 pts de POC/VAH/VAL de la sesion RTH previa (verde); corto: maximo>ultimo swing alto y "
         "delta<delta del swing, maximo a <=2 pts")

SWING = 3
TOL = 2.0
INI = hhmm(9, 30)
FIN = hhmm(16)


def _cerca(ind, i, precio):
    mejor = None
    for k, nom in (("poc", "POC"), ("vah", "VAH"), ("val", "VAL")):
        x = ind[k][i]
        if x == x:
            dd = abs(precio - x)
            if dd <= TOL and (mejor is None or dd < mejor[2]):
                mejor = (nom, x, dd)
    return mejor


def _eventos(ind, a, b):
    om, h, l, cvd = ind["om"], ind["high"], ind["low"], ind["cvd"]
    dia = -1
    w = 2 * SWING
    for i in range(a, b):
        t = om[i]
        m = t % 1440
        d = t // 1440
        if d != dia:
            dia, i0 = d, None
            psh = psl = None  # (precio, cvd, indice)
        if m < INI or m >= FIN:
            continue
        if i0 is None:
            i0 = i
        cv = cvd[i]
        if cv == cv:
            if psl is not None and l[i] < psl[0] and cv > psl[1]:
                lv = _cerca(ind, i, l[i])
                if lv is not None:
                    yield i, 1, (psl, lv)
            elif psh is not None and h[i] > psh[0] and cv < psh[1]:
                lv = _cerca(ind, i, h[i])
                if lv is not None:
                    yield i, -1, (psh, lv)
        # pivotes confirmados con datos hasta i (después de evaluar la vela i)
        if i - w >= i0:
            c = i - SWING
            if h[c] >= max(h[i - w:i + 1]):
                psh = (h[c], cvd[c], c)
            if l[c] <= min(l[i - w:i + 1]):
                psl = (l[c], cvd[c], c)


def senales(ind, incluir_amarillo=True):
    n = len(ind["close"])
    return senales_eventos(n, _eventos(ind, 0, n))


def motivo(ind, i, side):
    s = evento_en(_eventos(ind, inicio_dia(ind["om"], i), i + 1), i, side)
    if s is None:
        return "sin evento"
    (sp, scv, _k), (nom, x, dd) = s
    cv = ind["cvd"][i]
    if side == "long":
        base = "minimo %s<swing bajo %s; delta acum. aprox. %s>%s" % (
            fmt(ind["low"][i]), fmt(sp), fmt(cv, 0), fmt(scv, 0))
    else:
        base = "maximo %s>swing alto %s; delta acum. aprox. %s<%s" % (
            fmt(ind["high"][i]), fmt(sp), fmt(cv, 0), fmt(scv, 0))
    return "%s; a %s pts de %s %s (sesion previa) (verde)" % (base, fmt(dd), nom, fmt(x))
