# FVG_TERCERA_VELA: Clasificación de FVG por el Comportamiento de la Tercera Vela en NQ/MNQ

## 1. Hipótesis Operativa
Un Fair Value Gap (FVG) de tres velas se define por la vela 1 (base), la vela 2 (desplazamiento, la que genera el hueco) y la vela 3 (confirmación). La mayoría de operadores marca el FVG y espera el retesteo sin evaluar la vela 3, que es la que cierra el hueco y revela la intención de la contraparte.

La hipótesis: **el cierre de la vela 3 respecto a la vela 2 clasifica el FVG en tres tipos con probabilidad de llenado y de continuación distintas.**

- **Tipo 1 · Consolidación (alta probabilidad de retesteo):** la vela 3 es de cuerpo pequeño. No hay agresión inmediata; el precio tiende a volver a llenar el gap antes de continuar. Se opera el retesteo.
- **Tipo 2 · Escape / Breakaway Gap (BAG):** la vela 3 cierra por encima del máximo de la vela 2 con fuerza. El gap suele quedar sin llenar durante varias velas. No se espera retroceso: se busca un FVG en una temporalidad menor dentro del mismo movimiento.
- **Tipo 3 · Rechazo (baja probabilidad):** la vela 3 sube pero cierra dentro del cuerpo o cerca de la vela 2, con mecha superior grande. Indica vendedores activos. Si el precio regresa al gap, tiende a fallar; el FVG se considera débil y no se opera.

El nombre de estrategia es `FVG_TERCERA_VELA`. Se aplica a FVG alcistas y bajistas (espejo).

---

## 2. Parámetros de Mercado e Instrumentos
- **Contratos:** MNQ ($2.00/punto, $0.50/tick) para ejecución; NQ ($20.00/punto, $5.00/tick) solo con riesgo por operación acotado al colchón de drawdown.
- **Sesión:** RTH (09:30–16:00 ET). Ventana preferida: 09:45–11:30 ET y 13:30–15:30 ET.
- **Temporalidades:**
  - Contexto (FVG origen): 15 min o 60 min.
  - Ejecución: 1 min (entrada) y 3 min (confirmación de estructura).
- **Tamaño mínimo del FVG:** 8 puntos en NQ. Por debajo, el hueco es ruido de tick.

---

## 3. Definiciones Medibles (para eliminar la ambigüedad del concepto)
Para que la clasificación sea reproducible, se fijan umbrales:
- **Cuerpo pequeño (Tipo 1):** cuerpo de la vela 3 ≤ 35% del rango total de la vela 3 Y cuerpo ≤ 0.5 × cuerpo de la vela 2.
- **Escape (Tipo 2):** cierre de la vela 3 > máximo de la vela 2, con cuerpo de la vela 3 ≥ 60% de su rango.
- **Rechazo (Tipo 3):** cierre de la vela 3 dentro del rango de cuerpo de la vela 2 (≤ punto medio de la vela 2) O mecha superior de la vela 3 ≥ 50% de su rango total.
- Si ninguna condición se cumple, el FVG no se clasifica y no se opera.

---

## 4. Reglas de Entrada

### Tipo 1 (Consolidación) — Retesteo:
1. El FVG alcista queda sin mitigar tras la vela 3.
2. Esperar que el precio retroceda al FVG y lo toque.
3. Gatillo: vela de 1 min que toca el límite superior del FVG o su 50% (Consequent Encroachment) y cierra alcista.
4. Entrada: compra al cierre de la vela de gatillo.

### Tipo 2 (Escape / BAG) — No esperar retroceso:
1. Tras el BAG, buscar un FVG alcista de 3 min o 5 min dentro del mismo impulso.
2. Entrada: compra en el retesteo del FVG de menor temporalidad, o a mercado si el precio no retrocede en 5 velas de 1 min y cierra con cuerpo sobre el máximo de la vela 2 del BAG.

### Tipo 3 (Rechazo) — No operar:
- Se marca el FVG como débil. No se toma entrada. Si el precio cierra con cuerpo bajo el mínimo de la vela 1 en el futuro, el FVG se invalida.

(Versión bajista espejo: vela 3 de cuerpo pequeño, cierre bajo el mínimo de la vela 2 o mecha inferior dominante.)

---

## 5. Gestión de Riesgo y Salida

- **Hard Stop Loss:**
  - Tipo 1: 2 ticks por debajo de la base del FVG (vela 1).
  - Tipo 2: por debajo del mínimo de la vela 2 del BAG.
  - Stop máximo: 30 puntos NQ ($60 en MNQ). Si la distancia lo excede, la operación se descarta.
- **Take Profit:**
  - Tipo 1: TP1 en el máximo del impulso (60% de la posición); TP2 en el siguiente nivel de liquidez de 15 min (40%). Ratio mínimo 1:2.
  - Tipo 2: TP1 en la proyección de 1.0 × el rango de la vela 2; TP2 en 2.0 × o en el siguiente FVG de temporalidad mayor.
- **Break Even:** al llenarse TP1, mover el stop del resto a +2 ticks.
- **Invalidación:** cierre de vela de 3 min con cuerpo completo bajo el mínimo de la vela 1 invalida cualquier hipótesis alcista sobre ese FVG.

---

## 6. Reglas de Cuenta Fondeada (Prop Firm Compliance)
- **Riesgo por operación:** máximo 0.75% del trailing drawdown real. Ejemplo: $2,000 de DD → $150 de riesgo → con stop de 25 puntos en MNQ ($50/contrato), 3 contratos.
- **Límite diario:** máximo 2 operaciones perdedoras por sesión; al tocar la segunda, el setup queda apagado por el día.
- **Sin promediar:** prohibido agregar contratos a una posición en pérdida.
- **Cierre forzoso:** flat antes de las 15:55 ET.

---

## 7. Validación Pendiente (antes de cualquier uso en vivo)
- Backtest con costos reales: $0.62 por lado en MNQ / $2.10 en NQ, más 1–2 ticks de slippage en órdenes de mercado.
- Validación fuera de muestra (walk-forward): los umbrales de la sección 3 deben fijarse con datos de entrenamiento y comprobarse en un periodo posterior.
- Reportar: número de operaciones por tipo (meta ≥ 100 operaciones), drawdown máximo y distribución de resultados por día (evitar que un solo día concentre la utilidad).

---

## 8. Arquitectura NinjaTrader 8 (NinjaScript)
- `Calculate.OnBarClose` sobre 1 min; series secundarias de 3 y 15 min.
- Clasificación en `OnBarUpdate` en función de cuerpos y mechas de las tres últimas velas (ver umbrales de la sección 3).
- Máquina de estados: `Flat → FVG_Detectado → Clasificado → EsperandoRetesteo → EnPosicion → Cerrado`.
- Órdenes con `SetStopLoss` y `SetProfitTarget` por `CalculationMode.Price`, tras la entrada (nunca posiciones sin stop).

---

## Referencias
- Ideas: [[FVG_TERCERA_VELA_01]]
- Ideas: [[FVG_TERCERA_VELA_02]]
- Ideas: [[FVG_TERCERA_VELA_03]]
- Fuentes y research:
  - Alchemy Markets: Fair Value Gap trading guide (rejection FVG y reglas de entrada).
  - The Right Trader: Fair Value Gap pattern (entrada, stop y objetivo).
  - ICT Traders: ICT Breakaway Gap concept (BAG como gap no mitigado en movimiento agresivo).
  - jira/trading_agent_persona.md: Reglas de trailing drawdown, backtesting honesto y estándares NinjaScript.
