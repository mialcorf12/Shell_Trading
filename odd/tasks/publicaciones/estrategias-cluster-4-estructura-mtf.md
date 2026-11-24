# Feature: estrategias-cluster-4-estructura-mtf
Persona: jira/trading_agent_persona.md (NQ/MNQ futures, algorithmic trading in NinjaTrader 8, prop-firm risk management).
Target folder: publicaciones/estrategias/
Source ideas: publicaciones/ideas/

## Specs
- S1: "en estrategias quiero que busques construir Estrategias para trading basado en el contenido de ideas, reforzando buscando en web info adicional. recuerde actualizar las referencias"
- S2: "en todo momento quiero usar trading_agent_persona.md" -> risk math first, hypothesis before code, NQ/MNQ specs ($20/pt vs $2/pt), trailing drawdown and daily loss circuit breakers, measurable rules, hard stops, validation caveats.
- S3: Preserve and maintain `## Referencias` in each file in `publicaciones/estrategias/` (one item per line, bidirectional with publicaciones/ideas/).

## Tasks
- T1: Build publicaciones/estrategias/ESTRUCTURA_TENDENCIA_RANGO_BOS_CHOCH_NQ.md (Idea: ESTRUCTURA_TENDENCIA_RANGO_BOS_CHOCH_NQ_01.md; swing structure, trend/range, BOS and CHoCH on NQ). route: inline.
- T2: Build publicaciones/estrategias/ESTRUCTURA_LIQUIDEZ_CHOCH_FVG.md (Idea: ESTRUCTURA_LIQUIDEZ_CHOCH_FVG_01.md; 4-step structure + liquidity + CHoCH + FVG entry). route: inline.
- T3: Build publicaciones/estrategias/TOP_DOWN_SMC_OB_4PASOS.md (Idea: TOP_DOWN_SMC_OB_4PASOS_01.md; daily bias, 4H sweep, 1H OB, 15m MSS entry). route: inline.
- T4: Build publicaciones/estrategias/CRT_NASDAQ_OB.md (Idea: CRT_NASDAQ_OB_01.md; CRT top-down daily to 15m order block). route: inline.
- T5: Build publicaciones/estrategias/DESACOPLE_SMT_NQ_ES.md (Idea: DESACOPLE_SMT_NQ_ES_01.md; SMT divergence NQ vs ES at 5m highs/lows). route: inline.
- T6: Verify cluster 4 references and run test suite. route: inline.

## Log
- L1 (user verbatim): "quiero que revises los folder /estrategias/ y /ideas/. en estrategias quiero que busques construir Estrategias para trading basado en el contenido de ideas, reforzando buscando en web info adicional. recuerde actualizar las referencias"
- L2: user approved moving to Cluster 4 (Estructura & MTF).
