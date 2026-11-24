# Feature: estrategias-cluster-3-order-flow-volumen
Persona: jira/trading_agent_persona.md (NQ/MNQ futures, algorithmic trading in NinjaTrader 8, prop-firm risk management).
Target folder: publicaciones/estrategias/
Source ideas: publicaciones/ideas/

## Specs
- S1: "en estrategias quiero que busques construir Estrategias para trading basado en el contenido de ideas, reforzando buscando en web info adicional. recuerde actualizar las referencias"
- S2: "en todo momento quiero usar trading_agent_persona.md" -> risk math first, hypothesis before code, NQ/MNQ specs ($20/pt vs $2/pt), trailing drawdown and daily loss circuit breakers, measurable entry triggers, hard stops, walk-forward and cost-aware backtest caveats.
- S3: Preserve and maintain `## Referencias` in each file in `publicaciones/estrategias/` (one item per line, bidirectional with publicaciones/ideas/).

## Tasks
- T1: Build publicaciones/estrategias/VOLUMEN_RUPTURA.md (Idea: VOLUMEN_RUPTURA_01.md; breakout acceptance / rejection / initiative by volume change). route: inline. status: pending
- T2: Build publicaciones/estrategias/PERFIL_GORDO_DELGADO.md (Idea: PERFIL_GORDO_DELGADO_01.md; balance vs imbalance volume profile shapes). route: inline. status: pending
- T3: Build publicaciones/estrategias/LVN_DELTA_TPO_CONFLUENCIA.md (Idea: LVN_DELTA_TPO_CONFLUENCIA_01.md; LVN retest with abnormal delta and TPO single prints). route: inline. status: pending
- T4: Build publicaciones/estrategias/LVN_BARRIDO_STOPS_930.md (Idea: LVN_BARRIDO_STOPS_930_01.md; trendline + equal lows stops sweep into LVN after 9:30). route: inline. status: pending
- T5: Build publicaciones/estrategias/VWAP_REVERSION_AGOTAMIENTO.md (Idea: VWAP_REVERSION_AGOTAMIENTO_01.md; fade ±2-3 sigma VWAP bands on exhaustion). route: inline. status: pending
- T6: Build publicaciones/estrategias/DOBLE_VWAP_DIARIO_NY.md (Idea: DOBLE_VWAP_DIARIO_NY_01.md; daily VWAP (18:00 ET) + NY VWAP (09:30 ET) bias filter). route: inline. status: pending
- T7: Verify cluster 3 references and run test suite. route: inline. status: pending

## Log
- L1 (user verbatim): "quiero que revises los folder /estrategias/ y /ideas/. en estrategias quiero que busques construir Estrategias para trading basado en el contenido de ideas, reforzando buscando en web info adicional. recuerde actualizar las referencias"
- L2: user approved moving to Cluster 3 (Order Flow & Volumen).
- L3: web research: LVN retest and POC retest (ATAS, ChartFanatics, Lucas Prop Firm), VWAP 2-3 sigma fade and exhaustion (Trader Profesional, FutureShive, MyTradeEdge), Globex 18:00 ET anchor for NQ/ES daily VWAP (footprint-lab, VWAP Suite guides).
- L4: idea PERFIL_GORDO_DELGADO_01.md states "Estrategia sugerida: TENDENCIA_O_CHOP" (user edit). Kept existing strategy name PERFIL_GORDO_DELGADO; flag for user decision.
