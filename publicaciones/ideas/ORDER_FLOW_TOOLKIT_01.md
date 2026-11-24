# Reel: seis herramientas de order flow en NQ (borrador)

Fuente: https://www.instagram.com/reels/Df774wjqXIV/ (TraderDeConfianza)
Alcance: video completo (transcripción local + 4 frames revisados). Resumen de subagente de lectura: verificar contra el video antes de promover.
Estrategia sugerida: ORDER_FLOW_TOOLKIT (no es FVG ni VOLUMEN_RUPTURA).

## Tesis
Lista de seis herramientas de order flow para NQ. No es una estrategia con reglas de entrada o salida: muestra qué informa cada una sobre quién está ganando.

## Herramientas
1. **Volumen:** un movimiento con poco volumen es ruido; con volumen alto, hay convicción.
2. **VWAP:** precio de referencia institucional. Por encima, ganan compradores; por debajo, vendedores. Comprar lejos de VWAP es pagar de más.
3. **TPO:** el precio tiende a volver a donde pasó más tiempo (valor). Los niveles atravesados rápido no tuvieron interés. Sirve para ubicar el value area y el POC.
4. **Delta / delta %:** compras agresivas menos ventas agresivas. Si el delta empuja y el precio no se mueve, hay absorción.
5. **DOM / heatmap:** muestra liquidez en límites; el precio frena o rebota en esos "muros", que también pueden retirarse.
6. **Footprint:** volumen bid × ask por precio en cada vela. Revela absorción, desequilibrios y trampas.

## Pendiente de depurar
- Sin umbrales, reglas de entrada, stop, target ni timeframe: no hay nada concreto para backtest.
- Transcripción dudosa: "bigwap" (VWAP), "FODPRINT" (footprint), "DOMSORFACE" (DOM/heatmap, sin confirmar).
- Cuál de las seis herramientas aporta la hipótesis principal para una estrategia.

## Referencias
- Contexto: [[ORDER_FLOW_TOOLKIT]]
- Draft: [[reel_Df774wjqXIV]]
