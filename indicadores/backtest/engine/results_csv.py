"""Actualización en sitio de ``stats/resultados.csv`` y del JSON de operaciones.

Se emparejan filas por (simbolo, estrategia, tp_usd, sl_usd, contratos, anos)
comparando números; ``contratos`` vacío o ausente vale 1 y ``anos`` vacío o
ausente vale 6 (historia completa). ``simbolo`` es
obligatorio en cada actualización y se compara como texto exacto.

Filas NQ heredadas (calculadas antes de la tabla de instrumentos, con valor de
punto NQ sobre datos MNQ): se conservan y en cada escritura se les antepone
``engine.INVALIDO_PREFIX`` a ``notas`` (una sola vez). Se reconocen por
``simbolo == "NQ"`` y ``notas`` sin "USD/punto" (las notas nuevas lo incluyen);
no se recalculan. Un CSV viejo sin la columna
``contratos`` se migra: se inserta después de ``periodo`` con 1 en cada fila.
Un CSV sin la columna ``anos`` se migra igual: se inserta después de ``periodo``
con 6 en cada fila (esas filas son la corrida sobre la historia completa); los
demás valores no cambian.
Se conserva el orden de filas (las nuevas van al final), las filas no tocadas y
el fin de línea original. Escritura atómica: archivo temporal en la misma carpeta y
``os.replace``.
"""

import csv
import io
import json
import os
import tempfile

from . import INVALIDO_PREFIX

HEADER = ["estrategia", "simbolo", "timeframe", "periodo", "anos", "contratos", "tp_usd", "sl_usd",
          "trades",
          "win_rate_pct", "payoff", "profit_factor", "expectancy_usd", "net_profit_usd",
          "max_dd_usd", "max_consec_losses", "sharpe", "sortino", "top3_pct", "notas"]


def _num(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def _atomic_write_text(path, text):
    folder = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(prefix=".tmp_", suffix=".part", dir=folder)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


KEY_COLS = ("simbolo", "estrategia", "tp_usd", "sl_usd", "contratos", "anos")
ANOS_DEFAULT = 6


def _contracts(v):
    n = _num(v)
    return 1 if n is None else int(n)


def _anos(v):
    n = _num(v)
    return ANOS_DEFAULT if n is None else int(n)


def _migrate_anos(header, body):
    """Inserta ``anos`` (=6, historia completa) después de ``periodo`` si falta."""
    if "anos" in header:
        return header, body
    pos = header.index("periodo") + 1 if "periodo" in header else len(header)
    header = header[:pos] + ["anos"] + header[pos:]
    out = []
    for row in body:
        row = list(row)
        if len(row) < pos:
            row.extend([""] * (pos - len(row)))
        out.append(row[:pos] + [str(ANOS_DEFAULT)] + row[pos:])
    return header, out


def _migrate_contratos(header, body):
    """Inserta ``contratos`` (=1) después de ``periodo`` si falta."""
    if "contratos" in header:
        return header, body
    pos = header.index("periodo") + 1 if "periodo" in header else len(header)
    header = header[:pos] + ["contratos"] + header[pos:]
    out = []
    for row in body:
        row = list(row)
        if len(row) < pos:
            row.extend([""] * (pos - len(row)))
        out.append(row[:pos] + ["1"] + row[pos:])
    return header, out


def is_legacy_nq(simbolo, notas):
    """Fila NQ calculada antes de la tabla de instrumentos (notas sin "USD/punto")."""
    return simbolo == "NQ" and "USD/punto" not in notas


def mark_legacy_invalid(header, body):
    """Antepone ``INVALIDO_PREFIX`` a ``notas`` de las filas NQ heredadas (idempotente)."""
    if "simbolo" not in header or "notas" not in header:
        return 0
    isy, ino = header.index("simbolo"), header.index("notas")
    count = 0
    for row in body:
        if len(row) <= isy:
            continue
        if len(row) <= ino:
            row.extend([""] * (ino + 1 - len(row)))
        notas = row[ino]
        if notas.startswith(INVALIDO_PREFIX) or not is_legacy_nq(row[isy], notas):
            continue
        row[ino] = INVALIDO_PREFIX + notas
        count += 1
    return count


def update_results(path, updates):
    """``updates``: dicts con simbolo, estrategia, tp_usd, sl_usd, contratos (1 si falta),
    anos (6 si falta) y columnas a fijar. También marca como INVALIDO las filas NQ heredadas (ver módulo)."""
    with open(path, "r", encoding="utf-8", newline="") as f:
        raw = f.read()
    eol = "\r\n" if "\r\n" in raw else "\n"
    rows = list(csv.reader(io.StringIO(raw)))
    if not rows:
        header, body = list(HEADER), []
    else:
        header, body = rows[0], rows[1:]
    for col in ("simbolo", "estrategia", "tp_usd", "sl_usd"):
        if col not in header:
            raise ValueError("columna faltante en %s: %s" % (path, col))
    header, body = _migrate_contratos(header, body)
    header, body = _migrate_anos(header, body)
    idx = {name: k for k, name in enumerate(header)}
    isy, ie, it, isl, ic, ia = (idx[c] for c in KEY_COLS)
    need = max(isy, ie, it, isl)
    mark_legacy_invalid(header, body)
    for up in updates:
        if not up.get("simbolo"):
            raise ValueError("actualizacion sin simbolo: %r" % (up,))
        n_up = _contracts(up.get("contratos"))
        a_up = _anos(up.get("anos"))
        key = (up["simbolo"], up["estrategia"], _num(up["tp_usd"]), _num(up["sl_usd"]), n_up, a_up)
        target = None
        for row in body:
            if len(row) <= need:
                continue
            if (row[isy], row[ie], _num(row[it]), _num(row[isl]),
                    _contracts(row[ic] if len(row) > ic else ""),
                    _anos(row[ia] if len(row) > ia else "")) == key:
                target = row
                break
        if target is None:
            target = [""] * len(header)
            target[isy] = up["simbolo"]
            target[ie] = up["estrategia"]
            target[it] = str(up["tp_usd"])
            target[isl] = str(up["sl_usd"])
            body.append(target)
        if len(target) < len(header):
            target.extend([""] * (len(header) - len(target)))
        target[ic] = str(n_up)
        target[ia] = str(a_up)
        for col, val in up.items():
            if col in KEY_COLS or col not in idx:
                continue
            target[idx[col]] = "" if val is None else str(val)
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator=eol)
    w.writerow(header)
    w.writerows(body)
    _atomic_write_text(path, buf.getvalue())


def _fmt_usd(x):
    return "%d" % x if float(x).is_integer() else "%g" % x


def trades_json_path(folder, simbolo, estrategia, tp, sl, contratos=1, anos=ANOS_DEFAULT):
    """``<folder>/<SIMBOLO>_<estrategia>_tp<tp>_sl<sl>_c<N>_a<anos>.json``."""
    return os.path.join(folder, "%s_%s_tp%s_sl%s_c%d_a%d.json"
                        % (simbolo, estrategia, _fmt_usd(tp), _fmt_usd(sl), int(contratos),
                           int(anos)))


def write_trades_json(folder, simbolo, estrategia, tp, sl, trade_dicts, contratos=1,
                      anos=ANOS_DEFAULT):
    os.makedirs(folder, exist_ok=True)
    path = trades_json_path(folder, simbolo, estrategia, tp, sl, contratos, anos)
    text = "[\n" + ",\n".join(json.dumps(t, separators=(",", ":")) for t in trade_dicts) + "\n]\n"
    _atomic_write_text(path, text)
    return path
