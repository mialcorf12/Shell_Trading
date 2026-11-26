# Indicadores TradingView — Pine Script v6
Rama: Tradingview
Objetivo: Implementar indicador único en Pine Script v6 (overlay=true) integrando indicadores de orden, estructura, contexto, tabla de lecturas en tiempo real y leyenda explicativa.
Runner de verificación: TradingView Pine Editor (v6)

## Specs
- S1: Script único en Pine v6 `overlay=true`, con interruptores individuales por indicador según orden de `indicadores/indicadores.md`.
- S2: Conceptos de estructura: BOS, CHoCH, CRT, FVG, iFVG, liquidez, MSS, order block, PDH/PDL y SMT (NQ vs ES1!).
- S3: Indicadores de contexto: EMA 9/21/50/200, RSI 14, ADX 14, Bollinger, MACD (12,26,9), ATR 14 y sesiones ORB NY (09:30-09:45) y UK (01:00-01:15).
- S4: Tabla de lecturas en `position.top_right`, 2 columnas (Lectura | Valor), 20 filas (encabezado + 19): VolRel, RSI 14, ADX 14, MACD hist, MACD, ATR 14, VAH, POC, VAL, LVN, Single prints, Delta 1m (aprox.), Delta mejorado (5m), Sesgo estructura, Debería y deberia2 a deberia5. Sin símbolos en las filas. Texto con `size.small`.
- S5: Lógica "debería" evaluando MACD histograma (`macdH > 0` para compra, `macdH < 0` para venta) en conjunción con RSI, ADX y VolRel.
- S6: Delta mejorado con lógica de 5 minutos para operativa de NQ en 1m, con modos "Vela 5m en curso" (con indicador de progreso `[X/5m]`) y "Ventana rodante (últimos 5 min)".
- S7: Tabla Leyenda en `position.bottom_right`, 10 columnas y 10 filas, con 24 términos alfabéticos en negrita. Fila inferior fusionada con nota operativa para divergencias Delta 1m vs 5m (pullback/absorción vs giro de tendencia). Bloque 1 con dos columnas de símbolo (solo CRT y Delta usan la segunda); bloques 2 y 3 con una columna de símbolo.
- S8: Marcas "deberia" en la gráfica desde la carga: "C" para Comprar y "V" para Vender, una por vela. Compra verde = C color verde; Compra amarillo = C color amarillo. Venta verde = V color verde; Venta amarillo = V color amarillo. Se evalúan en todas las velas (no solo en la última) y se controlan con un interruptor.
- S9: Marcas "deberia" solo con letra y color, sin símbolo de fondo (plotchar): C/V verde o amarilla. Segundo grupo "deberia2" igual que deberia pero con la línea MACD (macdL) en lugar del histograma (macdH); se muestra como fila en la tabla lectura y como marcas c/v en la gráfica para comparar cantidades.
- S10: Grupos "deberia3" (igual a deberia, histograma MACD) y "deberia4" (igual a deberia2, línea MACD). Ambos agregan al inicio de la fórmula un AND con el Sesgo de estructura: alcista (trend == 1) para compras y bajista (trend == -1) para ventas. Se muestran como filas 17 y 18 de la tabla lectura y como marcas C3/V3 y C4/V4 en la gráfica.
- S11: Grupo "deberia5": Comprar cuando sesgo alcista (trend == 1), cierre por encima del VWAP NY y el MACD línea cruza 0 hacia arriba (ta.crossover); Vender con el espejo (trend == -1, cierre bajo VWAP NY, ta.crossunder). Fila 19 de la tabla y marcas C5/V5 en verde.
- S12: La leyenda muestra el símbolo visual de cada término en su propia celda, con el mismo color que en la gráfica, sin texto explicativo del símbolo dentro del término. Símbolos: CRT ▲ verde / ▼ naranja; Delta 1m (aprox.) ▲ verde / ▼ rojo; MSS ◆ gris; PDH/PDL ┄┄ naranja; SMT ✕ fucsia; VolRel ● morado; ORB ━ fucsia (#ff00dd); POC ━ amarillo; VAH/VAL ━ cyan (aqua).
- S13: Los símbolos no van en la tabla de lectura. Esa tabla conserva dos columnas (Lectura | Valor) y el orden de filas VAH, POC, VAL.

## Tasks
- T1 (S1-S4) [done] Implementación base de `indicadores/shell_trading_indicadores.pine`.
- T2 (S5) [done] Ajuste de lógica: evaluación de MACD histograma en fila "deberia".
- T3 (S6) [done] Implementación de Delta mejorado 5m MTF para operativa en 1m y reubicación de ambos deltas arriba de Sesgo estructura.
- T4 (S7) [done, superado por T12] Actualización de la leyenda y nota operativa sobre absorción en 1m vs tendencia 5m.
- T5 (S1-S13) [pending] Validación y prueba interactiva en consola Pine de TradingView.
- T6 (S8) [done, sin verificar en TradingView] Condiciones de "deberia" movidas a alcance global y marcas C/V agregadas.
- T7 (S9) [done, sin verificar en TradingView] plotchar sin fondo; grupo deberia2 con macdL; fila en tabla lectura y marcas c/v.
- T8 (S10) [done, sin verificar en TradingView] Grupos deberia3/deberia4 con sesgo, filas de la tabla, marcas C3/V3 y C4/V4.
- T9 (S11) [done, sin verificar en TradingView] Grupo deberia5 con cruce MACD línea, VWAP NY y sesgo.
- T10 (S7, S12) [done, sin verificar en TradingView] Leyenda con símbolos coloreados en celdas propias; término ORB; símbolos de POC, VAH/VAL y ORB; eliminadas las columnas vacías (10 columnas).
- T11 (S13) [done, sin verificar en TradingView] Tabla lectura en 2 columnas, sin símbolos; orden VAH, POC, VAL; `size.small` en las 40 celdas.
- T12 (S4, S7) [done, sin verificar en TradingView] Documentación actualizada: `Jira/User_Story.md` y este archivo, movido a `odd/tasks/indicadores/indicadores-tradingview.md`.

Commits: ninguno. Los cambios están sin commitear en la rama Tradingview.

## Log
- L1: Usuario solicita implementación y depuración de script en Pine v6 a partir de `indicadores/indicadores.md`.
- L2: Ajustes solicitados por el usuario tras operaciones: MACD pasa a evaluar histograma; Delta mejorado adaptado a contexto de 5m para scalping de NQ en 1m; reordenamiento de filas en tabla de lecturas; incorporación de notas operativas en leyenda.
- L3: Engram Mirror: PENDIENTE. En el entorno actual `ENGRAM_STARTUP_POLICY=disabled` (el core de Engram no está inicializado en esta instalación). Progreso preservado canónicamente en `odd/tasks/indicadores/indicadores-tradingview.md` y `Jira/User_Story.md`.
- L4: Usuario pide que las señales deberia aparezcan de inmediato en la gráfica al cargar, con C/V una por vela. Pine dibuja el histórico al cargar; la vela en curso puede cambiar hasta el cierre.
- L5: Usuario pide marcas sin fondo (solo letra en color) porque la gráfica se ve saturada; y un 2.º grupo deberia2 con macdL en lugar de macdH, en la tabla lectura y en la gráfica, para comparar la cantidad de C y V.
- L6: Usuario pide grupos deberia3 y deberia4 (iguales a deberia y deberia2) con AND del Sesgo de estructura al inicio: alcista para compras, bajista para ventas.
- L7: Usuario pide implementar deberia5 (la recomendación de filtros de contexto y disparador de evento).
- L8: Usuario: "se ve demasiado saturado. 1) en la tabla de leyendas, puedes cambiar la explicación de los símbolos en letras por solo los símbolos visuales". Después pide colores ("probemos") y que los símbolos de VolRel y Delta 1m aparezcan en la tabla de lectura.
- L9: Usuario: "en la tabla de lectura, quiero conservar 2 columnas: Lectura | Valor, sin símbolos". Se descartó la opción de emojis en el texto de lectura.
- L10: Usuario: "las columnas 7 y 11 están vacías, las podemos eliminar?". Confirmado: eran el segundo símbolo de los bloques 2 y 3 de la leyenda.
- L11: Usuario: "podemos reducir el tamaño de letra de la tabla lectura?" y pide elegir el tamaño. Elegido: `size.small` (antes `size.auto`).
- L12: Usuario: "agrega el término ORB así como el símbolo línea fucsia; también línea amarilla para POC y línea cyan para VAH/VAL. En tabla lectura, mueve la fila POC en medio de VAH y VAL".
- L13: Usuario: "si falta algo por agregar actualiza los docs (y muévelas a /odd/tasks/indicadores/indicadores-tradingview.md), y User_Story.md sección feature 'indicadores para tradingview'". Este archivo pasa de `odd/tasks/indicadores-tradingview.md` a `odd/tasks/indicadores/indicadores-tradingview.md`.
