# Post: day-trader-skill, ORB en TSLA con stop al medio del rango y 1R (borrador)

Fuente: https://www.instagram.com/p/De-_AcTjbbr/
Alcance: 9 slides leídas + caption. Resumen de subagente: verificar contra las slides.
Estrategia sugerida: ORB_STOP_MEDIO_RANGO_1R (no es igual a ORB_MULTI_SESSION ni ORB_FALLO_VWAP).

**Advertencia:** es una demo de herramienta de terceros (11 skills de Claude, mismo tema que `reel_DfB5uzwkiN7`/`reel_DfpYB3UnLDm`, ya descartados). El propio post dice que su simulación da "casi cara o cruz".

## Setup del ejemplo (TSLA 5 min)
- Rango de apertura 354,47–362,18. Entrada 364,18 (cierre de la vela de ruptura). Stop 358,32 (medio del rango). Objetivo 370,04 = 1R. Salir antes de la campana.
- Simulación: 29,4% objetivo, 25,5% stop, 45,1% abiertos al cierre.
- 59 sesiones reales: 33 disparos, 13 ganadores (~39% a 1R).

## Pendiente de depurar
- Largo del rango no indicado (visualmente ~30 min).
- "10:10": ¿apertura o cierre de la vela?
- Hora exacta de salida antes de la campana no dada.
- Qué verifica el escáner y el disparador del trader: no se muestra.
- Estrellas y forks del repo: de una captura, no verificados.

## Referencias
- Estrategia: [[ORB_STOP_MEDIO_RANGO_1R]]
- Draft: [[post_De-_AcTjbbr]]
