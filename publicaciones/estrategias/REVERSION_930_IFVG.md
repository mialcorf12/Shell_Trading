# REVERSION_930_IFVG: Modelo de Reversión de las 9:30 con Inversión de FVG (iFVG) en NQ/MNQ

## 1. Hipótesis Operativa y Fundamento de Manipulación (Judas Swing)
El algoritmo institucional de precios en los futuros de Nasdaq a menudo ejecuta un movimiento falso de apertura ("Judas Swing") entre las 09:30 y las 09:45 ET. 
- **La Secuencia AMD (Acumulación, Manipulación, Distribución):**
  1. *Acumulación Pre-Market (08:30–09:30 ET):* El precio se consolida generando liquidez de órdenes stop por encima y por debajo del rango previo.
  2. *Manipulación a las 09:30 ET:* Al abrir el contado, se inyecta volatilidad agresiva en contra de la dirección real del día, barriendo la liquidez externa (DOL: Draw On Liquidity) y adentrándose en un punto de interés de temporalidad mayor (1H FVG o nivel de soporte/resistencia institucional).
  3. *Inversión de Polaridad (iFVG):* Durante el movimiento rápido de caída de 1 minuto se genera un Fair Value Gap bajista. Si los compradores institucionales toman el control, el precio no respeta ese FVG como resistencia sino que lo atraviesa con fuerza. Un cierre de vela de 1M con cuerpo por encima del FVG confirma la **inversión** (iFVG), transformando el desequilibrio en un soporte inmediato.

---

## 2. Parámetros de Mercado e Instrumentos
- **Contratos:** MNQ ($2.00/punto) como instrumento predilecto por la volatilidad inicial del Nasdaq; NQ ($20.00/punto) reservado para cuentas que admitan un stop de 25–35 puntos sin comprometer las reglas de drawdown de la firma.
- **Sesión y Horario:** RTH (Nueva York).
  - *Ventana de Monitoreo:* 09:30:00 a 10:00:00 ET ("Judas Window").
  - *Ventana de Entrada:* 09:35 a 10:15 ET. Prohibido entrar después de las 10:30 ET (el movimiento de la mañana ya estará consumado).
- **Temporalidades:**
  - `Contexto Mayor (1H)`: Identificación de la dirección del flujo de órdenes, el objetivo de liquidez (`DOL`) y zonas de FVG de 1 hora.
  - `Estructura Intermedia (15M)`: Detección del barrido de mínimos/máximos del pre-market.
  - `Ejecución y Gatillo (1M)`: Detección del FVG de 3 velas y confirmación de la inversión (iFVG).

---

## 3. Reglas Mecánicas de Entrada

### Configuración Larga (Bullish Reversal 9:30):
1. **Paso 1 (Contexto 1H):** En el gráfico de 1H, el precio tiene un sesgo alcista general o cotiza inmediatamente sobre un 1H Bullish FVG no mitigado. Se identifica un nivel claro de mínimos iguales (`EQ_Lows`) o mínimo del pre-market como `DOL` (Draw On Liquidity).
2. **Paso 2 (Barrido a las 09:30 ET):**
   - Entre las 09:30 y las 09:40 ET, el precio se desploma y barre el mínimo de liquidez (`DOL`), penetrando en el 1H FVG.
3. **Paso 3 (Formación de FVG en 1M):**
   - En la pierna bajista de 1 minuto, se crea un FVG bajista evidente (hueco de 3 velas donde el mínimo de la vela 1 no se solapa con el máximo de la vela 3).
4. **Paso 4 (La Inversión - iFVG):**
   - El precio gira bruscamente al alza. Una vela de 1 minuto **cierra con su cuerpo completo por encima del límite superior del FVG bajista**.
   - En ese instante, el FVG bajista queda validado como **iFVG alcista**.
5. **Paso 5 (Gatillo de Entrada):**
   - Colocar una orden `Limit` de compra en el límite superior del iFVG (o en el 50% Consequent Encroachment del gap).
   - La entrada se ejecuta en el retroceso inmediato (retesteo del iFVG como soporte).

### Configuración Corta (Bearish Reversal 9:30):
- Simétrica: Barrido alcista de `EQ_Highs` / máximo pre-market a las 09:30 ET en un 1H Bearish FVG, formación de FVG alcista de 1M, cierre bajista de 1M con cuerpo por debajo del FVG (inversión a iFVG bajista), y venta en el retesteo.

---

## 4. Gestión de Riesgo y Salida (Hard Rules)

- **Hard Stop Loss (no negociable):**
  - Colocado 2 ticks por debajo del mínimo absoluto del barrido de manipulación (Sweep Low).
  - Límite máximo de Stop: **30 a 35 puntos en NQ** ($60 a $70 en MNQ). Si la distancia desde el iFVG hasta el Sweep Low excede los 40 puntos, la operación se **invalida automáticamente** (riesgo desmedido para prop-firm).
- **Take Profit (Múltiples Salidas):**
  - **TP1 (60% de la posición):** Al alcanzar el máximo del rango previo a la apertura (08:30–09:30 ET high).
  - Al llenarse TP1: el Stop del 40% restante se desplaza automáticamente a Break Even (+2 ticks).
  - **TP2 (40% restante):** Nivel de liquidez externo de 15M o ratio fijo de 1:2.5 / 1:3.0 sobre el riesgo inicial.
- **Invalidez de Entrada:**
  - Si el precio cierra con cuerpo de vela de 1M por debajo de la base del iFVG durante el retroceso, la inversión ha fallado; cancelar órdenes pendientes o abortar posición a mercado.

---

## 5. Reglas de Cuenta Fondeada (Prop Firm Compliance)
- **Mitigación de Slippage:**
  - La entrada se realiza con orden `Limit` en el retesteo del iFVG, **nunca con orden de mercado durante el primer minuto de apertura**. Esto evita el slippage devastador de 2 a 6 ticks típico de las 09:30:00 a 09:32:00 ET en NQ.
- **Límite de Riesgo de Trailing Drawdown:**
  - Riesgo máximo por trade: **0.75% a 1.0% del trailing drawdown real** (ej. máximo $150 de riesgo en cuenta con $2,000 de trailing DD = 2 contratos MNQ con stop de 35 puntos).
- **Máximo 1 Trade de Apertura:**
  - Este modelo se opera una sola vez por día. Si el setup no se presenta entre las 09:30 y las 10:15 ET, la sesión de apertura se da por concluida.
- **Liquidación Obligatoria:** Todas las posiciones deben estar cerradas a las 11:30 ET.

---

## 6. Arquitectura NinjaTrader 8 (NinjaScript)
- Detección de FVG mediante cálculo en serie de 1 minuto:
  ```csharp
  // Detección de FVG Bajista en 1M (para buscar inversión)
  bool isBearishFVG = Lows[0][2] > Highs[0][0]; // Brecha entre vela 2 barras atrás y vela actual
  double fvgTop = Lows[0][2];
  double fvgBottom = Highs[0][0];
  ```
- Estado de Inversión (`iFVG`):
  ```csharp
  // Confirmación de Inversión: cierre de cuerpo por encima del fvgTop
  if (Close[0] > fvgTop && priorBearishFVGActive)
  {
      iFVGActive = true;
      iFVGSupportLevel = fvgTop;
  }
  ```

---

## Referencias
- Ideas: [[REVERSION_930_IFVG_01]]
- Fuentes y research:
  - Zero-G Trading Research: Inverse Fair Value Gap Strategy for NQ.
  - Strefa Tradingu: First Presented Fair Value Gap — NY Opening Range Setup.
  - Michael Phillips / ICT Killzone: Inversion FVG Polarity Flip.
  - jira/trading_agent_persona.md: Reglas de trading algorítmico y ejecución disciplinada en cuentas fondeadas.
