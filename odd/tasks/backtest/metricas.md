Aquí tienes una lista directa y práctica de estadísticas para evaluar tu backtest, separada entre las **imprescindibles** y las **de control fino**:

### Esenciales (las primeras que debes revisar)

* **Net Profit (después de comisiones y slippage):** Resultado neto real de la muestra.
* **Profit Factor:** Ganancia bruta dividida entre pérdida bruta. Busca que supere **1.2** en sistemas activos y **1.5+** con costos realistas.
* **Expectancy (Expectativa matemática por trade):** Ganancia o pérdida promedio esperada por operación (o por unidad de riesgo $R$) tras costos. Tiene que ser positiva.
* **Win Rate (% de aciertos):** Porcentaje de trades ganadores; siempre léelo junto al *Payoff Ratio*.
* **Payoff Ratio (Reward-to-Risk promedio):** Ganancia promedio entre pérdida promedio. Define cuánto necesitas ganar por trade para compensar las pérdidas.
* **Max Drawdown (MDD):** Caída máxima desde un pico de equidad hasta el valle siguiente. Mide tu peor golpe histórico.

### De control fino (para validar estabilidad y evitar sorpresas)

* **Time to Recovery:** Cuánto tarda la curva de equidad en volver a superar el máximo previo tras un *drawdown*.
* **Max Consecutive Losses:** Racha máxima de pérdidas seguidas para calcular exposición y aguante.
* **Concentración de ganancias (Top 1 / Top 3 / Top 5 trades):** Qué porcentaje del beneficio total depende de tus mejores operaciones.
* **Sharpe Ratio y Sortino Ratio:** Rendimiento ajustado por volatilidad total (Sharpe) y por volatilidad a la baja (Sortino).
* **MAE y MFE:** Qué tanto va el precio en contra (*Maximum Adverse Excursion*) y a favor (*Maximum Favorable Excursion*) dentro de cada trade para ajustar stops y targets.
* **Rendimiento por periodo / régimen:** Resultados separados por mes, sesión/hora o condiciones de volatilidad para detectar tramos tóxicos.
* **Total de trades:** Tamaño de muestra suficiente para que las métricas anteriores tengan peso estadístico.