# TOP_DOWN_SMC_OB_4PASOS: Método Top-Down de Cuatro Pasos (Diario → 4H → 1H → 15 min) con Order Block en NQ/MNQ

## 1. Hipótesis Operativa
Un método multi-temporalidad que parte del sesgo diario y baja hasta una entrada de 15 minutos, con cuatro filtros en orden. Cada filtro restringe al siguiente: sin sesgo diario no hay operación; sin barrido de 4H no hay zona; sin order block de 1H no hay entrada.

1. **Diario:** sesgo direccional de las últimas 2–3 velas.
2. **4H:** barrido de liquidez de la vela de 4 horas previa, en el sentido del sesgo.
3. **1H:** order block (OB) formado tras el barrido.
4. **15 min:** cambio de estructura (MSS) dentro del OB, con entrada desde la zona de descuento (alcista) o premium (bajista).

La lógica: el barrido de 4H es la trampa que atrae liquidez en contra del movimiento, y el OB de 1H es el lugar desde el que el precio realmente se mueve. El 15 min da la entrada precisa.

---

## 2. Definiciones Medibles
- **Sesgo diario alcista:** las últimas 2 o 3 velas diarias forman un patrón de continuación alcista (cierres por encima del rango previo). Patrón de consolidación (rango lateral de 3 velas sin cierre fuera de su rango): sin sesgo, sin operación.
- **Barrido de 4H:** en alcista, mecha que supera el mínimo de la vela 4H previa y cierre de vuelta por encima. En bajista, espejo.
- **Order block de 1H:** la última vela de compra (en alcista) antes del impulso que sigue al barrido. Su rango (apertura–mínimo) es la zona. Definición de vela de compra: cuerpo alcista, cuerpo ≥ 50% del rango.
- **Vela cementada (definición propia):** vela de 15 min que cierra con cuerpo completo más allá del swing de MSS, dentro de la zona del OB.
- **Premium / descuento:** dividir el movimiento de referencia en 50%. Por debajo del 50% es descuento (zona de compra en alcista); por encima es premium (zona de venta en bajista).

El video no define "vela cementada" ni el parámetro de la caja de Gann; las definiciones de esta sección son propias.

---

## 3. Parámetros de Mercado e Instrumentos
- **Contratos:** MNQ ($2.00/punto) para ejecución; NQ ($20.00/punto) con riesgo acotado al colchón de drawdown.
- **Instrumento:** NQ/MNQ (el método se presenta para varios pares; esta versión lo limita al Nasdaq, de acuerdo con la persona).
- **Sesión:** RTH (09:30–16:00 ET). Ventana preferida: 09:45–12:00 ET.
- **Temporalidades:** diario (sesgo), 4H (barrido), 1H (OB), 15 min (MSS y entrada).

---

## 4. Reglas de Entrada (sesgo alcista; espejo para bajista)

1. **Paso 1 (diario):** sesgo alcista confirmado por las últimas 2–3 velas. Si no hay sesgo, no operar el día.
2. **Paso 2 (4H):** barrido del mínimo de la vela 4H previa, con cierre de vuelta por encima. El cierre debe ser de cuerpo, no de mecha.
3. **Paso 3 (1H):** identificar el OB alcista formado tras el barrido (sección 2). La zona del OB es el rango de esa vela.
4. **Paso 4 (15 min):** esperar que el precio entre en la zona del OB y que se produzca un MSS alcista: un cierre de vela de 15 min que supera el último swing high de 15 min dentro de la zona.
5. **Entrada:** compra en la zona de descuento del movimiento de referencia (por debajo del 50%), al cierre de la vela cementada de 15 min, o en retesteo del OB.

**Restricción:** solo operar los días y los pares que el método define como válidos. En NQ/MNQ, aplicar el filtro de sesgo diario en cada sesión.

---

## 5. Gestión de Riesgo y Salida
- **Hard Stop Loss:** por debajo del mínimo del barrido de 4H (alcista), con 2 ticks de margen. Máximo 35 puntos NQ ($70 MNQ). El video sitúa el stop justo por encima del máximo barrido en bajista; el espejo se aplica en alcista. La distancia máxima es propia.
- **Take Profit:**
  - TP1 (50%): en el mínimo reciente de 15 min, en el lado opuesto del barrido (máximo previo de 15 min en alcista).
  - TP2 (50%): en el mínimo de 1H de la estructura. Ratio mínimo 1:2 sobre el stop. Si el TP2 está a menos de 2 R, no operar (el video menciona 1:3 o 1:2 según el par; se toma 1:2 como mínimo).
- **Break Even:** al llenarse TP1, stop del resto a +2 ticks.
- **Invalidación:** cierre de vela de 15 min por debajo del mínimo del barrido de 4H antes de TP1: salida inmediata.

---

## 6. Reglas de Cuenta Fondeada (Prop Firm Compliance)
- **Riesgo por operación:** máximo 0.75% del trailing drawdown real. Ejemplo: $2,000 de DD → $150 de riesgo → con stop de 25 puntos en MNQ ($50/contrato), 3 contratos.
- **Máximo 1 operación por día** (el método no está pensado para múltiples entradas).
- **Sin promediar ni ampliar stop.**
- **Cierre forzoso:** flat antes de las 15:55 ET.

---

## 7. Honestidad Estadística y Validación Pendiente
- El material fuente es una publicación educativa con un ejemplo en BTC/USD (no NQ) y un enlace de cierre a una promoción de cuentas fondeadas. El ejemplo está fechado el 09/09/26 (futuro): el video no es verificable.
- Las ilustraciones son esquemáticas y podrían ser generadas. No hay precios, estadística ni expectativa.
- Hay tres conceptos sin definición en el original ("vela cementada", caja de Gann, sesgo diario) que aquí se definen por cuenta propia. La definición afecta mucho los resultados: deben validarse.
- Backtest con costos reales ($0.62/lado MNQ, $2.10/lado NQ) y slippage de 1–2 ticks.
- Walk-forward para las definiciones de OB y de vela cementada. Muestra mínima: ≥ 100 operaciones. Como el método limita a 1 operación diaria, la muestra requiere varios años de datos.

---

## 8. Arquitectura NinjaTrader 8 (NinjaScript)
- Series: diaria (sesgo), 4 h (barrido), 1 h (OB), 15 min (MSS y entrada).
- Sesgo diario calculado en la apertura; barrido y OB detectados con la serie de 1 h al cierre de la vela 4h.
- Máquina de estados: `Sesgo_Diario → Barrido_4h → OB_1h_Marcado → MSS_15m → EnPosicion → Cerrado`.
- `SetStopLoss` y `SetProfitTarget` por precio tras la entrada.

---

## Referencias
- Ideas: [[TOP_DOWN_SMC_OB_4PASOS_01]]
- Fuentes y research:
  - Publicación de origen (@mstraderjh, caption con crédito a @bearishharry): método top-down SMC/ICT en 4 pasos (educativo, con ejemplo en BTC/USD).
  - Concepto de premium y descuento (50% del movimiento de referencia): marco de SMC/ICT.
  - jira/trading_agent_persona.md: Hipótesis antes que código, validación y trailing drawdown.
