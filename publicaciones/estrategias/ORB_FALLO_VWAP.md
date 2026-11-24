# ORB_FALLO_VWAP: Fallo del Rango de Apertura y Reclamación de VWAP en NQ/MNQ

## 1. Hipótesis Operativa y Fundamento de Mercado
El 9:30 AM ET (apertura del contado en EE.UU.) concentra una inyección masiva de volumen institucional que enfrenta el inventario acumulado durante la sesión overnight de Globex con el flujo de órdenes del mercado al contado.
En los primeros 15 minutos (9:30–9:45 ET), el mercado establece el Rango de Apertura (Opening Range, ORB 15M: `ORH` y `ORL`).
- **Comportamiento del retail:** Los operadores de ruptura agresivos entran en el quiebre de `ORL` (o `ORH`), colocando sus stops por encima del rango o de la vela de quiebre.
- **La trampa de liquidez:** Estudios empíricos en índices de futuros (ES/NQ) demuestran que más del 50–60% de las rupturas tempranas de los primeros 10–15 minutos fallan en expandirse y reingresan al rango dentro de los siguientes 5 a 10 minutos. Los creadores de mercado y algoritmos barren la liquidez de venta por debajo de `ORL` para llenar órdenes de compra institucionales.
- **La confirmación (Reclaim):** La reentrada al rango no basta por sí sola (puede ser consolidación pre-ruptura). La señal inequívoca de aceptación compradora ocurre cuando una vela de 1 minuto cierra con cuerpo pleno por encima del **VWAP anclado a la apertura de NY (9:30 ET)**, demostrando que los compradores tienen el control del precio promedio ponderado por volumen de la sesión contado.

---

## 2. Parámetros de Mercado e Instrumentos
- **Instrumentos preferidos:** MNQ (Micro E-mini Nasdaq-100) para cuentas de evaluación y dimensionamiento granular ($2.00/punto, $0.50/tick); NQ ($20.00/punto, $5.00/tick) únicamente cuando el colchón de trailing drawdown supere 4× el riesgo del trade.
- **Sesión operativa:** RTH (Regular Trading Hours), ventana de ejecución de 9:45 ET a 10:45 ET. No se abren nuevas posiciones después de las 11:00 ET.
- **Temporalidades:**
  - `Estructura y Rango`: 15 minutos (9:30–9:45 ET para definir `ORH` y `ORL`).
  - `Ejecución y Gatillo`: 1 minuto (cierre de vela).
  - `Contexto institucional`: Indicador VWAP dual:
    1. **VWAP NY Cash:** Anclado a las 09:30 ET.
    2. **VWAP Diario Globex:** Anclado a las 18:00 ET del día anterior.

---

## 3. Reglas de Entrada Mecánicas

### Configuración Larga (Fallo de ORL - Long Reversal):
1. **Definición de Rango:** A las 09:45:00 ET, fijar los niveles estáticos `ORH` (máximo) y `ORL` (mínimo) de la vela 9:30–9:45 ET.
2. **Filtro de Amplitud:** El rango `ORH - ORL` debe ser razonable según la volatilidad reciente: entre 40 y 120 puntos de NQ. Si el rango supera 150 puntos (por evento macro o apertura descontrolada), el trade queda **cancelado** (riesgo desproporcionado).
3. **El Barrido (Falso Quiebre):** Entre las 09:45 ET y las 10:15 ET, el precio penetra por debajo de `ORL` (mínimo 1 tick por debajo), atrapando a vendedores.
4. **Reabsorción:** El precio rebota y vuelve a cotizar dentro del rango `[ORL, ORH]`.
5. **Gatillo de Entrada:** Comprar a mercado (o orden stop-limit en el máximo de la vela) en el cierre de la primera vela de 1 minuto cuyo **cuerpo cierre estrictamente por encima del VWAP NY (9:30 ET)**.

### Configuración Corta (Fallo de ORH - Short Reversal):
- Simétrica: barrido por encima de `ORH`, reabsorción hacia el interior del rango, y cierre de vela de 1 min con cuerpo por debajo del VWAP NY.

---

## 4. Gestión de Riesgo y Salida (Hard Rules)

- **Hard Stop Loss (no negociable):**
  - Para Long: Colocado 2 ticks por debajo del mínimo absoluto del barrido (Sweep Low), o por debajo del VWAP Diario Globex si este se encuentra cerca.
  - Tamaño máximo de Stop: 30 a 40 puntos en NQ ($60 a $80 en MNQ). Si la distancia al mínimo del barrido exige más de 45 puntos, se reduce drásticamente el tamaño a MNQ o se invalida el setup.
- **Take Profit (Gestión en 2 Tramos):**
  - **TP1 (50% de la posición):** Al alcanzar el nivel opuesto del rango (`ORH` en posición larga). Al llenarse TP1, el stop del resto de la posición se mueve automáticamente a Break Even (+2 ticks para cubrir comisiones).
  - **TP2 (50% restante):** Proyección de expansión de 1.0× la amplitud del rango por encima de `ORH`, o trailing stop basado en la pérdida de la media móvil exponencial de 9 períodos en 1 min.
- **Invalidación Intradía:**
  - Si el precio no alcanza el VWAP NY dentro de los 15 minutos posteriores a la reentrada al rango, la orden se descarta.
  - Si una vela de 1 min cierra nuevamente por fuera del rango después de la entrada, se ejecuta salida de emergencia manual o a mercado.

---

## 5. Reglas de Cuenta Fondeada (Prop Firm Compliance)
- **Cálculo de Riesgo por Trailing Drawdown:**
  - El tamaño de posición se calcula contra el colchón real disponible, nunca contra el saldo nominal (ej. cuenta de $50k con $2k de drawdown máximo = cuenta de $2,000).
  - Riesgo máximo por trade: **0.5% a 1.0% del drawdown total** (ej. $100–$150 de riesgo en una cuenta de $2,000 de trailing DD = 1 a 2 contratos MNQ con stop de 35 puntos).
- **Límite Diario de Pérdidas (Circuit Breaker):**
  - Máximo 1 trade de este setup por sesión.
  - Si el trade toca stop loss, el bot o el operador se desconecta por el resto de la sesión de apertura. Prohibido "revenge trading" o martingala.
- **Cierre Forzoso:**
  - Toda posición abierta se liquida a más tardar a las 11:30 ET (fin de la ventana de volatilidad de la mañana). Ninguna posición se mantiene durante el almuerzo de NY ni hacia el cierre de sesión (15:55 ET obligatorio flat).

---

## 6. Arquitectura para NinjaTrader 8 (NinjaScript / C#)
- **Modo de cálculo:** `Calculate.OnBarClose` en gráfico de 1 minuto con serie secundaria de 15 minutos (`AddDataSeries(BarsPeriodType.Minute, 15)`).
- **Gestión de órdenes:** Uso obligatorio de `SetStopLoss(CalculationMode.Price, ...)` y `SetProfitTarget(CalculationMode.Price, ...)`.
- **Detección de reconexión:** En `OnBarUpdate`, verificar `State == State.Historical` vs `State.Realtime` y sincronizar posiciones abiertas antes de emitir órdenes.

---

## Referencias
- Ideas: [[ORB_FALLO_VWAP_01]]
- Fuentes y research:
  - MADDOG Research: Opening Range Breakout Failure Rate en ES/NQ.
  - CME Group: Nasdaq-100 Futures Contract Specifications.
  - jira/trading_agent_persona.md: Directivas de trading algorítmico y control de riesgo prop firm.
