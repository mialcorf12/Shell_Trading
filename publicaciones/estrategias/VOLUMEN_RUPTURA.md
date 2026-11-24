# VOLUMEN_RUPTURA: Lectura de Rupturas por Cambio de Volumen en NQ/MNQ

## 1. Hipótesis Operativa
El volumen (contratos ejecutados por vela) no indica por sí solo la dirección. Lo informativo es **cómo cambia el volumen cuando el precio rompe un rango**. Una ruptura puede ser:

- **Aceptación:** rompe con volumen similar al del rango. El mercado acepta el nuevo valor y el precio tiende a sostenerse por encima (o debajo) del nivel roto.
- **Rechazo:** rompe pero el volumen cae. Participación insuficiente: el precio tiende a volver al rango, donde estaba el mayor negocio previo.
- **Iniciativa / agresión:** rompe con volumen que se dispara. Un lado tomó la iniciativa de forma explícita; el precio busca nuevo valor en la dirección de la ruptura.

El argumento de fondo: un contrato ejecutado no se puede retirar del tape (a diferencia de una orden en el libro), por lo que el volumen de ejecución es una confirmación del estado del precio. **No es una señal de entrada por sí solo**: la estrategia usa el volumen como filtro sobre una ruptura ya definida.

---

## 2. Parámetros de Mercado e Instrumentos
- **Contratos:** MNQ ($2.00/punto, $0.50/tick) para ejecución; NQ ($20.00/punto) solo con riesgo acotado al colchón de drawdown.
- **Sesión:** RTH (09:30–16:00 ET). Ventana preferida: 09:45–11:30 ET y 13:30–15:30 ET.
- **Temporalidades:**
  - Rango de referencia: 15 o 30 minutos (una definición fija para todo el backtest).
  - Lectura de volumen: 1 o 5 minutos.
- **Definición medible de volumen (elimina la ambigüedad del video):**
  - `VolRel = Volumen_vela_ruptura / SMA(Volumen, 20)` calculado sobre la temporalidad de lectura.
  - **Aceptación:** 0.8 ≤ VolRel ≤ 1.2.
  - **Rechazo:** VolRel < 0.8.
  - **Iniciativa:** VolRel > 1.5.
  - Umbrales iniciales; deben validarse en walk-forward (sección 7).

---

## 3. Reglas de Entrada

### Ruptura alcista con aceptación (largo):
1. El precio cierra con cuerpo completo por encima del máximo del rango (`RangeHigh`) en una vela de 5 min.
2. `VolRel` entre 0.8 y 1.2 en esa vela.
3. Entrada: compra a mercado al cierre de la siguiente vela de 5 min, si esta no cierra por debajo de `RangeHigh`.

### Ruptura alcista con iniciativa (largo, versión agresiva):
1. Cierre con cuerpo por encima de `RangeHigh` con `VolRel > 1.5`.
2. Entrada en el retesteo de `RangeHigh` (orden limit en `RangeHigh + 2 ticks`), sin perseguir el precio. Si no hay retesteo en 3 velas de 5 min, no entrar.

### Rechazo (no operar la ruptura; operar el retorno):
- Ruptura con `VolRel < 0.8`: no entrar en la ruptura. Si el precio vuelve al rango y cierra adentro, se puede operar la reentrada hacia el lado opuesto del rango, con stop más allá del extremo de la ruptura. Esta variante queda como **hipótesis secundaria**, sin validación previa.

Versiones bajistas: espejo sobre `RangeLow`.

---

## 4. Gestión de Riesgo y Salida

- **Hard Stop Loss (aceptación):** por debajo de `RangeHigh` (en largo), con 2 ticks de margen. Si la distancia excede 30 puntos NQ ($60 MNQ), no operar.
- **Take Profit:**
  - TP1 (50%): 1.0 × Amplitud del rango, proyectado desde `RangeHigh`.
  - TP2 (50%): 2.0 × Amplitud, o el siguiente nodo de alto volumen (HVN) superior.
- **Break Even:** al llenarse TP1, stop del resto a +2 ticks.
- **Invalidación:** cierre de vela de 5 min por debajo de `RangeHigh` tras la entrada: salida inmediata. Es la condición de "rechazo post-entrada".

---

## 5. Reglas de Cuenta Fondeada (Prop Firm Compliance)
- **Riesgo por operación:** máximo 0.75% del trailing drawdown real. Ejemplo: $2,000 de DD → $150 de riesgo → con stop de 25 puntos en MNQ ($50/contrato), 3 contratos.
- **Máximo 2 operaciones por sesión.** Tras dos stops, apagar la estrategia por el día.
- **Sin promediar ni ampliar stop.**
- **Cierre forzoso:** flat antes de las 15:55 ET.

---

## 6. Honestidad Estadística
- El video no entrega precios, timeframe, instrumento ni estadística. El ejemplo es un gráfico con datos simulados: el propio creador lo presenta como ilustración.
- Los umbrales de `VolRel` (0.8 / 1.5) son una operacionalización propia, no una cifra del autor.
- Sin backtest no hay expectativa: E = (acierto × ganancia) − (fallo × pérdida) − costos. Costos: $0.62/lado MNQ, $2.10/lado NQ, más 1–2 ticks de slippage en rupturas (el slippage en rupturas suele ser mayor que en un movimiento lento).

---

## 7. Validación Pendiente
- Backtest sobre ≥ 100 rupturas por variante (aceptación, iniciativa, rechazo) con costos reales.
- Walk-forward para los umbrales 0.8 / 1.2 / 1.5 y la amplitud mínima del rango.
- Reportar distribución por día; un solo día no debe concentrar la utilidad.

---

## 8. Arquitectura NinjaTrader 8 (NinjaScript)
- `Calculate.OnBarClose` sobre 5 minutos; serie secundaria de 15 minutos para el rango.
- Cálculo de `VolRel` con `SMA(Volume, 20)`; estado `Rango_Definido → Ruptura_Detectada → Clasificada → EnPosicion → Cerrado`.
- Órdenes con `SetStopLoss` y `SetProfitTarget` por precio, colocadas al entrar.

---

## Referencias
- Ideas: [[VOLUMEN_RUPTURA_01]]
- Fuentes y research:
  - Publicación de origen (@thenqdog): lectura del volumen en rupturas (contenido educativo, sin estadística).
  - jira/trading_agent_persona.md: Hipótesis antes que código, validación honesta y trailing drawdown.
