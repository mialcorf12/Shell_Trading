# PERFIL_GORDO_DELGADO: Lectura de Forma del Perfil de Volumen (Balance vs Desbalance) en NQ/MNQ

## 1. Hipótesis Operativa
Según la teoría de subasta de mercado (Auction Market Theory), el precio explora el valor hasta que encuentra aceptación. El perfil de volumen de una sesión muestra esa exploración:

- **Perfil "gordo" (balance):** mucho volumen concentrado en pocos niveles. Ambos lados acuerdan el precio; el mercado rota dentro de la zona. Operativamente, el precio tiende a volver al centro de masa (POC) y las zonas extremas suelen revertir.
- **Perfil "delgado" (desbalance):** poco volumen en una franja amplia. Un lado tomó el control y el precio atravesó zonas sin negocio. Operativamente, el precio tiende a continuar hasta encontrar un nuevo volumen (HVN), y los retrocesos a la zona delgada suelen ser oportunidades de seguimiento.

La hipótesis de la estrategia: **hacer fade de extremos en perfiles gordos (rotación) y seguir retrocesos en perfiles delgados (desbalance)**. La forma del perfil define la estrategia a aplicar; no hay operación sin clasificar primero el perfil.

---

## 2. Parámetros de Mercado e Instrumentos
- **Contratos:** MNQ ($2.00/punto, $0.50/tick) para ejecución; NQ ($20.00/punto) solo con riesgo acotado al colchón de drawdown.
- **Sesión:** RTH (09:30–16:00 ET). Perfil de referencia: sesión de ayer (o rango de 3 días para contexto).
- **Temporalidades:** perfil construido sobre 1 min (o 5 min); decisión sobre 5 min.

---

## 3. Definiciones Medibles (eliminan la ambigüedad del video)
Para clasificar el perfil se usan tres mediciones calculadas sobre el perfil de la sesión de referencia, con el área de valor (Value Area, 70% del volumen):

- **Ancho de valor relativo:** `VA_Width / Rango_Total`.
  - **Gordo (balance):** `VA_Width / Rango_Total` ≤ 0.35.
  - **Delgado (desbalance):** `VA_Width / Rango_Total` ≥ 0.55.
  - Entre 0.35 y 0.55: **zona gris**, sin operación.
- **Posición del POC:** si el POC está en el tercio superior o inferior del rango, el perfil tiene sesgo (no es balance puro).
- **Desbalance direccional:** en un perfil delgado, la cola sin volumen se encuentra a un solo lado del POC.

Los umbrales 0.35 / 0.55 son una operacionalización propia; deben validarse en walk-forward (sección 7).

---

## 4. Reglas de Entrada

### Setup A — Rotación en perfil gordo (fade de extremos):
1. Perfil de la sesión de ayer clasificado como gordo.
2. Hoy el precio abre dentro del área de valor de ayer (VAL ≤ Open ≤ VAH).
3. Entrada corta cerca de VAH (o larga cerca de VAL) cuando una vela de 5 min cierra con cuerpo de regreso hacia el interior del área de valor.
4. Objetivo: POC de ayer.

### Setup B — Continuación en perfil delgado (seguir retroceso):
1. Perfil de ayer clasificado como delgado, con cola sin volumen hacia arriba (o abajo).
2. Hoy el precio abre fuera del área de valor de ayer y se sostiene 30 minutos por fuera.
3. Entrada en el primer retroceso hacia el borde de la zona delgada que no penetra más allá de su mitad, con vela de 5 min de confirmación en la dirección del desbalance.
4. Objetivo: el siguiente HVN en la dirección del desbalance.

Versiones bajistas: espejo.

---

## 5. Gestión de Riesgo y Salida

- **Hard Stop Loss:**
  - Setup A: 2 ticks más allá del extremo del área de valor (VAH/VAL), máximo 30 puntos NQ ($60 MNQ).
  - Setup B: 2 ticks por debajo de la mitad de la zona delgada que sirvió de entrada; máximo 35 puntos NQ.
- **Take Profit:**
  - Setup A: TP1 en POC (60%); TP2 en VAL (lado opuesto del área de valor) (40%).
  - Setup B: TP1 a 1.0 R (50%); TP2 en el siguiente HVN (50%). Ratio mínimo 1:2 sobre el stop; si no existe ese objetivo, no operar.
- **Break Even:** al llenarse TP1, stop del resto a +2 ticks.
- **Invalidación:**
  - Setup A: cierre de vela de 5 min fuera del área de valor con cuerpo y sostenido 15 minutos.
  - Setup B: cierre de vela de 5 min que reingresa a la zona delgada más allá de su mitad.

---

## 6. Reglas de Cuenta Fondeada (Prop Firm Compliance)
- **Riesgo por operación:** máximo 0.75% del trailing drawdown real. Ejemplo: $2,000 de DD → $150 de riesgo → con stop de 25 puntos en MNQ ($50/contrato), 3 contratos.
- **Máximo 1 operación por setup por día.** Tras una pérdida del mismo setup, no reentrar ese día.
- **Sin promediar ni ampliar stop.**
- **Cierre forzoso:** flat antes de las 15:55 ET.

---

## 7. Validación Pendiente y Honestidad Estadística
- El material fuente usa datos simulados (marcados así en pantalla). No hay estadística ni precios reales: la hipótesis no está probada.
- Los umbrales (0.35 / 0.55 de ancho relativo y 30 minutos de sostenimiento) son propios; deben fijarse con datos de entrenamiento y comprobarse fuera de muestra.
- Backtest con costos reales ($0.62/lado MNQ, $2.10/lado NQ) y 1–2 ticks de slippage.
- Muestra mínima: ≥ 100 operaciones por setup. Reportar distribución por día.
- Clasificar cada sesión **antes** de ver el resultado (regla de no-hindsight): la clasificación se registra en el momento de la apertura.

---

## 8. Arquitectura NinjaTrader 8 (NinjaScript)
- Series: 1 min (construcción del perfil), 5 min (decisión). Perfil de la sesión anterior calculado al inicio de sesión mediante histograma de precios en memoria.
- Estados: `Clasificar_Perfil → Esperar_Apertura → Setup_A_Activo | Setup_B_Activo → EnPosicion → Cerrado`.
- `SetStopLoss` y `SetProfitTarget` por precio tras la entrada.

---

## Referencias
- Ideas: [[PERFIL_GORDO_DELGADO_01]]
- Fuentes y research:
  - Teoría de Subasta de Mercado (Auction Market Theory, J. Dalton / Steidlmayer): perfil de volumen, balance y desbalance.
  - YMI Blog (Cameron Bennion): Volume Profile para ES y NQ (VPOC, HVN, LVN).
  - jira/trading_agent_persona.md: Hipótesis antes que código, validación fuera de muestra y trailing drawdown.
