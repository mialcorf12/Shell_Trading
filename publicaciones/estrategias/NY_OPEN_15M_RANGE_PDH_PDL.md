# NY_OPEN_15M_RANGE_PDH_PDL: Ruptura y Retesteo del Rango 15M con Objetivo en PDH/PDL en NQ/MNQ

## 1. Hipótesis Operativa y Fundamento de Liquidez
El máximo del día anterior (`PDH`) y el mínimo del día anterior (`PDL`) son los dos niveles de referencia de liquidez externa más respetados por los algoritmos institucionales en los índices estadounidenses (NQ/ES). Alrededor de `PDH` se acumulan órdenes de compra de stop (Buy Stops) de operadores bajistas y al alza; alrededor de `PDL` se concentran Sell Stops.

- **La Ruptura con Retesteo (Break & Retest):**
  La primera vela de 15 minutos tras la campana de apertura (09:30–09:45 ET) absorbe el choque inicial entre el contado y Globex. Las rupturas directas de este primer rango frecuentemente sufren latigazos. Esperar que el precio rompa, retroceda a la zona del rango (`ORH` o `ORL`) y demuestre rechazo (respeto del nivel como soporte/resistencia) confirma la aceptación del mercado hacia el objetivo de liquidez del día anterior (`PDH` o `PDL`).

---

## 2. Parámetros de Mercado e Instrumentos
- **Instrumento Principal:** MNQ ($2.00/punto) para cuentas prop firm; NQ ($20.00/punto) solo si el stop loss en puntos no excede el presupuesto de riesgo de la cuenta.
- **Sesión Operativa:** RTH (Regular Trading Hours de Nueva York), ventana activa de 09:45 ET a 11:30 ET.
- **Niveles Previos:**
  - `PDH` = Máximo de la sesión regular/diaria anterior (CME Globex settlement del día previo).
  - `PDL` = Mínimo de la sesión regular/diaria anterior.
- **Temporalidades:**
  - `15 Minutos`: Definición del rango inicial de apertura `[ORL_15M, ORH_15M]`.
  - `1 a 3 Minutos`: Detección del retesteo y vela gatillo de rechazo.

---

## 3. Filtros Previos Obligatorios (Pre-Trade Checks)
1. **Filtro de Ubicación del Rango:**
   - Para buscar Largos hacia `PDH`: El rango de apertura debe formarse **por debajo de PDH**. Si el mercado abrió con un gap por encima de `PDH`, el objetivo ya fue consumido; el setup alcista queda **cancelado**.
   - Para buscar Cortos hacia `PDL`: El rango de apertura debe formarse **por encima de PDL**.
2. **Filtro de Ratio Beneficio/Riesgo Espacial:**
   - Distancia al Objetivo: La distancia desde `ORH_15M` hasta `PDH` debe ser al menos **1.5 veces el tamaño del Stop Loss estimado** (mínimo 40–50 puntos de recorrido libre). Si `PDH` está a solo 15 puntos por encima del rango, el espacio es insuficiente y el trade se ignora.

---

## 4. Reglas Mecánicas de Entrada

### Configuración Larga (Retest hacia PDH):
1. A las 09:45:00 ET, fijar `ORH_15M` y `ORL_15M`.
2. **Ruptura Inicial:** Entre las 09:45 y las 10:15 ET, una vela de 1M o 3M cierra con su cuerpo por encima de `ORH_15M`.
3. **El Retesteo:** El precio corrige hacia la zona de `ORH_15M` (permite penetración de hasta 3–5 puntos por debajo del nivel).
4. **Gatillo de Rechazo:**
   - Una vela de 1M o 3M toca `ORH_15M`, rechaza con mecha inferior prominente y **cierra con cuerpo verde alcista por encima de ORH_15M**.
   - Entrada: Compra a mercado al cierre de la vela de rechazo.

### Configuración Corta (Retest hacia PDL):
1. Ruptura bajista de `ORL_15M`.
2. Retesteo alcista hacia `ORL_15M`.
3. Vela de rechazo con mecha superior que cierra con cuerpo bajista por debajo de `ORL_15M`. Entrada en venta corta.

---

## 5. Gestión de Riesgo y Salida (Hard Rules)

- **Hard Stop Loss:**
  - Colocado 2 ticks por debajo del mínimo de la vela de retesteo (para largos) o por encima del máximo de la vela de retesteo (para cortos).
  - Límite máximo de stop: **35 puntos NQ** ($70 en MNQ). Si la mecha del retesteo exige más de 35 puntos, no se toma la operación.
- **Take Profit:**
  - **TP1 (70% de la posición):** 2 puntos por debajo de `PDH` (para asegurar llenado ante órdenes pasivas front-running). Al llenarse TP1, mover stop a Break Even (+2 ticks).
  - **TP2 (30% restante):** Liquidación por trailing o al superar `PDH` en 15 puntos (extensión de barrido de liquidez).
- **Time Stop:** Toda posición abierta se liquida a más tardar a las 11:45 ET. Si el precio no llegó a `PDH` tras 60 minutos de posición abierta y pierde el VWAP de la sesión, cerrar a mercado.

---

## 6. Reglas de Cuenta Fondeada (Prop Firm Compliance)
- **Riesgo Máximo por Trade:** Limitado al **0.75% a 1.0% del colchón de trailing drawdown** disponible.
  - Cuenta con $2,000 de trailing DD → Riesgo máximo $150. Con stop de 30 puntos en MNQ ($60/cto), operar 2 contratos MNQ ($120 de riesgo real).
- **Prohibición de Promediar (No Martingale):** Prohibido agregar contratos a una posición en pérdida o reentrar inmediatamente si el retesteo es perforado.
- **Límite Diario:** 1 trade perdedor detiene la operativa de esta estrategia por el resto de la sesión.

---

## 7. Arquitectura NinjaTrader 8 (NinjaScript)
- Uso de `BarsInProgress` para leer la serie de 15M y la serie primaria de 1M.
- Propiedades públicas: `MinDistanceToTargetPoints`, `MaxStopPoints`, `TrailAtBreakeven`.
- Declaración de niveles mediante `PriorDayOHLC` disponible en NinjaTrader core para derivar con exactitud matemática `PDH` y `PDL`.

---

## Referencias
- Ideas: [[NY_OPEN_15M_RANGE_PDH_PDL_01]]
- Fuentes y research:
  - SecondBell Research: Opening Range, PDH/PDL and Retest Framework.
  - Jeremy Hsu: Project Kintoun Regime-Filtered ORB Strategy.
  - jira/trading_agent_persona.md: Estándares de ingeniería NinjaScript y mitigación de trailing drawdown.
