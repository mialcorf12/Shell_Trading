"""Simulación de una estrategia con TP/SL en USD totales de la operación (qty N, sin pyramiding).

Orden por vela i (como Pine con ``process_orders_on_close=true``):

1. Si hay posición abierta de una vela anterior, se revisa la salida con el
   high/low de la vela i. Largo: si ``low <= SL`` sale en ``SL - 1 tick``;
   si no, si ``high >= TP`` sale en ``TP``. Si ambos caen en la vela, gana SL.
   Corto en espejo. Supuesto: sin relleno por gap (se usa el precio del nivel,
   no la apertura de la vela).
2. Señales de la vela i al cierre (ya precalculadas).
3. Entrada si hay flanco (``soloPrimeraVela``) y la cuenta está plana: largo
   en ``close + 1 tick``, corto en ``close - 1 tick``. La salida se revisa
   desde la vela i+1. Tras una salida en la vela j, se puede entrar en j.

Una posición todavía abierta al final de los datos no cuenta como operación.

Contratos ``qty``: TP/SL son USD TOTALES de la operación (todos los contratos),
así que la distancia en puntos se divide entre qty: ``points_for`` =
usd / (point_value x qty) (MNQ, SL 600: qty 1 -> 300 puntos, qty 4 -> 75).
Sin redondeo a tick: el PnL bruto en TP es exactamente tp_usd. Slippage = 1 tick
del instrumento por orden (precio de fill). Todo sale del instrumento
(``engine.INSTRUMENTS``): PnL = diferencia de precio x point_value x qty -
comision_rt x qty (MNQ: x 2 y 4 USD por contrato; NQ: x 20 y 4 USD por contrato).

Una posición a la vez: tras cada corrida ``check_no_overlap`` verifica que la
salida de la operación k sea <= la entrada de la k+1 (la vela de salida puede
alojar la siguiente entrada a su cierre) y lanza ``OverlapError`` si no.

Por eficiencia se recorren solo las velas candidatas a entrada (flanco ya
calculado) y, con posición abierta, las velas hasta la salida.
"""

from dataclasses import dataclass

from . import DEFAULT_SIMBOLO, INSTRUMENTS


@dataclass
class Trade:
    entry_index: int
    exit_index: int
    side: int  # 1 largo, -1 corto
    entry: float
    exit: float
    pnl_usd: float
    reason: str  # "TP" | "SL"


def entry_candidates(buy, sell, start=0, edge=True):
    """Lista ordenada de (indice, lado) de velas que cumplen la condición de entrada."""
    n = len(buy)
    out = []
    for i in range(max(start, 0), n):
        bi = buy[i]
        si = sell[i]
        if not (bi or si):
            continue
        if bi and (not edge or i == 0 or not buy[i - 1]):
            out.append((i, 1))
        elif si and (not edge or i == 0 or not sell[i - 1]):
            out.append((i, -1))
    return out


def points_for(usd, instrument, qty=1):
    """Distancia en puntos de un TP/SL en USD TOTALES de la operación con ``qty`` contratos."""
    return usd / (instrument.point_value * qty)


class OverlapError(RuntimeError):
    """Dos operaciones abiertas a la vez."""


def count_overlaps(trades):
    """Pares consecutivos donde la operación k+1 entra antes de que salga la k."""
    return sum(1 for a, b in zip(trades, trades[1:]) if b.entry_index < a.exit_index)


def check_no_overlap(trades):
    n = count_overlaps(trades)
    if n:
        raise OverlapError("%d operaciones solapadas" % n)
    return 0


def simulate(bars, buy, sell, tp_usd, sl_usd, start=0, edge=True,
             candidates=None, qty=1, instrument=None):
    """``instrument``: ``engine.Instrument`` (por defecto el de ``DEFAULT_SIMBOLO``)."""
    ins = instrument if instrument is not None else INSTRUMENTS[DEFAULT_SIMBOLO]
    point_value, tick, commission_rt = ins.point_value, ins.tick, ins.commission_rt
    high, low, close = bars.high, bars.low, bars.close
    n = len(close)
    tp_pts = points_for(tp_usd, ins, qty)
    sl_pts = points_for(sl_usd, ins, qty)
    if candidates is None:
        candidates = entry_candidates(buy, sell, start, edge)
    trades = []
    free_from = 0  # primera vela en la que se puede entrar (cuenta plana)
    for i, side in candidates:
        if i < free_from:
            continue
        if side == 1:
            entry = close[i] + tick
            sl_px = entry - sl_pts
            tp_px = entry + tp_pts
            j = i + 1
            while j < n:
                if low[j] <= sl_px:
                    ex, reason = sl_px - tick, "SL"
                    break
                if high[j] >= tp_px:
                    ex, reason = tp_px, "TP"
                    break
                j += 1
            else:
                return trades
            pnl = (ex - entry) * point_value * qty - commission_rt * qty
        else:
            entry = close[i] - tick
            sl_px = entry + sl_pts
            tp_px = entry - tp_pts
            j = i + 1
            while j < n:
                if high[j] >= sl_px:
                    ex, reason = sl_px + tick, "SL"
                    break
                if low[j] <= tp_px:
                    ex, reason = tp_px, "TP"
                    break
                j += 1
            else:
                return trades
            pnl = (entry - ex) * point_value * qty - commission_rt * qty
        trades.append(Trade(i, j, side, entry, ex, pnl, reason))
        free_from = j  # step 1 deja la cuenta plana antes de step 3 en la vela j
    return trades
