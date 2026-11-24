# ORB_MULTI_SESSION: Ruptura de Rango de Apertura Multi-Sesión en NQ/MNQ

## 1. Hipótesis Operativa y Fundamento Cuantitativo
El principio del Opening Range Breakout (ORB) asume que el flujo de órdenes inicial de una sesión institucional establece los límites de valor temporal (`ORH` y `ORL`). La ruptura de uno de esos extremos respaldada por volumen señala la dirección dominante para el resto de la ventana operativa.
A diferencia de los enfoques minoristas que operan ciegamente cualquier horario, el mercado de futuros de Nasdaq (NQ/MNQ) opera en regímenes de liquidez claramente diferenciados:

1. **Sesión Europea / Apertura de Londres (03:00–03:15 ET):**
   - Inyección de liquidez de bancos europeos y fondos de Londres.
   - Datos estadísticos históricos (2.800+ días de NQ): en el **98.4% de las sesiones**, el máximo o mínimo establecido durante Londres es testeado o quebrado durante la sesión de Nueva York. El ORB de Londres (03:00–03:15 ET) captura la dirección que buscará liquidez antes del contado de EE.UU.
2. **Ventana Pre-Market de EE.UU. (09:15–09:30 ET):**
   - Transición crítica posterior a los datos macro de las 08:30 ET (CPI, NFP, PPI) y anterior al campanazo de Wall Street. Un quiebre limpio de esta ventana suele marcar el sesgo direccional con el que abrirá el contado.
3. **Apertura Regular de Contado RTH (09:30–09:45 ET):**
   - El volumen institucional máximo del día. Máxima expansión de rango pero también mayor probabilidad de trampas y whipsaws.

---

## 2. Parámetros de Mercado y Especificaciones
- **Contratos:**
  - `MNQ` (Micro E-mini): $2/punto ($0.50/tick). **Mandatorio para sesiones overnight (Londres)** donde la profundidad del libro de órdenes (DOM) es menor y la tolerancia a slippage es crítica.
  - `NQ` (E-mini): $20/punto ($5.00/tick). Solo aplicable en RTH (09:30+) y con cuentas que cuenten con un colchón holgado de drawdown.
- **Ventanas de Rango y Operación:**
  - **Ventana Londres:** Rango definido de 03:00 a 03:15 ET. Operaciones permitidas hasta las 06:00 ET.
  - **Ventana Pre-Market:** Rango definido de 09:15 a 09:30 ET. Operaciones permitidas de 09:30 a 10:15 ET (con estricto filtro de noticias macro).
  - **Ventana RTH NY:** Rango definido de 09:30 a 09:45 ET. Operaciones permitidas de 09:45 a 11:30 ET.
- **Temporalidad:** 5 minutos para definición de rango y gatillo de confirmación (cierre de barra).

---

## 3. Reglas Mecánicas de Entrada

### Paso 1: Bloqueo del Rango (Range Freeze)
- Al completar los 15 minutos de la ventana seleccionada, registrar `ORH` (máximo más alto) y `ORL` (mínimo más bajo).
- **Filtro de volatilidad:** La amplitud `Amplitud = ORH - ORL` debe cumplir:
  - Londres: Entre 25 y 65 puntos NQ.
  - RTH / Pre-market: Entre 40 y 110 puntos NQ.
  - Si la amplitud excede el límite superior, el mercado está sobre-extendido; se cancela la operativa de la sesión.

### Paso 2: Filtro de Noticias Macro (Obligatorio)
- Si a las 08:30 ET se publican eventos Tier-1 (CPI, PPI, NFP, Retail Sales), la ventana Pre-Market (09:15–09:30) queda **completamente inhabilitada**. No se emiten órdenes antes de las 09:45 ET.

### Paso 3: Gatillo de Ruptura (Breakout Trigger)
- **Largo (ORB Long):**
  - Una vela de 5 minutos cierra con su **cuerpo completo por encima de ORH**.
  - **Filtro de volumen:** El volumen de la vela de ruptura debe ser superior a la media de 20 períodos de volumen en 5M (`Volume > SMA(Volume, 20)`).
  - Entrada: Orden `Stop-Market` o `Market` en la apertura de la siguiente vela tras el cierre confirmado.
- **Corto (ORB Short):**
  - Cierre de vela de 5 min con cuerpo completo por debajo de `ORL` con volumen superior a la media de 20 períodos.

---

## 4. Gestión de Riesgo y Salidas

- **Hard Stop Loss:**
  - Opción A (Mecánica Estricta): En el **punto medio del rango** (`Midpoint = (ORH + ORL) / 2`). Reduce el riesgo a la mitad de la amplitud del rango.
  - Opción B (Estructural): 2 ticks por debajo del mínimo de la vela de ruptura (para largos) o 2 ticks por encima del máximo de la vela de ruptura (para cortos).
  - Stop Máximo Permitido: 35 puntos en Londres; 45 puntos en RTH.
- **Take Profit (Múltiplos de Rango):**
  - **TP1 (60% de la posición):** Proyección de `1.0 × Amplitud` a partir del nivel de ruptura (`ORH + Amplitud`). Al alcanzar TP1, mover el stop loss del 40% restante a Break Even (+2 ticks).
  - **TP2 (40% de la posición):** Proyección de `2.0 × Amplitud` o nivel de liquidez previo (máximo/mínimo de la sesión anterior).
- **Invalidación por Tiempo:**
  - Si transcurren 6 barras de 5 minutos (30 minutos) sin que el precio alcance TP1 ni el Stop, y el precio reingresa al rango original, liquidar posición a mercado (falla de momento).

---

## 5. Reglas de Cuenta Fondeada (Prop Firm Compliance)
- **Restricción Overnight y Horarios de Flat:**
  - Toda posición abierta en sesión Londres **debe cerrarse obligatoriamente antes de las 08:15 ET** (antes de la apertura de noticias macro de NY).
  - Toda posición en RTH debe liquidarse antes de las 15:55 ET. Prohibido mantener contratos durante el cierre diario de CME (16:59–18:00 ET).
- **Control de Drawdown:**
  - Máximo 1 trade ganador o perdedor por ventana horaria.
  - Límite de pérdida por trade: no superior al **1.0% del colchón de trailing drawdown** (máximo $200 de riesgo en cuenta de $50k con $2k de DD). Con un stop de 40 puntos en MNQ ($80 de riesgo por contrato), el tamaño máximo es de 2 contratos MNQ.
- **Adversidad a la Sobre-optimización:**
  - Los backtests sin comisiones ni slippage son ficticios. En NinjaTrader 8 se deben configurar comisiones de $0.62 por lado en MNQ / $2.10 en NQ más 1 a 2 ticks de slippage real en órdenes de mercado.

---

## 6. Arquitectura NinjaTrader 8 (NinjaScript)
- Uso de `Calculate.OnBarClose` en gráfico de 5 minutos.
- Propiedades parametrizables con `[NinjaScriptProperty]`:
  - `SessionStartHour`, `SessionStartMinute` (03:00, 09:15, 09:30).
  - `RangeDurationMinutes` (15 por defecto).
  - `StopMode` (Midpoint vs BreakoutBarExtreme).
  - `ProfitMultiplier` (1.0 y 2.0).
- Máquina de estados: `State.Historical` para warm-up de SMA(Volume, 20), `ExecutionStage.WaitingForRange`, `ExecutionStage.Armado`, `ExecutionStage.InTrade`.

---

## Referencias
- Ideas: [[ORB_MULTI_SESSION_01]]
- Fuentes y research:
  - TradingStats Research: London Breakout Strategy (2,839 Days of NQ Data).
  - TradeTerminal: Futures Opening Range Breakout Framework.
  - CME Group: E-mini & Micro E-mini Nasdaq-100 Liquidity Hours.
  - jira/trading_agent_persona.md: Reglas de disciplina y protección de cuentas de evaluación.
