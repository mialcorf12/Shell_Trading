"""vwap_rebote: rebote/rechazo en el VWAP NY o su primera banda (idea 2 de 00_Nuevas.md).

Solo desde las 10:30 ET (tras la primera hora) hasta las 16:00 ET.

* Tendencia: estructura alcista (``trend`` = 1) para largos, bajista para cortos.
* Toque con rechazo (vela de 1m): largo si el mínimo toca el VWAP NY o la banda
  +1 sigma (``low <= nivel < close``) con mecha inferior >= 50% del rango de la
  vela; corto en espejo (VWAP o -1 sigma, mecha superior >= 50%).
* Confirmación: el RSI(14) de 5m cruza de vuelta 50 a favor de la tendencia
  (vela de 5m recién cerrada con RSI > 50 y la anterior <= 50; corto: < 50 y
  >= 50) dentro de los 15 minutos siguientes al rechazo (incluida la misma
  vela), con el cierre todavía del lado de la tendencia respecto del VWAP.

SIMPLIFICACIÓN: el documento pide "divergencia o agotamiento en RSI"; aquí se
usa el cruce de vuelta del RSI(14) de 5m por 50, sin detectar divergencias.
Solo nivel verde.
"""

from ._comun import VERDE, evento_en, fmt, hhmm, hora, inicio_dia, senales_eventos

ID = 11
NOMBRE = "vwap_rebote"
DESCRIPCION = "Rechazo en VWAP NY o banda de 1 sigma tras la primera hora, confirmado por RSI 5m."
REGLA = ("desde 10:30 ET, estructura alcista, minimo toca VWAP NY o +1 sigma y cierra arriba con "
         "mecha inferior>=50% del rango, RSI14 5m cruza sobre 50 en <=15 min, cierre>VWAP (verde); "
         "corto en espejo (VWAP o -1 sigma, RSI14 5m cruza bajo 50)")

INI = hhmm(10, 30)
FIN = hhmm(16)
VENTANA_MIN = 15
MECHA_MIN = 0.5


def _eventos(ind, a, b):
    om, o, h, l, c = ind["om"], ind["open"], ind["high"], ind["low"], ind["close"]
    vw, sg, tr = ind["vwapNY"], ind["sigmaNY"], ind["trend"]
    nuevo5, idx5, rsi5 = ind["nuevo5"], ind["idx5"], ind["rsi5m"]
    dia = -1
    arm_l = arm_c = None  # (om, nivel, texto, indice)
    for i in range(a, b):
        t = om[i]
        m = t % 1440
        d = t // 1440
        if d != dia:
            dia, arm_l, arm_c = d, None, None
        if m < INI or m >= FIN:
            continue
        v, s = vw[i], sg[i]
        rng = h[i] - l[i]
        if v == v and s == s and rng > 0:
            if tr[i] == 1 and (min(o[i], c[i]) - l[i]) >= MECHA_MIN * rng:
                for nivel, nom in ((v, "VWAP NY"), (v + s, "+1 sigma")):
                    if l[i] <= nivel < c[i]:
                        arm_l = (t, nivel, nom, i)
                        break
            if tr[i] == -1 and (h[i] - max(o[i], c[i])) >= MECHA_MIN * rng:
                for nivel, nom in ((v, "VWAP NY"), (v - s, "-1 sigma")):
                    if h[i] >= nivel > c[i]:
                        arm_c = (t, nivel, nom, i)
                        break
        if not nuevo5[i]:
            continue
        k = idx5[i]
        if k < 1:
            continue
        r, rp = rsi5[k], rsi5[k - 1]
        if arm_l is not None and t - arm_l[0] <= VENTANA_MIN and r > 50 and rp <= 50 \
                and tr[i] == 1 and c[i] > v:
            yield i, 1, (arm_l, r, rp)
            arm_l = None
        elif arm_c is not None and t - arm_c[0] <= VENTANA_MIN and r < 50 and rp >= 50 \
                and tr[i] == -1 and c[i] < v:
            yield i, -1, (arm_c, r, rp)
            arm_c = None


def senales(ind, incluir_amarillo=True):
    n = len(ind["close"])
    return senales_eventos(n, _eventos(ind, 0, n))


def motivo(ind, i, side):
    info = evento_en(_eventos(ind, inicio_dia(ind["om"], i), i + 1), i, side)
    if info is None:
        return "sin evento"
    (t0, nivel, nom, j), r, rp = info
    lado = "alcista" if side == "long" else "bajista"
    op = ">" if side == "long" else "<"
    return ("estructura %s; rechazo en %s %s a las %s (min %s, max %s, cierre %s); RSI14 5m %s->%s "
            "cruza 50; cierre %s%sVWAP NY %s (verde)" % (
                lado, nom, fmt(nivel), hora(t0), fmt(ind["low"][j]), fmt(ind["high"][j]),
                fmt(ind["close"][j]), fmt(rp), fmt(r), fmt(ind["close"][i]), op,
                fmt(ind["vwapNY"][i])))
