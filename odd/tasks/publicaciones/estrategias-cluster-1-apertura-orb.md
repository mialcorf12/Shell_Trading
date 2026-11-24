# Feature: estrategias-cluster-1-apertura-orb
Persona: jira/trading_agent_persona.md (NQ/MNQ futures, algorithmic trading in NinjaTrader 8, prop-firm risk management).
Target folder: publicaciones/estrategias/
Source ideas: publicaciones/ideas/

## Specs
- S1: "en estrategias quiero que busques construir Estrategias para trading basado en el contenido de ideas, reforzando buscando en web info adicional. recuerde actualizar las referencias"
- S2: "en todo momento quiero usar trading_agent_persona.md" -> Risk math first, hypothesis before code, NQ/MNQ contract specs ($20/pt vs $2/pt), trailing drawdown and daily loss circuit breakers, explicit entry triggers, hard stops, walk-forward & backtest caveats.
- S3: Preserve and maintain `## Referencias` in each file in `publicaciones/estrategias/`.

## Tasks
- T1: Build publicaciones/estrategias/ORB_FALLO_VWAP.md (Idea: ORB_FALLO_VWAP_01.md, NY 9:30-9:45 ORB trap + NY VWAP reclaim). route: inline. status: completed.
- T2: Build publicaciones/estrategias/ORB_MULTI_SESSION.md (Idea: ORB_MULTI_SESSION_01.md, 15m ORB rules across overnight vs pre-market vs RTH). route: inline. status: completed.
- T3: Build publicaciones/estrategias/ORB_STOP_MEDIO_RANGO_1R.md (Idea: ORB_STOP_MEDIO_RANGO_1R_01.md, Mid-range stop 1R mechanical breakout on NQ/index). route: inline. status: completed.
- T4: Build publicaciones/estrategias/NY_OPEN_15M_RANGE_PDH_PDL.md (Idea: NY_OPEN_15M_RANGE_PDH_PDL_01.md, First 15m candle breakout targeting PDH/PDL). route: inline. status: completed.
- T5: Build publicaciones/estrategias/REVERSION_930_IFVG.md (Idea: REVERSION_930_IFVG_01.md, 9:30 open sweep of DOL into 1H FVG + 1m iFVG entry). route: inline. status: completed.
- T6: Build publicaciones/estrategias/RANGO_8AM_BARRIDO_IFVG.md (Idea: RANGO_8AM_BARRIDO_IFVG_01.md, 8:00 AM 1H candle sweep into key level + 1m iFVG/OB). route: inline. status: completed.
- T7: Verification of cluster 1 (suite test check, references validation). route: inline. status: completed.

## Log
- L1 (user verbatim): "quiero que revises los folder /estrategias/ y /ideas/. en estrategias quiero que busques construir Estrategias para trading basado en el contenido de ideas, reforzando buscando en web info adicional. recuerde actualizar las referencias"
- L2: user confirmed cluster approach, starting with Cluster 1: Apertura & ORB (6 strategies).
- L3: web research conducted for each of the 6 setups, incorporating institutional NQ/MNQ quantitative studies (MADDOG 16-year ES/NQ data, TradingStats 2,839 days London data, Loomi.Ai 3,884 NQ sessions for midpoint stops, and ICT Judas 9:30 & 8AM range models).
- L4: all 6 strategy files written under jira/trading_agent_persona.md guidelines (NQ/MNQ specifications, trailing drawdown budgeting, daily loss circuit breakers, explicit entry triggers, hard stops, profit targets, time stops and NinjaTrader 8 architecture).
- L5: verified bidirectional references across all 6 strategies and 6 ideas; 61/61 pytest suite tests passing.
