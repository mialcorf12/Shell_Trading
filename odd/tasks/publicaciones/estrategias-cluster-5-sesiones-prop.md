# Feature: estrategias-cluster-5-sesiones-prop
Persona: jira/trading_agent_persona.md (NQ/MNQ, NinjaTrader 8, prop-firm risk).
Target folder: publicaciones/estrategias/ (setups) y publicaciones/contexto/ (material no operable).

## Specs
- S1: "de las faltantes cuales pueden ser categorizadas como estrategias?" -> respuesta: PROP_PHASED_RISK_MOMENTUM_3D (reglas completas) y SESIONES_7H_C2_C3 (candidata con definición del usuario).
- S2: "1. si. 2. ya inclui la definicion en el archivo. 3. si" -> construir ambas como estrategias; mover el resto a publicaciones/contexto/.
- S3: Preservar referencias bidireccionales (publicaciones/estrategias/ <-> publicaciones/ideas/, publicaciones/contexto/ <-> publicaciones/ideas/).
- S4: Validación honesta: PROP_PHASED es in-sample según el propio video; SESIONES usa una interpretación de C1/C2/C3 que debe confirmarse.

## Tasks
- T1: publicaciones/estrategias/PROP_PHASED_RISK_MOMENTUM_3D.md (regla de entrada 9:30 por cierre vs cierre de hace 3 días; stop 50 pts; riesgo y objetivo por fase; conversión a contratos NQ/MNQ). route: inline.
- T2: publicaciones/estrategias/SESIONES_7H_C2_C3.md (sesiones de 7 h en NY; roles C1/C2/C3 operacionalizados; caso 1, 2 y 3). route: inline.
- T3: Mover a publicaciones/contexto/: CONFIRMACION_5_INDICADORES, INDICADORES_TOP_7, VWAP_VS_EMA_BOLLINGER, ORDER_FLOW_TOOLKIT, PLANTILLA_TRADINGVIEW_APERTURA_NY, PROP_CHALLENGE_RISK_MATH. Actualizar la referencia en publicaciones/ideas/ de "Estrategia:" a "Contexto:". route: inline.
- T4: Verificar referencias y tests. route: inline.

## Log
- L1 (user): "de las faltantes cuales pueden ser categorizadas como estrategias?"; "1. si. 2. ya inclui la definicion en el archivo. 3. si".
- L2: la definición de C2/C3 del usuario en publicaciones/ideas/SESIONES_7H_C2_C3_01.md es: "C1, C2 y C3 indican el cierre de la sesión" (y casos 1-3). No define roles explícitos; se operacionaliza en la estrategia y se marca pendiente de confirmación.
