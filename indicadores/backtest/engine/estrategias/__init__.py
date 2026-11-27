"""Registro de estrategias: un módulo por estrategia, ``eNN_<nombre>.py``.

El prefijo numérico ``NN`` es el ID estable y debe coincidir con ``ID``. Para
agregar una estrategia basta con crear ``e10_<nombre>.py`` en esta carpeta con
la misma interfaz; no hay que tocar otro código.

Interfaz de cada módulo (puro, sin E/S):

* ``ID`` (int), ``NOMBRE`` (str, p. ej. ``"deberia_1_verde"``), ``DESCRIPCION`` (str).

Estrategias actuales (18): deberia_1..deberia_4 en dos módulos cada una, verde
(solo buyG) y amarilla (buyY y no buyG), y deberia_5_verde (sin amarillo):
``e01_deberia_1_verde`` .. ``e08_deberia_4_amarilla``, ``e09_deberia_5_verde``.
Ideas de ``00_Nuevas.md`` (solo verde): ``e10_orb``, ``e11_vwap_rebote``,
``e12_barrida_liquidez``, ``e13_pullback_ema``, ``e14_gap``,
``e15_premarket_ruptura``, ``e16_delta_divergencia``, ``e17_macd_momentum``,
``e18_power_hour``. La idea 9 (noticias macro) no se implementa: no hay
calendario económico en los datos.
* ``REGLA`` (str): texto de la regla con operadores y umbrales reales (notas).
* ``senales(ind, incluir_amarillo=True) -> (buy, sell, tier)``: ``bytearray``
  0/1 por vela; ``tier`` 1 verde, 2 amarillo, 0 nada. ``ind`` trae los arrays
  precalculados (rsi, adx, macdL, macdH, volRel, trend, vwapNY, close,
  macdCrossUp0, macdCrossDn0, y las claves perezosas de sesión/5m de
  ``engine.signals.Indicadores``); los módulos no recalculan indicadores.
* ``motivo(ind, i, side) -> str``: disparo de la vela ``i`` (``"long"`` o
  ``"short"``) con los valores reales.
"""

import importlib
import os
import re

ATRIBUTOS = ("ID", "NOMBRE", "DESCRIPCION", "REGLA", "senales", "motivo")
_PATRON = re.compile(r"^e(\d+)_\w+\.py$")


class EstrategiaInvalida(ValueError):
    """Un módulo de estrategia no cumple la interfaz."""


def validar(mod, num=None):
    nombre = getattr(mod, "__name__", repr(mod))
    faltan = [a for a in ATRIBUTOS if not hasattr(mod, a)]
    if faltan:
        raise EstrategiaInvalida("estrategia %s: falta(n) %s" % (nombre, ", ".join(faltan)))
    if not isinstance(mod.ID, int) or isinstance(mod.ID, bool):
        raise EstrategiaInvalida("estrategia %s: ID debe ser int" % nombre)
    if num is not None and mod.ID != num:
        raise EstrategiaInvalida("estrategia %s: ID %r no coincide con el prefijo e%02d"
                                 % (nombre, mod.ID, num))
    for a in ("NOMBRE", "DESCRIPCION", "REGLA"):
        v = getattr(mod, a)
        if not isinstance(v, str) or not v.strip():
            raise EstrategiaInvalida("estrategia %s: %s debe ser texto no vacio" % (nombre, a))
        if "\n" in v or "\r" in v:
            raise EstrategiaInvalida("estrategia %s: %s debe ser una sola linea" % (nombre, a))
    for a in ("senales", "motivo"):
        if not callable(getattr(mod, a)):
            raise EstrategiaInvalida("estrategia %s: %s debe ser una funcion" % (nombre, a))
    return mod


def cargar(paquete=__name__):
    """Importa y valida los módulos ``eNN_*.py`` de ``paquete``, ordenados por ID."""
    pkg = importlib.import_module(paquete)
    carpeta = os.path.dirname(os.path.abspath(pkg.__file__))
    encontrados = []
    for fn in os.listdir(carpeta):
        m = _PATRON.match(fn)
        if m:
            encontrados.append((int(m.group(1)), fn[:-3]))
    encontrados.sort()
    mods, ids, nombres = [], set(), set()
    for num, stem in encontrados:
        mod = validar(importlib.import_module("%s.%s" % (paquete, stem)), num)
        if mod.ID in ids:
            raise EstrategiaInvalida("ID repetido: %d (%s)" % (mod.ID, stem))
        if mod.NOMBRE in nombres:
            raise EstrategiaInvalida("NOMBRE repetido: %s (%s)" % (mod.NOMBRE, stem))
        ids.add(mod.ID)
        nombres.add(mod.NOMBRE)
        mods.append(mod)
    return mods


ESTRATEGIAS = cargar()
POR_ID = {m.ID: m for m in ESTRATEGIAS}
POR_NOMBRE = {m.NOMBRE: m for m in ESTRATEGIAS}
