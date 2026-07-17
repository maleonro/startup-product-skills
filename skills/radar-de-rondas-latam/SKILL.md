---
name: radar-de-rondas-latam
description: Monitorea semanalmente rondas de inversión de startups LATAM desde un pipeline multi-fuente (LatamList, newsletters curados, prensa brasileña), las consolida en un ledger acumulativo con clasificación de señal comercial, y regenera un artefacto explorador. Usar cuando el usuario pida correr el radar de rondas, actualizar las rondas LATAM, buscar rondas de inversión nuevas en Latinoamérica, o detectar empresas en modo expansión para prospección.
---

# Radar de rondas LATAM

Corrida semanal que trae rondas nuevas, las mergea en `data/rondas-latam.csv` (ledger acumulativo) y reporta las empresas en señal de expansión. Reglas permanentes: español con acentos correctos, sin emojis en ningún output.

## Corrida semanal (workflow)

### 1. Discovery — fetches en paralelo (mismo turno)

Lanzar en paralelo, según cadencia (detalles y URLs exactas en [references/fuentes.md](references/fuentes.md)):

- **Siempre (semanal):** LatamList categoría funding, páginas 1-3 + última edición de LatAm Tech Weekly (sección "Deals of the week").
- **Cada 2 semanas:** Brazil Journal (private equity & VC) + NeoFeed (startups) + Finsiders Brasil.
- **Una vez por mes:** latamfintech.co "Top 10 financiación" del mes cerrado.

LinkedIn NUNCA se usa para discovery (verificado: el buscador no indexa el feed). Si una fuente falla (403, timeout), seguir con el resto y anotarla para el reporte final.

### 2. Extracción a CSV crudo

Volcar cada ronda encontrada a un CSV temporal con columnas:
`company, country, round_type, amount, currency, date, investors, sector, source_url, source_type, linkedin_person, linkedin_post_url`

Reglas obligatorias (el detalle y los casos borde están en fuentes.md):
- **Fecha estricta**: la del anuncio original, no la de la edición del agregador que lo cita.
- **Exclusiones**: M&A/adquisiciones, levantamientos de fondos de VC, empresas con HQ fuera de LATAM.
- Todo instrumento cuenta (equity, deuda, grants) preservando el tipo en `round_type`.
- `source_type` según la fuente: `latamlist`, `latamfintech`, `newsletter`, `prensa-br`.
- No inventar campos: lo que no está en la fuente queda vacío.

### 3. Consolidación

```bash
python3 scripts/consolidar.py --input <crudo.csv> --ledger data/rondas-latam.csv \
  --run-date YYYY-MM-DD --fx-brl <tasa BRL/USD del día>
```

Buscar la tasa BRL/USD del día antes de correr (no usar un valor recordado). El script normaliza montos y tipos de ronda, dedupea intra-corrida y contra el ledger, clasifica `signal` (`expansion`/`early`/`scale`/`other`), marca `first_seen_date` y escribe `data/nuevas-YYYY-MM-DD.csv` con el delta.

### 4. Enriquecimiento LinkedIn (solo filas expansion)

Para cada fila NUEVA con `signal=expansion`: una búsqueda `site:linkedin.com "<empresa>"` buscando el post del founder anunciando la ronda. Si aparece, completar `linkedin_person` y `linkedin_post_url` en el ledger; si no, dejar vacío sin insistir (máximo 1 búsqueda por empresa).

### 5. Regenerar artefacto

Actualizar `const DATA` en `artifact/explorador-capital-latam.jsx` con el ledger completo. Si la sesión tiene tool de publicación de artefactos, publicar/actualizar; si no, dejar el `.jsx` listo. La sección "señales de esta semana" muestra las filas nuevas `signal=expansion` con su `linkedin_person`.

### 6. Reporte final

Cerrar con: rondas nuevas por fuente, por país y sector, cuántas en `signal=expansion` (las de interés para prospección), total acumulado del ledger, y qué fuentes fallaron si alguna falló. Incluir siempre los caveats de datos listados en fuentes.md al compartir cifras públicamente.

## Estructura

```
radar-de-rondas-latam/
├── SKILL.md
├── references/fuentes.md      # URLs, cadencias, keywords, exclusiones, caveats
├── scripts/consolidar.py      # normalización + dedup + señal + merge
├── artifact/explorador-capital-latam.jsx
└── data/
    ├── rondas-latam.csv       # ledger maestro (no editar a mano)
    └── nuevas-YYYY-MM-DD.csv  # delta por corrida
```
