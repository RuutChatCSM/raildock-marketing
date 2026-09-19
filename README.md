# RailDock website system

Production-oriented website package researched from the public `mona-chen/raildock` repository on **2026-09-19**.

The site is three apps built and deployed as **one RailDock service**:

- `marketing/` — multi-page product website, dependency-free static HTML/CSS/JS.
- `docs/` — 29-page documentation site powered by **Holocron** (SSR Node).
- `api-reference/` — interactive **Scalar** API explorer backed by a derived OpenAPI 3.1 document.
- `openapi/` — source OpenAPI document for the current researched Rails route surface.
- `server.mjs` — unified Node gateway: marketing at `/`, Holocron at `/docs/`, Scalar at `/api-reference/`, health at `/_up`.
- `raildock.toml` — RailDock manifest describing the single-service deploy.
- `deployment/` — Caddy, nginx, systemd and Docker examples for non-RailDock hosting.

The root `package.json` uses npm workspaces (`docs`, `api-reference`) so one `npm install` and one `npm run build` produce the whole site.

## What changed from the existing RailDock landing page

The current repository landing page is a strong single-file product page, but the product now has enough surface area that marketing, operating guidance, and API detail compete for the same scroll. This redesign promotes the platform's real differentiators into dedicated routes:

- `/platform/` — project/service lifecycle, networking, observability and API.
- `/manifests/` — desired-state reconciliation and drift.
- `/reliability/` — backups, PITR, recovery drills and destructive-operation guardrails.
- `/self-hosting/` — installer and control-plane architecture.
- `/security/` — authentication, access and privileged-operation boundaries.
- `/open-source/` — source model and contribution surface.
- `/compare/` — factual deployment-model comparison and current scope.
- `/docs/` — authored Holocron documentation.
- `/api-reference/` — Scalar API reference.

The copy is deliberately based on capabilities visible in the repository. There are no fake testimonials, customer logos, benchmark numbers, enterprise certifications, uptime claims, or assumed cloud regions.

## Local development

Install once from the repository root (npm workspaces install `docs` and `api-reference`):

```bash
npm install
```

### Unified dev server

```bash
npm run dev
```

This starts the Holocron dev server (port 5173), the Scalar dev server (port 5174), and a gateway on `http://localhost:8080` that serves marketing at `/`, docs at `/docs/`, and the API reference at `/api-reference/`, including Vite HMR websockets. Cross-app links work because everything is on one origin.

### Production build and run

```bash
npm run build
npm start
```

`npm run build` builds Holocron (`docs/dist/rsc/index.js`) and Scalar (`api-reference/dist`). `npm start` runs `server.mjs`, which serves marketing and the API reference statically and spawns the Holocron Node server on `DOCS_PORT` (default `3001`).

Holocron uses `docs/dist` as its dev cache, so `npm run dev` replaces the production build there. Always run `npm run build` before `npm start` (RailDock does this automatically).

| Variable | Default | Purpose |
| --- | --- | --- |
| `PORT` | `3000` | Public gateway port (RailDock/Dokku set this). |
| `DOCS_PORT` | `3001` | Internal Holocron server port. |
| `HOST` | `0.0.0.0` | Gateway bind address. |

### Running a single app

```bash
npm --prefix docs run dev
npm --prefix api-reference run dev
```

### Holocron managed hosting (optional)

```bash
npm --prefix docs run deploy:holocron
```

`--base-path /docs` on Holocron-managed hosting is a Holocron Pro feature. Self-hosting the Holocron Node output at `/docs/` does not require that hosted subpath feature.

## Deploy with RailDock

`raildock.toml` describes the whole site as a single `web` service. RailDock builds it with nixpacks (`npm install` + `npm run build`) and runs `node server.mjs`:

```toml
[[services]]
name = "raildock-web"
category = "app"
subtype = "web"
builder = "nixpacks"
source = { type = "git", repo = "https://github.com/RuutChatCSM/raildock-marketing.git", branch = "main" }
start_command = "node server.mjs"
port = 3000
domains = ["raildock.example.com"]
```

Set `domains` to the real production hostname before applying. The service exposes `/_up` for health checks. A single service is required because RailDock routes by host (`Host()` rules), not by path prefix, and Holocron is SSR-only.

### Non-RailDock hosting

`deployment/Caddyfile` and `deployment/nginx.conf` describe the same routing if you host it yourself: marketing (`/`), Holocron Node (`/docs/*`), and the Scalar bundle (`/api-reference/*`). In that setup build with `npm run build`, run Holocron with `PORT=3000 node docs/dist/rsc/index.js`, and serve `marketing/` and `api-reference/dist/` statically.

## API reference accuracy

The repository does not currently ship a canonical OpenAPI document. `openapi/raildock.openapi.yaml` is therefore a **derived reference** from the current public Rails route/controller surface researched on 2026-09-19.

The spec covers 149 paths / 176 operations. Where controller behavior exposed a concrete contract (for example login, health, authentication, destructive project preconditions, manifest state, run-command requirements), the spec models it. Where exact payload shape was not explicit, the schema stays permissive rather than inventing a brittle contract.

`api-reference/public/openapi.yaml` is generated by `npm run sync:openapi` (run automatically by `npm run build:api`) so the Scalar copy cannot drift from `openapi/raildock.openapi.yaml`.

Long term, the ideal architecture is to generate the OpenAPI document from the Rails application/test suite and treat this website copy as the renderer/consumer of that canonical artifact.

## Repository layout

This standalone repository deploys from its root:

```text
raildock-marketing/
├── marketing/          # static product site
├── docs/               # Holocron workspace
├── api-reference/      # Scalar workspace
├── openapi/            # canonical OpenAPI source
├── scripts/            # sync-openapi, dev gateway, http helpers
├── server.mjs          # unified production gateway
├── raildock.toml       # RailDock manifest
├── package.json        # npm workspaces + build/start
└── .github/workflows/  # website-checks
```

To fold it into the main RailDock repository instead, place it under `website/` and point the manifest's `source.repo` at `mona-chen/raildock` with `root_directory = "website"`. The workspace scripts work unchanged because they resolve paths relative to the package root.

## Validation

Run the repository-local checks with:

```bash
npm run validate
```

That runs `python3 validate.py` (OpenAPI structure, docs navigation, marketing routes/metadata), `node --check` on the marketing script, the Scalar entry, and `server.mjs`. CI runs `npm ci`, `npm run validate`, and `npm run build`.

Holocron itself also performs internal broken-link checks during `vite build`/development, which fail the build on dead internal links. External marketing routes linked from docs are declared in `docs.json` `knownPaths`. Both production builds were verified locally (Holocron with Vite 8, Scalar with Vite 8).

## Brand refresh (2026-09-19)

The marketing surface now uses the approved purple Raildock rail/portal mark throughout the navbar, hero, product mock, page hero watermarks, CTAs, footer, favicon, and PWA assets. Brand assets live in `marketing/assets/` as `raildock-icon.png`, `raildock-logo.png`, `favicon.png`, `apple-touch-icon.png`, and `icon-512.png`. The visual system is centered on the Raildock purple spectrum rather than the earlier neutral-violet placeholder identity.

## Design pass 2 — less "AI landing page", more product company

A second design pass was applied after reviewing the rendered marketing pages. The goal was to remove the common generative-design tells—oversized gradient headline fragments, purple glow everywhere, pill-heavy metadata, card soup, ornamental watermarks, repetitive reveal animation, and a giant boxed CTA—and replace them with a quieter engineering-led visual system.

Notable changes:

- Added `marketing/assets/raildock-icon-on-dark.png` and `raildock-logo-on-dark.png` for dark surfaces. The low-luminance structural parts of the mark are lifted to pale lavender while the vivid purple panels remain purple, so the mark keeps its geometry instead of disappearing into the background.
- Removed the top promo/announcement bar and the `OSS` badge from the wordmark.
- Reduced header height and made navigation active state a simple rail-like underline.
- Rewrote the homepage hero around a concrete product statement, a real install command with copy action, and operational facts instead of a decorative slogan pill.
- Removed 3D rotation from the control-plane preview and made it read as a product surface rather than a floating mockup.
- Replaced most boxed feature cards with open editorial columns separated by rules.
- Removed scroll-reveal animation. The site now prioritizes stable product information over decorative movement.
- Replaced gradient-filled headline words with a single solid lavender accent.
- Removed oversized logo watermarks and repetitive radial-glow treatment from inner-page heroes.
- Reworked page metadata pills into plain technical metadata.
- Replaced the large rounded gradient CTA panels with rule-separated editorial CTAs.
- Tightened vertical rhythm across hero, sections, CTAs and footer to avoid the oversized empty areas visible in the first render.

The authored source remains `build_site.py`; running it regenerates the complete marketing surface with this system.

## Marketing design v4 — research-led, product-specific

The current marketing pass was rebuilt after reviewing Railway, Porter, Vercel, PostHog, Qovery, Coolify and Dokploy. Its main design rule is **crop to the claim**: supplied Raildock application screenshots are used only where a focused interface region proves a specific capability. Architecture and lifecycle concepts use custom rail/dock geometry instead of additional screenshots.

The homepage now combines a focused project-topology hero, lifecycle rail, project-system diagram, manifest/drift chapter, a single-surface operational context viewer, ownership/runtime architecture, and concise open-source facts. Motion is limited to state/flow and respects `prefers-reduced-motion`.

Regenerate and validate with:

```bash
python build_site.py
python validate.py
node --check marketing/assets/site.js
```

See `DESIGN_RESEARCH.md` for the competitor study and `DESIGN_REVIEW.md` for the implementation rationale.
