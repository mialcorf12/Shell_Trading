# DESACOPLE_SMT_NQ_ES: Divergencia SMT entre NQ y ES en Extremos de 5 Minutos

## 1. Hipótesis Operativa
Los futuros de Nasdaq-100 (NQ) y S&P 500 (ES) están muy correlacionados: normalmente marcan máximos y mínimos juntos. Cuando uno rompe un extremo y el otro no lo confirma, se produce un **desacople** (divergencia SMT, *Smart Money Technique*). La lectura de la escuela SMT: el mercado que no confirma el extremo muestra que la liquidez no tiene soporte amplio, y el movimiento tiende a revertir.

La estrategia usa el desacople como **filtro de sesgo y disparador**: si el NQ barre un máximo y el ES no, se busca venta, y viceversa para mínimos y compras. La confirmación de la reversión es un cierre de vela en 5 minutos en la dirección opuesta al barrido.

---

## 2. Definiciones Medibles
- **Barrido de máximo (o mínimo):** una vela de 5 min del instrumento supera el máximo (o mínimo) de los últimos N swings de 5 min (N = 3) con mecha, sin que la vela cierre en el sentido del barrido.
- **Desacople:** el instrumento de referencia no supera ese mismo nivel en la misma ventana de 5 min (±1 vela), o lo supera sin barrer, o cierra por dentro.
- **Desacople alcista (SMT en mínimos):** uno hace un mínimo más bajo y el otro no lo confirma (su mínimo es más alto que su mínimo previo). Sesgo alcista.
- **Desacople bajista (SMT en máximos):** uno hace un máximo más alto y el otro no lo confirma. Sesgo bajista.
- **Confirmación de reversión:** cierre de vela de 5 min en la dirección opuesta al barrido, con cuerpo ≥ 60% de su rango, que supera el cuerpo de la vela de barrido.

El video no define qué índice debe barrer primero ni cuál confirma. En esta versión, **el instrumento operado es NQ** (su barrido o su falta de confirmación); el ES es solo referencia. Se operan ambos desacoples, uno en cada sentido.

---

## 3. Parámetros de Mercado e Instrumentos
- **Contratos:** MNQ ($2.00/punto, $0.50/tick) para ejecución; NQ ($20.00/punto) con riesgo acotado al colchón de drawdown. El ES solo se usa como dato de referencia.
- **Sesión:** RTH (09:30–16:00 ET). El video menciona "horario clave" sin definirlo; esta versión limita las entradas a 09:45–11:30 ET y 13:30–15:30 ET (propio).
- **Temporalidades:** 5 min para detectar barridos y desacoples; 1 min opcional para la entrada.
- **Requisito de datos:** ambos instrumentos con datos de la misma sesión y con sincronización de reloj. Sin ello, la ventana de ±1 vela no es fiable.

---

## 4. Reglas de Entrada

### Desacople alcista (corto → sesgo bajista, en NQ):
1. El NQ barre un máximo de 5 min (sección 2) y su vela cierra por dentro.
2. El ES no supera ese mismo máximo en la ventana ±1 vela: desacople confirmado.
3. Gatillo: vela de 5 min en NQ con cuerpo bajista ≥ 60% de su rango, que cierra por debajo del mínimo de la vela de barrido.
4. Entrada: venta a mercado al cierre del gatillo.

### Desacople en mínimos (largo → sesgo alcista, en NQ):
- Espejo: el NQ barre un mínimo de 5 min con cierre de vuelta por encima; el ES no marca mínimo nuevo. Gatillo alcista con cuerpo ≥ 60%; compra.

**Desacople inverso (ES barre, NQ no):** la misma lógica, pero la entrada se opera en el ES con el mismo filtro. Esta versión lo deja como hipótesis secundaria a validar por separado.

---

## 5. Gestión de Riesgo y Salida
- **Hard Stop Loss:** por encima del máximo del barrido (corto) o debajo del mínimo del barrido (largo), con 2 ticks de margen. Máximo 20 puntos NQ ($40 en MNQ). El video sitúa el stop bajo el mínimo en su ejemplo alcista; el tope de distancia es propio.
- **Take Profit:**
  - TP1 (50%): 1.0 R, o en el último swing de 5 min del lado opuesto (lo que ocurra primero).
  - TP2 (50%): en el vacío de liquidez o máximo previo de 15 min. Ratio mínimo 1:2 sobre el stop; si no hay objetivo a 2 R, no operar.
- **Break Even:** al llenarse TP1, stop del resto a +2 ticks.
- **Invalidación:** el ES supera el máximo barrido en las velas siguientes (el desacople se disuelve): salida inmediata. También cierre de vela de 5 min en la dirección del barrido por encima (corto) del máximo de barrido.

---

## 6. Reglas de Cuenta Fondeada (Prop Firm Compliance)
- **Riesgo por operación:** máximo 0.75% del trailing drawdown real. Ejemplo: $2,000 de DD → $150 de riesgo → con stop de 15 puntos en MNQ ($30/contrato), 4 contratos ($120 de riesgo).
- **Máximo 2 operaciones por día.** Tras un stop, esperar un nuevo desacople.
- **Sin promediar ni ampliar stop.**
- **Cierre forzoso:** flat antes de las 15:55 ET.
- **Sin operar durante eventos macro:** en los 15 minutos alrededor de anuncios de alto impacto, el desacople entre NQ y ES se produce por diferencias de liquidez y no por flujo informado.

---

## 7. Honestidad Estadística y Validación Pendiente
- El material fuente es una publicación de captación (CTA a una clase con un 95% de efectividad sin sustento). Ni sus cifras ni su ejemplo son verificables.
- El "horario clave", el índice que barre primero y el disparador no están definidos en el original. Las definiciones de esta estrategia (ventanas, ±1 vela, cuerpo ≥ 60%) son propias.
- Las divergencias SMT son frecuentes; la pregunta medible es si las que cumplen las reglas tienen expectativa positiva después de costos. No hay datos que lo muestren todavía.
- Backtest con datos sincronizados de NQ y ES, costos reales ($0.62/lado MNQ, $2.10/lado NQ) y slippage de 1–2 ticks.
- Walk-forward para la ventana de ±1 vela y el cuerpo mínimo. Muestra mínima: ≥ 100 operaciones, con resultados separados por sentido (corto/largo) y por desacople directo/inverso.

---

## 8. Arquitectura NinjaTrader 8 (NinjaScript)
- Dos series de 5 min cargadas: NQ (primaria, ejecución) y ES (secundaria, referencia). Verificar la sincronización de tiempo entre ambas series en `OnBarUpdate` antes de comparar.
- Detección de barridos por instrumento: comparación de máximos y mínimos de los últimos 3 swings de 5 min.
- Estados: `Vigilar_Barridos → Barrido_NQ → Desacople_Confirmado → Gatillo_5m → EnPosicion → Cerrado`.
- `SetStopLoss` y `SetProfitTarget` por precio tras la entrada.

---

## Referencias
- Ideas: [[DESACOPLE_SMT_NQ_ES_01]]
- Fuentes y research:
  - ICT / SMT (Smart Money Technique): divergencia entre mercados correlacionados en máximos y mínimos (NQ y ES como par clásico).
  - QuantVPS: SMT Divergence, cómo detectarla y operarla en ES y NQ.
  - Publicación de origen (@alanmiqueas.tt): desacople NAS100 vs S&P 500 (educativo; CTA a clase de pago, sin estadística verificable).
  - jira/trading_agent_persona.md: Hipótesis antes que código, validación honesta y trailing drawdown.
