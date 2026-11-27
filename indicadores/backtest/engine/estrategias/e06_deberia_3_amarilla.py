"""deberia_3_amarilla: RSI + histograma MACD + sesgo de estructura, solo nivel amarillo (amarillo = buyY y no buyG)."""

from ._comun import AMARILLO, REGLA_NIVEL, fmt, motivo_filtro, sesgo, senales_tier

ID = 6
NOMBRE = "deberia_3_amarilla"
DESCRIPCION = "RSI e histograma MACD con sesgo de estructura, solo nivel amarillo (ADX>=20 o VolRel>=0.8, sin verde)."
REGLA = ("RSI>50, MACD hist>0, estructura alcista, " + REGLA_NIVEL[AMARILLO]
         + "; corto: RSI<50, MACD hist<0, estructura bajista, mismo filtro")


def senales(ind, incluir_amarillo=True):
    rsi, x, tr = ind["rsi"], ind["macdH"], ind["trend"]
    n = len(rsi)
    largo, corto = bytearray(n), bytearray(n)
    for i in range(n):
        r = rsi[i]
        h = x[i]
        if r > 50 and h > 0 and tr[i] == 1:
            largo[i] = 1
        elif r < 50 and h < 0 and tr[i] == -1:
            corto[i] = 1
    return senales_tier(ind, largo, corto, AMARILLO, incluir_amarillo)


def motivo(ind, i, side):
    r, h = fmt(ind["rsi"][i]), fmt(ind["macdH"][i])
    if side == "long":
        base = "RSI %s>50; MACD hist %s>0" % (r, h)
    else:
        base = "RSI %s<50; MACD hist %s<0" % (r, h)
    return "%s; %s; %s" % (base, sesgo(ind, i), motivo_filtro(ind, i))
