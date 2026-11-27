"""deberia_5_verde: cruce de la línea MACD por 0 + precio vs VWAP NY + sesgo.

Sin nivel amarillo: toda entrada se marca verde. El cruce usa las banderas
precalculadas ``macdCrossUp0`` / ``macdCrossDn0`` (ver ``engine.signals``).
"""

from ._comun import VERDE, fmt, sesgo

ID = 9
NOMBRE = "deberia_5_verde"
DESCRIPCION = "Cruce de la linea MACD por 0 con precio vs VWAP NY y sesgo de estructura."
REGLA = ("estructura alcista, precio>VWAP NY, cruce MACD linea sobre 0; "
         "corto: estructura bajista, precio<VWAP NY, cruce MACD linea bajo 0; sin amarillo")


def senales(ind, incluir_amarillo=True):
    close, vw, tr = ind["close"], ind["vwapNY"], ind["trend"]
    up, dn = ind["macdCrossUp0"], ind["macdCrossDn0"]
    n = len(close)
    buy, sell, tier = bytearray(n), bytearray(n), bytearray(n)
    for i in range(n):
        if up[i]:
            if tr[i] == 1 and close[i] > vw[i]:
                buy[i] = 1
                tier[i] = VERDE
        elif dn[i]:
            if tr[i] == -1 and close[i] < vw[i]:
                sell[i] = 1
                tier[i] = VERDE
    return buy, sell, tier


def motivo(ind, i, side):
    c, v = fmt(ind["close"][i]), fmt(ind["vwapNY"][i])
    m = "%+.2f" % ind["macdL"][i]
    op = ">" if side == "long" else "<"
    return "%s; precio %s%sVWAP NY %s; cruce MACD linea 0 (%s)" % (sesgo(ind, i), c, op, v, m)
