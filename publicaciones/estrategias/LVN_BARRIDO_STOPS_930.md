# LVN_BARRIDO_STOPS_930: Barrido de Stops hacia un Nodo de Bajo Volumen tras la Apertura de 9:30 en NQ/MNQ

## 1. Hipótesis Operativa
Los operadores colocan stops de protección justo por debajo de líneas de tendencia y de mínimos iguales (ahí se acumulan órdenes de venta protectoras). En la apertura de Nueva York (09:30 ET), el flujo institucional puede empujar el precio hasta esas zonas para ejecutar esos stops. Si por debajo de esa liquidez existe un **Low Volume Node (LVN)**, el precio tiende a atravesarlo con rapidez, sin subastar, porque no hay volumen acumulado que lo frene.

La secuencia que la estrategia busca:
1. Liquidez visible: línea de tendencia alcista + mínimos iguales.
2. LVN en el perfil de volumen ubicado justo por debajo de esa liquidez.
3. Apertura de 09:30 ET: el precio barre la liquidez y se desliza por el LVN hacia el siguiente nodo de volumen.

Se opera **corto** en el sentido del barrido hacia el LVN. La hipótesis es que el movimiento a través del LVN es rápido y que la entrada se toma antes de que el precio llegue al nodo, no dentro de él (el video advierte: si el precio ya está dentro del LVN, se llegó tarde).

---

## 2. Parámetros de Mercado e Instrumentos
- **Contratos:** MNQ ($2.00/punto, $0.50/tick) para ejecución; NQ ($20.00/punto) solo con riesgo acotado al colchón de drawdown.
- **Sesión:** apertura de Nueva York. Ventana de análisis: 09:25–10:00 ET. Sin nuevas entradas después de las 10:30 ET.
- **Temporalidades:**
  - Perfil de volumen de la sesión anterior (y pre-market) para ubicar el LVN.
  - Línea de tendencia y mínimos iguales: 15 minutos.
  - Ejecución: 1 minuto.
- **Definiciones medibles (el video no las da):**
  - **Mínimos iguales:** dos o más swing lows de 15 min con diferencia ≤ 4 puntos NQ.
  - **Línea de tendencia:** unión de al menos dos mínimos crecientes de 15 min; debe tener al menos 2 toques.
  - **LVN válido:** nivel con volumen ≤ 40% del POC de la sesión de referencia y franja de al menos 0.75 puntos de alto.

---

## 3. Reglas de Entrada (venta corta)

1. **Paso 1 — Mapa previo (antes de 09:30 ET):** marcar la línea de tendencia y los mínimos iguales. Identificar el LVN válido inmediatamente por debajo de esa liquidez, a una distancia de 10 a 60 puntos.
2. **Paso 2 — Apertura (09:30 ET):** el precio barre la línea de tendencia o los mínimos iguales (mecha por debajo de ese nivel, en una vela de 1 min).
3. **Paso 3 — Filtro de no-llegada:** el precio aún no ha entrado en el LVN. Si ya está dentro de la franja, la operación queda cancelada (llegó tarde).
4. **Paso 4 — Gatillo de venta:** una vela de 1 min cierra con cuerpo bajista por debajo del punto de barrido, con volumen superior a la media de 20 velas de 1 min. Entrada a mercado al cierre de esa vela, o limit en la reentrada al nivel barrido.

**Filtro de horario:** si la apertura no produce el barrido entre 09:30 y 09:45 ET, no operar la sesión.

---

## 4. Gestión de Riesgo y Salida

- **Hard Stop Loss:** por encima del máximo de la vela de barrido, con 2 ticks de margen. Máximo 25 puntos NQ ($50 MNQ). Si el stop excede ese límite, no operar.
- **Take Profit:**
  - TP1 (50%): a 1.0 R, o justo antes del límite superior del LVN (lo que ocurra primero).
  - TP2 (50%): dentro del LVN o en el siguiente HVN por debajo. Ratio mínimo 1:2 sobre el stop; si el HVN está a menos de 2 R, no operar.
- **Break Even:** al llenarse TP1, stop del resto a +2 ticks.
- **Invalidación:**
  - Cierre de vela de 5 min por encima del punto de barrido: la hipótesis de barrido-y-caída queda anulada; salida inmediata.
  - Si el precio no alcanza TP1 en 30 minutos tras la entrada, cerrar a mercado.

---

## 5. Reglas de Cuenta Fondeada (Prop Firm Compliance)
- **Riesgo por operación:** máximo 0.75% del trailing drawdown real. Ejemplo: $2,000 de DD → $150 de riesgo → con stop de 20 puntos en MNQ ($40/contrato), 3 contratos.
- **Máximo 1 operación por sesión de apertura.**
- **Sin promediar ni ampliar stop.**
- **Cierre forzoso:** flat antes de las 11:30 ET (ventana de apertura) y en cualquier caso antes de las 15:55 ET.
- **Riesgo de slippage en apertura:** las órdenes de mercado entre 09:30 y 09:32 ET sufren slippage elevado. Usar orden limit donde sea posible.

---

## 6. Honestidad Estadística y Validación Pendiente
- El material fuente es una publicación promocional de una clase de pago. No muestra precios reales, estadística ni ejemplo verificable.
- El concepto de LVN como zona de paso rápido tiene respaldo en la literatura de Volume Profile, pero la hipótesis específica de barrido a las 9:30 no está probada.
- Backtest con costos reales y slippage de apertura. Walk-forward para los umbrales (4 puntos de mínimos iguales, 40% de volumen para LVN, 10–60 puntos de distancia).
- Muestra mínima: ≥ 100 sesiones con operación. Reportar distribución por día y por tipo de liquidez barrida.

---

## 7. Arquitectura NinjaTrader 8 (NinjaScript)
- Series: 15 min (liquidez y tendencia), 1 min (apertura y gatillo).
- Cálculo del LVN en memoria a partir del perfil de la sesión anterior (histograma por precio).
- Estados: `Mapa_Previo → Apertura_Barrido → Filtro_No_Llegada → Gatillo_Venta → EnPosicion → Cerrado`.
- `SetStopLoss` y `SetProfitTarget` por precio inmediatamente tras la entrada.

---

## Referencias
- Ideas: [[LVN_BARRIDO_STOPS_930_01]]
- Fuentes y research:
  - ATAS (Volume Profile Strategy with Order Flow: NQ Case Study): perfil de volumen y niveles de bajo volumen en NQ.
  - YMI Blog (Cameron Bennion): Volume Profile para ES y NQ (VPOC, HVN, LVN).
  - jira/trading_agent_persona.md: Hipótesis antes que código, validación honesta y trailing drawdown.
