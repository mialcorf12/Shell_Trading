# entorno general:
en todo momento quiero usar trading_agent_persona.md

# model routing
• Tareas rápidas, tiempo real y bajo costo (Claude Haiku 5.5): Ideal para respuestas inmediatas, preguntas cotidianas, clasificación, resúmenes breves y subagentes que ejecutan pasos simples.
• Trabajo diario, código y redacción (Claude Sonnet 5.5): Ofrece el mejor balance entre velocidad, capacidad y costo para programar a diario, revisar código, redactar documentos o presentaciones y ejecutar flujos con pasos claros.
• Ingeniería compleja y trabajo pesado (Claude Opus 5.5): Recomendado para programación agéntica avanzada, refactorización grande, arquitectura y análisis donde un error resulta costoso.
• Problemas de máxima ambigüedad y larga duración (Claude Fable 5.2): Pensado para investigación exhaustiva, análisis de datos complejos y agentes autónomos que operan durante horas.

# Proyecto:
vamos a trabajar un nuevo proyecto llamado 'Shell_Trading'. 

## feature:'ideas de estrategias'.
vamos a tener 2 carpetas Ideas y Estrategias. Ideas/Draft es para yo incluir el resumen de reels que haya encontrado en internet. a partir de estos reels, necesito depurar/mejorar el contenido para trabajar los archivos en estrategias. puedo tener 100 ideas del mismo tema de estrategia, para un mismo archivo de estrategia (ejemplo 100 archivos en Ideas que hablen de FVG, pero solo 1 archivo de FVG en Estrategias). la idea es depurar/mejorar con el tiempo ese archivo de estrategias. Aunque una idea use los mismos indicadores de trading, debemos agruparlas con forme al nombre de la estrategia (ejemplo: una idea puede contener el indicador EMA9, pero si se indica que es parte de la estrategia ORB, entonces se debe de hacer unicamente esta relacion. Para mantener ambos directorios limpios, vamos a crear el folder Ideas/Draft, aqui es donde se incluirian las "ideas sucias/borrador", y cuando se mejoren (se mueven al folder Ideas, con nombre similar a ORB_NY_01.md etc, estas relacionadas con la Estrategia ORB_NY.md ). conserva al final de los archivos md la referencias entre estrategias e ideas, asi como en draft, la referencia al archivo en ideas y viceversa.
En python quiero que armes una interfaz web que me permita gestionar el orden del directorio (ejemplo ideas sin revision (folder draft), Ideas depuradas (folder ideas), estrategias (estrategias) ) y de una forma visual, facil e intuitiva me permitas entender la relacion entre los archivos, algo similar a un mindmap de obsidian. dame la opcion con un boton de limpiar ideas/draft, esto seria, que me ayudes a redactar mejor el contenido de draft y crear un nuevo archivo idea (no olvides de generar la relacion entre los archivos de Ideas y Ideas/Draft)

## feature:'indicadores para tradingview'.
con pine script v6, quiero que uses indicadores/indicadores.md, para crear un archivo en el mismo folder, que pueda cargarlo dentro de tradingview. usa las mismas secciones y orden para separarlos en la entrada de datos, que yo pueda activarlos o desactivarlos.

### Estado (sesión de trabajo)
**Archivos**
- `indicadores/shell_trading_indicadores.pine`: indicador principal, Pine v6, `overlay=true`.
- `indicadores/test_movimiento.pine`: prueba de aislamiento (EMA 9 y VWAP) usada para diagnosticar; se puede borrar.

**Entradas de datos (mismo orden que `indicadores/indicadores.md`)**
- **1. Indicadores:** bandas σ del VWAP (desactivada por defecto), delta aproximado 1m y delta mejorado 5m (contexto MTF en 1m: acumulado de la vela de 5m en curso o rodante 5m), perfil de volumen (POC, VAH, VAL, LVN), TPO aproximado (single prints), volumen (VolRel), VWAP NY 09:30 ET, VWAP Diario 18:00 ET (antes "VWAP Globex").
- **3. Conceptos de estructura y niveles:** BOS, CHoCH, CRT, FVG, iFVG, liquidez (desactivada por defecto), MSS, order block, PDH/PDL, SMT (requiere ES1!).
- **4. Indicadores de contexto:** EMA 9/21/50/200 (cada una activable), RSI 14, ADX 14, Bandas de Bollinger (desactivadas por defecto), MACD (12, 26, 9), ATR 14 (agregado por pedido; no está en `indicadores.md`), ORB NY 09:30–09:45 ET (vence 17:00 ET) y ORB UK 01:00–01:15 ET (vence 06:00 ET), cada uno con su interruptor.
- **Visualización:** etiquetas pequeñas al final de cada línea (activable).

**Estilo (pestaña Estilo, valores constantes)**
- EMA 9 azul grosor 2; EMA 21 naranja grosor 2 punteada; EMA 50 fucsia grosor 1; EMA 200 gris grosor 2.
- VWAP NY `rgb(135, 206, 235)` grosor 1; VWAP Diario gris grosor 1 punteada.
- PDH y PDL con el mismo estilo que EMA 21 (naranja, grosor 2, punteada).
- ORB NY y ORB UK: color `#ff00dd`, grosor 4. Se dibujan como `plot` para poder editarlos desde Estilo.
- Valores ocultos en la línea de estado en todas las líneas y marcas (`display.all - display.status_line`).

**Tabla de lecturas (superior derecha)**
- VolRel (verde ≥ 1.5, amarillo 0.8–1.5, rojo < 0.8), RSI (verde > 50), ADX (verde ≥ 25, amarillo 20–25, rojo < 20), MACD histograma y MACD línea (verde > 0, rojo < 0), ATR en puntos con escala x = ATR / media 50 (azul < 0.8, verde 0.8–1.2, amarillo 1.2–1.5, rojo > 1.5), POC, VAH, VAL, LVN, single prints, delta 1m aproximado, delta mejorado 5m (muestra progreso [X/5m] o rodante), sesgo de estructura.
- Fila **"deberia"**, con la lógica en este orden de prioridad (evalúa MACD histograma):
  - Comprar verde: RSI > 50 y MACD histograma > 0 y ADX ≥ 25 y VolRel ≥ 1.5.
  - Vender verde: RSI < 50 y MACD histograma < 0 y ADX ≥ 25 y VolRel ≥ 1.5.
  - Comprar amarillo: RSI > 50 y MACD histograma > 0 y (ADX ≥ 20 o VolRel ≥ 0.8).
  - Vender amarillo: RSI < 50 y MACD histograma < 0 y (ADX ≥ 20 o VolRel ≥ 0.8).
  - Si ninguna se cumple: "—".

**Leyenda (inferior derecha)**
- Tabla con los 23 términos (incluye SMT, Delta 1m y Delta mejorado 5m), en orden alfabético y nombres en negrita, llenada de arriba abajo y luego de izquierda a derecha. Incluye fila inferior fusionada con nota operativa para interpretar divergencias entre Delta 1m y Delta 5m (absorción vs giro de tendencia).

**Pendientes**
- Compilar y probar en TradingView: el código no se pudo compilar desde la sesión. Revisar la consola de Pine.
- Validar la fila "deberia" con backtest, costos reales y fuera de muestra antes de usarla. Los umbrales son propuestas, no datos validados.
- Leyenda en el panel inferior: Pine solo puede ubicar la tabla en el panel inferior con un script aparte (`overlay=false`). Pendiente de decisión.
- ORB UK: revisar el color por defecto si se confunde con el ORB NY.
- Borrar `test_movimiento.pine` cuando ya no haga falta.
