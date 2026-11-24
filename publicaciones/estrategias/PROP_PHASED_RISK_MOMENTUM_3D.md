# PROP_PHASED_RISK_MOMENTUM_3D: Entrada Diaria por Momentum de 3 Días con Riesgo Escalonado por Fase de Cuenta Fondeada en NQ/MNQ

## 1. Hipótesis Operativa
La regla de entrada es un filtro de momentum de tres días: si el cierre de ayer supera al cierre de hace tres días, el sesgo es comprador; si no, vendedor. La operación ocurre una vez al día a la apertura de Nueva York.

El diferencial de la estrategia no está en la entrada, sino en la **gestión del riesgo por fase de la cuenta**: el tamaño de posición y el objetivo diario cambian según la etapa (evaluación, primer día fondeado, hasta el primer pago, después de cada pago). La lógica es mantener el riesgo acotado mientras la cuenta es frágil y aumentar la exposición solo cuando el colchón lo permite.

**Advertencia de validez:** el video reconoce que los parámetros de riesgo se calibraron con los mismos datos del resultado mostrado. Todo el análisis que sigue es in-sample hasta que se valide fuera de muestra.

---

## 2. Parámetros de Mercado e Instrumentos
- **Instrumentos:** NQ ($20.00/punto) y MNQ ($2.00/punto). La conversión a contratos se hace con la fórmula de la sección 4.
- **Sesión:** RTH. Entrada única a la apertura: 09:30 ET.
- **Datos de decisión:** cierre diario de ayer (CME settlement de RTH) y cierre diario de hace tres días. Se usan cierres diarios, no intradía.
- **Frecuencia:** una operación por día, sin reentradas.

---

## 3. Regla de Entrada (mecánica)
1. Calcular `C1` = cierre diario de ayer y `C3` = cierre diario de hace tres sesiones.
2. Si `C1 > C3`: **compra** a mercado a la apertura de 09:30 ET.
3. Si `C1 ≤ C3`: **venta** a mercado a la apertura de 09:30 ET.
4. Sin filtro de volatilidad ni de noticias en la versión del video. Esta estrategia lo deja como **pendiente** (sección 7).

---

## 4. Gestión de Riesgo por Fase (cálculo de contratos y objetivo)

El stop es fijo en **50 puntos** en todas las fases. La regla de tamaño es:

- **Contratos NQ** = `Riesgo_$ / (50 × 20)` = `Riesgo_$ / 1000`
- **Contratos MNQ** = `Riesgo_$ / (50 × 2)` = `Riesgo_$ / 100`
- **Puntos de objetivo** = `Objetivo_$ / (contratos × valor por punto)`

| Fase | Riesgo máximo | Objetivo diario | NQ (contratos) | MNQ (contratos) | Objetivo en puntos (NQ) |
|---|---|---|---|---|---|
| Evaluación | $2,000 | $1,500 | 2 | 20 | 37.5 pts |
| Primer día fondeado | $2,000 | $4,000 | 2 | 20 | 100 pts |
| Hasta el primer pago | $1,000 | $625 | 1 | 10 | 31.25 pts |
| Después de cada pago | $1,200 | $480 | 1.2 → usar 1 NQ o 12 MNQ | 12 | 24 pts (con 1 NQ) |

**Ajuste de redondeo:** en la fila "Después de cada pago", 1.2 NQ no es posible. Se usa 1 NQ (riesgo real $1,000) o 12 MNQ (riesgo real $1,200). Esta estrategia adopta **12 MNQ** para respetar el riesgo declarado. Con 12 MNQ el objetivo de $480 equivale a 20 puntos, no 24.

**Corrección importante:** el objetivo en puntos de la fila "Después de cada pago" se recalcula con los contratos reales de la sección 4. Para 12 MNQ: `480 / (12 × 2) = 20 pts`.

---

## 5. Salidas
- **Stop loss:** 50 puntos en contra de la entrada, colocado en la orden al entrar.
- **Objetivo:** el objetivo diario en puntos de la sección 4. Al alcanzarse, cerrar la posición del día.
- **Sin trailing ni breakeven:** la versión del video no los usa; agregarlos cambia la distribución de resultados y debe validarse por separado.
- **Cierre por tiempo:** toda posición se cierra antes de las 15:55 ET.

---

## 6. Reglas de Cuenta Fondeada (Prop Firm Compliance)
- **Límite de contratos:** verificar el límite de contratos de la firma antes de usar 2 NQ o 20 MNQ en evaluación.
- **Límite de pérdida diaria y drawdown trailing:** el riesgo por día ($1,000–$2,000) debe quedar por debajo del límite diario de la firma, con margen. Cuando el riesgo se acerque al límite, reducir contratos.
- **Regla de consistencia:** muchas firmas limitan el peso del mejor día en la utilidad total. El escalado de riesgo tras cada pago no elimina ese riesgo: revisar la regla de la firma específica.
- **Sin promediar ni ampliar stop.**

---

## 7. Validación Pendiente (obligatoria antes de uso)
- **Fuera de muestra:** el resultado del video (149 evaluaciones, 42 pagos, neto $54,695 entre enero 2024 y julio 2026) es in-sample. Hay que separar datos de calibración y de prueba.
- **Costos:** el video dice que incluye comisiones; no especifica slippage. Usar $0.62/lado MNQ y $2.10/lado NQ, más 1–2 ticks de slippage en la apertura.
- **Muestra de decisiones:** cada día genera una sola operación. Para tener ≥ 100 operaciones se necesitan varios años de datos; reportar la distribución por año.
- **Filtros pendientes:** el video no define filtro de volatilidad ni de eventos; probar si ayuda o perjudica.
- **Fecha:** el video menciona "julio de 2026" como fin de muestra; verificar que el periodo sea real y no un error de transcripción.
- **Régimen:** un momentum de tres días puede comportarse distinto en tendencia y en rango; reportar por régimen.

---

## 8. Arquitectura NinjaTrader 8 (NinjaScript)
- Serie diaria para `C1` y `C3`; serie de 1 min para la entrada a las 09:30 ET.
- Cálculo de contratos en `OnBarUpdate` a partir de la fase activa (variable de estado persistida entre sesiones; la fase cambia tras un pago registrado).
- Estados: `Esperar_Apertura → Decidir_Sesgo → EnPosicion → Cerrado_Por_Objetivo | Cerrado_Por_Stop | Cerrado_Por_Tiempo`.
- Órdenes con `SetStopLoss` (50 pts) y `SetProfitTarget` (objetivo en puntos) inmediatamente tras la entrada.

---

## Referencias
- Ideas: [[PROP_PHASED_RISK_MOMENTUM_3D_01]]
- Fuentes y research:
  - Publicación de origen (@reel Df5-uI2gpAM): sistema NASDAQ con riesgo por fase de cuenta fondeada (in-sample; promocional).
  - jira/trading_agent_persona.md: Validación fuera de muestra, backtesting honesto y trailing drawdown.
