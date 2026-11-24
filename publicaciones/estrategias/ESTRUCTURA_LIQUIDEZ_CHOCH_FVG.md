# ESTRUCTURA_LIQUIDEZ_CHOCH_FVG: Estructura Principal, Liquidez Intermedia, CHoCH de Confirmación y Entrada en FVG en NQ/MNQ

## 1. Hipótesis Operativa
La estrategia separa tres temporalidades con funciones distintas:

1. **Estructura principal (4 h):** define el sesgo. Tendencia bajista = mínimo más bajo y máximo más bajo.
2. **Liquidez (1 h, una temporalidad abajo):** los máximos casi iguales dentro de la estructura son liquidez. El precio tiende a barrerlos antes de girar.
3. **Confirmación (1–3 min):** tras el barrido, un CHoCH de la temporalidad menor (quiebre con cuerpo del último impulso) indica que el flujo cambió. El quiebre debe dejar un FVG, y ese FVG es la zona de entrada.

La hipótesis: un barrido de liquidez seguido de un CHoCH con FVG, a favor del sesgo de la estructura principal, ofrece una entrada con stop definido y objetivo en la siguiente liquidez.

---

## 2. Definiciones Medibles
- **Estructura principal:** swings de 4 h con la regla de 5 velas (swing = máximo/mínimo central de 5 velas). Tendencia bajista: último LH y LL confirmados por cierre.
- **Máximos casi iguales:** dos swing highs de 1 h con diferencia ≤ 5 puntos NQ.
- **Barrido:** mecha que supera el nivel de liquidez, seguida por un cierre de vela de 1 h que vuelve por debajo.
- **CHoCH de confirmación:** cierre con cuerpo de vela de 3 min (o 1 min) que supera el último swing high de la temporalidad menor, en dirección contraria al barrido. Mechas no cuentan.
- **FVG de la confirmación:** hueco de tres velas formado por el impulso que genera el CHoCH.

**Nota sobre la tabla del video:** el narrador dice liquidez en 1 h para una estructura de 4 h, pero la tabla empareja la estructura de 4 h (dentro de semanal) con liquidez de 4 h. Esta estrategia adopta la versión del narrador (1 h) porque es la única con regla explícita; el emparejamiento de la tabla queda pendiente de verificar.

---

## 3. Parámetros de Mercado e Instrumentos
- **Contratos:** MNQ ($2.00/punto, $0.50/tick) para ejecución; NQ ($20.00/punto) con riesgo acotado al colchón de drawdown.
- **Sesión:** RTH (09:30–16:00 ET). Ventana preferida: 09:45–12:00 ET y 13:30–15:30 ET.
- **Temporalidades:** sesgo en 4 h, liquidez en 1 h, confirmación en 3 min (con 1 min opcional).
- **Tamaño de FVG:** mínimo 6 puntos NQ para ser operable.

---

## 4. Reglas de Entrada (sesgo bajista; espejo para alcista)

1. **Sesgo:** estructura de 4 h bajista confirmada (LH + LL).
2. **Liquidez:** en 1 h, marcar máximos casi iguales por encima del precio (dentro de la estructura bajista).
3. **Barrido:** el precio supera la liquidez y cierra de vuelta por debajo en 1 h.
4. **CHoCH de confirmación (3 min):** tras el barrido, un cierre con cuerpo por debajo del último swing low de 3 min del impulso de regreso.
5. **FVG:** el impulso que genera el CHoCH deja un FVG bajista de 3 min.
6. **Entrada:** orden limit en la zona del FVG, o en su 50% (Consequent Encroachment), esperando el retesteo. Si el FVG es muy grande (> 20 puntos), entrar solo al 50%.

---

## 5. Gestión de Riesgo y Salida
- **Hard Stop Loss:** por encima del FVG (o del máximo del barrido si está más arriba), con 2 ticks de margen. Máximo 30 puntos NQ ($60 MNQ). El video sitúa el stop por encima del FVG; el tope de distancia es propio.
- **Take Profit:**
  - TP1 (50%): en el mínimo de 1 h o 15 min (siguiente liquidez inferior).
  - TP2 (50%): en las ineficiencias o mínimos casi iguales siguientes. Ratio mínimo 1:2 sobre el stop; si no existe objetivo a 2 R, no operar.
- **Break Even:** al llenarse TP1, stop del resto a +2 ticks.
- **Invalidación:** cierre de vela de 3 min por encima del máximo del barrido antes de TP1: salida inmediata.

---

## 6. Reglas de Cuenta Fondeada (Prop Firm Compliance)
- **Riesgo por operación:** máximo 0.75% del trailing drawdown real. Ejemplo: $2,000 de DD → $150 de riesgo → con stop de 20 puntos en MNQ ($40/contrato), 3 contratos.
- **Máximo 1 operación por barrido de liquidez.** Máximo 2 por día.
- **Sin promediar ni ampliar stop.**
- **Cierre forzoso:** flat antes de las 15:55 ET.

---

## 7. Honestidad Estadística y Validación Pendiente
- El material fuente es un reel de método con un ejemplo puntual (R:R de 4.52 en un trade). No hay estadística, ni de frecuencia de acierto ni de expectativa.
- Hay inconsistencia interna en las temporalidades del video (ver sección 2). Debe resolverse con backtest antes de usar la tabla completa.
- El tope de distancia del stop y el umbral de FVG (6 y 20 puntos) son propios.
- Backtest con costos reales ($0.62/lado MNQ, $2.10/lado NQ) y slippage de 1–2 ticks.
- Walk-forward para la definición de swing y de CHoCH. Muestra mínima: ≥ 100 operaciones, con resultados separados por tipo de barrido.

---

## 8. Arquitectura NinjaTrader 8 (NinjaScript)
- Series: 4 h (sesgo), 1 h (liquidez y barrido), 3 min (CHoCH y FVG), 1 min (opcional, gatillo).
- Detección de swings con la regla de 5 velas en cada serie; detección de FVG de tres velas en 3 min.
- Estados: `Sesgo_4h → Liquidez_1h_Marcada → Barrido_Detectado → CHoCH_3m → FVG_Formado → EnPosicion → Cerrado`.
- `SetStopLoss` y `SetProfitTarget` por precio tras la entrada.

---

## Referencias
- Ideas: [[ESTRUCTURA_LIQUIDEZ_CHOCH_FVG_01]]
- Fuentes y research:
  - YMI Blog (Cameron Bennion): CHoCH y BOS para futuros (el CHoCH como cambio de carácter, no como cualquier ruptura).
  - Tickwise Funding (Raphael): estructura de mercado para futuros; quiebre definido por cierre.
  - ICT SMT / liquidez: el barrido de máximos iguales como objetivo de liquidez previo al giro.
  - jira/trading_agent_persona.md: Hipótesis antes que código, validación y trailing drawdown.
