# Reel: método de 4 pasos con sincronización de temporalidades (borrador)

Fuente: https://www.instagram.com/reels/DdzVsutv3AQ/
Alcance: transcripción (31 líneas) + 4 de 45 frames revisados. Resumen de subagente: verificar contra el video.
Estrategia sugerida: ESTRUCTURA_LIQUIDEZ_CONFIRMACION_FVG (el paso de sincronización es el núcleo).

## Reglas del video
1. **Estructura** en 4 h: un mínimo más bajo y un máximo más bajo = tendencia bajista.
2. **Liquidez** una temporalidad abajo (1 h para estructura de 4 h; 30 o 15 min si 1 h no muestra nada). Los máximos casi iguales cuentan como liquidez; el objetivo está por encima.
3. **Confirmación:** tras el barrido, marcar el último impulso en 1 o 3 min. Su quiebre con cuerpo de vela confirma el cambio de dirección (mechas no alcanzan).
4. **Entrada:** el quiebre debe dejar un FVG; zona de entrada = todo el FVG (si es muy grande, al 50%). Stop por encima del FVG. Objetivo: mínimo de 1 h o 15 min, ineficiencias o mínimos casi iguales.
- Tabla "Sincronización de temporalidades": mapea cada estructura a su estructura interna, temporalidad de liquidez y de confirmación (mensual, semanal, diaria, horaria, 15 min).

## SINCRONIZACION DE TEMPORALIDADES 
| ESTRUCTURA PRINCIPAL | ESTRUCTURA INTERNA | LIQUIDEZ | CONFIRMACION |
| MENSUAL | 1 SEM / 1D | 1D | 4H |
| SEMANAL | 1D / 4H | 4H | 1H /15M |
| DIARIO | 2H / 1H | 1H | 15M / 5M / 3M |
| HORARIA | 15M / 5M | 5M | 3M / 1M |
| 15 MINUTOS  | 3М | 1M | 1M / SEGUNDOS |

## Pendiente de depurar
- Inconsistencia: el narrador dice liquidez en 1 h para estructura de 4 h, pero la tabla empareja estructura 4 h (dentro de semanal) con liquidez 4 h. Sin resolver.
- Ejemplo: NQ, 4 h, 15 dic 2025; trade corto con R:R 4,52 (ejemplo puntual, no estadística).
- Transcripción dudosa: "conmecha" (con mecha), "quebril" (quiebre), "FBG" (FVG).

## Referencias
- Estrategia: [[ESTRUCTURA_LIQUIDEZ_CHOCH_FVG]]
- Draft: [[reel_DdzVsutv3AQ]]
