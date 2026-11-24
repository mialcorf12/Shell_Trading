# SESIONES_7H_C2_C3: Dirección de la Siguiente Sesión con Velas de 7 Horas (C1 / C2 / C3 / C4) en NQ/MNQ

## Estado: BLOQUEADA — falta el criterio de clasificación C1 / C2 / C3
La estrategia no es operable hasta que se defina cómo se asigna cada rol a una vela de 7 horas. Antes de esa definición, cualquier backtest tomaría una regla inventada.

- **Qué dice el material fuente (Ideas/SESIONES_7H_C2_C3_01.md):** C1, C2 y C3 indican el cierre de la sesión al cabo de 7 horas. C4 es el movimiento potencial posterior. Los casos de abajo se expresan con esos roles.
- **Qué no dice:** el criterio que separa C1 de C2 y de C3 a partir de precios. Sin ese criterio no hay forma de etiquetar una vela.
- **Qué se descartó:** una versión anterior de esta estrategia definía C2 como barrido y cierre de vuelta, y C3 como ruptura del lado opuesto. Ese criterio no está en el material fuente y se retira.

---

## 1. Hipótesis (según el material fuente)
Cada sesión mayor (Asia, Londres, Nueva York) se resume en una vela de 7 horas. El rol de la vela al cerrar indica el movimiento probable de la siguiente sesión.

## 2. Ventanas de Sesión (hora de Nueva York)
- **Asia:** 18:00–01:00 ET.
- **Londres:** 01:00–08:00 ET.
- **Nueva York:** 08:00–15:00 ET.

Las ventanas son de 7 horas por vela. El video menciona también "08:00 a 18:00", que daría 10 horas; esa inconsistencia no se resuelve aquí.

## 3. Casos (reglas del material fuente)
- **Caso 1:** Asia es C2 → Londres C3 suele continuar; Nueva York C4 puede continuar o revertir.
- **Caso 2:** Londres es C2 → Nueva York suele ser C3 y continúa el movimiento de Londres.
- **Caso 3:** Asia y Londres no aportan → Nueva York será el C2.

Las reglas de caso son operables solo cuando el criterio de la sección "Estado" esté definido.

## 4. Entradas Propuestas (pendientes de validación)
- **Caso 1:** entrada a la apertura de Londres (01:00 ET), en la dirección que indique el criterio de C2 de Asia.
- **Caso 2:** entrada a la apertura de Nueva York (08:00 ET), en la dirección que indique el criterio de C2 de Londres.
- **Caso 3:** sin operación en esta versión. El material no define el siguiente movimiento tras el C2 de Nueva York.

El sentido de la operación en cada caso depende del criterio pendiente; no se fija aquí.

## 5. Gestión de Riesgo (cuando el criterio esté definido)
- **Stop:** más allá del extremo que define el rol de C2 (criterio pendiente), con 2 ticks de margen. Máximo 30 puntos NQ ($60 MNQ).
- **Objetivo:** pendiente. El material fuente no define objetivo ni salida.
- **Riesgo:** máximo 0.75% del trailing drawdown real; máximo 1 operación por día; flat antes de las 15:55 ET; sin promediar ni ampliar stop.

## 6. Validación Pendiente
- Definir el criterio de C1, C2 y C3 (y, si aplica, C4) a partir de precios de la vela de 7 horas.
- Definir la salida: el material no la da.
- Backtest con costos reales ($0.62/lado MNQ, $2.10/lado NQ) y slippage de 1–2 ticks en las aperturas de 01:00 y 08:00 ET.
- Muestra mínima: ≥ 100 operaciones por caso, con resultados separados.

## 7. Arquitectura NinjaTrader 8 (cuando esté definida)
- Velas de 7 horas construidas en `OnBarUpdate` a partir de datos de 1 minuto, con los cortes de la sección 2.
- Clasificación de rol al cierre de cada vela de 7 horas, según el criterio definido.
- `SetStopLoss` y `SetProfitTarget` por precio tras la entrada.

---

## Referencias
- Ideas: [[SESIONES_7H_C2_C3_01]]
- Fuentes y research:
  - Publicación de origen (@reel DfvLuIhuPos, cuenta "Vincit Trades"): velas de 7 horas por sesión y roles C1–C4 (educativo, sin estadística ni criterio de clasificación).
  - jira/trading_agent_persona.md: Hipótesis antes que código, validación y trailing drawdown.
