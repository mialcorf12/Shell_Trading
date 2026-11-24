# Reel: doble VWAP (diario y de apertura de NY) como filtro de sesgo (borrador)

Fuente: https://www.instagram.com/reels/DezSdzPxj6N/
Alcance: transcripción (12 líneas) + 4 frames revisados. Resumen de subagente: verificar contra el video.
Estrategia sugerida: DOBLE_VWAP_DIARIO_NY (no es VWAP_REVERSION_AGOTAMIENTO: no hay setup de agotamiento).

## Tesis
Dos VWAP como filtro: el diario (ancla 18:00) refleja el precio justo de toda la jornada; el de apertura de NY (ancla 9:30) reacciona más rápido. Ambos encima = sesgo comprador; ambos debajo = vendedor.

## Reglas del video
- Precio encima de los dos VWAP: comprador en control. Debajo de ambos: vendedor.
- Si el precio está entre los dos y están bien separados, operar desde uno hacia el otro.
- Entrada: una vela que cierra con cuerpo más allá del VWAP. Ejemplo en pantalla: compra con cierre de cuerpo sobre el VWAP de NY, objetivo en el VWAP diario.

## Pendiente de depurar
- Sin stop ni target exactos.
- "Bien separados" sin umbral.
- Zona horaria de las 18:00 asumida como ET.
- Sección 3 (probablemente "el de NY") no vista en los frames.
- Transcripción dudosa: "bigwap" (VWAP), "¿Cómo lo suyó?" (¿cómo los uso?).

## Referencias
- Estrategia: [[DOBLE_VWAP_DIARIO_NY]]
- Draft: [[reel_DezSdzPxj6N]]
