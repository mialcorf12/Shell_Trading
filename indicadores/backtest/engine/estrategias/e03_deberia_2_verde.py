"""deberia_2_verde: RSI + línea MACD, solo nivel verde (buyG)."""

from ._comun import VERDE, REGLA_NIVEL, fmt, motivo_filtro, senales_tier

ID = 3
NOMBRE = "deberia_2_verde"
DESCRIPCION = "RSI y linea MACD, solo nivel verde (ADX>=25 y VolRel>=1.5)."
REGLA = ("RSI>50, MACD linea>0, " + REGLA_NIVEL[VERDE]
         + "; corto: RSI<50, MACD linea<0, mismo filtro")


def senales(ind, incluir_amarillo=True):
    rsi, x = ind["rsi"], ind["macdL"]
    n = len(rsi)
    largo, corto = bytearray(n), bytearray(n)
    for i in range(n):
        r = rsi[i]
        h = x[i]
        if r > 50 and h > 0:
            largo[i] = 1
        elif r < 50 and h < 0:
            corto[i] = 1
    return senales_tier(ind, largo, corto, VERDE, incluir_amarillo)


def motivo(ind, i, side):
    r, h = fmt(ind["rsi"][i]), fmt(ind["macdL"][i])
    if side == "long":
        base = "RSI %s>50; MACD linea %s>0" % (r, h)
    else:
        base = "RSI %s<50; MACD linea %s<0" % (r, h)
    return base + "; " + motivo_filtro(ind, i)
