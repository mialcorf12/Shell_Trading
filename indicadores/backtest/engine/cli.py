"""CLI: ``python3 -m engine`` desde ``indicadores/backtest/``.

Por defecto corre 9 estrategias x 6 configuraciones x 4 valores de contratos
x 3 ventanas (``anos`` 6, 3 y 1: 648 corridas; 216 por ventana) del símbolo MNQ
sobre ``data/mnq_1m.csv`` y escribe ``stats/resultados.csv`` (filas por simbolo,
estrategia, tp, sl, contratos, anos) y
``stats/trades/<SIMBOLO>_<estrategia>_tp<tp>_sl<sl>_c<N>_a<anos>.json``.

* ``--anos 6,3,1``: ventanas en años (por defecto las tres). Fin = fecha de
  apertura de la última vela; inicio = fin menos N años calendario (6 = historia
  completa, inicio = primera vela). Solo se toman operaciones cuya vela de
  ENTRADA abre en o después del inicio; los indicadores se calculan sobre toda
  la historia (calientes al inicio). ``periodo`` = fecha de apertura de la
  primera..última operación de la ventana (sin operaciones: inicio..última vela).

* ``--simbolo MNQ|NQ``: instrumento (valor del punto, tick, comisión). Por
  defecto MNQ. El CSV por defecto es ``data/<simbolo en minúsculas>_1m.csv``;
  ``--data`` lo reemplaza. NQ queda solo como referencia (no hay datos NQ).

* ``--limit-bars N``: corrida corta; NO escribe salvo que se pase ``--write``.
* ``--no-write``: corrida en seco.
* ``--estrategias 1,3``: subconjunto por ID 1..9 (prefijo ``eNN`` del módulo en
  ``engine/estrategias/``). Por defecto todas.
* ``--strategies deberia_1_verde,deberia_5_verde``: subconjunto por nombre.
  Excluyente con ``--estrategias``.
* ``--contratos 1,2,3,4``: contratos por operación (1 a 4; por defecto los cuatro).
* ``--configs base|1a1|all``: conjunto de TP/SL (USD totales). ``base`` (por
  defecto): las 6 de siempre (100/600, 200/600, 300/600, 600/600, 1000/2000,
  1500/2000). ``1a1``: relación 1:1 (100/100, 200/200, 300/300). ``all``: ambos.
  Las filas 1:1 agregan ``config 1:1 (TP = SL); `` en ``notas``.

``notas`` por corrida: ``#eNN_<NOMBRE>: <REGLA>; verdes V, amarillas A;
ventana N anos (inicio..fin); <estándar>``
(en una estrategia verde A = 0; en una amarilla V = 0).
Cada operación del JSON lleva ``motivo`` (disparo con valores reales de la vela
de entrada) y ``tier`` (``verde`` en las estrategias verdes, ``amarillo`` en las amarillas).

Tras cada corrida se verifica que no haya operaciones solapadas (una posición a
la vez); si las hay, la corrida falla con ``OverlapError``. El resumen muestra
los solapes por corrida y el total (debe ser 0).
"""

import argparse
import os
from bisect import bisect_left
import sys
import time

from . import (ANOS, CONFIGS, CONJUNTO_DEFAULT, CONJUNTOS, CONTRACTS, DEFAULT_SIMBOLO,
               INSTRUMENTS, notas_estrategia, ventana_texto, window_start)
from .estrategias import ESTRATEGIAS, POR_ID, POR_NOMBRE
from .estrategias._comun import AMARILLO, TIER_NOMBRE
from .data import format_open, load_csv, open_date
from .metrics import compute_metrics, format_metrics
from .results_csv import update_results, write_trades_json
from .signals import compute_indicators, compute_signals, warmup_index
from .simulate import check_no_overlap, count_overlaps, entry_candidates, simulate

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def build_parser():
    p = argparse.ArgumentParser(prog="python3 -m engine",
                                description="Backtest de las estrategias deberia sobre MNQ/NQ 1m.")
    p.add_argument("--simbolo", choices=sorted(INSTRUMENTS), default=DEFAULT_SIMBOLO,
                   help="instrumento: valor del punto, tick y comision (por defecto MNQ)")
    p.add_argument("--data", default=None,
                   help="CSV de velas de 1 minuto (por defecto data/mnq_1m.csv con MNQ, "
                        "data/nq_1m.csv con NQ)")
    p.add_argument("--results", default=os.path.join(BASE, "stats", "resultados.csv"),
                   help="CSV de resultados a actualizar (por defecto stats/resultados.csv)")
    p.add_argument("--trades-dir", default=os.path.join(BASE, "stats", "trades"),
                   help="carpeta de los JSON de operaciones (por defecto stats/trades)")
    p.add_argument("--limit-bars", type=int, default=None,
                   help="usar solo las primeras N velas (no escribe salvo --write)")
    sel = p.add_mutually_exclusive_group()
    sel.add_argument("--estrategias", default=None,
                     help="IDs separados por comas, p. ej. 1,3 (por defecto las %d: %s; %d corridas "
                          "con 4 contratos por ventana, %d con las %d ventanas)"
                          % (len(ESTRATEGIAS), ",".join(str(m.ID) for m in ESTRATEGIAS),
                             len(ESTRATEGIAS) * len(CONFIGS) * len(CONTRACTS),
                             len(ESTRATEGIAS) * len(CONFIGS) * len(CONTRACTS) * len(ANOS), len(ANOS)))
    sel.add_argument("--strategies", default=None,
                     help="nombres separados por comas, p. ej. deberia_1_verde,deberia_1_amarilla "
                          "(por defecto todas: %s)" % ",".join(m.NOMBRE for m in ESTRATEGIAS))
    p.add_argument("--contratos", default=",".join(str(c) for c in CONTRACTS),
                   help="contratos por operación, separados por comas (1 a 4; por defecto 1,2,3,4)")
    p.add_argument("--anos", default=",".join(str(a) for a in ANOS),
                   help="ventanas en años hasta la última vela, separadas por comas (6, 3 o 1; "
                        "6 = historia completa; por defecto 6,3,1). Los indicadores usan toda "
                        "la historia")
    p.add_argument("--configs", choices=[c.clave for c in CONJUNTOS] + ["all"],
                   default=CONJUNTO_DEFAULT,
                   help="conjunto de TP/SL: base (por defecto, %s), 1a1 (relacion 1:1, %s) o all"
                        % (", ".join("%d/%d" % c for c in CONJUNTOS[0].configs),
                           ", ".join("%d/%d" % c for c in CONJUNTOS[1].configs)))
    g = p.add_mutually_exclusive_group()
    g.add_argument("--write", action="store_true", help="forzar escritura (con --limit-bars)")
    g.add_argument("--no-write", action="store_true", help="corrida en seco, no escribe nada")
    return p


def _trade_dict(bars, t, motivo, tier):
    return {
        "open_time": format_open(bars.om[t.entry_index]),
        "exit_time": format_open(bars.om[t.exit_index]),
        "side": "long" if t.side == 1 else "short",
        "entry": t.entry,
        "exit": t.exit,
        "pnl_usd": round(t.pnl_usd, 2),
        "reason": t.reason,
        "motivo": motivo,
        "tier": TIER_NOMBRE.get(tier, ""),
    }


def parse_estrategias(ids_text=None, names_text=None):
    """Módulos elegidos, ordenados por ID. Sin selección: todos."""
    chosen = set()
    if ids_text is not None:
        for part in ids_text.split(","):
            part = part.strip()
            if not part:
                continue
            if not part.isdigit() or int(part) not in POR_ID:
                raise SystemExit("estrategia desconocida: %s (IDs: %s)"
                                 % (part, ",".join(str(k) for k in sorted(POR_ID))))
            chosen.add(int(part))
    elif names_text is not None:
        for part in names_text.split(","):
            part = part.strip()
            if not part:
                continue
            if part not in POR_NOMBRE:
                raise SystemExit("estrategia desconocida: %s" % part)
            chosen.add(POR_NOMBRE[part].ID)
    else:
        return list(ESTRATEGIAS)
    if not chosen:
        raise SystemExit("estrategias vacio")
    return [m for m in ESTRATEGIAS if m.ID in chosen]


def parse_contracts(text):
    out = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if not part.isdigit() or int(part) not in CONTRACTS:
            raise SystemExit("contratos invalidos: %s (permitido: 1 a 4)" % part)
        if int(part) not in out:
            out.append(int(part))
    if not out:
        raise SystemExit("contratos vacio")
    return out


def parse_anos(text):
    out = []
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if not part.isdigit() or int(part) not in ANOS:
            raise SystemExit("anos invalidos: %s (permitido: %s)"
                             % (part, ",".join(str(a) for a in ANOS)))
        if int(part) not in out:
            out.append(int(part))
    if not out:
        raise SystemExit("anos vacio")
    return out


def parse_configs(clave):
    """Lista de (conjunto, tp, sl) para ``--configs`` (``base``, ``1a1`` o ``all``).
    Sin duplicados de (tp, sl); el orden es el del conjunto."""
    if clave == "all":
        elegidos = list(CONJUNTOS)
    else:
        elegidos = [c for c in CONJUNTOS if c.clave == clave]
        if not elegidos:
            raise SystemExit("configs desconocido: %s (permitido: %s, all)"
                             % (clave, ", ".join(c.clave for c in CONJUNTOS)))
    out, vistos = [], set()
    for conj in elegidos:
        for tp, sl in conj.configs:
            if (tp, sl) not in vistos:
                vistos.add((tp, sl))
                out.append((conj, tp, sl))
    return out


def window_index(bars, inicio):
    """Primera vela cuya apertura es >= ``inicio`` (fecha, 00:00 ET)."""
    return bisect_left(bars.om, inicio.toordinal() * 1440)


def default_data_path(simbolo):
    return os.path.join(BASE, "data", "%s_1m.csv" % simbolo.lower())


def run(args, out=None):
    out = out or sys.stdout
    t0 = time.time()
    simbolo = args.simbolo
    ins = INSTRUMENTS[simbolo]
    data_path = args.data or default_data_path(simbolo)
    print("instrumento=%s point_value=%g USD/punto tick=%g comision=%g/lado (supuesto) datos=%s"
          % (ins.simbolo, ins.point_value, ins.tick, ins.commission_side, data_path), file=out)
    mods = parse_estrategias(args.estrategias, args.strategies)
    contracts = parse_contracts(args.contratos)
    anos_list = parse_anos(args.anos)
    configs = parse_configs(getattr(args, "configs", CONJUNTO_DEFAULT))
    write = not args.no_write and (args.limit_bars is None or args.write)

    bars = load_csv(data_path, args.limit_bars)
    n = len(bars)
    if n == 0:
        raise SystemExit("sin datos en %s" % data_path)
    t_load = time.time()
    inds = compute_indicators(bars)
    warm = warmup_index(inds)
    sigs = compute_signals(bars, inds, estrategias=mods)
    t_ind = time.time()
    primera, ultima = open_date(bars.om[0]), open_date(bars.om[-1])
    print("velas=%d datos=%s..%s warmup=%d carga=%.1fs indicadores=%.1fs"
          % (n, primera.isoformat(), ultima.isoformat(), warm, t_load - t0, t_ind - t_load),
          file=out)
    ventanas = []
    for anos in anos_list:
        inicio = window_start(primera, ultima, anos)
        wi = window_index(bars, inicio)
        ventanas.append((anos, inicio, wi))
        print("anos=%d ventana=%s..%s vela_inicial=%d (indicadores sobre toda la historia)"
              % (anos, inicio.isoformat(), ultima.isoformat(), wi), file=out)
    print("%4s %-18s %3s %6s %6s %7s %12s %8s %7s" % ("anos", "estrategia", "c", "tp", "sl",
                                                       "trades", "net_usd", "PF", "solapes"),
          file=out)

    updates = []
    total_overlaps = 0
    runs = 0
    motivos_por = {m.NOMBRE: {} for m in mods}  # (indice, lado) -> texto; solo velas de entrada
    for anos, inicio, wi in ventanas:
        ventana = ventana_texto(anos, inicio, ultima)
        for mod in mods:
            name = mod.NOMBRE
            buy, sell, tier = sigs[name]
            start = max(warm, wi)
            cands = entry_candidates(buy, sell, start, edge=True)
            motivos = motivos_por[name]
            for qty in contracts:
                for conj, tp, sl in configs:
                    trades = simulate(bars, buy, sell, tp, sl, start=start, candidates=cands, qty=qty,
                                      instrument=ins)
                    overlaps = count_overlaps(trades)
                    total_overlaps += overlaps
                    runs += 1
                    check_no_overlap(trades)
                    pnls = [t.pnl_usd for t in trades]
                    days = [bars.om[t.exit_index] // 1440 for t in trades]
                    m = compute_metrics(pnls, days)
                    f = format_metrics(m)
                    amarillas = sum(1 for t in trades if tier[t.entry_index] == AMARILLO)
                    notas = notas_estrategia("e%02d_%s" % (mod.ID, name), mod.REGLA, len(trades) - amarillas, amarillas,
                                             qty, simbolo, con_trades=bool(trades), ventana=ventana,
                                             conjunto=conj)
                    if trades:
                        periodo = "%s..%s" % (open_date(bars.om[trades[0].entry_index]).isoformat(),
                                              open_date(bars.om[trades[-1].entry_index]).isoformat())
                    else:
                        periodo = "%s..%s" % (inicio.isoformat(), ultima.isoformat())
                    row = {"estrategia": name, "tp_usd": tp, "sl_usd": sl, "contratos": qty,
                           "anos": anos, "simbolo": simbolo, "timeframe": "1m", "periodo": periodo,
                           "notas": notas}
                    row.update(f)
                    updates.append(row)
                    print("%4d %-18s %3d %6d %6d %7d %12s %8s %7d"
                          % (anos, name, qty, tp, sl, len(trades), f["net_profit_usd"] or "-",
                             f["profit_factor"] or "-", overlaps), file=out)
                    if write:
                        dicts = []
                        for t in trades:
                            key = (t.entry_index, t.side)
                            txt = motivos.get(key)
                            if txt is None:
                                txt = mod.motivo(inds, t.entry_index, "long" if t.side == 1 else "short")
                                motivos[key] = txt
                            dicts.append(_trade_dict(bars, t, txt, tier[t.entry_index]))
                        write_trades_json(args.trades_dir, simbolo, name, tp, sl, dicts, qty, anos)
    print("corridas: %d; solapes totales: %d" % (runs, total_overlaps), file=out)
    if write:
        update_results(args.results, updates)
        print("escrito: %s" % args.results, file=out)
    else:
        print("corrida en seco: no se escribio nada", file=out)
    print("tiempo total: %.1fs" % (time.time() - t0), file=out)
    return updates


def main(argv=None):
    args = build_parser().parse_args(argv)
    run(args)
    return 0
