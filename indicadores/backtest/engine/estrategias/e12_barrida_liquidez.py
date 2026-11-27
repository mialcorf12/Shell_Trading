"""barrida_liquidez: barrida de los extremos de Asia y Londres en la apertura NY
(idea 3 de 00_Nuevas.md), con cambio de estructura y entrada en el FVG.

Niveles: máximo/mínimo de Asia (18:00-02:00 ET) y de Londres (02:00-08:30 ET)
de la misma fecha. Secuencia corta (largo en espejo), por fecha:

1. Barrida (09:30-10:30 ET): desde 09:30 el máximo supera un nivel alto y una
   vela cierra de vuelta por debajo del nivel barrido (el más alto superado).
   Extremo de la barrida = máximo desde 09:30.
2. Cambio de estructura (MSS) en 1m: cierre por debajo del último swing bajo
   confirmado (``ultSL`` de la vela previa, pivotes de 3 velas).
3. FVG bajista (3 velas: ``low[k-2] > high[k]``) formado desde la barrida; se
   usa el último. Entrada al cierre de la primera vela posterior al MSS cuyo
   máximo llega al medio del FVG y cierra por debajo de su borde superior.

Se cancela (vuelve al paso 1) si el máximo supera el extremo de la barrida; todo
vence a las 12:00 ET. Como máximo una entrada por lado y fecha. Fill al cierre
de la vela (no orden límite en el medio del FVG). Solo nivel verde.
"""

from ._comun import evento_en, fmt, hhmm, hora, inicio_dia, senales_eventos

ID = 12
NOMBRE = "barrida_liquidez"
DESCRIPCION = ("Barrida de maximos/minimos de Asia y Londres en la apertura NY, MSS en 1m y "
               "entrada en el retroceso al medio del ultimo FVG.")
REGLA = ("09:30-10:30 ET minimo rompe min Asia/Londres y cierra dentro, cierre>ultimo swing alto "
         "(MSS), retroceso al medio del ultimo FVG alcista con cierre>borde inferior, antes de 12:00 "
         "(verde); corto en espejo con maximos")

INI = hhmm(9, 30)
FIN_BARRIDA = hhmm(10, 30)
FIN = hhmm(12)


def _nuevo():
    return {"etapa": 0}


def _eventos(ind, a, b):
    om, h, l, c = ind["om"], ind["high"], ind["low"], ind["close"]
    aH, aL, lH, lL = ind["asiaH"], ind["asiaL"], ind["londresH"], ind["londresL"]
    ush, usl = ind["ultSH"], ind["ultSL"]
    dia = -1
    run_h = run_l = None
    st_c = st_l = None
    for i in range(a, b):
        t = om[i]
        m = t % 1440
        d = t // 1440
        if d != dia:
            dia, run_h, run_l, st_c, st_l = d, None, None, _nuevo(), _nuevo()
        if m < INI or m >= FIN:
            continue
        hi, lo, ci = h[i], l[i], c[i]
        run_h = hi if run_h is None or hi > run_h else run_h
        run_l = lo if run_l is None or lo < run_l else run_l

        # ---- corto: barrida de máximos ----
        s = st_c
        if s["etapa"] in (1, 2) and hi > s["ext"]:
            s = st_c = _nuevo()
        if s["etapa"] == 0:
            if m < FIN_BARRIDA:
                niv = [x for x in ((aH[i], "max Asia"), (lH[i], "max Londres"))
                       if x[0] == x[0] and run_h > x[0]]
                if niv:
                    nivel = max(niv)
                    if ci < nivel[0]:
                        s.update(etapa=1, nivel=nivel, ext=run_h, ini=i, t=t, fvg=None)
        elif s["etapa"] in (1, 2):
            if i - 2 >= s["ini"] and l[i - 2] > hi:
                s["fvg"] = (l[i - 2], hi, i)  # (borde superior, borde inferior, vela)
            if s["etapa"] == 1:
                if i > s["ini"] and ci < usl[i - 1]:
                    s.update(etapa=2, mss=usl[i - 1], tmss=t)
            else:
                f = s["fvg"]
                if f is not None and f[2] < i:
                    mid = (f[0] + f[1]) / 2.0
                    if hi >= mid and ci < f[0]:
                        s["etapa"] = 3
                        yield i, -1, dict(s, mid=mid)

        # ---- largo: barrida de mínimos ----
        s = st_l
        if s["etapa"] in (1, 2) and lo < s["ext"]:
            s = st_l = _nuevo()
        if s["etapa"] == 0:
            if m < FIN_BARRIDA:
                niv = [x for x in ((aL[i], "min Asia"), (lL[i], "min Londres"))
                       if x[0] == x[0] and run_l < x[0]]
                if niv:
                    nivel = min(niv)
                    if ci > nivel[0]:
                        s.update(etapa=1, nivel=nivel, ext=run_l, ini=i, t=t, fvg=None)
        elif s["etapa"] in (1, 2):
            if i - 2 >= s["ini"] and h[i - 2] < lo:
                s["fvg"] = (lo, h[i - 2], i)  # (borde superior, borde inferior, vela)
            if s["etapa"] == 1:
                if i > s["ini"] and ci > ush[i - 1]:
                    s.update(etapa=2, mss=ush[i - 1], tmss=t)
            else:
                f = s["fvg"]
                if f is not None and f[2] < i:
                    mid = (f[0] + f[1]) / 2.0
                    if lo <= mid and ci > f[1]:
                        s["etapa"] = 3
                        yield i, 1, dict(s, mid=mid)


def senales(ind, incluir_amarillo=True):
    n = len(ind["close"])
    return senales_eventos(n, _eventos(ind, 0, n))


def motivo(ind, i, side):
    s = evento_en(_eventos(ind, inicio_dia(ind["om"], i), i + 1), i, side)
    if s is None:
        return "sin evento"
    top, bot, _k = s["fvg"]
    if side == "long":
        txt = "barrida %s %s (min %s) a las %s y cierre dentro; MSS cierre>swing alto %s a las %s"
        fv = "FVG alcista %s-%s, medio %s; minimo %s<=medio; cierre %s>%s"
        fv = fv % (fmt(bot), fmt(top), fmt(s["mid"]), fmt(ind["low"][i]), fmt(ind["close"][i]),
                   fmt(bot))
    else:
        txt = "barrida %s %s (max %s) a las %s y cierre dentro; MSS cierre<swing bajo %s a las %s"
        fv = "FVG bajista %s-%s, medio %s; maximo %s>=medio; cierre %s<%s"
        fv = fv % (fmt(bot), fmt(top), fmt(s["mid"]), fmt(ind["high"][i]), fmt(ind["close"][i]),
                   fmt(top))
    txt = txt % (s["nivel"][1], fmt(s["nivel"][0]), fmt(s["ext"]), hora(s["t"]), fmt(s["mss"]),
                 hora(s["tmss"]))
    return "%s; %s (verde)" % (txt, fv)
