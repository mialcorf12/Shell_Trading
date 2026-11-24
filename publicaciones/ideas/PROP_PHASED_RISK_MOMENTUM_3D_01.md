# Reel: sistema NASDAQ con riesgo por fase de cuenta fondeada (borrador)

Fuente: https://www.instagram.com/reels/Df5-uI2gpAM/
Alcance: transcripción (11 líneas) + 4 de 28 frames revisados. Resumen de subagente: verificar contra el video.
Estrategia sugerida: PROP_PHASED_RISK_MOMENTUM_3D.

## Tesis
La regla de entrada no cambia; cambian solo el riesgo y el objetivo diario según la fase de la cuenta (evaluación, primer día fondeado, hasta el primer pago, después de cada pago).

## Reglas del video
- Entrada a las 9:30: si el cierre de ayer es mayor que el cierre de hace 3 días, comprar; si no, vender. Stop de 50 puntos.
- Evaluación: riesgo $2.000 con objetivo diario $1.500.
- Primer día fondeado: riesgo $2.000 con objetivo $4.000.
- Hasta el primer pago: riesgo $1.000 con objetivo $625 diarios.
- Después de cada pago: riesgo $1.200 con objetivo $480.

## Advertencia (ODD / persona de trading)
- El resultado mostrado es in-sample: el propio video admite que los ajustes de riesgo se calibraron con los mismos datos.
- No hay walk-forward ni holdout fuera de muestra, así que no es una expectativa de rendimiento.
- Cifras declaradas: 149 evaluaciones compradas, 45 aprobadas, 42 pagos, neto $54.695 entre enero 2024 y julio 2026.
- Costos: el video dice que incluye comisiones; no se especificaron slippage ni fechas de corte.

## Pendiente de depurar
- Transcripción dudosa: "se roa arriba" (cerró arriba), "me esperdió" (me perdió), "el mes típico de jamil 255" (ilegible).
- Fecha "julio de 2026" a validar.
- Validar con datos propios antes de cualquier uso.

## Referencias
- Estrategia: [[PROP_PHASED_RISK_MOMENTUM_3D]]
- Draft: [[reel_Df5-uI2gpAM]]
