# Raildock marketing design — v4 research-led pass

## Direction

Raildock should feel like an infrastructure product with a specific operating model, not a generic dark SaaS template. The design now takes its identity from three native sources: the rail/portal mark, the project topology model, and the operator workflow visible in the application.

The page is deliberately not a screenshot gallery. Product captures are cropped to the exact surface needed for a claim, while architecture and state transitions are explained with purpose-built diagrams that borrow Raildock's rail and dock geometry.

## Homepage narrative

1. **Ownership + topology** — "Your servers. A platform to run them." with a focused crop of the project graph and a one-line installer.
2. **Lifecycle rail** — source → build → runtime → data → recover, expressed as a moving infrastructure signal rather than a card grid.
3. **Project model** — an abstract connected-system diagram explains apps, workers, data and private links without pretending to be application UI.
4. **Desired state** — the manifest editor crop is paired with drift/preview/apply states and a restrained reconciliation story.
5. **Operate in context** — one viewer switches between service deployments, database inspection and operational history. Only one crop is visible at a time.
6. **Ownership boundary** — an architecture diagram places the Raildock mark between the Rails/API control plane and Linux/Dokku/Docker execution.
7. **Open-source facts** — compact factual band for license, stack and API.
8. **Install** — restrained final action, no giant gradient panel.

## Product imagery policy

The supplied application screenshots are treated as source material, not page furniture. Each marketing asset removes Safari/macOS chrome and irrelevant navigation so the useful interface is readable at normal page scale.

Focused assets:

- `marketing/assets/product/topology-focus.webp`
- `marketing/assets/product/manifest-focus.webp`
- `marketing/assets/product/deployments-focus.webp`
- `marketing/assets/product/database-focus.webp`
- `marketing/assets/product/activity-focus.webp`
- `marketing/assets/product/integrations-focus.webp`

The homepage never shows a wall of all six. The primary context viewer exposes one operational surface at a time.

## Geometry system

The logo contributes reusable geometry instead of decorative watermarks:

- converging rails for lifecycle and architecture paths;
- diamond stations for state transitions;
- vertical dock bars for edge structure and masks;
- angled clipping on product imagery;
- fine parallel lines for relationships and section boundaries.

This allows the site to remain recognizably Raildock even when the logo itself is not visible.

## Motion

Motion is reserved for state and flow:

- page progress on the header rail;
- lifecycle signal movement;
- diagram path movement;
- controlled context-viewer transitions;
- copy/install interaction feedback.

All motion is disabled or reduced under `prefers-reduced-motion`.

## Code

`build_site.py` remains the source of truth. It emits all eight marketing routes, `site.css`, and `site.js`. The generated site stays dependency-free so the marketing layer is easy to serve behind Caddy/nginx while Holocron and Scalar own `/docs/` and `/api-reference/` respectively.

See `DESIGN_RESEARCH.md` for the competitor review and design rules used in this pass.
