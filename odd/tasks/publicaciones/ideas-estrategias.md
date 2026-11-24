# Feature: ideas-estrategias
Repo: Shell_Trading. Branch: feature/ideas-estrategias. Stack: Python 3 + Flask, JS vanilla, Cytoscape.js (CDN), Claude API for the cleanup button.
Persona for every LLM call and agent task: jira/trading_agent_persona.md.

## Specs
- S1: "vamos a tener 2 carpetas Ideas y Estrategias"; "vamos a crear el folder publicaciones/ideas/draft, aqui es donde se incluirian las 'ideas sucias/borrador'".
- S2: "cuando se mejoren (se mueven al folder Ideas, con nombre similar a ORB_NY_01.md etc, estas relacionadas con la Estrategia ORB_NY.md)". Idea file name = <STRATEGY>_<NN>.md; strategy = name without the _NN suffix.
- S3: "puedo tener 100 ideas del mismo tema de estrategia, para un mismo archivo de estrategia (ejemplo 100 archivos en Ideas que hablen de FVG, pero solo 1 archivo de FVG en Estrategias)"; "Aunque una idea use los mismos indicadores ... entonces se debe de hacer unicamente esta relacion." Relation is by strategy name only, never by indicator.
- S4: "conserva al final de los archivos md la referencias entre estrategias e ideas, asi como en draft, la referencia al archivo en ideas y viceversa." References live in a final section `## Referencias` of each md.
- S5: "armes una interfaz web que me permita gestionar el orden del directorio (ejemplo ideas sin revision (folder draft), Ideas depuradas (folder ideas), estrategias (estrategias))". Web UI must move files between the three folders and create strategies.
- S6: "de una forma visual, facil e intuitiva me permitas entender la relacion entre los archivos, algo similar a un mindmap de obsidian". Visual graph: strategy -> ideas -> draft.
- S7: "dame la opcion con un boton de limpiar ideas/draft, esto seria, que me ayudes a redactar mejor el contenido de draft y crear un nuevo archivo idea (no olvides de generar la relacion entre los archivos de Ideas y publicaciones/ideas/draft)". Button: rewrites a draft with the Claude API, creates the idea file in Ideas, moves the draft out of Draft, and writes both references.
- S8: "en todo momento quiero usar trading_agent_persona.md" -> the cleanup LLM call uses that file as system prompt.
- S9: "En python quiero que armes una interfaz web".

## Tasks
- T1 (S1, S9): scaffold app/ and folders publicaciones/ideas/draft, Ideas, Estrategias. route: inline. commit: e0a4c03
- T2 (S2, S3, S4): core: list files per folder, strategy name from file name, read/write `## Referencias` section. route: inline, TDD. commit: e0a4c03
- T3 (S2, S4, S7): core: move draft -> Ideas with new name <STRATEGY>_<NN>.md and bidirectional references; create strategy file. route: inline, TDD. commit: e0a4c03
- T4 (S5): Flask routes: GET /api/tree, POST /api/promote, POST /api/strategy. route: inline, TDD. commit: 04d68a2
- T5 (S6): UI page with Cytoscape mindmap + folder panels. route: inline. commit: 04d68a2 (browser check pending)
- T6 (S7, S8): POST /api/clean/<draft>: Claude API call with persona as system prompt, LLM client injectable for tests. route: inline, TDD. commit: 04d68a2 (browser check pending)
- T7: README in app/ with run instructions and env vars (ANTHROPIC_API_KEY, CLAUDE_MODEL). route: inline. commit: 04d68a2

## Log
- L1 (original request, verbatim): "vamos a trabajar /Jira/User_Story.md" (story text is the Specs S1-S9 above, quoted from Jira/User_Story.md).
- L2: user answers: cleanup button uses the Claude API; web stack Flask + JS vanilla.
- L3: interpretation: the cleaned draft moves out of publicaciones/ideas/draft to Ideas (its improved version), so Draft stays clean. Model id comes from env CLAUDE_MODEL (default set in code, to be confirmed by user).
- L4: verification: 31/31 pytest; app serves / and /api/tree (200); app.js syntax OK. NOT verified: the mindmap and cleanup button in a real browser.
- L5: slice size: 772 authored lines in 2 commits (e0a4c03, 04d68a2), above the ~400-line slice; delivery shape left to the user.
