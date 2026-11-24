# LVN_DELTA_TPO_CONFLUENCIA: Retest de Nodo de Bajo Volumen con Delta Anormal y TPO de Precio Único en NQ/MNQ

## 1. Hipótesis Operativa
Un **Low Volume Node (LVN)** es una zona de precio con poco volumen transado. El precio tiende a atravesarlas rápido, sin subastar. La estrategia combina tres lecturas independientes que deben coincidir en la misma zona:

1. **Volume Profile:** el impulso que originó el movimiento dejó un LVN (franja delgada en el perfil).
2. **Delta anormal:** el impulso tuvo un desequilibrio de agresión (compras o ventas de mercado) muy superior a lo normal. Confirma que el movimiento fue iniciado por un lado, no por subasta bilateral.
3. **TPO de precio único (single prints):** en el perfil de tiempo, esos mismos niveles aparecen con una sola letra (precio visitado una única vez). Confirma que el precio pasó rápido, sin aceptación.

La hipótesis: cuando el precio regresa al LVN confirmado por las tres lecturas, la zona actúa como soporte (en largo) porque ahí hay poca oferta acumulada y la agresión previa sigue siendo válida. El video describe el rechazo rápido y la absorción de vendedores como gatillo.

---

## 2. Parámetros de Mercado e Instrumentos
- **Contratos:** MNQ ($2.00/punto, $0.50/tick) para ejecución; NQ ($20.00/punto) solo con riesgo acotado al colchón de drawdown.
- **Sesión:** RTH (09:30–16:00 ET). Ventana preferida: 10:00–12:00 ET (perfil del impulso ya formado).
- **Temporalidades:**
  - Perfil de volumen y TPO: sesión en curso o impulso de 30–60 minutos.
  - Delta y gatillo: 1 min y 5 min.

---

## 3. Definiciones Medibles (los tres filtros)

### Filtro 1 — LVN:
- Dentro del perfil del impulso, un LVN es un nivel cuyo volumen es ≤ 40% del volumen del POC del mismo perfil.
- La franja LVN debe tener al menos 3 ticks de alto (0.75 puntos NQ) para ser operable.

### Filtro 2 — Delta anormal:
- `Delta_vela = Volumen_comprador_agresivo − Volumen_vendedor_agresivo`, por vela de 1 min.
- **Delta anormal:** `|Delta_impulso| ≥ 2.0 × media_absoluta_del_delta_de_30_min_previos`, en el tramo que originó el LVN.
- Dirección del delta debe coincidir con la dirección del impulso.

### Filtro 3 — TPO de precio único:
- En el perfil TPO de la misma sesión, los niveles del LVN aparecen con **una sola letra** (single print) en al menos el 60% de su franja.
- Si el TPO no muestra single prints, el filtro falla aunque el LVN exista.

Los umbrales 40%, 2.0× y 60% son una operacionalización propia del autor del video (que no los dio). Deben validarse en walk-forward.

---

## 4. Reglas de Entrada (solo si los tres filtros se cumplen)

### Largo (LVN alcista tras impulso con delta positivo):
1. Impulso alcista que deja el LVN confirmado por los tres filtros.
2. El precio regresa al LVN (retest), tocando su límite superior.
3. **Gatillo de rechazo:** una vela de 1 min toca la franja LVN, mete mecha inferior dominante (≥ 50% del rango), y cierra con cuerpo alcista por encima del punto medio de la franja.
4. **Confirmación de delta:** el delta de esa vela es positivo y mayor que el delta de la vela anterior (absorción de vendedores).
5. Entrada: compra a mercado al cierre de la vela de confirmación.

Versión corta: espejo sobre LVN bajista con delta negativo.

---

## 5. Gestión de Riesgo y Salida

- **Hard Stop Loss:** 2 ticks por debajo del límite inferior de la franja LVN. Máximo 25 puntos NQ ($50 MNQ). Si la franja y el stop exceden el máximo, no operar.
- **Take Profit:**
  - TP1 (50%): en el POC del perfil del impulso.
  - TP2 (50%): en el máximo del impulso que generó el LVN. Ratio mínimo 1:2 sobre el stop.
- **Break Even:** al llenarse TP1, stop del resto a +2 ticks.
- **Invalidación:**
  - Cierre de vela de 5 min con cuerpo por debajo de la franja LVN tras la entrada: salida inmediata.
  - Delta negativo sostenido (3 velas consecutivas de 1 min) tras la entrada: reducir o salir.

---

## 6. Reglas de Cuenta Fondeada (Prop Firm Compliance)
- **Riesgo por operación:** máximo 0.75% del trailing drawdown real. Ejemplo: $2,000 de DD → $150 de riesgo → con stop de 20 puntos en MNQ ($40/contrato), 3 contratos ($120 de riesgo).
- **Máximo 1 operación por LVN confirmado.** Máximo 2 operaciones por sesión.
- **Sin promediar ni ampliar stop.**
- **Cierre forzoso:** flat antes de las 15:55 ET.

---

## 7. Honestidad Estadística y Validación Pendiente
- El video no entrega estadística, precios, instrumento ni timeframe. Su checklist de tres confluencias no se vio completo en los frames revisados (el filtro TPO no está confirmado en el material fuente).
- Los umbrales (40%, 2.0×, 60%) son propios; se fijan con datos de entrenamiento y se comprueban fuera de muestra.
- Requiere datos de tick o de order flow (delta) de calidad: sin ellos, el filtro 2 no es reproducible en NinjaTrader 8 con datos de barra estándar.
- Backtest con costos reales ($0.62/lado MNQ, $2.10/lado NQ) y slippage de 1–2 ticks.
- Muestra mínima: ≥ 100 operaciones. Reportar distribución por día.

---

## 8. Arquitectura NinjaTrader 8 (NinjaScript)
- Serie de 1 min con datos de tick o `Volumetric` (VolumetricBars) para el delta por vela; serie de 5 min para contexto.
- Perfil de volumen en memoria (`Dictionary<double, long>`) y cálculo de single prints desde la serie de letras TPO.
- Estados: `Buscar_Impulso → LVN_Confirmado → Esperar_Retest → Gatillo_Delta → EnPosicion → Cerrado`.
- `SetStopLoss` y `SetProfitTarget` por precio tras la entrada.

---

## Referencias
- Ideas: [[LVN_DELTA_TPO_CONFLUENCIA_01]]
- Fuentes y research:
  - ATAS (Volume Profile Strategy with Order Flow: NQ Case Study): uso de HVN/LVN con order flow.
  - Chart Fanatics (Carmine LVN strategy): LVN como zona de retesteo tras impulso rápido.
  - YMI Blog (Cameron Bennion): VPOC, HVN y LVN para ES y NQ.
  - jira/trading_agent_persona.md: Validación honesta, datos de calidad y trailing drawdown.
