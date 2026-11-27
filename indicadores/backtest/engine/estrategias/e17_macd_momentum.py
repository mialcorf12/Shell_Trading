"""macd_momentum: scalping de momentum con el histograma MACD (idea 8 de 00_Nuevas.md).

Solo velas con apertura en 09:30-11:30 ET o 15:00-16:00 ET (se evita el
mediodía, 12:00-14:00 en el documento). Largo: histograma MACD(12,26,9) > 0 y
mayor que el de la vela previa (cruce de cero o expansión), estructura alcista
(``trend`` = 1, precio sobre la estructura inmediata). Filtros de volatilidad y
volumen como el indicador: ATR ratio = ATR(14) / SMA(ATR, 50) entre 0.8 y 1.5
(ni muerto ni extremo) y VolRel >= 1.5. Corto en espejo. Solo nivel verde.
"""

from ._comun import VERDE, fmt, hhmm, hora, sesgo

ID = 17
NOMBRE = "macd_momentum"
DESCRIPCION = ("Histograma MACD que cruza cero o se expande a favor de la estructura, 09:30-11:30 "
               "y 15:00-16:00 ET, con ATR ratio y VolRel.")
REGLA = ("09:30-11:30 o 15:00-16:00 ET, MACD hist>0 y sube vs vela previa, estructura alcista, "
         "0.8<=ATR ratio<=1.5, VolRel>=1.5 (verde); corto: hist<0 y baja, estructura bajista, mismo filtro")

VENTANAS = ((hhmm(9, 30), hhmm(11, 30)), (hhmm(15), hhmm(16)))
ATR_MIN, ATR_MAX = 0.8, 1.5
VOLREL_MIN = 1.5


def senales(ind, incluir_amarillo=True):
    om, hist, tr = ind["om"], ind["macdH"], ind["trend"]
    ar, vr = ind["atrRatio"], ind["volRel"]
    n = len(om)
    buy, sell, tier = bytearray(n), bytearray(n), bytearray(n)
    (a1, b1), (a2, b2) = VENTANAS
    for i in range(1, n):
        m = om[i] % 1440
        if not (a1 <= m < b1 or a2 <= m < b2):
            continue
        x = ar[i]
        if not (ATR_MIN <= x <= ATR_MAX and vr[i] >= VOLREL_MIN):
            continue
        hh, hp = hist[i], hist[i - 1]
        if hh > 0 and hh > hp and tr[i] == 1:
            buy[i], tier[i] = 1, VERDE
        elif hh < 0 and hh < hp and tr[i] == -1:
            sell[i], tier[i] = 1, VERDE
    return buy, sell, tier


def motivo(ind, i, side):
    hh, hp = ind["macdH"][i], ind["macdH"][i - 1]
    op = ">" if side == "long" else "<"
    return ("hora %s; MACD hist %s%s0 y %s previa %s; %s; ATR ratio %s en 0.8-1.5; "
            "VolRel %s>=1.5 (verde)" % (
                hora(ind["om"][i]), fmt(hh), op, op, fmt(hp), sesgo(ind, i),
                fmt(ind["atrRatio"][i]), fmt(ind["volRel"][i])))
