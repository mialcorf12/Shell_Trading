"""Motor de backtest en Python puro (solo stdlib) para las estrategias "deberia".

Replica la lógica de las estrategias deberia (y desde S13 las de ``00_Nuevas.md``; los Pine originales se eliminaron; ver odd/tasks/backtest/backtesting.md, L16)
sobre el CSV histórico de 1 minuto (por defecto MNQ, ``data/mnq_1m.csv``) y
escribe las estadísticas en ``indicadores/backtest/stats/resultados.csv``.

Convenciones (ver también los docstrings de cada módulo):

* Las marcas de tiempo del CSV son el CIERRE de la vela (ET). La apertura es
  ``marca - 1 minuto`` y se usa para el ancla del VWAP NY, la sesión y el log.
* Ejecución tipo ``process_orders_on_close=true``: la entrada se llena al cierre
  de la vela de la señal (+/- 1 tick de slippage adverso); las salidas TP/SL se
  revisan a partir de la vela siguiente. Si TP y SL caen en la misma vela, se
  asume SL primero (conservador).
* Instrumento (``INSTRUMENTS``): valor del punto, tick y comisión salen del
  símbolo elegido (``--simbolo``, por defecto MNQ). TP/SL en puntos =
  ``usd / (point_value x N)``; slippage = 1 tick; PnL = puntos x point_value x N.
  - MNQ: 2 USD/punto, tick 0.25.
  - NQ: 20 USD/punto, tick 0.25 (solo referencia; no hay datos NQ propios).
* SUPUESTO a confirmar por el usuario: comisión 2 USD por contrato y lado
  (4 USD por contrato por operación completa) para MNQ y NQ.
* Contratos N (1 a 4): una operación = N contratos, una posición a la vez. TP/SL
  son USD TOTALES de la operación (todos los contratos juntos): la distancia en
  puntos se divide entre N (MNQ, SL 600: N=1 -> 300 puntos, N=4 -> 75 puntos).
  PnL bruto en TP = tp_usd; en SL = -sl_usd antes de costos. La comisión
  (4 USD x N por operación) y el slippage (1 tick por orden, 1 tick x
  point_value x N en USD) escalan con N.

* Estrategias: un módulo por estrategia en ``engine/estrategias/eNN_<nombre>.py``
  (ID estable = NN). Ver ``engine.estrategias`` para la interfaz.
  Son 18: deberia_1..deberia_4 en verde (``e01``, ``e03``, ``e05``, ``e07``) y
  amarilla (``e02``, ``e04``, ``e06``, ``e08``), ``e09_deberia_5_verde`` y las
  ideas de ``00_Nuevas.md`` ``e10_orb`` .. ``e18_power_hour`` (solo verde; ver S13).
* ``notas`` por corrida: ``#eNN_<NOMBRE>: <REGLA>; verdes V, amarillas A;
  ventana N anos (inicio..fin); <estándar>``
  (V/A = operaciones de esa corrida por nivel de la vela de entrada; una estrategia
  verde tiene A = 0 y una amarilla V = 0).
* Ventana (``anos`` = 6, 3 o 1): fin = fecha de apertura de la última vela;
  inicio = esa fecha menos N años calendario (29-feb -> 28-feb). ``anos = 6`` es
  la historia completa (inicio = primera vela). Solo se opera si la vela de
  ENTRADA abre en o después del inicio; los indicadores se calculan sobre toda
  la historia (llegan calientes al inicio de la ventana).

Uso: ``python3 -m engine [--simbolo MNQ|NQ] [--estrategias 1,3]`` desde
``indicadores/backtest/``.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Instrument:
    simbolo: str
    point_value: float  # USD por punto
    tick: float  # syminfo.mintick
    commission_side: float  # USD por contrato y lado (supuesto)

    @property
    def commission_rt(self):
        """USD por contrato por operación completa (entrada + salida)."""
        return 2.0 * self.commission_side


INSTRUMENTS = {
    "MNQ": Instrument("MNQ", 2.0, 0.25, 2.0),
    "NQ": Instrument("NQ", 20.0, 0.25, 2.0),  # solo referencia
}
DEFAULT_SIMBOLO = "MNQ"

from .estrategias import ESTRATEGIAS  # noqa: E402  (registro ordenado por ID)

STRATEGIES = tuple(m.NOMBRE for m in ESTRATEGIAS)


@dataclass(frozen=True)
class ConjuntoConfigs:
    """Conjunto de configuraciones TP/SL (USD totales). ``clave``: valor de ``--configs``;
    ``nombre``: texto para el usuario y ``notas``."""
    clave: str
    nombre: str
    configs: tuple


CONFIGS_BASE = ((100, 600), (200, 600), (300, 600), (600, 600), (1000, 2000), (1500, 2000))
CONFIGS_1A1 = ((100, 100), (200, 200), (300, 300))  # relacion 1:1 (TP = SL)
CONJUNTO_BASE = ConjuntoConfigs("base", "base", CONFIGS_BASE)
CONJUNTO_1A1 = ConjuntoConfigs("1a1", "1:1", CONFIGS_1A1)
CONJUNTOS = (CONJUNTO_BASE, CONJUNTO_1A1)
CONJUNTO_DEFAULT = "base"
CONFIGS = CONFIGS_BASE  # conjunto por defecto (sin cambios)
CONTRACTS = (1, 2, 3, 4)
ANOS = (6, 3, 1)
ANOS_COMPLETO = 6  # historia completa: inicio = primera vela


def restar_anos(d, anos):
    """``d`` menos ``anos`` años calendario; el 29 de febrero pasa a 28 si el año no es bisiesto."""
    try:
        return d.replace(year=d.year - anos)
    except ValueError:
        return d.replace(year=d.year - anos, day=28)


def window_start(primera, ultima, anos):
    """Fecha de inicio de la ventana. ``anos == 6``: ``primera`` (historia completa)."""
    if anos == ANOS_COMPLETO:
        return primera
    return restar_anos(ultima, anos)


def ventana_texto(anos, inicio, fin):
    return "ventana %d anos (%s..%s)" % (anos, inicio.isoformat(), fin.isoformat())

# Filas NQ calculadas antes de la tabla de instrumentos: datos MNQ con valor de punto NQ.
INVALIDO_PREFIX = "INVALIDO: datos MNQ procesados con valor de punto NQ; "


def _fmt_num(x):
    return "%d" % x if float(x).is_integer() else "%g" % x


def notas_base(simbolo=DEFAULT_SIMBOLO):
    """Texto estándar de ``notas`` para un instrumento."""
    ins = INSTRUMENTS[simbolo]
    return ("motor python; %s %s USD/punto; fills en cierre; SL prioridad si ambos; "
            "comision %s/lado (supuesto); slippage 1 tick"
            % (ins.simbolo, _fmt_num(ins.point_value), _fmt_num(ins.commission_side)))


NOTAS = notas_base(DEFAULT_SIMBOLO)


def notas_for(contratos, simbolo=DEFAULT_SIMBOLO):
    """Texto de ``notas``: el estándar; con N > 1 aclara que TP/SL son USD totales."""
    base = notas_base(simbolo)
    if contratos <= 1:
        return base
    return ("%d contratos; TP/SL en USD totales de la operacion; "
            "N contratos dividen la distancia en puntos; %s" % (contratos, base))


def notas_estrategia(nombre, regla, verdes, amarillas, contratos, simbolo=DEFAULT_SIMBOLO,
                     con_trades=True, ventana=None, conjunto=None):
    """``#<nombre>: <regla>; verdes V, amarillas A; [config 1:1 (TP = SL); ][<ventana>; ]
    [sin trades; ]<notas_for>`` en una línea. ``ventana``: texto de ``ventana_texto``
    (opcional). ``conjunto``: un ``ConjuntoConfigs``; solo el 1:1 agrega texto (el base
    deja ``notas`` igual que antes)."""
    base = notas_for(contratos, simbolo)
    if not con_trades:
        base = "sin trades; " + base
    if ventana:
        base = ventana + "; " + base
    if conjunto is not None and conjunto.clave == CONJUNTO_1A1.clave:
        base = "config 1:1 (TP = SL); " + base
    txt = "#%s: %s; verdes %d, amarillas %d; %s" % (nombre, regla, verdes, amarillas, base)
    return " ".join(txt.split("\r\n")).replace("\r", " ").replace("\n", " ")
