# CRT_NASDAQ_OB: Candle Range Theory Top-Down (Diario → 4H → 1H → 15 min) con Order Block de 15 min en NQ/MNQ

## 1. Hipótesis Operativa
La Candle Range Theory (CRT) describe un patrón de tres movimientos en una vela de referencia: el precio toma el mínimo (o máximo) del rango de la vela, y luego cierra de vuelta dentro del rango. Ese barrido indica que la liquidez de ese extremo fue capturada, y el precio tiende a dirigirse al lado opuesto del rango.

La estrategia aplica CRT en cascada, de temporalidades altas a bajas:

1. **Diario:** marca el objetivo (DOL: draw on liquidity), en este caso el máximo del día anterior tras una vela de expansión alcista.
2. **4H:** rango CRT contra el objetivo. Una vela que toma el mínimo del rango y cierra de nuevo adentro confirma el sesgo alcista.
3. **1H:** mismo patrón en la misma dirección. Si D, 4H y 1H se alinean, la probabilidad se considera alta.
4. **15 min:** entrada en el order block (OB) bajista previo al movimiento alcista.

Según el video, la alineación de las tres temporalidades es el filtro principal. Sin alineación, no hay operación.

---

## 2. Definiciones Medibles
- **Vela de referencia CRT:** la vela de la temporalidad analizada cuyo rango (máximo–mínimo) define los niveles.
- **Barrido CRT alcista:** una vela toma el mínimo del rango de la vela de referencia (mecha por debajo) y cierra con su cuerpo de nuevo dentro del rango. Mechas que cierran fuera no cuentan.
- **Vela de expansión (diario):** vela alcista con cuerpo ≥ 60% de su rango, que cierra por encima del máximo de las dos velas previas. El video no la define; esta definición es propia.
- **Order block de 15 min:** la última vela bajista de cuerpo grande (cuerpo ≥ 50% del rango, cierre bajista) antes del impulso alcista que sigue al barrido de 15 min.
- **Alineación:** barrido CRT alcista en diario, 4H y 1H en la misma dirección, sin barrido contrario más reciente que el de la alineación.

---

## 3. Parámetros de Mercado e Instrumentos
- **Contratos:** MNQ ($2.00/punto) para ejecución; NQ ($20.00/punto) con riesgo acotado al colchón de drawdown.
- **Instrumento:** NQ/MNQ. El video muestra EURUSD, NASDAQ y XAUUSD; la regla debe validarse por separado para el Nasdaq y no se asume transferible a otros activos.
- **Sesión:** RTH (09:30–16:00 ET). Ventana preferida: 09:45–12:00 ET.
- **Temporalidades:** diario (objetivo), 4H (rango CRT), 1H (confirmación), 15 min (OB y entrada).

---

## 4. Reglas de Entrada (sesgo alcista; espejo para bajista)

1. **Diario:** marcar el DOL (máximo del día anterior, tras la vela de expansión alcista).
2. **4H:** barrido CRT alcista contra el mínimo del rango de la vela 4H de referencia.
3. **1H:** barrido CRT alcista en la misma dirección. Verificar la alineación D + 4H + 1H.
4. **15 min:** identificar el OB bajista (sección 2) formado antes del movimiento alcista. Entrada cuando el precio retesta el OB y se produce un cierre alcista de 15 min que supera el máximo del OB.
5. **Entrada:** compra a mercado al cierre de la vela de confirmación en 15 min, o limit en el OB si el precio lo retesta.

---

## 5. Gestión de Riesgo y Salida
- **Hard Stop Loss:** por debajo del mínimo de la vela de barrido de 15 min, con 2 ticks de margen. El video sitúa el stop bajo el mínimo; la distancia máxima de 30 puntos NQ ($60 MNQ) es propia.
- **Take Profit:**
  - TP1 (50%): en el primer nivel de liquidez intermedio (mínimo de 1H por encima del precio).
  - TP2 (50%): en el DOL diario (máximo del día anterior). Ratio mínimo 1:2 sobre el stop; si el DOL está a menos de 2 R, no operar.
- **Break Even:** al llenarse TP1, stop del resto a +2 ticks.
- **Invalidación:** cierre de vela de 15 min por debajo del OB (mínimo de la vela bajista previa) tras la entrada: salida inmediata.

---

## 6. Reglas de Cuenta Fondeada (Prop Firm Compliance)
- **Riesgo por operación:** máximo 0.75% del trailing drawdown real. Ejemplo: $2,000 de DD → $150 de riesgo → con stop de 25 puntos en MNQ ($50/contrato), 3 contratos.
- **Máximo 1 operación por alineación.** Máximo 2 por día.
- **Sin promediar ni ampliar stop.**
- **Cierre forzoso:** flat antes de las 15:55 ET.

---

## 7. Honestidad Estadística y Validación Pendiente
- El material fuente es un reel con varios instrumentos y un reclamo de resultados ("más de $50.000 retirados el mes pasado") no verificable. No hay estadística ni precios reales.
- La regla de alineación de tres temporalidades y las definiciones de vela de expansión y de barrido son propias; el video no las define.
- En el frame del diario hay ambigüedad: el "barrido" podría ser un patrón CRT diario o una simple vela de expansión. Hay que resolverlo con datos antes de usar la regla.
- Backtest con costos reales ($0.62/lado MNQ, $2.10/lado NQ) y slippage de 1–2 ticks.
- Walk-forward para la alineación y la definición de OB. Muestra mínima: ≥ 100 operaciones, con resultados separados por número de temporalidades alineadas.

---

## 8. Arquitectura NinjaTrader 8 (NinjaScript)
- Series: diaria (objetivo), 4 h (CRT), 1 h (CRT de confirmación), 15 min (OB y entrada).
- Detección de barrido CRT: comparación de mínimo/máximo con el rango de la vela de referencia y cierre dentro del rango, por serie.
- Estados: `Objetivo_Diario → CRT_4h → CRT_1h → Alineacion_Verificada → OB_15m → EnPosicion → Cerrado`.
- `SetStopLoss` y `SetProfitTarget` por precio tras la entrada.

---

## Referencias
- Ideas: [[CRT_NASDAQ_OB_01]]
- Fuentes y research:
  - Candle Range Theory (CRT): marco de barrido de rango de vela y reentrada, usado en análisis top-down.
  - Publicación de origen (@reel DaVrmqhuZhb): CRT top-down con order block de 15 min (educativo; reclamo de resultados no verificable).
  - jira/trading_agent_persona.md: Hipótesis antes que código, validación y trailing drawdown.
