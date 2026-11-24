# Reel: ORB probado fuera de la apertura de NY, en MNQ (borrador)

Fuente: https://www.instagram.com/reels/DefhNnsz8hP/
Alcance: transcripción (12 líneas) + 4 frames revisados. Resumen de subagente: verificar contra el video.
Estrategia sugerida: ORB_MULTI_SESSION (o ORB_RANGO_15M).

## Tesis
El ORB es el mismo bot con las mismas reglas aplicado a distintos horarios; el autor sostiene que la ventaja viene de las reglas, no de la hora.

## Reglas (inferidas del dibujo; el video no las dice)
- Rango de 15 min. Compra si rompe arriba ("ORB Long"); vende si rompe abajo ("ORB Short"). Take profit fijo ("ORB TP").

## Resultados mostrados (backtest en TradingView, MNQ 5 min, cuenta de $100k)
- Rango nocturno 1:00–1:15 ET: 90 días, 61 trades, 75% ganadores, más de $26k.
- Rango 9:15–9:30 (antes de la apertura): 1 año, 376 trades, $74k.

## Pendiente de depurar
- Sin win rate, drawdown ni stop/TP exactos.
- No se aclara si los montos son netos de comisiones ni cuántos contratos.
- Backtest sin validación fuera de muestra: no tomar como expectativa.
- Transcripción dudosa: "Orp" (ORB), "Yo lo provee" (yo lo probé).

## Referencias
- Estrategia: [[ORB_MULTI_SESSION]]
- Draft: [[reel_DefhNnsz8hP]]
