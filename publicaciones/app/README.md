# Ideas y Estrategias (publicaciones/)

Interfaz web para depurar ideas de trading y agruparlas por estrategia.

## Estructura

- `publicaciones/ideas/draft/`: borradores sin revisar (resúmenes de reels).
- `publicaciones/ideas/`: ideas depuradas, nombradas `<ESTRATEGIA>_<NN>.md` (ej. `ORB_NY_01.md`).
- `publicaciones/estrategias/`: un archivo por estrategia (ej. `ORB_NY.md`).

La relación es por nombre de estrategia, no por indicadores. Cada archivo guarda
al final una sección `## Referencias` con los vínculos (idea ↔ estrategia, idea ↔ draft de origen).

## Ejecutar

```bash
cd publicaciones/app
python3 -m pip install -r requirements.txt
export ANTHROPIC_API_KEY=...        # solo para el botón "Limpiar draft"
export CLAUDE_MODEL=...             # opcional, por defecto claude-sonnet-4-5
python3 server.py                   # http://127.0.0.1:5000
```

## Error con el puerto del servidor
```bash
flask --app server run --debug --port 5001
```

## Tests

```bash
cd publicaciones/app && python3 -m pytest -q
```

## Notas

- El botón de limpieza envía el persona `jira/trading_agent_persona.md` (en la raíz del proyecto) como system prompt
  y el draft como usuario. Si la API falla, el draft queda en `publicaciones/ideas/draft/`.
- Los drafts sin promover aparecen en el panel pero no tienen aristas en el mindmap
  (no tienen referencia todavía).
