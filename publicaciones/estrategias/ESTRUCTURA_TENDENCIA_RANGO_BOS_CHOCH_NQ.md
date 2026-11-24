# ESTRUCTURA_TENDENCIA_RANGO_BOS_CHOCH_NQ: Lectura de Estructura de Mercado (Tendencia, Rango, BOS, CHoCH) en NQ/MNQ

## 1. Hipótesis Operativa
La estructura de mercado es el registro de máximos y mínimos de swing que deja el precio. Se clasifica en tres estados:

- **Tendencia alcista:** máximos más altos (HH) y mínimos más altos (HL). Tendencia bajista: LH y LL.
- **Rango:** el precio rota entre máximos iguales y mínimos iguales; la liquidez se acumula en los extremos.

Dos eventos cambian el estado:

- **BOS (Break of Structure):** un cierre de vela supera el último swing a favor de la tendencia. Confirma la continuación.
- **CHoCH (Change of Character):** un cierre de vela rompe el último swing de la tendencia en contra. Es un aviso de posible cambio, no una confirmación.

La hipótesis: **operar la continuación tras un BOS, y tratar el CHoCH como cambio de sesgo solo cuando la nueva secuencia (LH + LL o HL + HH) se confirma.** Un quiebre por mecha no cuenta como evento: solo un cierre de vela.

---

## 2. Definiciones Medibles (eliminan la ambigüedad del concepto)
- **Swing high:** máximo de la vela central de una ventana de 5 velas (2 velas a cada lado con máximo inferior). **Swing low:** simétrico.
- **Cierre que rompe:** cierre de vela (no mecha) por encima del swing high (o debajo del swing low).
- **BOS alcista:** cierre por encima del último swing high dentro de una tendencia alcista.
- **CHoCH bajista (en tendencia alcista):** cierre por debajo del último swing low (HL) que produjo la tendencia alcista.
- **Rango:** al menos 2 máximos y 2 mínimos dentro de ±0.5% de su nivel medio, sin BOS en las últimas 6 velas de la temporalidad de análisis.

Esta definición de swing (5 velas) es una decisión de implementación del autor de la estrategia; debe validarse porque el video no la define.

---

## 3. Parámetros de Mercado e Instrumentos
- **Contratos:** MNQ ($2.00/punto) para ejecución; NQ ($20.00/punto) con riesgo acotado al colchón de drawdown.
- **Sesión:** RTH (09:30–16:00 ET). Ventana preferida: 09:45–11:30 ET y 13:30–15:30 ET.
- **Temporalidades:** contexto de estructura en 1 hora o 4 horas; ejecución en 5 minutos.

---

## 4. Reglas de Entrada

### Continuación (BOS a favor de la tendencia):
1. Estructura de 1H o 4H en tendencia alcista (HH + HL confirmados).
2. Retroceso que forma un nuevo HL sin cerrar por debajo del HL anterior.
3. Gatillo en 5 min: un cierre de vela que supera el último swing high de 5 min tras el retroceso (BOS de 5 min en la dirección del sesgo).
4. Entrada: compra a mercado al cierre de la vela de BOS de 5 min.

### Cambio de sesgo (CHoCH confirmado):
1. Tendencia alcista previa; se produce un CHoCH bajista (cierre por debajo del último HL).
2. **No entrar en el CHoCH.** Esperar la nueva secuencia bajista: un LH que no supera el máximo previo, seguido de un cierre por debajo del último LL de 5 min.
3. Entrada corta al cierre de la vela que confirma el LL. Sin esa secuencia, no hay operación.

### Rango:
- No operar la continuación. Solo esperar la ruptura con cierre; el video lo resume como "espera la ruptura, no la adivines".

---

## 5. Gestión de Riesgo y Salida
- **Hard Stop Loss:** más allá del último swing de la estructura de entrada (en largo, debajo del HL de 5 min), con 2 ticks de margen. Máximo 30 puntos NQ ($60 MNQ). El video sugiere "más allá del último swing" sin distancia; el tope de 30 puntos es propio.
- **Take Profit:**
  - TP1 (50%): en el máximo de la pierna previa (último HH de 1H o 4H).
  - TP2 (50%): extensión de 2 R, o siguiente nivel de liquidez externa. Ratio mínimo 1:2 sobre el stop.
- **Break Even:** al llenarse TP1, stop del resto a +2 ticks.
- **Invalidación:** cierre de vela de 5 min por debajo del último HL tras la entrada alcista (BOS invalidado).

---

## 6. Reglas de Cuenta Fondeada (Prop Firm Compliance)
- **Riesgo por operación:** máximo 0.75% del trailing drawdown real. Ejemplo: $2,000 de DD → $150 de riesgo → con stop de 20 puntos en MNQ ($40/contrato), 3 contratos.
- **Máximo 2 operaciones por día.** Tras un stop, esperar un nuevo BOS (no reentrar en el mismo swing).
- **Sin promediar ni ampliar stop.**
- **Cierre forzoso:** flat antes de las 15:55 ET.

---

## 7. Honestidad Estadística y Validación Pendiente
- El material fuente es una publicación promocional (carrusel con llamado a una guía de pago). Tiene el hook "sin indicadores, solo precio", pero no entrega reglas completas, precios ni estadística. Dos de sus slides no tuvieron contenido legible en la primera descarga; el contenido completo se leyó después de extraer los videos animados.
- La clasificación de swing (5 velas) y el tope de 30 puntos son propios.
- Backtest con costos reales ($0.62/lado MNQ, $2.10/lado NQ) y slippage de 1–2 ticks.
- Walk-forward para validar la definición de swing y la regla de CHoCH con secuencia confirmada.
- Muestra mínima: ≥ 100 operaciones. Separar resultados de continuación y de cambio de sesgo.

---

## 8. Arquitectura NinjaTrader 8 (NinjaScript)
- Series: 1 hora o 4 horas (estructura), 5 minutos (ejecución).
- Detección de swings con la regla de 5 velas en `OnBarUpdate`; registro de HH, HL, LH, LL en variables de estado.
- Máquina de estados: `Clasificar_Estructura → Tendencia | Rango → Esperar_Retroceso → BOS_Confirmado → EnPosicion → Cerrado`. CHoCH pasa a `Esperar_Secuencia_Opuesta`.
- `SetStopLoss` y `SetProfitTarget` por precio tras la entrada.

---

## Referencias
- Ideas: [[ESTRUCTURA_TENDENCIA_RANGO_BOS_CHOCH_NQ_01]]
- Fuentes y research:
  - YMI Blog (Cameron Bennion): CHoCH y BOS para futuros (distinción entre ambos y error de llamar cambio a toda ruptura).
  - Tickwise Funding (Raphael): market structure para futuros; el cierre define la ruptura, no la mecha.
  - TradingLab: market structure (CHoCH y BOS).
  - jira/trading_agent_persona.md: Reglas de riesgo, validación y trailing drawdown.
