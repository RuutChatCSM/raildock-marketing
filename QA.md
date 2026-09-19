# Raildock Website QA — v4

## Automated checks

- `python -m py_compile build_site.py` — passed
- `npm run validate` — passed (OpenAPI structure, docs nav, marketing metadata, JS syntax)
- `npm install` — passed (npm workspaces for `docs` and `api-reference`)
- `npm run build` — passed:
  - Holocron SSR build → `docs/dist/rsc/index.js` (Vite 8)
  - Scalar build → `api-reference/dist` with `openapi.yaml` synced (Vite 8)
- OpenAPI — 149 paths / 176 operations
- Holocron docs — 29 navigation pages / 29 MDX files
- Marketing — 8 generated routes

## Coupled service checks

`server.mjs` was run locally and verified over HTTP:

- `/` — marketing (200)
- `/platform/` — marketing route (200)
- `/_up` — health (200)
- `/api-reference/` — Scalar SPA (200)
- `/api-reference/openapi.yaml` — synced spec (200)
- `/docs/` and `/docs/getting-started/install` — Holocron SSR (200), asset under `/docs/assets/*` (200)
- unknown path — marketing `404.html` (404)

The gateway spawns the Holocron server on `DOCS_PORT` (3001) and proxies `/docs/*` while preserving the path, which matches Holocron's `/docs/` Vite base. `raildock.toml` declares the whole site as one `web` service.

## Asset/link checks

- All marketing `/assets/*` references resolve inside the package.
- Focused product imagery is WebP and is loaded only by the sections that use it.
- Public HTML contains no design-process/meta copy such as "not a mockup" or commentary about screenshot authenticity.
- The dark-surface Raildock mark is used in navbar/footer contexts.

## Focused product captures

The current implementation uses six cropped views derived from supplied application screenshots:

- project topology
- manifest editor
- service deployments
- PostgreSQL data browser
- activity/recovery history
- plugins/integrations

The crops remove browser chrome and unrelated navigation to preserve legibility and reduce visual repetition.

## Interaction/accessibility checks

- Product context controls are real buttons with `aria-selected` state.
- Context auto-rotation pauses on pointer hover and restarts after explicit selection.
- Mobile navigation updates `aria-expanded`.
- Copy actions use keyboard-accessible buttons.
- Images include descriptive alt text.
- `prefers-reduced-motion` collapses animation/transition timing.

## Browser-render limitation in this environment

The sandbox browser is blocked from navigating to local HTTP/file URLs by administrator policy, so an automated Chromium screenshot cannot be used as a deterministic visual gate here. Static route generation, image existence, HTML structure, Python compilation, JavaScript syntax, docs navigation, and OpenAPI validation all pass. A final real-browser review should still be done after pulling the package into the normal development environment.
