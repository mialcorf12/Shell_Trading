# Indicadores

Listado de indicadores que aparecen en las estrategias de `publicaciones/estrategias/`, en orden alfabético.

Alcance: las secciones 1 y 2 cubren indicadores y herramientas de volumen usados en estrategias. La sección 4 reúne indicadores de contexto (EMA, RSI, ADX, Bollinger, MACD) sin configuración validada. La sección 3 reúne los conceptos de estructura de precio y niveles (FVG, order block, BOS/CHoCH, liquidez, CRT, SMT, PDH/PDL). EMA, Bandas de Bollinger, MACD, ADX, ATR y RSI no aparecen en ninguna estrategia.

## 1. Indicadores de las estrategias (orden alfabético)

Configuración y temporalidades tal como aparecen en cada estrategia. Donde la estrategia no define un valor, se indica.
Los indicadores de contexto (EMA, RSI, ADX, Bandas de Bollinger, MACD) están en la sección 4.

### Bandas de desviación estándar del VWAP (±1σ, ±2σ, ±3σ)
- **Configuración:** bandas a 1σ, 2σ y 3σ por encima y por debajo del VWAP de sesión (ancla 09:30 ET), con desviación estándar ponderada por volumen.
- **Dónde verlo:** estiramiento en velas de 5 min (cierre entre +2σ y +3σ); agotamiento en 1 min; clasificación del día al cierre de la primera hora (10:30 ET).
- **Nota:** la fórmula exacta de la desviación no está definida en la fuente; debe coincidir con el software de referencia.

### Delta
- **Configuración:** delta de cada vela = volumen comprador agresivo − volumen vendedor agresivo. Delta anormal: |delta del impulso| ≥ 2.0 × la media absoluta del delta de los 30 min previos. El signo del delta debe coincidir con la dirección del impulso.
- **Dónde verlo:** cálculo por vela de 1 min; gatillo y confirmación en 1 min y 5 min.
- **Nota:** requiere datos de tick o de order flow (en NinjaTrader 8, VolumetricBars).

### Perfil de volumen (POC, HVN, LVN, área de valor VAH/VAL)
- **Configuración:** perfil de la sesión anterior o del impulso. Área de valor = 70% del volumen. LVN = nivel con volumen ≤ 40% del POC y franja de al menos 0.75 pts. Forma del perfil por ancho relativo del área de valor: gordo ≤ 0.35, delgado ≥ 0.55, zona gris entre ambos.
- **Dónde verlo:** perfil de la sesión anterior como contexto; perfil del impulso de 30–60 min (LVN_DELTA_TPO); construcción sobre 1 min o 5 min; contexto de 15 y 60 min (FVG).

### TPO (perfil de tiempo, single prints)
- **Configuración:** una letra por periodo en cada nivel de precio. Single print = nivel con una sola letra. Filtro válido si al menos el 60% de la franja LVN tiene single prints.
- **Dónde verlo:** perfil TPO de la sesión en curso o del impulso de 30–60 min.

### Volumen (volumen por vela, media de volumen, VolRel)
- **Configuración:** VolRel = volumen de la vela de ruptura / SMA(volumen, 20). Aceptación: 0.8 ≤ VolRel ≤ 1.2. Rechazo: < 0.8. Iniciativa: > 1.5. En ORB_MULTI_SESSION, media de 20 períodos en 5 min; en LVN_BARRIDO y CRT, media de 20 velas de 1 min.
- **Dónde verlo:** 1 min o 5 min según la estrategia; la lectura se hace en la vela de ruptura.

### VWAP
- **Configuración:** volumen ponderado, reiniciado en cada ancla. Anclas: 09:30 ET (sesión de NY) y 18:00 ET (diario de Globex). En DOBLE_VWAP, los dos VWAP deben estar separados al menos 15 pts para operar.
- **Dónde verlo:** sesgo en 5 min, gatillo en 1 min (DOBLE_VWAP y ORB_FALLO_VWAP).
- **Nota:** el ancla de 18:00 ET requiere datos de sesión extendida para reproducirse.

## 2. Referencias a estrategias por indicador

### Bandas de desviación estándar del VWAP
- [[VWAP_REVERSION_AGOTAMIENTO]]

### Delta
- [[LVN_DELTA_TPO_CONFLUENCIA]]

### Perfil de volumen
- [[FVG]]
- [[LVN_BARRIDO_STOPS_930]]
- [[LVN_DELTA_TPO_CONFLUENCIA]]
- [[PERFIL_GORDO_DELGADO]]
- [[VOLUMEN_RUPTURA]]

### TPO
- [[LVN_DELTA_TPO_CONFLUENCIA]]

### Volumen
- [[CRT_ACUMULACION_APERTURA_IFVG]]
- [[FVG]]
- [[LVN_BARRIDO_STOPS_930]]
- [[ORB_MULTI_SESSION]]
- [[VOLUMEN_RUPTURA]]
- [[VWAP_REVERSION_AGOTAMIENTO]]

### VWAP
- [[DOBLE_VWAP_DIARIO_NY]]
- [[NY_OPEN_15M_RANGE_PDH_PDL]]
- [[ORB_FALLO_VWAP]]
- [[VWAP_REVERSION_AGOTAMIENTO]]

## 3. Conceptos de estructura y niveles (no son indicadores clásicos)

Conceptos de estructura de precio y niveles que usan las estrategias. Se listan aparte porque no son indicadores calculados sobre precio o volumen.

### BOS (Break of Structure)
- [[ESTRUCTURA_LIQUIDEZ_CHOCH_FVG]]
- [[ESTRUCTURA_TENDENCIA_RANGO_BOS_CHOCH_NQ]]

### CHoCH (Change of Character)
- [[ESTRUCTURA_LIQUIDEZ_CHOCH_FVG]]
- [[ESTRUCTURA_TENDENCIA_RANGO_BOS_CHOCH_NQ]]

### CRT (Candle Range Theory)
- [[CRT_ACUMULACION_APERTURA_IFVG]]
- [[CRT_NASDAQ_OB]]

### FVG (Fair Value Gap)
- [[CRT_ACUMULACION_APERTURA_IFVG]]
- [[ESTRUCTURA_LIQUIDEZ_CHOCH_FVG]]
- [[FVG]]
- [[FVG_IFVG_EQH_LIQUIDITY]]
- [[FVG_TERCERA_VELA]]
- [[IFVG_LIQUIDEZ_1A1]]
- [[RANGO_8AM_BARRIDO_IFVG]]
- [[REVERSION_930_IFVG]]

### iFVG (Inversion Fair Value Gap)
- [[CRT_ACUMULACION_APERTURA_IFVG]]
- [[FVG_IFVG_EQH_LIQUIDITY]]
- [[IFVG_LIQUIDEZ_1A1]]
- [[RANGO_8AM_BARRIDO_IFVG]]
- [[REVERSION_930_IFVG]]

### Liquidez (barrido, DOL, máximos o mínimos iguales)
- [[AMD_RANGO_FALSA_RUPTURA]]
- [[CRT_ACUMULACION_APERTURA_IFVG]]
- [[CRT_NASDAQ_OB]]
- [[DESACOPLE_SMT_NQ_ES]]
- [[ESTRUCTURA_LIQUIDEZ_CHOCH_FVG]]
- [[ESTRUCTURA_TENDENCIA_RANGO_BOS_CHOCH_NQ]]
- [[FVG]]
- [[FVG_IFVG_EQH_LIQUIDITY]]
- [[FVG_TERCERA_VELA]]
- [[IFVG_LIQUIDEZ_1A1]]
- [[LVN_BARRIDO_STOPS_930]]
- [[NY_OPEN_15M_RANGE_PDH_PDL]]
- [[ORB_FALLO_VWAP]]
- [[ORB_MULTI_SESSION]]
- [[RANGO_8AM_BARRIDO_IFVG]]
- [[REVERSION_930_IFVG]]
- [[TOP_DOWN_SMC_OB_4PASOS]]

### MSS (cambio de estructura)
- [[TOP_DOWN_SMC_OB_4PASOS]]

### Order block (OB)
- [[CRT_NASDAQ_OB]]
- [[RANGO_8AM_BARRIDO_IFVG]]
- [[TOP_DOWN_SMC_OB_4PASOS]]

### PDH / PDL (máximo y mínimo del día anterior)
- [[NY_OPEN_15M_RANGE_PDH_PDL]]

### SMT (divergencia NQ / ES)
- [[DESACOPLE_SMT_NQ_ES]]
- [[ESTRUCTURA_LIQUIDEZ_CHOCH_FVG]]

## 4. Indicadores de contexto (no usados en las estrategias)

Estos indicadores aparecen en el material de `contexto/` y en ideas descartadas. Ninguna estrategia los usa. Lo que sigue es lo que dice cada fuente; no hay configuración validada.

### EMA (medias móviles exponenciales)
- **Períodos mencionados:** EMA 9 (tendencia de corto plazo), EMA 21 (entrada y salida), EMA 50 (punto de stop) y EMA 200 (tendencia de largo plazo). Fuente: `INDICADORES_TOP_7` (contexto).
- **Otra configuración:** EMA 20 y EMA 50, con precio por encima de ambas como tendencia alcista, y cruce 20/50 como posible señal. Fuente: `CONFIRMACION_5_INDICADORES` (contexto).
- **Dónde verlo:** no definido en el material. Ninguna fuente indica temporalidad para EMA 9.
- **Nota:** EMA 4/8/16 (1 min, EUR/USD) y EMA 20 (5 min, NQ) aparecieron en reels descartados. Esos borradores fueron eliminados del repo y no se usan como configuración.

### RSI
- **Configuración:** niveles 70 (sobrecompra) y 30 (sobreventa). Línea media 50 como momentum: sobre 50 alcista, bajo 50 bajista. Periodo no definido. Fuentes: `INDICADORES_TOP_7` y `CONFIRMACION_5_INDICADORES` (contexto).
- **Dónde verlo:** no definido.

### ADX
- **Configuración:** umbrales de fuerza de tendencia: bajo 20 débil, entre 20 y 25 media, sobre 25 fuerte. Periodo no definido. Fuente: `CONFIRMACION_5_INDICADORES` (contexto).
- **Dónde verlo:** no definido.

### Bandas de Bollinger
- **Configuración:** sin periodo ni número de desviaciones en el material. Uso indicado: medir volatilidad. Fuentes: `INDICADORES_TOP_7` y `VWAP_VS_EMA_BOLLINGER` (contexto).
- **Dónde verlo:** no definido.

### MACD
- **Configuración:** sin parámetros en el material. Uso indicado: señales de compra y venta, sin regla de cruce precisa. Fuente: `INDICADORES_TOP_7` (contexto).
- **Dónde verlo:** no definido.
