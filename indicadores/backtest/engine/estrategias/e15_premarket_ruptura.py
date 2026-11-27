"""premarket_ruptura: ruptura del máximo/mínimo pre-market con retesteo (idea 6 de 00_Nuevas.md).

Rango pre-market = velas con apertura en [08:00, 09:30) ET (``pmH``/``pmL``).
Desde 09:30 hasta 12:00 ET, largo:

1. Ruptura: cierre > máximo pre-market con cierre previo <= máximo.
2. Retesteo en <= 15 minutos desde la vela de ruptura (vela posterior): el mínimo
   vuelve al nivel (``low <= pmH``) y la vela cierra por encima (el nivel sostiene).
   Entrada al cierre de esa vela.
3. Si antes del retesteo una vela cierra en o por debajo del nivel, o pasan más
   de 15 minutos, la ruptura se descarta y se espera una nueva.

Corto en espejo con el mínimo. Un largo y un corto por fecha como máximo. El
filtro de compresión previa a las 09:30 del documento no se aplica. Solo verde.
"""

from ._comun import evento_en, fmt, hhmm, hora, inicio_dia, senales_eventos

ID = 15
NOMBRE = "premarket_ruptura"
DESCRIPCION = "Ruptura del maximo/minimo pre-market (08:00-09:29 ET) con retesteo que sostiene en 15 min."
REGLA = ("09:30-12:00 ET cierre>max pre-market 08:00-09:29, luego en <=15 min minimo<=nivel y cierre>"
         "nivel (retesteo sostenido) (verde); corto en espejo con el minimo")

INI = hhmm(9, 30)
FIN = hhmm(12)
RETEST_MIN = 15


def _eventos(ind, a, b):
    om, h, l, c = ind["om"], ind["high"], ind["low"], ind["close"]
    pH, pL = ind["pmH"], ind["pmL"]
    dia = -1
    for i in range(a, b):
        t = om[i]
        m = t % 1440
        d = t // 1440
        if d != dia:
            dia = d
            rl = rc = None  # (om, indice) de la ruptura pendiente
            hecho_l = hecho_c = False
        if m < INI or m >= FIN or i == 0:
            continue
        H, L, ci, cp = pH[i], pL[i], c[i], c[i - 1]
        if H != H:
            continue
        # largo
        if not hecho_l:
            if rl is not None and (t - rl[0] > RETEST_MIN):
                rl = None
            if rl is None:
                if ci > H and cp <= H:
                    rl = (t, i)
            elif ci <= H:
                rl = None
            elif l[i] <= H:
                hecho_l = True
                yield i, 1, {"nivel": H, "t": rl[0], "cb": c[rl[1]]}
                rl = None
        # corto
        if not hecho_c:
            if rc is not None and (t - rc[0] > RETEST_MIN):
                rc = None
            if rc is None:
                if ci < L and cp >= L:
                    rc = (t, i)
            elif ci >= L:
                rc = None
            elif h[i] >= L:
                hecho_c = True
                yield i, -1, {"nivel": L, "t": rc[0], "cb": c[rc[1]]}
                rc = None


def senales(ind, incluir_amarillo=True):
    n = len(ind["close"])
    return senales_eventos(n, _eventos(ind, 0, n))


def motivo(ind, i, side):
    s = evento_en(_eventos(ind, inicio_dia(ind["om"], i), i + 1), i, side)
    if s is None:
        return "sin evento"
    t = ind["om"][i]
    if side == "long":
        return ("ruptura max pre-market %s (cierre %s a las %s); retesteo a las %s: minimo %s<=nivel, "
                "cierre %s>nivel (verde)" % (fmt(s["nivel"]), fmt(s["cb"]), hora(s["t"]), hora(t),
                                             fmt(ind["low"][i]), fmt(ind["close"][i])))
    return ("ruptura min pre-market %s (cierre %s a las %s); retesteo a las %s: maximo %s>=nivel, "
            "cierre %s<nivel (verde)" % (fmt(s["nivel"]), fmt(s["cb"]), hora(s["t"]), hora(t),
                                         fmt(ind["high"][i]), fmt(ind["close"][i])))
