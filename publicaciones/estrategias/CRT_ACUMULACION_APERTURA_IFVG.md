# CRT_ACUMULACION_APERTURA_IFVG: Sesgo CRT, Acumulación Pre-Apertura y Entrada en iFVG a las 9:30 ET en NQ/MNQ

## 1. Hipótesis Operativa
La estrategia combina tres capas, en este orden:

1. **Sesgo direccional por CRT (Candle Range Theory):** una vela barre el máximo o mínimo previo; el sentido del barrido marca el objetivo opuesto. Barrido del máximo previo = sesgo bajista (objetivo: mínimo del rango previo). Barrido del mínimo previo = sesgo alcista (objetivo: máximo del rango previo).
2. **Acumulación pre-apertura:** antes de las 09:30 ET se forma un rango lateral de liquidez. En la apertura del contado, el precio suele hacer un movimiento falso (manipulación) contra la dirección real, y luego el movimiento real.
3. **Entrada en iFVG:** tras la manipulación, la inversión de un FVG que el precio atraviesa con cierre de vela marca la entrada en la dirección del sesgo CRT.

La regla de oro del autor ("no buscar entradas sin dirección") se aplica como filtro: sin sesgo CRT válido no hay operación.

---

## 2. Parámetros de Mercado e Instrumentos
- **Contratos:** MNQ ($2.00/punto, $0.50/tick) para ejecución; NQ ($20.00/punto) solo con riesgo acotado al colchón de drawdown.
- **Sesión:** apertura de Nueva York. Ventana de acumulación: 08:30–09:30 ET. Ventana de ejecución: 09:30–10:30 ET. Sin nuevas entradas después de las 10:30 ET.
- **Temporalidades:**
  - Sesgo CRT: 60 minutos (vela CRT) y 15 minutos (confirmación de barrido).
  - Rango pre-apertura: 15 minutos (08:30–09:30 ET).
  - Ejecución (FVG e iFVG): 1 minuto y 3 minutos.
- **Umbral de rango (definición medible):** rango pre-apertura entre 25 y 80 puntos NQ. Fuera de ese intervalo, no se opera.

---

## 3. Reglas Mecánicas

### Paso 1 — Sesgo CRT (antes de 09:30 ET)
- En 60 min, identificar la vela CRT previa (la última vela horaria cerrada).
- Si su mecha superior barre el máximo de la vela horaria anterior y cierra dentro del rango: **sesgo bajista**. Objetivo: el mínimo del rango de esa vela.
- Si su mecha inferior barre el mínimo previo y cierra dentro: **sesgo alcista**. Objetivo: el máximo del rango.
- Si ambas mechas o ninguna barren niveles: **sin sesgo, sin operación**.

### Paso 2 — Rango pre-apertura (08:30–09:30 ET)
- Registrar `RangeHigh` y `RangeLow` del periodo 08:30–09:30 ET.
- Validar el umbral de amplitud (25–80 puntos). Si no se cumple, cancelar la sesión.

### Paso 3 — Manipulación a la apertura (09:30–09:45 ET)
- Esperar un movimiento falso **contra** el sesgo: en sesgo alcista, el precio rompe `RangeLow` (barrido de mínimos); en sesgo bajista, rompe `RangeHigh`.
- El barrido debe volver a cerrar dentro del rango en una vela de 1 min (confirmación de que fue trampa, no ruptura real).

### Paso 4 — FVG a favor del sesgo (1 min)
- Tras la reentrada, identificar un FVG en la dirección del sesgo (alcista para sesgo alcista). Se marca el FVG más reciente generado por volumen direccional tras la apertura.
- Nota: el término "volumen alcista" del autor no está definido; aquí se operacionaliza como una vela de desplazamiento con cuerpo ≥ 60% de su rango y volumen superior a la media de 20 velas de 1 min.

### Paso 5 — Inversión (iFVG) y entrada
- Para sesgo alcista: el precio regresa y penetra un FVG bajista previo de 3 min (el FVG antiguo que mencionó el autor, situado en el rango). Una vela de 3 min cierra con cuerpo completo **por encima** del límite superior de ese FVG bajista: queda confirmado el iFVG alcista.
- **Gatillo:** compra a mercado al cierre de la vela de inversión, o limit en el límite superior del iFVG en el retesteo.
- Espejo para sesgo bajista.

---

## 4. Gestión de Riesgo y Salida
- **Hard Stop Loss:** bajo el mínimo de la manipulación (sesgo alcista), con 2 ticks de margen. Cabe mencionar que el video sitúa el stop bajo el FVG; se adopta el mínimo de la manipulación por ser el nivel de invalidación más claro.
- **Distancia máxima de stop:** 30 puntos NQ ($60 en MNQ). Si se excede, no operar.
- **Take Profit:**
  - TP1 (50%): al alcanzar el punto medio del rango CRT (`(CRT_High + CRT_Low) / 2`) o a 1.5 R, lo que ocurra primero.
  - TP2 (50%): en el objetivo CRT (máximo del rango previo en sesgo alcista).
- **Break Even:** al llenarse TP1, stop del resto a +2 ticks.
- **Invalidación:** cierre de vela de 3 min con cuerpo por debajo del mínimo de la manipulación antes de TP1: salida inmediata.

---

## 5. Reglas de Cuenta Fondeada (Prop Firm Compliance)
- **Riesgo por operación:** máximo 0.75% del trailing drawdown real. Ejemplo: $2,000 de DD → $150 de riesgo → con stop de 25 puntos en MNQ ($50/contrato), 3 contratos.
- **Máximo 1 operación por sesión de apertura.**
- **Sin promediar.**
- **Cierre forzoso:** flat antes de las 11:30 ET (ventana de apertura); ninguna posición se mantiene a la hora del almuerzo.

---

## 6. Validación Pendiente
- El video no muestra precios, timeframes exactos del CRT ni estadística; la hipótesis no está probada.
- El autor reconoce que el resultado de su "trade perfecto" es un ejemplo, no una muestra.
- Backtest con costos reales y slippage de 1–2 ticks en la apertura (el slippage en 09:30 suele superar esa cifra).
- Walk-forward para validar los umbrales de amplitud (25–80 pts) y el volumen direccional.
- Muestra mínima: ≥ 100 sesiones con operación para cualquier conclusión.

---

## 7. Arquitectura NinjaTrader 8 (NinjaScript)
- Series: 60 minutos (CRT), 15 minutos (confirmación), 3 minutos (FVG/iFVG), 1 minuto (ejecución).
- Máquina de estados: `EsperandoSesgo → SesgoValido → RangoRegistrado → Manipulacion_Detectada → iFVG_Confirmado → EnPosicion → Cerrado`.
- Órdenes con `SetStopLoss` y `SetProfitTarget` por precio tras la entrada.

---

## Referencias
- Ideas: [[CRT_ACUMULACION_APERTURA_IFVG_01]]
- Fuentes y research:
  - Pedro Bogni (publicación de origen): setup CRT + acumulación + iFVG (formato de publicidad educativa; no verificado).
  - ICT Killzone (Michael Phillips): Inversion FVG — polaridad invertida tras desplazamiento.
  - jira/trading_agent_persona.md: Hipótesis antes que código, honestidad en backtesting y trailing drawdown.
