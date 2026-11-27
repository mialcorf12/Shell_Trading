"""Dashboard de solo lectura para las estadísticas de backtest de las estrategias deberia.

Lee `indicadores/backtest/stats/resultados.csv` (una fila por corrida) y muestra
la tabla con el veredicto del checklist (odd/tasks/indicadores/backtest/checklist.md).
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request

STATS_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CSV = STATS_DIR / "resultados.csv"
DEFAULT_PORT = 5002
# Símbolos que el dashboard no muestra (NQ fue retirado: los datos son MNQ).
HIDDEN_SYMBOLS = {"NQ"}


# Columnas enteras (se devuelven como int en la API).
INTEGER = ["contratos", "anos"]

NUMERIC = [
    "tp_usd", "sl_usd", "trades", "win_rate_pct", "payoff", "profit_factor",
    "expectancy_usd", "net_profit_usd", "max_dd_usd", "max_consec_losses",
    "sharpe", "sortino", "top3_pct",
]

# Umbrales explícitos de checklist.md. top3_pct <= 50 es un supuesto propio (ver backtesting.md, S9).
THRESHOLDS = {
    "trades": ("min", 100),
    "net_profit_usd": ("min_exclusive", 0),
    "profit_factor": ("min", 1.25),
    "expectancy_usd": ("min_exclusive", 0),
    "sharpe": ("min", 1.0),
    "top3_pct": ("max", 50),
}


def _to_number(raw: str | None):
    if raw is None or raw.strip() == "":
        return None
    try:
        return float(raw)
    except ValueError:
        return None


def _to_int(raw: str | None):
    value = _to_number(raw)
    return None if value is None or not value.is_integer() else int(value)


def check_row(row: dict) -> dict:
    """Devuelve el resultado de cada umbral: True (cumple), False (no cumple) o None (sin dato)."""
    out = {}
    for key, (kind, limit) in THRESHOLDS.items():
        value = row.get(key)
        if value is None:
            out[key] = None
        elif kind == "min":
            out[key] = value >= limit
        elif kind == "min_exclusive":
            out[key] = value > limit
        else:  # max
            out[key] = value <= limit
    return out


def verdict(row: dict, checks: dict) -> str:
    if row.get("trades") is None:
        return "pendiente"
    values = list(checks.values())
    if any(v is False for v in values):
        return "descarta"
    if any(v is None for v in values):
        return "incompleto"
    return "aprueba"


def load_rows(csv_path: Path) -> list[dict]:
    if not Path(csv_path).exists():
        return []
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for raw in csv.DictReader(f):
            row = dict(raw)
            row["simbolo"] = (raw.get("simbolo") or "").strip()
            if row["simbolo"] in HIDDEN_SYMBOLS:
                continue
            for key in NUMERIC:
                row[key] = _to_number(raw.get(key))
            for key in INTEGER:
                row[key] = _to_int(raw.get(key))
            checks = check_row(row)
            row["checks"] = checks
            row["veredicto"] = verdict(row, checks)
            rows.append(row)
    return rows


# Ventanas que debe tener un grupo para entrar al ranking de recomendadas.
REC_WINDOWS = (6, 3, 1)
# Campos de detalle por ventana en las recomendadas (sin MDD a pedido del usuario).
REC_DETAIL = [
    "win_rate_pct", "profit_factor", "expectancy_usd", "net_profit_usd",
    "max_consec_losses", "sharpe", "top3_pct", "veredicto",
]


def _num_key(value) -> str:
    """100.0 -> "100"; 16.5 -> "16.5"."""
    return str(int(value)) if float(value).is_integer() else str(value)


def _clean(value):
    """Floats enteros como int (600.0 -> 600) para que el JSON quede limpio."""
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def _min_or_none(values):
    present = [v for v in values if v is not None]
    return min(present) if len(present) == len(values) else None


def recommend(rows: list[dict], top_n: int = 5) -> dict:
    """Top `top_n` grupos (estrategia, sl_usd, contratos) por cada TP presente, en orden de TP ascendente.

    Solo entran grupos con las tres ventanas (6, 3 y 1 años). Orden: ventanas con veredicto
    aprueba (desc), ventanas con neto > 0 (desc), PF mínimo (desc), Sharpe mínimo (desc); un
    mínimo sin dato va al final. Empate final: estrategia, sl_usd, contratos ascendente.
    """
    groups: dict = {}
    for r in rows:
        if r.get("tp_usd") is None or r.get("anos") not in REC_WINDOWS:
            continue
        key = (r["tp_usd"], r["estrategia"], r["sl_usd"], r["contratos"])
        # Si hubiera filas repetidas para la misma ventana se conserva la primera.
        groups.setdefault(key, {}).setdefault(r["anos"], r)

    por_tp: dict = {}
    for (tp, estrategia, sl, contratos), win in groups.items():
        if any(a not in win for a in REC_WINDOWS):
            continue
        ws = [win[a] for a in REC_WINDOWS]
        cand = {
            "estrategia": estrategia,
            "tp_usd": _clean(tp),
            "sl_usd": _clean(sl),
            "contratos": contratos,
            "aprueba": sum(1 for w in ws if w["veredicto"] == "aprueba"),
            "neto_by_anos": {str(a): _clean(win[a]["net_profit_usd"]) for a in REC_WINDOWS},
            "detalle": {str(a): {k: _clean(win[a].get(k)) for k in REC_DETAIL} for a in REC_WINDOWS},
        }
        positivos = sum(1 for w in ws if (w["net_profit_usd"] or 0) > 0)
        pf_min = _min_or_none([w["profit_factor"] for w in ws])
        sh_min = _min_or_none([w["sharpe"] for w in ws])
        rank = (
            -cand["aprueba"], -positivos,
            pf_min is None, -(pf_min or 0),
            sh_min is None, -(sh_min or 0),
            estrategia, sl if sl is not None else float("inf"), contratos if contratos is not None else 0,
        )
        por_tp.setdefault(tp, []).append((rank, cand))

    return {
        _num_key(tp): [c for _, c in sorted(items, key=lambda x: x[0])][:top_n]
        for tp, items in sorted(por_tp.items())
    }


def create_app(csv_path: Path = DEFAULT_CSV) -> Flask:
    app = Flask(__name__)
    app.config["STATS_CSV"] = Path(csv_path)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.get("/api/results")
    def results():
        rows = load_rows(app.config["STATS_CSV"])
        contratos = request.args.get("contratos", type=int)
        if contratos is not None:
            rows = [r for r in rows if r["contratos"] == contratos]
        anos = request.args.get("anos", type=int)
        if anos is not None:
            rows = [r for r in rows if r["anos"] == anos]
        tp = request.args.get("tp_usd", type=float)
        if tp is not None:
            rows = [r for r in rows if r["tp_usd"] == tp]
        simbolo = (request.args.get("simbolo") or "").strip()
        if simbolo:
            rows = [r for r in rows if r["simbolo"] == simbolo]
        return jsonify({"rows": rows, "thresholds": THRESHOLDS})

    @app.get("/api/recommended")
    def recommended():
        # Sin ordenar claves: jsonify ordena por texto ("1000" antes de "200") y el TP va en orden numérico.
        body = json.dumps({"por_tp": recommend(load_rows(app.config["STATS_CSV"]))}, ensure_ascii=False)
        return Response(body, mimetype="application/json")

    return app


if __name__ == "__main__":
    import threading
    import webbrowser

    url = f"http://127.0.0.1:{DEFAULT_PORT}/"
    threading.Timer(1.0, lambda: webbrowser.open(url)).start()
    create_app().run(debug=True, port=DEFAULT_PORT)
