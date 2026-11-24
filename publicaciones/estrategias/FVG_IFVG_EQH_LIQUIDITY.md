# FVG_IFVG_EQH_LIQUIDITY: Entrada Larga tras Barrido de Máximos Iguales con FVG de 1H e iFVG de 5M en NQ/MNQ

## 1. Hipótesis Operativa
Los máximos iguales (Equal Highs, EQH) son acumulaciones de órdenes stop por encima de un mismo nivel. Actúan como **liquidez pendiente**: el precio tiende a dirigirse a capturarla. Esta estrategia usa los EQH como objetivo direccional y exige tres confirmaciones antes de entrar:

1. **Zona de interés en 1H:** el precio toca un FVG alcista de 1H no mitigado (desequilibrio de precio que actúa como imán).
2. **Cambio de polaridad en 5M:** un FVG bajista de 5M formado en el último impulso se convierte en **iFVG** (inversión) cuando una vela cierra con cuerpo por encima de su límite superior.
3. **Confirmación estructural:** una vela cierra con cuerpo por encima del último swing high de 5M.

La entrada es larga con objetivo en el nivel de EQH.

---

## 2. Parámetros de Mercado e Instrumentos
- **Contratos:** MNQ ($2.00/punto, $0.50/tick) para ejecución; NQ ($20.00/punto) solo con riesgo acotado al colchón de drawdown.
- **Sesión:** RTH (09:30–16:00 ET). Ventana operativa preferida: 09:45–12:00 ET.
- **Temporalidades:**
  - Zona de interés y EQH: 1 hora.
  - Iniciación iFVG y estructura: 5 minutos.
  - Ajuste fino de entrada: 1 minuto (opcional).
- **Definición de EQH:** dos o más swing highs de 1H cuya diferencia sea ≤ 5 puntos NQ. Si la diferencia es mayor, no son EQH válidos.

---

## 3. Reglas Mecánicas de Entrada

1. **Paso 1 — Objetivo de liquidez (1H):** marcar los EQH sobre el precio actual. Se confirma que el precio cotiza por debajo de ellos.
2. **Paso 2 — Zona de interés (1H):** marcar el FVG alcista más reciente no mitigado. Esperar que el precio lo toque (penetración mínima de 25% del gap).
3. **Paso 3 — FVG bajista en 5M:** dentro del impulso bajista que tocó el FVG de 1H, identificar el **último** FVG bajista de 5M (no uno anterior y más alto).
4. **Paso 4 — Inversión a iFVG (5M):** esperar que una vela de 5M cierre con su cuerpo completo **por encima del límite superior** de ese FVG bajista. En ese momento el FVG queda invertido y pasa a actuar como soporte.
5. **Paso 5 — Confirmación estructural (5M):** esperar una vela de 5M que cierre con cuerpo por encima del último swing high de 5M previo al barrido.
6. **Paso 6 — Gatillo de entrada:** compra a mercado al cierre de la vela del paso 5, o orden limit en el límite superior del iFVG en el retesteo.

**Filtro de ratio:** la distancia entre la entrada y los EQH debe ser ≥ 2 veces la distancia al stop. Si no, no se opera (el R:R visual del video es aproximadamente 1:1, insuficiente para cuentas fondeadas).

---

## 4. Gestión de Riesgo y Salida

- **Hard Stop Loss:** por debajo del mínimo más bajo de la zona de barrido (mínimo de la zona del FVG de 1H tocado), con 2 ticks de margen.
  - Stop máximo: 35 puntos NQ ($70 en MNQ). Si la distancia lo excede, la operación se descarta.
- **Take Profit:**
  - TP1 (50%): en el primer nivel de liquidez intermedio (mínimo de los últimos 30 minutos de referencia) o a 1.0 R.
  - TP2 (50%): en los **Equal Highs** (objetivo principal de la hipótesis).
- **Break Even:** al llenarse TP1, mover el stop del resto a +2 ticks.
- **Invalidación:**
  - Cierre de vela de 5M con cuerpo completo por debajo de la base del iFVG antes de la entrada: hipótesis anulada.
  - Cierre de vela de 1H por debajo del FVG de 1H tras la entrada: salida inmediata.

---

## 5. Reglas de Cuenta Fondeada (Prop Firm Compliance)
- **Riesgo por operación:** máximo 0.75% del trailing drawdown real. Ejemplo: $2,000 de DD → $150 de riesgo → con stop de 30 puntos en MNQ ($60/contrato), 2 contratos.
- **Límite de operaciones:** máximo 1 operación por día bajo este setup.
- **Sin ampliación de stop:** prohibido mover el stop hacia atrás.
- **Cierre forzoso:** flat antes de las 15:55 ET; antes de las 16:00 ET no abrir nuevas posiciones.

---

## 6. Validación Pendiente
- El video no entrega precios, win rate ni R:R declarado: la hipótesis no está probada.
- Backtest con costos reales ($0.62/lado MNQ, $2.10/lado NQ) y 1–2 ticks de slippage.
- Walk-forward: definir los umbrales (tolerancia de EQH, penetración del FVG) con datos de entrenamiento y comprobarlos en un periodo posterior.
- Meta de muestra: ≥ 100 operaciones antes de cualquier conclusión.

---

## 7. Arquitectura NinjaTrader 8 (NinjaScript)
- Series múltiples: 1 hora (zona y EQH), 5 minutos (iFVG y estructura), 1 minuto (opcional, ajuste de gatillo).
- Detección de EQH por tolerancia de precio (≤ 5 puntos NQ) sobre swing highs de la serie de 1H.
- Estados: `Buscando_EQH → FVG_1H_Tocado → iFVG_5M_Confirmado → EnPosicion → Cerrado`.
- Órdenes con `SetStopLoss` y `SetProfitTarget` por precio, colocadas inmediatamente tras la entrada.

---

## Referencias
- Ideas: [[FVG_IFVG_EQH_LIQUIDITY_01]]
- Fuentes y research:
  - ICT Killzone (Michael Phillips): Inversion FVG — polarity flip de un FVG tras desplazamiento.
  - Tradezella (Joshua Cutler): IFVG model para NQ/ES tras barrido de liquidez.
  - jira/trading_agent_persona.md: Estándares de backtesting honesto, trailing drawdown y NinjaScript.
