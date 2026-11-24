# Feature: estrategias-cluster-2-fvg-liquidez
Persona: jira/trading_agent_persona.md (NQ/MNQ futures, algorithmic trading in NinjaTrader 8, prop-firm risk management).
Target folder: publicaciones/estrategias/
Source ideas: publicaciones/ideas/

## Specs
- S1: "en estrategias quiero que busques construir Estrategias para trading basado en el contenido de ideas, reforzando buscando en web info adicional. recuerde actualizar las referencias"
- S2: "en todo momento quiero usar trading_agent_persona.md" -> Risk math first, hypothesis before code, NQ/MNQ contract specs ($20/pt vs $2/pt), trailing drawdown and daily loss circuit breakers, explicit entry triggers, hard stops, walk-forward & backtest caveats.
- S3: Preserve and maintain `## Referencias` in each file in `publicaciones/estrategias/`.

## Tasks
- T1: Build publicaciones/estrategias/FVG.md (Idea: FVG_01.md, FVG vs Volume Profile high/low volume nodes). route: inline. commit: -
- T2: Build publicaciones/estrategias/FVG_TERCERA_VELA.md (Ideas: FVG_TERCERA_VELA_01, 02, 03; 3rd candle taxonomy: consolidation, breakaway gap, rejection). route: inline. commit: -
- T3: Build publicaciones/estrategias/FVG_IFVG_EQH_LIQUIDITY.md (Idea: FVG_IFVG_EQH_LIQUIDITY_01.md, 1H FVG tap + 5M iFVG shift targeting Equal Highs). route: inline. commit: -
- T4: Build publicaciones/estrategias/IFVG_LIQUIDEZ_1A1.md (Idea: IFVG_LIQUIDEZ_1A1_01.md, 15m liquidity sweep into FVG + 3m iFVG inversion 1:1 risk-reward). route: inline. commit: -
- T5: Build publicaciones/estrategias/CRT_ACUMULACION_APERTURA_IFVG.md (Idea: CRT_ACUMULACION_APERTURA_IFVG_01.md, Candle Range Theory bias + pre-open accumulation + 9:30 sweep into iFVG). route: inline. commit: -
- T6: Build publicaciones/estrategias/AMD_RANGO_FALSA_RUPTURA.md (Idea: AMD_RANGO_FALSA_RUPTURA_01.md, Accumulation-Manipulation-Distribution false breakout model on NQ). route: inline. commit: -
- T7: Verification of cluster 2 (suite test check, references validation). route: inline. commit: -

## Log
- L1 (user verbatim): "quiero que revises los folder /estrategias/ y /ideas/. en estrategias quiero que busques construir Estrategias para trading basado en el contenido de ideas, reforzando buscando en web info adicional. recuerde actualizar las referencias"
- L2: user approved moving to Cluster 2: FVG, Inversión & Liquidez (6 strategies).
