# ORB_STOP_MEDIO_RANGO_1R: Ruptura Mecánica de ORB con Stop al Punto Medio y Objetivo 1R en NQ/MNQ

## 1. Hipótesis Operativa y Fundamento Cuantitativo
En instrumentos de alta volatilidad como el Nasdaq-100 (NQ/MNQ), colocar el Stop Loss en el extremo opuesto del rango de apertura (Full-Range Stop) impone un riesgo excesivo por contrato (frecuentemente 60–100 puntos), lo que destruye el ratio beneficio/riesgo y viola las reglas de trailing drawdown de las firmas de fondeo.

- **El Punto Medio como Frontera de Invalidez:**
  El punto medio (`Midpoint = (ORH + ORL) / 2`) representa el precio de equilibrio del subastador durante la primera ventana de RTH. Si una ruptura es genuina y tiene convicción institucional, el precio no debe reingresar y cruzar el 50% del rango.
- **Evidencia Cuantitativa (Estudio de 3.884 sesiones de NQ):**
  Ajustar el stop loss al punto medio reduce el riesgo monetario promedio por operación en aproximadamente un **50%**, permitiendo un dimensionamiento de contratos el doble de eficiente sin degradar los puntos netos obtenidos a largo plazo.
- **La Lógica de 1R:**
  Para compensar la tasa de acierto típica de las rupturas (~45–55%), un objetivo fijo de 1R (distancia exacta entre el precio de entrada y el midpoint) garantiza una salida rápida antes de que aparezcan retrocesos bruscos en la sesión de la mañana, logrando curvas de capital suaves compatibles con las reglas de consistencia de prop firms.

---

## 2. Parámetros de Mercado y Especificaciones
- **Contratos:** MNQ ($2.00/punto) como instrumento base; NQ ($20.00/punto) solo si la distancia de riesgo por contrato no excede el 0.75% del trailing drawdown.
- **Sesión y Horario:** RTH (Regular Trading Hours de EE.UU.).
  - Definición del rango: **09:30:00 a 09:45:00 ET** (ORB 15M).
  - Ventana de disparo permitida: **09:45:01 a 10:30:00 ET**. Órdenes canceladas después de las 10:30 ET.
- **Filtro de Amplitud de Rango (Range Width Filter):**
  - Amplitud mínima: 35 puntos NQ (evita rangos muertos o días de feriado bancario).
  - Amplitud máxima: 90 puntos NQ. Si el rango de 15 minutos supera los 90 puntos, la volatilidad de apertura es extrema y el riesgo al midpoint sigue siendo demasiado amplio; el trade queda cancelado.

---

## 3. Reglas de Entrada Mecánicas

### Configuración Larga (Long Breakout):
1. A las 09:45:00 ET, calcular y registrar:
   - `ORH` = Precio máximo de 09:30 a 09:45 ET.
   - `ORL` = Precio mínimo de 09:30 a 09:45 ET.
   - `Midpoint = (ORH + ORL) / 2`.
2. **Confirmación de Ruptura:** Una vela de 5 minutos (o vela de 1 minuto para operadores agresivos) cierra con su **cuerpo completo por encima de ORH**.
3. **Entrada:** Orden `Market` o `Limit` en `ORH` en el retesteo inmediato, disparada en la apertura de la siguiente barra tras el cierre confirmado.

### Configuración Corta (Short Breakout):
1. Calcular los mismos niveles.
2. Una vela cierra con su **cuerpo completo por debajo de ORL**.
3. Entrada a la apertura de la siguiente barra.

---

## 4. Gestión de Riesgo y Salidas Estrictas

- **Hard Stop Loss:**
  - Situado en el nivel exacto del `Midpoint` (más 1 tick de resguardo).
  - Distancia de Riesgo: `R = Precio_Entrada - Midpoint`.
  - En ningún caso el Stop superará los 45 puntos en NQ ($90 en MNQ).
- **Take Profit (1R y Runner Opcional):**
  - **Objetivo 1R Primario (70% de la posición):** `Precio_Entrada + R` (para largos) o `Precio_Entrada - R` (para cortos).
  - Al llenarse el 1R, el stop del 30% restante se mueve inmediatamente a **Break Even (+2 ticks)** para asegurar comisiones cubiertas.
  - **Objetivo Runner (30% de la posición):** Proyección a 2R o liquidación automática a las 11:30 ET.
- **Invalidez por Tiempo:**
  - Si el trade no alcanza 1R dentro de los 45 minutos posteriores a la entrada, y el precio oscila cerca del precio de apertura, cerrar a mercado antes de las 11:30 ET.

---

## 5. Reglas de Cuenta Fondeada (Prop Firm Compliance)
- **Cálculo de Posición sobre Drawdown Real:**
  - Regla: Riesgo monetario total por trade ≤ **1.0% del drawdown disponible**.
  - Ejemplo: Cuenta $50K Topstep/Apex con trailing drawdown de $2,000.
    - Riesgo máximo permitido = $150–$200.
    - Si el riesgo al midpoint son 30 puntos en NQ = $60 por contrato en MNQ.
    - Número de contratos = 3 contratos MNQ ($180 de riesgo total).
- **Protección contra Regla de Consistencia:**
  - Muchas firmas (Tradeify, Lucid, etc.) prohíben que un solo día represente más del 40% del objetivo total de ganancias. Al tomar beneficios parciales a 1R y 2R en lugar de buscar "home runs" de 5R descontrolados, la estrategia mantiene una distribución de beneficios estable y consistente.
- **Límite Diario de Pérdidas:** Máximo 1 pérdida por día. Un stop en el midpoint apaga el robot hasta el día siguiente.

---

## 6. Arquitectura NinjaTrader 8 (NinjaScript)
- Cálculo en `Calculate.OnBarClose` sobre 5 minutos.
- Estructura de órdenes con OCO (One-Cancels-Other):
  ```csharp
  // Long entry
  EnterLong(Convert.ToInt32(DefaultQuantity), "ORB_Long");
  SetStopLoss("ORB_Long", CalculationMode.Price, midpointPrice, false);
  SetProfitTarget("ORB_Long", CalculationMode.Price, entryPrice + (entryPrice - midpointPrice), false);
  ```

---

## Referencias
- Ideas: [[ORB_STOP_MEDIO_RANGO_1R_01]]
- Fuentes y research:
  - Loomi.Ai Research: ORB Stop Loss Placement: Midpoint vs Full Range (3,884 NQ Sessions).
  - STS4x Learn: NQ Opening Range Breakout Entry, Midpoint Stop, and Take Profit Rules.
  - jira/trading_agent_persona.md: Gestión de trailing drawdown y contratos de futuros NQ/MNQ.
