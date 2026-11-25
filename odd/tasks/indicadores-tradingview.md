# Indicadores TradingView — Pine Script v6
Rama: Tradingview
Objetivo: Implementar indicador único en Pine Script v6 (overlay=true) integrando indicadores de orden, estructura, contexto, tabla de lecturas en tiempo real y leyenda explicativa.
Runner de verificación: TradingView Pine Editor (v6)

## Specs
- S1: Script único en Pine v6 `overlay=true`, con interruptores individuales por indicador según orden de `indicadores/indicadores.md`.
- S2: Conceptos de estructura: BOS, CHoCH, CRT, FVG, iFVG, liquidez, MSS, order block, PDH/PDL y SMT (NQ vs ES1!).
- S3: Indicadores de contexto: EMA 9/21/50/200, RSI 14, ADX 14, Bollinger, MACD (12,26,9), ATR 14 y sesiones ORB NY (09:30-09:45) y UK (01:00-01:15).
- S4: Tabla de lecturas en `position.top_right` (16 filas): VolRel, RSI 14, ADX 14, MACD hist, MACD, ATR 14, POC, VAH, VAL, LVN, Single prints, Delta 1m (aprox.), Delta mejorado (5m), Sesgo estructura, Debería.
- S5: Lógica "debería" evaluando MACD histograma (`macdH > 0` para compra, `macdH < 0` para venta) en conjunción con RSI, ADX y VolRel.
- S6: Delta mejorado con lógica de 5 minutos para operativa de NQ en 1m, con modos "Vela 5m en curso" (con indicador de progreso `[X/5m]`) y "Ventana rodante (últimos 5 min)".
- S7: Tabla Leyenda en `position.bottom_right` (6 columnas, 10 filas) con 23 términos alfabéticos en negrita y fila inferior fusionada con nota operativa para divergencias Delta 1m vs 5m (pullback/absorción vs giro de tendencia).

## Tasks
- T1 (S1-S4) [done] Implementación base de `indicadores/shell_trading_indicadores.pine`.
- T2 (S5) [done] Ajuste de lógica: evaluación de MACD histograma en fila "deberia".
- T3 (S6) [done] Implementación de Delta mejorado 5m MTF para operativa en 1m y reubicación de ambos deltas arriba de Sesgo estructura.
- T4 (S7) [done] Actualización de la leyenda y nota operativa sobre absorción en 1m vs tendencia 5m.
- T5 (S1-S7) [pending] Validación y prueba interactiva en consola Pine de TradingView.

## Log
- L1: Usuario solicita implementación y depuración de script en Pine v6 a partir de `indicadores/indicadores.md`.
- L2: Ajustes solicitados por el usuario tras operaciones: MACD pasa a evaluar histograma; Delta mejorado adaptado a contexto de 5m para scalping de NQ en 1m; reordenamiento de filas en tabla de lecturas; incorporación de notas operativas en leyenda.
- L3: Engram Mirror: PENDIENTE. En el entorno actual `ENGRAM_STARTUP_POLICY=disabled` (el core de Engram no está inicializado en esta instalación). Progreso preservado canónicamente en `odd/tasks/indicadores-tradingview.md` y `Jira/User_Story.md`.
