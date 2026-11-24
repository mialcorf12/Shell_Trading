# RANGO_8AM_BARRIDO_IFVG: Barrido del Rango Horario de las 8:00 AM con Nivel Clave e iFVG en NQ/MNQ

## 1. Hipótesis Operativa y Fundamento de Estructura Temporal
En los futuros del Nasdaq (NQ/MNQ), la vela horaria de las **08:00 AM ET (08:00 a 09:00 ET)** engloba el flujo de órdenes previo a la apertura de Nueva York, absorbiendo frecuentemente los informes macroeconómicos de las 08:30 ET (CPI, PPI, solicitudes de desempleo).
- **El Rango Ancla de las 8 AM:**
  Los extremos de esta vela (`8AM_High` y `8AM_Low`) actúan como fronteras de liquidez inmediatas. Los algoritmos institucionales utilizan la volatilidad de la apertura del contado (09:30 ET) para empujar el precio fuera del rango de las 8 AM, inducir compras o ventas prematuras y activar órdenes stop agrupadas sobre niveles clave previos (`Key Levels`: máximos/mínimos de sesiones anteriores o `Equal Highs/Lows`).
- **El Modelo de Entrega Extremo a Extremo:**
  Una vez que la liquidez de un extremo es capturada en un nivel clave y el precio confirma el rechazo en 1 minuto con una **Inversión de Fair Value Gap (iFVG)** y un **Order Block (OB)**, el algoritmo de entrega busca de forma sistemática el **extremo opuesto del rango de las 8 AM** (de `8AM_High` a `8AM_Low` o viceversa), generando un ratio beneficio/riesgo asimétrico de 2.5:1 a 4:1.

---

## 2. Parámetros de Mercado y Especificaciones
- **Contratos:** MNQ ($2.00/punto) para cuentas de evaluación o con colchón ajustado; NQ ($20.00/punto) solo si la distancia del stop en 1M no excede el presupuesto de riesgo.
- **Sesión y Horario:** RTH (Nueva York).
  - *Fijación del Rango Ancla:* A las 09:00:00 ET, se bloquean `8AM_High` y `8AM_Low` de la vela horaria de 08:00:00 a 08:59:59 ET.
  - *Ventana de Barrido y Gatillo:* De 09:15 ET a 10:15 ET (habitualmente gatillado durante el Judas Swing de 09:30–09:45 ET).
- **Temporalidades:**
  - `1 Hora (1H)`: Identificación de la vela de 8 AM y ubicación del `Key Level` (máximo/mínimo swing previo en las últimas 20 barras horarias).
  - `1 Minuto (1M)`: Detección del barrido, formación del iFVG, confirmación del Order Block y gatillo de entrada.

---

## 3. Reglas Mecánicas de Entrada ("Los 3 Pasos")

### Configuración Corta (Short Setup tras barrido de 8AM High):
1. **Paso 1 (Marcar el Rango de 8 AM):**
   - A las 09:00 ET, trazar líneas horizontales en `8AM_High` y `8AM_Low`.
2. **Paso 2 (Identificar el Nivel Clave `Key Level`):**
   - Buscar un swing high o zona de `Equal Highs` previo de 1H ubicado ligeramente por encima de `8AM_High` (a una distancia de 5 a 25 puntos).
3. **Paso 3 (El Barrido y la Doble Confirmación en 1M):**
   - Entre las 09:30 y las 10:00 ET, el precio supera `8AM_High` y penetra el `Key Level`.
   - Inmediatamente se produce una vela bajista violenta de 1M que desplaza el precio de regreso por debajo de `8AM_High`.
   - **Confirmación iFVG:** La vela bajista cruza con su cuerpo un FVG alcista previo de 1M, invalidándolo y convirtiéndolo en un **Inversion FVG bajista**.
   - **Confirmación Order Block (OB):** El cierre bajista se produce por debajo de la apertura de la última vela alcista que precedió al barrido, validando el bloque de órdenes institucional.
4. **Gatillo de Entrada:**
   - Colocar orden `Limit` de venta en el límite inferior del iFVG o en el cuerpo del OB bajista durante el retesteo inmediato.

### Configuración Larga (Long Setup tras barrido de 8AM Low):
- Simétrica: Barrido por debajo de `8AM_Low` en un Key Level de soporte, cierre alcista de 1M que invierte un FVG bajista (iFVG alcista) y valida un OB alcista, comprando en el retesteo hacia `8AM_High`.

---

## 4. Gestión de Riesgo y Salida (Hard Rules)

- **Hard Stop Loss (no negociable):**
  - Colocado 2 ticks por encima del máximo absoluto del barrido (Sweep High).
  - Stop Máximo Permitido: **30 a 35 puntos en NQ** ($60 a $70 en MNQ). Si la mecha del barrido supera los 40 puntos de distancia al punto de entrada, el trade se descarta por riesgo excesivo.
- **Take Profit (Entrega al Extremo Opuesto):**
  - **TP1 (50% de la posición):** Al alcanzar el punto medio del rango de las 8 AM (`(8AM_High + 8AM_Low) / 2`). Al llenarse TP1, el stop del resto de la posición se traslada obligatoriamente a Break Even (+2 ticks).
  - **TP2 (50% restante - Target Final):** 2 ticks antes de alcanzar el extremo opuesto del rango (`8AM_Low` en posición corta).
- **Time Stop:** Toda posición abierta se cierra antes de las 11:45 ET.

---

## 5. Reglas de Cuenta Fondeada (Prop Firm Compliance)
- **Riesgo por Colchón de Drawdown:**
  - Máximo riesgo por operación: **1.0% del trailing drawdown real** (ej. $150 de riesgo máximo en cuenta con $2,000 de trailing DD). Con un stop de 30 puntos en MNQ ($60 de riesgo por contrato), el tamaño de posición es de exactamente 2 contratos MNQ.
- **Filtro de Ruptura Sin Retorno:**
  - Si una vela de 1M cierra por encima del Sweep High tras la entrada, salir inmediatamente a mercado; no esperar a que el precio arrastre la cuenta al stop si la estructura falló.
- **Límite de Operativa:** Máximo 1 trade al día bajo este modelo.

---

## 6. Arquitectura NinjaTrader 8 (NinjaScript)
- Serie multitemporal: `BarsArray[0]` = 1 minuto (ejecución), `BarsArray[1]` = 60 minutos (para identificar y congelar la barra de las 08:00 ET).
- Detección de extremos horarios:
  ```csharp
  if (BarsInProgress == 1) // Serie de 1H
  {
      if (Time[0].Hour == 8)
      {
          range8amHigh = High[0];
          range8amLow = Low[0];
      }
  }
  ```

---

## Referencias
- Ideas: [[RANGO_8AM_BARRIDO_IFVG_01]]
- Fuentes y research:
  - The Soup Room Research: 8AM Candle Range Sweep & NY Market Open Moves.
  - crapanick / TradingView: 8AM Range + KL Sweep + IFVG Entry Model.
  - LiquidityLevels Study: ES & NQ Overnight-to-Cash Session Transitions.
  - jira/trading_agent_persona.md: Directivas de trading algorítmico, trailing drawdown y estándares NinjaTrader 8.
