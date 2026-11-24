# IFVG_LIQUIDEZ_1A1: Inversión de FVG tras Barrido de Liquidez con Objetivo 1:1 en NQ/MNQ

## 1. Hipótesis Operativa
Un Fair Value Gap (FVG) que el precio atraviesa con un cierre de vela en sentido contrario deja de ser resistencia o soporte como FVG y pasa a actuar como **Inversion FVG (iFVG)**: una zona de polaridad invertida. Esta estrategia combina tres piezas:

1. **Liquidez barrida:** un nivel de máximos o mínimos iguales (liquidez) es penetrado por un instante, capturando stops.
2. **FVG de 15 minutos tocado:** el barrido ocurre dentro o junto a un FVG de 15 min, que es la zona de interés.
3. **iFVG de 3 minutos:** un FVG de 3 min en el sentido del movimiento se invierte por cierre de vela. La entrada se toma en esa inversión, con objetivo de 1:1.

La hipótesis: si la liquidez fue barrida dentro de un FVG de temporalidad mayor y la inversión de 3 min confirma el cambio de flujo, el precio tiende a recorrer al menos la distancia equivalente al riesgo.

---

## 2. Parámetros de Mercado e Instrumentos
- **Contratos:** MNQ ($2.00/punto, $0.50/tick) para ejecución inicial; NQ ($20.00/punto) con riesgo acotado al colchón de drawdown.
- **Sesión:** RTH (09:30–16:00 ET). Ventana preferida: 09:45–12:00 ET y 13:30–15:30 ET.
- **Temporalidades:**
  - Zona de interés (FVG y liquidez): 15 minutos.
  - Disparo (FVG de 3 min e inversión): 3 minutos.
  - Ajuste de entrada opcional: 1 minuto.
- **Definición de liquidez:** máximos iguales (o mínimos iguales) de 15 min dentro de una tolerancia de 4 puntos NQ, o el máximo/mínimo previo de la sesión.

---

## 3. Reglas Mecánicas de Entrada

### Configuración Corta (Sweep de liquidez alta):
1. **Paso 1 — Liquidez:** marcar un nivel de máximos iguales de 15 min (o máximo de sesión previa) sobre el precio.
2. **Paso 2 — FVG de 15 min:** marcar un FVG bajista de 15 min no mitigado que contenga el nivel de liquidez o esté a ≤ 5 puntos de él (la condición de contención exacta debe validarse con backtest; ver sección 7).
3. **Paso 3 — Barrido:** el precio supera el nivel de liquidez y penetra el FVG de 15 min.
4. **Paso 4 — FVG de 3 min en el retroceso:** tras el barrido, la pierna bajista de 3 min genera un FVG bajista de 3 min.
5. **Paso 5 — Inversión (iFVG):** tras el barrido, el retroceso alcista de 3 min forma un FVG alcista de 3 min. La inversión que confirma la venta es una vela de 3 min que cierra con cuerpo completo **por debajo del límite inferior** de ese FVG alcista. El FVG pasa de soporte a resistencia (polaridad invertida).
6. **Paso 6 — Gatillo:** venta a mercado al cierre de la vela de inversión, o limit en el límite inferior del iFVG en el retesteo.

**Versión larga (espejo):** barrido de mínimos iguales dentro de un FVG alcista de 15 min, FVG alcista de 3 min en el retroceso, cierre con cuerpo por encima del límite superior del FVG de 3 min, compra.

---

## 4. Gestión de Riesgo y Salida (1:1)

- **Hard Stop Loss:** por encima del máximo del barrido (corto) o por debajo del mínimo del barrido (largo), con 2 ticks de margen.
  - Distancia de riesgo R = |entrada − stop|.
  - Stop máximo: 25 puntos NQ ($50 en MNQ). Si R supera 25 puntos, la operación se descarta.
- **Take Profit 1:1:** a una distancia exacta de R desde la entrada (en corto, por debajo del precio de entrada).
  - TP1 (50% de la posición) a 1R. Al llenarse, mover el stop del resto a Break Even (+2 ticks).
  - TP2 (50% restante) a 2R o en el mínimo de la última pierna de 15 min, lo que ocurra primero.
- **Invalidación:**
  - Cierre de vela de 3 min con cuerpo por encima del máximo del barrido (corto) antes de tocar TP1: salida inmediata a mercado.

---

## 5. Reglas de Cuenta Fondeada (Prop Firm Compliance)
- **Riesgo por operación:** máximo 0.75% del trailing drawdown real. Ejemplo: $2,000 de DD → $150 de riesgo → con R de 20 puntos en MNQ ($40/contrato), 3 contratos ($120 de riesgo).
- **Límite diario:** máximo 2 operaciones por sesión; al tocar un stop, espera 30 minutos antes de la siguiente.
- **Sin promediar ni ampliar stop.**
- **Cierre forzoso:** flat antes de las 15:55 ET.

---

## 6. Ventaja y Expectativa (honestidad estadística)
- El video no muestra precios, win rate ni muestra estadística. El R:R de 1:1 implica que el sistema necesita una tasa de acierto superior al 50% *después de costos* para ser rentable. Con comisiones ($0.62/lado MNQ) y slippage de 1–2 ticks, el 1R efectivo se reduce.
- **Expectativa mínima requerida:** calcular E = (tasa de acierto × 1R) − (tasa de pérdida × 1R) − costos, con datos de backtest, no con el video.

---

## 7. Validación Pendiente (antes de uso en vivo)
- Definir cuantitativamente "contener el nivel de liquidez" (tolerancia en puntos).
- Backtest con costos reales y slippage. Walk-forward para los umbrales.
- Muestra mínima: ≥ 100 operaciones.
- Reportar drawdown máximo y distribución por día.

---

## 8. Arquitectura NinjaTrader 8 (NinjaScript)
- Series: 15 minutos (zona y liquidez), 3 minutos (FVG e iFVG), 1 minuto (ajuste opcional).
- Detección de FVG en la serie de 3 min con la regla de tres velas.
- Estados: `Buscando_Liquidez → Barrido_Detectado → FVG_3m_Formado → iFVG_Confirmado → EnPosicion → Cerrado`.
- `SetStopLoss` y `SetProfitTarget` por precio inmediatamente tras la entrada.

---

## Referencias
- Ideas: [[IFVG_LIQUIDEZ_1A1_01]]
- Fuentes y research:
  - Zero-G Trading: Inverse Fair Value Gap Strategy para NQ (regla de inversión por cierre).
  - ICT Killzone (Michael Phillips): Inversion FVG — polarity flip tras desplazamiento.
  - jira/trading_agent_persona.md: Backtesting honesto, expectativa y trailing drawdown.
