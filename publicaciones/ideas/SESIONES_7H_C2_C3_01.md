# Reel: dirección diaria con velas de 7 horas (C2/C3 por sesión) (borrador)

Fuente: https://www.instagram.com/reels/DfvLuIhuPos/ (cuenta "Vincit Trades")
Alcance: transcripción corta (11 líneas) + 4 frames revisados. Resumen de subagente: verificar contra el video.
Estrategia sugerida: SESIONES_7H_C2_C3.

## Tesis
Usar el gráfico de 7 horas, donde cada sesión (Asia, Londres, Nueva York) es una sola vela. Según el rol de cada vela (C2 o C3), inferir la dirección de la siguiente sesión.

## Reglas del video
- Temporalidad: 7 horas, no 15m, 1H, 4H ni diario.
- Aperturas en hora de Nueva York: Asia 18:00, Londres 01:00, Nueva York 08:00.
 - C1, C2 y C3 indican el cierre de la sesión al cabo de 7 horas. C4 potencial movimiento.
- Caso 1: si Asia es C2, Londres C3 suele continuar; Nueva York C4 puede continuar o revertir.
- Caso 2: si Londres es C2, Nueva York suele ser C3 y continúa el movimiento de Londres.
- Caso 3: si Asia y Londres no aportan nada, Nueva York será el C2.

## Pendiente de depurar
- Sin regla de invalidación ni de salida.

## Referencias
- Estrategia: [[SESIONES_7H_C2_C3]]
- Draft: [[reel_DfvLuIhuPos]]
