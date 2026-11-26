Aquí tienes un *checklist* práctico con **umbrales orientativos** para filtrar una estrategia en un *backtest*. Tómalos como referencia de trabajo —no como reglas rígidas— porque el número ideal cambia según el instrumento, el *timeframe*, el estilo (intradía vs. *swing*) y las reglas de riesgo o evaluación de cada cuenta:

### 1. Filtro mínimo de viabilidad y muestra

* [ ] **Total de trades:** Al menos **100 a 200+ operaciones** (idealmente cubriendo distintos regímenes de volatilidad y horarios). Con pocas operaciones, un par de rachas distorsionan todo.
* [ ] **Costos incluidos:** Comisiones completas, *fees* y *slippage* realista ya descontados antes de leer cualquier métrica.
* [ ] **Net Profit:** Positivo tras todos los costos.

### 2. Ventaja matemática (Edge)

* [ ] **Profit Factor:** **Mayor o igual a 1.25 – 1.30** como piso en sistemas activos; **1.50+** para mayor margen frente a deslizamiento y ejecución en vivo.
* [ ] **Expectancy (por trade o en $R$):** Positiva de forma clara tras costos (por ejemplo, **mayor o igual a +0.10R a +0.20R** por trade en sistemas intradía/activos).
* [ ] **Win Rate vs. Payoff Ratio:** Coherentes entre sí y por encima del punto de equilibrio matemático ($\text{Win Rate mínimo} = 1 / (1 + \text{Payoff})$), dejando margen de seguridad para ejecución real.

### 3. Riesgo, caídas y aguante

* [ ] **Max Drawdown (MDD):** Acorde a tu tolerancia y a tus límites de pérdida o reglas de *trailing drawdown* (por ejemplo, que el peor *drawdown* histórico represente un porcentaje cómodo de tu margen/colchón y no roce el límite de cuenta en una racha normal).
* [ ] **Max Consecutive Losses:** La peor racha de pérdidas seguidas multiplicada por tu riesgo por trade no debe comprometer tu capital ni tu disciplina operativa.
* [ ] **Time to Recovery:** Que la curva de equidad recupere máximos anteriores en un lapso razonable para tu horizonte, sin quedar estancada eternamente.

### 4. Estabilidad y ausencia de sobreajuste

* [ ] **Concentración de ganancias:** Que los **mejores 1 a 5 trades** no expliquen la mayor parte del beneficio neto (por ejemplo, evitar que quitar el top 3 o top 5 deje la estrategia en negativo o en *breakeven*).
* [ ] **Estabilidad por periodo / sesión:** Que los resultados no dependan de un solo mes excepcional o de una ventana horaria aislada con comportamiento anómalo.
* [ ] **Sharpe / Sortino Ratio:** Valores positivos sólidos (por ejemplo, **Sharpe mayor o igual a 1.0** y **Sortino superior** en sistemas bien comportados, evitando picos irreales que sugieran *overfitting*).

---

### Cómo usarlo en la práctica

1. **Descarte rápido:** Si falla en **costos**, **tamaño de muestra**, **Expectancy** o **Profit Factor**, descarta o revisa la lógica antes de optimizar nada.
2. **Revisión de riesgo:** Si pasa la ventaja, revisa **MDD**, **rachas perdedoras** y **concentración de top trades** para ver si aguanta psicológicamente y bajo tus reglas de riesgo.
3. **Validación final:** Solo si pasa lo anterior, pruébala fuera de muestra (*out-of-sample* / *walk-forward*) o en un entorno controlado antes de escalar.