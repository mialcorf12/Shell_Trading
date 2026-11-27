"""Ayudas compartidas por los módulos de estrategia (puras, sin E/S).

* ``filtro_tiers``: filtro verde/amarillo del indicador sobre ADX y VolRel.
  verde = ADX >= 25 y VolRel >= 1.5; amarillo = ADX >= 20 o VolRel >= 0.8
  (solo si ``incluir_amarillo``). Devuelve 1 verde, 2 amarillo, 0 nada.
* ``senales_tier``: señales de UN nivel a partir de la condición base. Verde:
  buy = buyG. Amarillo: buy = buyY y no buyG (como en el gráfico, el amarillo
  solo se ve si la vela no es verde). Igual para sell.
* ``motivo_filtro``: texto del filtro con los valores reales de la vela.
* ``fmt``: número con hasta 2 decimales, sin ceros sobrantes.
"""

VERDE = 1
AMARILLO = 2
TIER_NOMBRE = {VERDE: "verde", AMARILLO: "amarillo"}

ADX_VERDE = 25
VOLREL_VERDE = 1.5
ADX_AMARILLO = 20
VOLREL_AMARILLO = 0.8

REGLA_FILTRO = "ADX>=25, VolRel>=1.5 (verde) o ADX>=20 o VolRel>=0.8 (amarillo)"
REGLA_VERDE = "ADX>=25, VolRel>=1.5 (verde)"
REGLA_AMARILLO = "ADX>=20 o VolRel>=0.8 (amarillo, sin verde)"
REGLA_NIVEL = {VERDE: REGLA_VERDE, AMARILLO: REGLA_AMARILLO}


def fmt(x, nd=2):
    s = "%.*f" % (nd, x)
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return "0" if s == "-0" else s


def filtro_tiers(ind, incluir_amarillo=True):
    adx, vr = ind["adx"], ind["volRel"]
    n = len(adx)
    out = bytearray(n)
    for i in range(n):
        a = adx[i]
        v = vr[i]
        if a >= ADX_VERDE and v >= VOLREL_VERDE:
            out[i] = VERDE
        elif incluir_amarillo and (a >= ADX_AMARILLO or v >= VOLREL_AMARILLO):
            out[i] = AMARILLO
    return out


def senales_tier(ind, largo, corto, nivel, incluir_amarillo=True):
    """``largo``/``corto``: condición base por vela (0/1, excluyentes). ``nivel``
    VERDE: buy = largo y verde. AMARILLO: buy = largo y amarillo y no verde
    (vacío si ``incluir_amarillo`` es falso). ``tier`` = ``nivel`` donde hay señal."""
    adx, vr = ind["adx"], ind["volRel"]
    n = len(adx)
    buy, sell, tier = bytearray(n), bytearray(n), bytearray(n)
    if nivel == AMARILLO and not incluir_amarillo:
        return buy, sell, tier
    for i in range(n):
        lg = largo[i]
        if not (lg or corto[i]):
            continue
        a = adx[i]
        v = vr[i]
        g = a >= ADX_VERDE and v >= VOLREL_VERDE
        if nivel == VERDE:
            ok = g
        else:
            ok = not g and (a >= ADX_AMARILLO or v >= VOLREL_AMARILLO)
        if not ok:
            continue
        if lg:
            buy[i] = 1
        else:
            sell[i] = 1
        tier[i] = nivel
    return buy, sell, tier


def motivo_filtro(ind, i):
    a = ind["adx"][i]
    v = ind["volRel"][i]
    if a >= ADX_VERDE and v >= VOLREL_VERDE:
        return "ADX %s>=25; VolRel %s>=1.5 (verde)" % (fmt(a), fmt(v))
    partes = []
    if a >= ADX_AMARILLO:
        partes.append("ADX %s>=20" % fmt(a))
    if v >= VOLREL_AMARILLO:
        partes.append("VolRel %s>=0.8" % fmt(v))
    if not partes:
        return "sin filtro (ADX %s, VolRel %s)" % (fmt(a), fmt(v))
    return " o ".join(partes) + " (amarillo)"


def sesgo(ind, i):
    t = ind["trend"][i]
    return "estructura alcista" if t == 1 else ("estructura bajista" if t == -1 else "estructura neutra")


# ---------- ayudas de tiempo para e10..e18 (``ind["om"]`` = minuto de APERTURA ET) ----------

def hhmm(h, m=0):
    """Minuto del día de ``h:m``."""
    return h * 60 + m


def hora(om_i):
    """Texto ``HH:MM`` (apertura) de un minuto absoluto."""
    m = om_i % 1440
    return "%02d:%02d" % (m // 60, m % 60)


def inicio_dia(om, i):
    """Primer índice de la misma fecha (de apertura) que la vela ``i``."""
    d = om[i] // 1440
    j = i
    while j > 0 and om[j - 1] // 1440 == d:
        j -= 1
    return j


def senales_eventos(n, eventos):
    """``eventos``: iterable de (i, lado, info) con lado 1 largo / -1 corto.
    Devuelve (buy, sell, tier) con tier verde en cada señal (largo gana si ambos)."""
    buy, sell, tier = bytearray(n), bytearray(n), bytearray(n)
    for i, lado, _info in eventos:
        if lado == 1:
            buy[i] = 1
            sell[i] = 0
        elif not buy[i]:
            sell[i] = 1
        tier[i] = VERDE
    return buy, sell, tier


def evento_en(eventos, i, side):
    """Info del evento de la vela ``i`` y lado ``side`` (``"long"``/``"short"``) o None."""
    lado = 1 if side == "long" else -1
    for j, l, info in eventos:
        if j == i and l == lado:
            return info
    return None
