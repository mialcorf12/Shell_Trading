# Reel: barrido del rango de la vela de 8 AM con nivel clave e iFVG de 1 min (borrador)

Fuente: https://www.instagram.com/reels/DeMw3u0t1YW/
Alcance: transcripción (32 líneas) + 4 frames revisados. Resumen de subagente: verificar contra el video.
Estrategia sugerida: RANGO_8AM_BARRIDO_IFVG (parecida a IFVG_LIQUIDEZ_1A1, pero el eje es el rango de 8 AM).

## Tesis
El rango de la vela horaria de las 8 AM define dos extremos. Un barrido de un lado hasta un nivel clave es el disparador; la operación busca el extremo opuesto.

## Reglas del video ("3 pasos", no operar si no se cumplen los tres)
1. En 1H: marcar máximo y mínimo de la vela de 8:00.
2. Buscar un nivel clave cerca de esos extremos: un máximo previo de 1H apenas arriba, o mínimos casi iguales apenas abajo.
3. Esperar que el precio barra un lado del rango y toque el nivel clave; operar hacia el extremo opuesto.
- Entrada en 1 min: un cierre a través de un FVG pequeño lo vuelve iFVG; el cierre bajo la última vela alcista forma un order block bajista. iFVG + OB dan la entrada corta.
- Stop: arriba de los máximos del barrido. Target final: el extremo opuesto del rango de 8 AM.

## Pendiente de depurar
- Sin instrumento explícito (el stop "3,7 (0,03%)" sugiere un índice).
- Zona horaria de "8 de la mañana" sin confirmar (probablemente NY).
- No se aclara si el nivel clave debe tocarse o solo acercarse.
- Sin TP parciales ni R:R mínimo.
- Transcripción dudosa: "IFWG" (IFVG), "bela" (vela), "soco" (tocó).

## Referencias
- Estrategia: [[RANGO_8AM_BARRIDO_IFVG]]
- Draft: [[reel_DeMw3u0t1YW]]
