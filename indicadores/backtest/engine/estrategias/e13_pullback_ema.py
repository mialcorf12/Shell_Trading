"""pullback_ema: retroceso a la zona EMA 9 / EMA 21 en 5 minutos (idea 4 de 00_Nuevas.md).

Se evalúa en cada vela de 5m cerrada (``nuevo5``; velas de 5m derivadas de 1m por
hora de apertura, ver ``engine.indicators.velas_5m``) y se entra al cierre de la
vela de 1m que la cierra, con apertura entre 09:30 y 16:00 ET. Vela de 5m ``k``:

* Tendencia alcista: EMA9 > EMA21, EMA9[k] > EMA9[k-5] (pendiente positiva en 5
  velas de 5m) y ADX(14) de 5m >= 25.
* Retroceso: el mínimo de la vela k o de la k-1 llega a la EMA9 (entra en la
  zona EMA9-EMA21) y ninguno de los dos cierres queda por debajo de la EMA21.
* Entrada: la vela k cierra por encima de la EMA9.

Corto en espejo. Solo nivel verde.
"""

from ._comun import VERDE, fmt, hhmm, hora

ID = 13
NOMBRE = "pullback_ema"
DESCRIPCION = "Retroceso a la zona EMA9-EMA21 de 5m con tendencia (pendiente EMA9 y ADX 5m>=25)."
REGLA = ("5m: EMA9>EMA21, EMA9 sube vs 5 velas, ADX14 5m>=25, minimo (vela o previa)<=EMA9, cierres "
         ">=EMA21, cierre>EMA9; 09:30-16:00 ET (verde); corto en espejo")

ADX_MIN = 25
PENDIENTE = 5
INI = hhmm(9, 30)
FIN = hhmm(16)


def _lado(ind, k):
    e9, e21, adx = ind["ema9_5m"], ind["ema21_5m"], ind["adx5m"]
    lo, hi, c = ind["low5m"], ind["high5m"], ind["close5m"]
    if k < PENDIENTE or not adx[k] >= ADX_MIN:
        return 0
    a, b = e9[k], e21[k]
    if a > b and a > e9[k - PENDIENTE]:
        if min(lo[k], lo[k - 1]) <= a and min(c[k], c[k - 1]) >= b and c[k] > a:
            return 1
    elif a < b and a < e9[k - PENDIENTE]:
        if max(hi[k], hi[k - 1]) >= a and max(c[k], c[k - 1]) <= b and c[k] < a:
            return -1
    return 0


def senales(ind, incluir_amarillo=True):
    om, nuevo5, idx5 = ind["om"], ind["nuevo5"], ind["idx5"]
    n = len(om)
    buy, sell, tier = bytearray(n), bytearray(n), bytearray(n)
    for i in range(n):
        if not nuevo5[i]:
            continue
        m = om[i] % 1440
        if m < INI or m >= FIN:
            continue
        s = _lado(ind, idx5[i])
        if s == 1:
            buy[i], tier[i] = 1, VERDE
        elif s == -1:
            sell[i], tier[i] = 1, VERDE
    return buy, sell, tier


def motivo(ind, i, side):
    k = ind["idx5"][i]
    e9, e21 = ind["ema9_5m"], ind["ema21_5m"]
    if side == "long":
        z = "minimo %s<=EMA9; cierre %s>EMA9" % (fmt(min(ind["low5m"][k], ind["low5m"][k - 1])),
                                                 fmt(ind["close5m"][k]))
        t = "EMA9 %s>EMA21 %s; EMA9 sube desde %s" % (fmt(e9[k]), fmt(e21[k]), fmt(e9[k - PENDIENTE]))
    else:
        z = "maximo %s>=EMA9; cierre %s<EMA9" % (fmt(max(ind["high5m"][k], ind["high5m"][k - 1])),
                                                 fmt(ind["close5m"][k]))
        t = "EMA9 %s<EMA21 %s; EMA9 baja desde %s" % (fmt(e9[k]), fmt(e21[k]), fmt(e9[k - PENDIENTE]))
    return "5m cerrada a las %s: %s; ADX 5m %s>=25; %s (verde)" % (
        hora(ind["om"][i] + 1), t, fmt(ind["adx5m"][k]), z)
