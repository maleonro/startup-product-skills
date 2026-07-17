# Fuentes, cadencias y reglas de datos

Arquitectura validada empíricamente (jul 2026): en la ventana de prueba 1-jun a 16-jul-2026, este pipeline encontró 31 rondas donde una corrida manual solo con LatamList encontró 17.

## Capa 1 — LatamList (semanal, columna vertebral)

- URL: `https://latamlist.com/category/startup-news/funding/` + `/page/2/` + `/page/3/` (fetch en paralelo).
- `source_type=latamlist`. Aporta ~75% del volumen.
- El título casi siempre trae company, monto y tipo de ronda. `country` y `sector` suelen faltar en el listado: para las filas que queden sin esos campos, hacer fetch del artículo individual (solo de esas filas, no de todas).

## Capa 2 — LatAm Tech Weekly (semanal)

- URL: `https://juliadeluca.substack.com/` — tomar la edición más reciente (sale viernes/sábado), sección "Deals of the week".
- `source_type=newsletter`. Viene pre-tabulado; captura micro-rondas y regionales que LatamList no cubre.
- Cuidado: mezcla rondas con M&A y levantamientos de fondos de VC — aplicar exclusiones. Verificar la fecha del anuncio original: el newsletter a veces cita rondas de semanas anteriores.

## Capa 3 — Prensa brasileña (quincenal)

- Brazil Journal: `https://braziljournal.com/hot-topic/private-equity-vc/`
- NeoFeed: `https://neofeed.com.br/startups/`
- Finsiders Brasil: `https://finsidersbrasil.com.br/` (sección giro/captações)
- `source_type=prensa-br`. Es la capa que aporta rondas que solo existen en portugués (~5 de 31 en la prueba). Verbos a reconocer: "capta", "recebe aporte", "levanta", "rodada".
- Los listados no traen fecha: abrir el artículo para confirmarla. Riesgo alto de rondas viejas resurfaceadas — descartar todo lo anterior a la última corrida **de esta capa** (si la capa nunca ha corrido, descartar solo lo que sea anterior a la ventana que el ledger ya cubre o lo que ya esté en él; verificado 2026-07-16: UY3 de enero resurfaceada en el home de Finsiders, correctamente descartada, mientras Shopper de junio entró porque la capa nunca había corrido).
- NO usar Startupi: sin RSS/categoría confiable, el search genérico devuelve ruido de años anteriores (verificado).

## Capa 4 — latamfintech.co (mensual)

- Buscar el listado "Top 10 financiación en fintech <mes> <año>" apenas cierre el mes.
- `source_type=latamfintech`. Un fetch, 10 rondas pre-tabuladas con país/monto/fecha exactos.

## Canales probados y muertos (no reintentar)

- `site:linkedin.com` + keywords como discovery: 0 señales utilizables en 13 queries; el buscador no indexa el feed. Solo sirve como enriquecimiento dirigido por empresa.
- WebSearch abierto en prensa general: todo lo que encuentra ya está en LatamList; solo agrega ruido y variación de cifras entre medios.
- Contxto, LAVCA, Sling Hub: reportes agregados o bases pagas, sin feed semanal de rondas.
- Forbes México: bloquea fetch (403).

## Exclusiones (aplicar en extracción)

- M&A, adquisiciones, acquihires, fusiones.
- Levantamientos de fondos de VC (el fondo no es una startup).
- Empresas con HQ fuera de LATAM aunque operen en la región (criterio: HQ o fundación en LATAM). Caso testigo: Mathew (HQ España, opera MX/CO) queda afuera.
- Programas/aceleradoras sin cheque directo a una startup concreta.

## Enriquecimiento LinkedIn (post-consolidación)

Solo para filas nuevas con `signal=expansion`: `site:linkedin.com "<nombre empresa>"` (probar también con keywords del anuncio: "Serie A", "raised"). Objetivo: el post del founder/empresa anunciando su propia ronda → `linkedin_person` + `linkedin_post_url`. Una búsqueda por empresa; si no aparece, vacío.

## Señal comercial (tesis)

Una ronda no es una noticia, es una señal comercial: una empresa post-Serie A entra en modo expansión (contrata, abre mercados, prueba herramientas) y está más receptiva a conversaciones de venta. `signal=expansion` = Series A/B/C del último año = lista de prospección prioritaria.

## Caveats a incluir siempre al publicar cifras

- Solo montos disclosed suman capital; las rondas sin monto se cuentan igual en volumen.
- Los totales mezclan equity + deuda + grants (ej. Nexu US$143M es debt facility) — no presentarlos como "venture capital puro".
- Conversiones BRL→USD a la tasa del día de corrida, aproximadas.
- Es cobertura de trackers + prensa, no censo del mercado (referencia: Pitchbook estima ~US$6.5B/año para LATAM; un ledger anual de ~US$5.3B es un subset creíble).
- El mes en curso siempre está parcial.
