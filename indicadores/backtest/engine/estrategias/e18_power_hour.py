"""power_hour: ruptura del rango del mediodía en la última hora (idea 10 de 00_Nuevas.md).

Rango = máximo/mínimo de las velas con apertura en [12:00, 15:00) ET
(``mdH``/``mdL``). Sesgo de la mañana = signo de (cierre - VWAP NY) en la última
vela con apertura antes de las 11:30 ET (la que cierra a las 11:30) de la misma
fecha. Entre 15:00 y 16:00 ET: largo al cierre de la primera vela que cierra por
encima del máximo del rango (cierre previo <= máximo) si el sesgo es alcista;
corto en espejo si el sesgo es bajista. Una entrada por fecha. El documento
sugiere un rango "estrecho"; no se filtra por ancho. Solo nivel verde.
"""

from ._comun import evento_en, fmt, hhmm, hora, inicio_dia, senales_eventos

ID = 18
NOMBRE = "power_hour"
DESCRIPCION = "Ruptura del rango 12:00-15:00 ET en la ultima hora a favor del sesgo de la manana (VWAP NY a las 11:30)."
REGLA = ("15:00-16:00 ET cierre>max rango 12:00-14:59 (primer cruce), sesgo manana alcista: cierre>"
         "VWAP NY a las 11:30 (verde); corto: cierre<min rango y sesgo bajista")

SESGO_FIN = hhmm(11, 30)
INI = hhmm(15)
FIN = hhmm(16)
RTH = hhmm(9, 30)


def _eventos(ind, a, b):
    om, c, vw = ind["om"], ind["close"], ind["vwapNY"]
    mH, mL = ind["mdH"], ind["mdL"]
    dia = -1
    for i in range(a, b):
        t = om[i]
        m = t % 1440
        d = t // 1440
        if d != dia:
            dia, sesgo, ref, hecho = d, 0, None, False
        if RTH <= m < SESGO_FIN:
            v = vw[i]
            if v == v:
                sesgo = 1 if c[i] > v else (-1 if c[i] < v else 0)
                ref = (t, c[i], v)
            continue
        if hecho or m < INI or m >= FIN or i == 0 or sesgo == 0:
            continue
        H, L = mH[i], mL[i]
        if H != H:
            continue
        ci, cp = c[i], c[i - 1]
        if sesgo == 1 and ci > H and cp <= H:
            hecho = True
            yield i, 1, (H, L, ref)
        elif sesgo == -1 and ci < L and cp >= L:
            hecho = True
            yield i, -1, (H, L, ref)


def senales(ind, incluir_amarillo=True):
    n = len(ind["close"])
    return senales_eventos(n, _eventos(ind, 0, n))


def motivo(ind, i, side):
    s = evento_en(_eventos(ind, inicio_dia(ind["om"], i), i + 1), i, side)
    if s is None:
        return "sin evento"
    H, L, (t0, c0, v0) = s
    c = fmt(ind["close"][i])
    if side == "long":
        x = "cierre %s>max 12:00-15:00 %s; sesgo alcista (cierre %s>VWAP NY %s a las %s)" % (
            c, fmt(H), fmt(c0), fmt(v0), hora(t0 + 1))
    else:
        x = "cierre %s<min 12:00-15:00 %s; sesgo bajista (cierre %s<VWAP NY %s a las %s)" % (
            c, fmt(L), fmt(c0), fmt(v0), hora(t0 + 1))
    return "hora %s; %s (verde)" % (hora(ind["om"][i]), x)
