# Ideas y Estrategias (Shell_Trading)

Interfaz web para depurar ideas de trading y agruparlas por estrategia.

## Estructura

- `Ideas/Draft/`: borradores sin revisar (resúmenes de reels).
- `Ideas/`: ideas depuradas, nombradas `<ESTRATEGIA>_<NN>.md` (ej. `ORB_NY_01.md`).
- `Estrategias/`: un archivo por estrategia (ej. `ORB_NY.md`).

La relación es por nombre de estrategia, no por indicadores. Cada archivo guarda
al final una sección `## Referencias` con los vínculos (idea ↔ estrategia, idea ↔ draft de origen).

## Ejecutar

```bash
cd app
python3 -m pip install -r requirements.txt
export ANTHROPIC_API_KEY=...        # solo para el botón "Limpiar draft"
export CLAUDE_MODEL=...             # opcional, por defecto claude-sonnet-4-5
python3 server.py                   # http://127.0.0.1:5000
```

## Tests

```bash
cd app && python3 -m pytest -q
```

## Notas

- El botón de limpieza envía el persona `Jira/trading_agent_persona.md` como system prompt
  y el draft como usuario. Si la API falla, el draft queda en `Ideas/Draft/`.
- Los drafts sin promover aparecen en el panel pero no tienen aristas en el mindmap
  (no tienen referencia todavía).
