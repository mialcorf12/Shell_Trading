# VWAP_REVERSION_AGOTAMIENTO: Fade de Precio Estirado a 2–3 Desviaciones del VWAP con Confirmación de Agotamiento en NQ/MNQ

## 1. Hipótesis Operativa
El VWAP de sesión es el precio promedio ponderado por volumen desde la apertura. Las bandas de desviación estándar (1σ, 2σ, 3σ) miden qué tan lejos está el precio de ese promedio. Un precio estirado a 2–3σ es, estadísticamente, una zona de extensión poco frecuente.

La hipótesis: **en un día de rango o balance, un precio que se estira a 2–3σ tiende a regresar al VWAP, pero solo después de que la presión compradora (o vendedora) se agota.** Entrar en la primera vela que toca la banda es un error frecuente: en un día de tendencia el precio puede cabalgar la banda durante horas.

La operación no es "tocó la banda, vendo". Es "tocó la banda, la presión se apagó, y entro contra el movimiento en el primer cierre de regreso".

---

## 2. Condición de Régimen (filtro obligatorio)
Esta estrategia **solo opera en días de rango o balance**. Antes de la sesión se clasifica el día:
- **Día de tendencia (no operar fade):** el precio se mantiene por encima (o debajo) del VWAP durante más de 70% de la sesión tras la primera hora, con cierres consecutivos fuera de la banda 1σ y noticias macro de impacto alto en el día.
- **Día de rango (operar):** el precio cruza el VWAP varias veces (≥ 3 cruces en la primera hora) y no sostiene ninguna banda 1σ más de 30 minutos.
- **Zona gris:** sin operación.

Esta clasificación evita la trampa principal del concepto: el fade contra tendencia.

---

## 3. Parámetros de Mercado e Instrumentos
- **Contratos:** MNQ ($2.00/punto, $0.50/tick) para ejecución; NQ ($20.00/punto) solo con riesgo acotado al colchón de drawdown.
- **Sesión:** RTH (09:30–16:00 ET). Ventana preferida: 10:00–13:30 ET (VWAP con muestra suficiente).
- **Ancla del VWAP:** 09:30 ET (apertura de NY). Desviaciones calculadas con volumen ponderado sobre la misma ancla.
- **Temporalidades:** bandas y contexto en 5 min; gatillo de agotamiento en 1 min.
- **Definiciones medibles:**
  - **Estiramiento:** cierre de vela de 5 min con precio ≥ +2σ (o ≤ −2σ), y con precio ≤ 3σ (fuera de 3σ el riesgo de tendencia se dispara; no operar).
  - **Agotamiento:** volumen de las últimas 3 velas de 1 min ≤ 80% del volumen promedio de las 3 velas que llevaron el precio a la banda.

---

## 4. Reglas de Entrada

### Venta (estiramiento alcista a +2σ):
1. Día clasificado como de rango (sección 2).
2. El precio cierra una vela de 5 min en ≥ +2σ y ≤ +3σ.
3. **Agotamiento:** el volumen de las últimas tres velas de 1 min cae ≤ 80% respecto a las tres velas que llevaron el precio a la banda. El máximo de la última vela no supera el máximo de la vela de estiramiento (no hay nuevos máximos).
4. **Gatillo:** una vela de 1 min con cuerpo bajista que cierra por debajo del mínimo de la vela previa, o un patrón de reversión (envolvente bajista, estrella fugaz) en la banda.
5. Entrada: venta a mercado al cierre del gatillo.

### Compra (estiramiento bajista a −2σ): espejo.

**Prohibido:** entrar mientras el precio sigue haciendo máximos nuevos, o antes de que el volumen se apague. La condición de agotamiento es obligatoria.

---

## 5. Gestión de Riesgo y Salida

- **Hard Stop Loss:** por encima del máximo de la vela de estiramiento (+3 ticks de margen). Si el stop supera 30 puntos NQ ($60 MNQ), no operar.
- **Take Profit:**
  - TP1 (50%): en la banda 1σ.
  - TP2 (50%): en el VWAP. Ratio mínimo 1:1.5 sobre el stop. Si el VWAP está a menos de 1.5 R, no operar.
- **Break Even:** al llenarse TP1, stop del resto a +2 ticks.
- **Invalidación:**
  - Cierre de vela de 5 min por encima de +3σ tras la entrada: salida inmediata (el día pasó a tendencia).
  - Nuevo máximo que supera el stop: salida automática.

---

## 6. Reglas de Cuenta Fondeada (Prop Firm Compliance)
- **Riesgo por operación:** máximo 0.75% del trailing drawdown real. Ejemplo: $2,000 de DD → $150 de riesgo → con stop de 20 puntos en MNQ ($40/contrato), 3 contratos.
- **Máximo 2 operaciones por día**, y solo en días clasificados como de rango.
- **Tras un stop, no reentrar en el mismo lado de la banda ese día.**
- **Sin promediar ni ampliar stop.**
- **Cierre forzoso:** flat antes de las 15:55 ET.

---

## 7. Honestidad Estadística y Validación Pendiente
- El material fuente (publicación de un educador sobre bandas VWAP) no muestra precios, estadística ni resultados verificables. Su ejemplo ilustra un día de rango, sin cifras.
- La clasificación de régimen y los umbrales de agotamiento (80% de volumen, 2σ–3σ) son propios: deben validarse con datos de entrenamiento y comprobarse fuera de muestra.
- Las bandas VWAP son ponderadas por volumen; el cálculo debe reproducir exactamente la fórmula del software de referencia (diferencias en la desviación estándar cambian las bandas).
- Backtest con costos reales ($0.62/lado MNQ, $2.10/lado NQ) y slippage de 1–2 ticks en la reversión.
- Muestra mínima: ≥ 100 operaciones, con separación explícita de días de rango y de tendencia (el resultado global puede esconder pérdidas concentradas en días de tendencia).

---

## 8. Arquitectura NinjaTrader 8 (NinjaScript)
- Series: 5 min (bandas y régimen), 1 min (agotamiento y gatillo).
- VWAP y desviaciones calculados por sesión desde el ancla de 09:30 ET con volumen ponderado.
- Clasificación de régimen al cierre de la primera hora (10:30 ET) y registro antes de cualquier entrada.
- Estados: `Clasificar_Dia → Esperar_Estiramiento → Agotamiento_Confirmado → EnPosicion → Cerrado`.
- `SetStopLoss` y `SetProfitTarget` por precio tras la entrada.

---

## Referencias
- Ideas: [[VWAP_REVERSION_AGOTAMIENTO_01]]
- Fuentes y research:
  - Trader Profesional (José Luis Cases Lozano): VWAP bands y uso de desviaciones estándar.
  - FutureShive: VWAP trading strategy para ES y NQ (setup de fade en bandas exteriores en días de rango).
  - MyTradeEdge: VWAP trading en NQ y ES (fórmula, bandas y setups, con advertencia sobre tendencia).
  - jira/trading_agent_persona.md: Régimen de mercado, validación honesta y trailing drawdown.
