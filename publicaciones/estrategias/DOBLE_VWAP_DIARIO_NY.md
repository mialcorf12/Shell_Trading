# DOBLE_VWAP_DIARIO_NY: Filtro de Sesgo con VWAP Diario (Globex 18:00 ET) y VWAP de Apertura NY (09:30 ET) en NQ/MNQ

## 1. Hipótesis Operativa
Dos VWAP con anclas distintas describen el valor del precio desde dos horizontes:

- **VWAP diario (ancla 18:00 ET, inicio de Globex):** promedio ponderado por volumen de toda la jornada, incluyendo la sesión asiática y la de Londres. Se mueve lento y representa el precio justo de la sesión completa.
- **VWAP de Nueva York (ancla 09:30 ET):** solo el volumen de la sesión regular de EE.UU. Reacciona más rápido porque su muestra es menor y se concentra en el flujo de la apertura.

La lectura de la relación entre ambos define el sesgo:
- **Precio encima de ambos VWAP:** control comprador.
- **Precio debajo de ambos VWAP:** control vendedor.
- **Precio entre ambos, con VWAP separados:** la operación va desde el VWAP que el precio ha superado hacia el que aún no ha alcanzado. Es la única configuración con operación.

La estrategia no es un generador de señales por sí misma: es un **filtro de sesgo** y un marco para entrar en el sentido del flujo, con entrada en un cierre de vela que supere el VWAP.

---

## 2. Parámetros de Mercado e Instrumentos
- **Contratos:** MNQ ($2.00/punto, $0.50/tick) para ejecución; NQ ($20.00/punto) solo con riesgo acotado al colchón de drawdown.
- **Sesión operativa:** RTH (09:30–16:00 ET). Ventana preferida: 09:45–12:00 ET.
- **Anclas (zona horaria explícita):**
  - VWAP diario: 18:00 ET del día anterior (reset de Globex).
  - VWAP NY: 09:30 ET del día actual.
- **Definiciones medibles:**
  - **VWAP separados:** distancia entre VWAP diario y VWAP NY ≥ 15 puntos NQ. Si la distancia es menor, el filtro no discrimina y no se opera.
  - **Cierre con cuerpo más allá del VWAP:** la vela de 5 min cierra con al menos 60% de su rango como cuerpo, del lado correspondiente del VWAP.
- **Temporalidades:** VWAP y sesgo en 5 min; gatillo en 1 min.

---

## 3. Reglas de Entrada

### Sesgo alcista (precio entre VWAP separados, por encima del VWAP NY):
1. Se confirma que el precio está por encima del VWAP NY y por debajo del VWAP diario. El VWAP diario está por encima del precio: es el objetivo.
2. Entrada larga cuando una vela de 5 min cierra con cuerpo (≥ 60% del rango) por encima del VWAP NY, desde debajo de él.
3. Gatillo de confirmación en 1 min: vela de 1 min que cierra por encima del máximo de la vela de 5 min de entrada, sin cerrar por debajo del VWAP NY.
4. Entrada: compra a mercado en el cierre del gatillo.

*Nota:* el video ilustra la compra con el precio cerrando por encima del VWAP NY y dirigido al VWAP diario. Esa es la configuración que se opera.

### Sesgo bajista (precio entre VWAP separados, por debajo del VWAP NY):
- Espejo: el precio cierra con cuerpo por debajo del VWAP NY, con el VWAP diario por debajo como objetivo.

### Sin operación:
- Precio encima (o debajo) de ambos VWAP: el sesgo es claro pero no hay "entrada entre VWAP"; se considera tendencia. No operar esta estrategia.
- VWAP con distancia < 15 puntos: no discrimina.

---

## 4. Gestión de Riesgo y Salida

- **Hard Stop Loss:** por debajo del mínimo de la vela de entrada de 5 min (sesgo alcista), con 2 ticks de margen. Máximo 25 puntos NQ ($50 MNQ). Si la distancia lo excede, no operar.
- **Take Profit:**
  - TP1 (50%): en el VWAP NY recuperado (o 1.0 R, lo que ocurra primero).
  - TP2 (50%): en el VWAP diario. Ratio mínimo 1:2 sobre el stop; si el VWAP diario está a menos de 2 R de la entrada, no operar.
- **Break Even:** al llenarse TP1, stop del resto a +2 ticks.
- **Invalidación:**
  - Cierre de vela de 5 min con cuerpo por debajo del VWAP NY tras la entrada (sesgo alcista): salida inmediata.
  - Cruce del VWAP diario por el lado contrario al sesgo (el precio pasa de debajo de VWAP diario a encima de VWAP NY que ya no es soporte): revisar la lectura; salir si pierde el VWAP NY.

---

## 5. Reglas de Cuenta Fondeada (Prop Firm Compliance)
- **Riesgo por operación:** máximo 0.75% del trailing drawdown real. Ejemplo: $2,000 de DD → $150 de riesgo → con stop de 20 puntos en MNQ ($40/contrato), 3 contratos.
- **Máximo 1 operación por sesión.**
- **Sin promediar ni ampliar stop.**
- **Cierre forzoso:** flat antes de las 15:55 ET.

---

## 6. Honestidad Estadística y Validación Pendiente
- El material fuente es una explicación conceptual con un ejemplo ilustrativo. No presenta estadística, precios ni muestra de operaciones: la hipótesis no está probada.
- Las anclas (18:00 ET y 09:30 ET) y los umbrales (15 puntos de separación, 60% de cuerpo) son propios. Deben validarse con datos de entrenamiento y comprobarse fuera de muestra.
- El cálculo del VWAP diario depende de incluir el volumen de Globex. Sin datos de sesión extendida, el ancla de 18:00 ET no es reproducible.
- Backtest con costos reales ($0.62/lado MNQ, $2.10/lado NQ) y slippage de 1–2 ticks.
- Muestra mínima: ≥ 100 operaciones. Reportar resultados separados por sesgo alcista y bajista, y por día.

---

## 7. Arquitectura NinjaTrader 8 (NinjaScript)
- Series: 5 min (sesgo y cierre con cuerpo), 1 min (gatillo).
- Dos VWAP en `OnBarUpdate`: uno reiniciado a las 18:00 ET (Globex) y otro a las 09:30 ET (NY), con volumen ponderado.
- Configurar la zona horaria de la sesión de forma explícita para que el reset ocurra en la hora de Nueva York, no en la del gráfico.
- Estados: `Calcular_VWAPs → Sesgo_Definido → Esperar_Cierre_Sobre_VWAP_NY → Gatillo_1m → EnPosicion → Cerrado`.
- `SetStopLoss` y `SetProfitTarget` por precio tras la entrada.

---

## Referencias
- Ideas: [[DOBLE_VWAP_DIARIO_NY_01]]
- Fuentes y research:
  - Footprint Lab (VWAP Trading Strategy for Futures: ES, NQ & Gold): anclas de sesión y reset de Globex a las 18:00 ET.
  - TradingView (Futures VWAP Suite NY / Globex): VWAP anclado a 09:30 ET y a 18:00 ET para futuros.
  - jira/trading_agent_persona.md: Validación honesta, zona horaria explícita y trailing drawdown.
