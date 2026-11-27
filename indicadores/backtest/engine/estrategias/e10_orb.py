"""orb: Opening Range Breakout de la apertura NY (idea 1 de 00_Nuevas.md).

Rango = máximo/mínimo de las velas con apertura en [09:30, 09:30 + ORB_MINUTOS)
ET (``orbH<N>``/``orbL<N>``; el documento permite 5, 15 o 30; por defecto 15).
Entrada al cierre de la primera vela de 1m que cierra fuera del rango (cruce:
cierre previo dentro), entre el fin del rango y las 16:00 ET, como máximo un
largo y un corto por fecha. Filtros: VolRel > 1.5 en la vela de ruptura y
ancho del rango < 50% del ATR diario (``atrD``: media del rango verdadero RTH
de las 14 sesiones anteriores). Solo nivel verde.
"""

from ._comun import VERDE, fmt, hhmm, hora

ORB_MINUTOS = 15
VOLREL_MIN = 1.5
MAX_FRAC_ATR = 0.5

ID = 10
NOMBRE = "orb"
DESCRIPCION = ("Ruptura del rango de apertura NY (%d min) con volumen relativo y rango menor "
               "al 50%% del ATR diario." % ORB_MINUTOS)
REGLA = ("cierre 1m > max rango 09:30-09:%02d ET (primer cruce del dia, hasta 16:00), VolRel>1.5, "
         "rango<0.5 x ATR diario 14 sesiones (verde); corto: cierre < min rango, mismo filtro"
         % (30 + ORB_MINUTOS))

_FIN = hhmm(16)


def _filtro(ind, i):
    hh = ind["orbH%d" % ORB_MINUTOS][i]
    ll = ind["orbL%d" % ORB_MINUTOS][i]
    a = ind["atrD"][i]
    return ind["volRel"][i] > VOLREL_MIN and (hh - ll) < MAX_FRAC_ATR * a


def senales(ind, incluir_amarillo=True):
    om, c = ind["om"], ind["close"]
    hh, ll = ind["orbH%d" % ORB_MINUTOS], ind["orbL%d" % ORB_MINUTOS]
    n = len(c)
    buy, sell, tier = bytearray(n), bytearray(n), bytearray(n)
    ini = hhmm(9, 30) + ORB_MINUTOS
    dia, hecho_l, hecho_c = -1, False, False
    for i in range(1, n):
        t = om[i]
        m = t % 1440
        if m < ini or m >= _FIN:
            continue
        d = t // 1440
        if d != dia:
            dia, hecho_l, hecho_c = d, False, False
        h, l = hh[i], ll[i]
        if h != h:
            continue
        ci, cp = c[i], c[i - 1]
        if not hecho_l and ci > h and cp <= h:
            hecho_l = True
            if _filtro(ind, i):
                buy[i], tier[i] = 1, VERDE
        elif not hecho_c and ci < l and cp >= l:
            hecho_c = True
            if _filtro(ind, i):
                sell[i], tier[i] = 1, VERDE
    return buy, sell, tier


def motivo(ind, i, side):
    hh = ind["orbH%d" % ORB_MINUTOS][i]
    ll = ind["orbL%d" % ORB_MINUTOS][i]
    c, a, v = ind["close"][i], ind["atrD"][i], ind["volRel"][i]
    if side == "long":
        base = "cierre %s>max ORB %dm %s" % (fmt(c), ORB_MINUTOS, fmt(hh))
    else:
        base = "cierre %s<min ORB %dm %s" % (fmt(c), ORB_MINUTOS, fmt(ll))
    return "%s a las %s; VolRel %s>1.5; rango %s<0.5 x ATR diario %s (verde)" % (
        base, hora(ind["om"][i]), fmt(v), fmt(hh - ll), fmt(a))
