"""Métricas por corrida a partir de la lista de operaciones cerradas.

* payoff = media de ganadoras / |media de perdedoras|; vacío si no hay
  ganadoras o no hay perdedoras.
* profit_factor = suma ganadoras / |suma perdedoras|; vacío si no hay perdedoras.
* Una operación con PnL == 0 no es ganadora ni perdedora (cuenta en trades).
* max_dd_usd: caída máxima pico-valle de la curva de equity cerrada (empieza en 0).
* sharpe / sortino: aproximación de TradingView. PnL diario = suma del PnL de
  las operaciones agrupado por la fecha ET de APERTURA de la vela de salida
  (solo días con operaciones). Desviación poblacional; downside =
  sqrt(media(min(x, 0)^2)) sobre todos esos días. Se anualiza con sqrt(252).
  Vacío si hay menos de 2 días o la desviación es 0.
* top3_pct = suma de las 3 mayores ganadoras / net * 100; vacío si net <= 0.
* Sin operaciones: todas las métricas vacías.
"""

import math

METRIC_KEYS = ("trades", "win_rate_pct", "payoff", "profit_factor", "expectancy_usd",
               "net_profit_usd", "max_dd_usd", "max_consec_losses", "sharpe", "sortino",
               "top3_pct")


def compute_metrics(pnls, exit_days=None):
    """``pnls``: PnL USD por operación en orden. ``exit_days``: clave de día por operación."""
    out = {k: None for k in METRIC_KEYS}
    n = len(pnls)
    if n == 0:
        return out
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]
    net = sum(pnls)
    out["trades"] = n
    out["win_rate_pct"] = len(wins) / n * 100.0
    if wins and losses:
        out["payoff"] = (sum(wins) / len(wins)) / abs(sum(losses) / len(losses))
    if losses:
        out["profit_factor"] = sum(wins) / abs(sum(losses))
    out["expectancy_usd"] = net / n
    out["net_profit_usd"] = net
    eq = peak = dd = 0.0
    run = best_run = 0
    for p in pnls:
        eq += p
        if eq > peak:
            peak = eq
        if peak - eq > dd:
            dd = peak - eq
        if p < 0:
            run += 1
            if run > best_run:
                best_run = run
        else:
            run = 0
    out["max_dd_usd"] = dd
    out["max_consec_losses"] = best_run
    if exit_days is not None:
        daily = {}
        for p, d in zip(pnls, exit_days):
            daily[d] = daily.get(d, 0.0) + p
        xs = list(daily.values())
        if len(xs) >= 2:
            m = sum(xs) / len(xs)
            sd = math.sqrt(sum((x - m) ** 2 for x in xs) / len(xs))
            dsd = math.sqrt(sum(min(x, 0.0) ** 2 for x in xs) / len(xs))
            if sd > 0:
                out["sharpe"] = m / sd * math.sqrt(252)
            if dsd > 0:
                out["sortino"] = m / dsd * math.sqrt(252)
    if net > 0:
        out["top3_pct"] = sum(sorted(wins, reverse=True)[:3]) / net * 100.0
    return out


_FMT = {
    "trades": "%d",
    "max_consec_losses": "%d",
    "win_rate_pct": "%.1f",
    "top3_pct": "%.1f",
}


def format_metrics(m):
    """Métricas -> strings para el CSV (vacío si None)."""
    out = {}
    for k in METRIC_KEYS:
        v = m.get(k)
        out[k] = "" if v is None else (_FMT.get(k, "%.2f") % v)
    return out
