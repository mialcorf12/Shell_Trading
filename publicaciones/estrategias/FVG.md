# FVG: Fair Value Gaps Filtrados por Perfil de Volumen (HVN / LVN) en NQ/MNQ

## 1. Hipótesis Operativa y Fundamento de Subasta (Auction Market Theory)
Un Fair Value Gap (FVG) es una ineficiencia de precios de tres velas producida por un desplazamiento agresivo de órdenes de mercado. Sin embargo, en el Nasdaq-100 (NQ/MNQ), dos FVG visualmente idénticos en el gráfico de velas pueden comportarse de manera radicalmente opuesta.

- **La Anatomía Real del FVG en el Perfil de Volumen:**
  Todo FVG genuino coincide con un **Low Volume Node (LVN)** o vacío de volumen en el Volume Profile. El mercado se movió tan rápido que no hubo tiempo de subastar contratos de forma bidireccional.
- **El Volumen como Imán (HVN vs. LVN):**
  - **FVG que "Aguanta" (Soporte/Resistencia Real):** Ocurre cuando el FVG se forma inmediatamente adyacente a un **High Volume Node (HVN)** o al **POC (Point of Control)** de la sesión previa o del impulso actual. El HVN representa aceptación y acumulación institucional previa; cuando el precio retrocede al FVG, los participantes defienden su zona de valor y el FVG actúa como muelle de rebote hacia el POC.
  - **FVG que es un "Pasillo" (Slip-Through):** Ocurre cuando el gran volumen institucional se encuentra al otro lado del gap (por encima o por debajo en una zona no mitigada). En este caso, el FVG es simplemente una zona de baja fricción: el precio lo atraviesa sin frenar para alcanzar el verdadero imán de liquidez ubicado en el siguiente HVN.

---

## 2. Parámetros de Mercado e Instrumentos
- **Contratos:** MNQ ($2.00/punto) como instrumento base para calibrar volatilidad intrabarra; NQ ($20.00/punto) solo con ratios de riesgo estrictamente delimitados.
- **Sesión Operativa:** RTH (09:30–16:00 ET). Ventana preferida: 09:45 a 11:30 ET (máxima eficiencia de subasta).
- **Herramientas de Subasta:**
  - `Volume Profile Intradía`: Perfil de sesión (Session Profile) o Perfil de Rango Fijo (Fixed Range Volume Profile) anclado al impulso que originó el FVG.
  - `Timeframes`:
    - Macro / Contexto de Volumen: 15 minutos / 60 minutos (para ubicar HVNs, LVNs y POC).
    - Gatillo y Estructura FVG: 1 minuto a 5 minutos.

---

## 3. Reglas Mecánicas de Entrada

### Configuración Larga (Bullish FVG Respaldado por HVN):
1. **Detección del FVG:**
   - En gráfico de 5M o 1M, identificar un FVG alcista de 3 velas: `Mínimo de Vela 3 > Máximo de Vela 1`.
   - Tamaño mínimo del FVG: al menos 8 puntos en NQ (para evitar ruido de ticks).
2. **Filtro de Perfil de Volumen:**
   - Trazar el Volume Profile sobre el impulso que generó el FVG.
   - El FVG debe estar situado inmediatamente por encima de un **HVN significativo o del POC del impulso**.
   - No debe existir un HVN dominante sin mitigar por debajo del FVG a menos de 15 puntos (de lo contrario, el precio buscará ese nivel inferior).
3. **Gatillo de Entrada:**
   - Esperar a que el precio retroceda y toque el límite superior del FVG o el **50% Consequent Encroachment (CE)** del gap.
   - Una vela de 1M toca la zona del FVG y cierra en sentido alcista con volumen decreciente en la venta (agotamiento).
   - Entrada: Orden `Limit` en el límite superior del FVG o compra a mercado al confirmar la vela alcista de rechazo.

### Configuración Corta (Bearish FVG Respaldado por HVN):
- Simétrica: FVG bajista situado inmediatamente por debajo de un HVN/POC superior; entrada en el retroceso al límite inferior o 50% CE del FVG.

---

## 4. Gestión de Riesgo y Salidas

- **Hard Stop Loss:**
  - Situado 2 ticks por debajo de la base del FVG (para largos) o por debajo del HVN que lo respalda.
  - Máximo stop tolerado: **25 a 35 puntos NQ** ($50 a $70 en MNQ). Si la distancia exige más de 35 puntos, la orden se cancela.
- **Take Profit:**
  - **TP1 (60% de la posición):** Al alcanzar el máximo del impulso que generó el FVG. Al llenarse TP1, mover el stop loss del 40% restante a Break Even (+2 ticks).
  - **TP2 (40% restante):** En el siguiente High Volume Node superior o nivel de liquidez externa de 15M (ratio mínimo 1:2.0).
- **Condición de Invalidez:**
  - Si una vela de 5 minutos cierra con su cuerpo completo atravesando el FVG y perforando el 50% CE, la hipótesis de soporte queda **anulada** (el FVG se convirtió en pasillo); salir de inmediato.

---

## 5. Reglas de Cuenta Fondeada (Prop Firm Compliance)
- **Riesgo por Trailing Drawdown:**
  - Máximo 0.75% a 1.0% del colchón real de pérdida disponible (ej. $150 de riesgo en cuenta con $2,000 de trailing DD = 2 contratos MNQ con stop de 35 puntos).
- **Filtro de Whipsaw en Apertura:**
  - No operar FVGs generados en los primeros 5 minutos de RTH (09:30–09:35 ET), ya que los vacíos de volumen a esa hora suelen ser barridos en ambas direcciones antes de estabilizar el POC.
- **Circuit Breaker:** Máximo 2 trades perdedores al día en este setup. Si se tocan 2 stops, apagar el bot por la sesión.

---

## 6. Arquitectura NinjaTrader 8 (NinjaScript)
- Detección algorítmica de extremos de FVG:
  ```csharp
  // 50% Consequent Encroachment (CE)
  double fvgTop = Lows[0][2];
  double fvgBottom = Highs[0][0];
  double consequentEncroachment = (fvgTop + fvgBottom) / 2.0;
  ```
- Integración con indicadores de volumen: cálculo de perfiles mediante histograma de precios en memoria (`Dictionary<double, long>`) para clasificar si el nodo subyacente es HVN (volumen superior al percentil 70 del perfil).

---

## Referencias
- Ideas: [[FVG_01]]
- Fuentes y research:
  - Steidlmayer, J. & Dalton, J.: Auction Market Theory & Volume Profile Frameworks.
  - CME Group: Nasdaq-100 Order Flow and Microstructure Characteristics.
  - jira/trading_agent_persona.md: Directivas de trading algorítmico y preservación de trailing drawdown.
