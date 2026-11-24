# entorno general:
en todo momento quiero usar trading_agent_persona.md

# model routing
• Tareas rápidas, tiempo real y bajo costo (Claude Haiku 5.5): Ideal para respuestas inmediatas, preguntas cotidianas, clasificación, resúmenes breves y subagentes que ejecutan pasos simples.
• Trabajo diario, código y redacción (Claude Sonnet 5.5): Ofrece el mejor balance entre velocidad, capacidad y costo para programar a diario, revisar código, redactar documentos o presentaciones y ejecutar flujos con pasos claros.
• Ingeniería compleja y trabajo pesado (Claude Opus 5.5): Recomendado para programación agéntica avanzada, refactorización grande, arquitectura y análisis donde un error resulta costoso.
• Problemas de máxima ambigüedad y larga duración (Claude Fable 5.2): Pensado para investigación exhaustiva, análisis de datos complejos y agentes autónomos que operan durante horas.

# Proyecto:
vamos a trabajar un nuevo proyecto llamado 'Shell_Trading'. 

## feature:'ideas de estrategias'.
vamos a tener 2 carpetas Ideas y Estrategias. Ideas/Draft es para yo incluir el resumen de reels que haya encontrado en internet. a partir de estos reels, necesito depurar/mejorar el contenido para trabajar los archivos en estrategias. puedo tener 100 ideas del mismo tema de estrategia, para un mismo archivo de estrategia (ejemplo 100 archivos en Ideas que hablen de FVG, pero solo 1 archivo de FVG en Estrategias). la idea es depurar/mejorar con el tiempo ese archivo de estrategias. Aunque una idea use los mismos indicadores de trading, debemos agruparlas con forme al nombre de la estrategia (ejemplo: una idea puede contener el indicador EMA9, pero si se indica que es parte de la estrategia ORB, entonces se debe de hacer unicamente esta relacion. Para mantener ambos directorios limpios, vamos a crear el folder Ideas/Draft, aqui es donde se incluirian las "ideas sucias/borrador", y cuando se mejoren (se mueven al folder Ideas, con nombre similar a ORB_NY_01.md etc, estas relacionadas con la Estrategia ORB_NY.md ). conserva al final de los archivos md la referencias entre estrategias e ideas, asi como en draft, la referencia al archivo en ideas y viceversa.
En python quiero que armes una interfaz web que me permita gestionar el orden del directorio (ejemplo ideas sin revision (folder draft), Ideas depuradas (folder ideas), estrategias (estrategias) ) y de una forma visual, facil e intuitiva me permitas entender la relacion entre los archivos, algo similar a un mindmap de obsidian. dame la opcion con un boton de limpiar ideas/draft, esto seria, que me ayudes a redactar mejor el contenido de draft y crear un nuevo archivo idea (no olvides de generar la relacion entre los archivos de Ideas y Ideas/Draft)