# Dashboard de backtest · estrategias deberia

Muestra `../resultados.csv` (una fila por corrida) con el veredicto del checklist.
Solo lee el CSV: no escribe nada ni llama a TradingView.

Una corrida = estrategia x TP/SL x contratos (1 a 4). La tabla tiene la columna
**Contratos** y el filtro **Contratos** (todos, 1, 2, 3, 4), y el filtro **TP** (todos, $100, $200, $300, $600, $1000, $1500), junto a Estrategia y
Veredicto. TP/SL en USD totales de la operacion; con N contratos la distancia en
puntos se divide entre N y el PnL y la comision escalan por N. La API
(`/api/results`) devuelve `contratos` como número entero y acepta
`?contratos=N` para filtrar. El veredicto usa los mismos umbrales para todo N.

Símbolo: la tabla tiene la columna **Símbolo** y el filtro **Símbolo** (MNQ). Las filas NQ no se muestran.

Años: cada corrida usa una ventana de historial (`anos` en el CSV): 6 = historia
completa, 3 y 1 = últimos años hasta la última vela (inicio = fecha de la última
vela menos N años). Solo se toman operaciones que abren dentro de la ventana; los
indicadores usan toda la historia para calentarse. La tabla tiene la columna
**Años** (después de Símbolo) y el filtro **Años** (todos, 6, 3, 1). La API
devuelve `anos` como entero y acepta `?anos=N`. `periodo` es el rango de fechas
operado (primera..última operación). El veredicto no cambia con la ventana.

## Estrategias recomendadas

Acordeón **Estrategias recomendadas** arriba de la tabla, cerrado por defecto. Al
abrirlo (y con **Recargar**) pide `/api/recommended`, que se calcula en cada pedido
desde `../resultados.csv`: al sumar backtests, el ranking se actualiza solo. Hay un
bloque por cada TP presente en los datos (orden numérico, sin lista fija) con las 5
mejores opciones.

- Grupo = (estrategia, SL, contratos) dentro del TP. Solo entra si tiene las tres
  ventanas (6, 3 y 1 años); los grupos incompletos no se rankean.
- Orden: ventanas con veredicto aprueba (desc), ventanas con neto > 0 (desc), PF
  mínimo de las tres ventanas (desc), Sharpe mínimo (desc). Un mínimo sin dato va al
  final; empate final por estrategia, SL y contratos.
- Columnas: Estrategia, SL $, Contratos, Aprueba (de 3años), Neto 6a / 3a / 1a $ (siempre
  las tres ventanas), y Win %, PF, Expectancy $, Net $, Racha pérd., Sharpe, Top3 % y
  Veredicto de la ventana elegida. Sin MDD.
- Selector **Años para detalle** (6 por defecto, 3, 1): solo cambia la ventana de las
  columnas de detalle; el ranking no cambia.

API: `{"por_tp": {"100": [{"estrategia", "tp_usd", "sl_usd", "contratos", "aprueba",
"neto_by_anos": {"6", "3", "1"}, "detalle": {"6": {...}, "3": {...}, "1": {...}}}], ...}}`;
valores faltantes como `null`.

## Cómo correrlo

```bash
cd indicadores/backtest/stats/app
python3 -m pip install -r requirements.txt
python3 server.py
```

Abre `http://127.0.0.1:5002/`.

## Cómo cargar resultados

1. Corré la estrategia en TradingView (Strategy Tester) con TP/SL de la fila.
2. Copiá las métricas en la fila correspondiente de `../resultados.csv`
   (`simbolo`, `estrategia`, `tp_usd`, `sl_usd`, `contratos`, `anos` identifican la corrida).
3. Recargá el dashboard.

Las filas sin `trades` figuran como **pendiente**.

## Veredicto

Umbrales de `odd/tasks/indicadores/backtest/checklist.md`:

| Métrica | Umbral |
|---|---|
| trades | ≥ 100 |
| net_profit_usd | > 0 |
| profit_factor | ≥ 1.25 |
| expectancy_usd | > 0 |
| sharpe | ≥ 1.0 |
| top3_pct | ≤ 50 (supuesto propio) |

- **aprueba**: cumple todos.
- **descarta**: no cumple alguno.
- **incompleto**: falta un dato.
- **pendiente**: sin corrida cargada.

## Tests

```bash
cd indicadores/backtest/stats/app
python3 -m pytest -q
```
