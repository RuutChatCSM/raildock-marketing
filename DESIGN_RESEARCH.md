# Raildock marketing design research — 2026-09-19

This pass treats the website as a product narrative, not a screenshot gallery. The research set includes commercial developer platforms and stronger open-source PaaS products because Raildock needs both the clarity of a commercial platform and the transparency expected from open source.

## What the stronger commercial sites do

### Railway — product canvas as the central mental model

Railway's product and docs make the project canvas the operator's "mission control". The site repeatedly returns to infrastructure relationships, deployments, networking, observability, and workflow rather than presenting isolated feature cards.

Sources:
- https://railway.com/
- https://docs.railway.com/quick-start
- https://docs.railway.com/build-deploy

**Raildock implication:** topology is the strongest visual proof we have, but it should be shown as a focused crop where the relationships are legible. Do not repeatedly paste the entire application shell.

### Porter — ownership boundary is the headline

Porter leads with "your own cloud" and makes the infrastructure boundary part of the product proposition rather than a footnote.

Source: https://www.porter.run/

**Raildock implication:** "your servers" should remain central. It is clearer and more differentiated than generic language about developer experience.

### Vercel — one visual chapter per idea

Vercel's homepage is organized into large product chapters. Each chapter has a specific visual tied to the message and a short list of supporting capabilities, rather than a continuous gallery of dashboard screenshots.

Source: https://vercel.com/

**Raildock implication:** each Raildock screenshot should answer one question. A deployment crop belongs beside deployment lifecycle copy. A database crop belongs beside data operations. A manifest crop belongs beside desired-state/drift. Screenshots should not be used merely to fill space.

### PostHog — interactive proof can be better than another screenshot

PostHog uses illustrative, interactive product sequences to explain how multiple product surfaces cooperate. The interaction is explicitly tied to the claim being made.

Source: https://posthog.com/

**Raildock implication:** use lightweight simulations for concepts the product screenshot alone cannot explain well, such as source → build → runtime → data → recovery and desired → plan → apply. Keep those simulations diagrammatic rather than pretending they are app UI.

### Qovery — workflow chapters, not a feature inventory

Qovery groups its story around deploy, operate, and production workflows. Product imagery supports those workflow chapters instead of becoming the whole page.

Source: https://www.qovery.com/

**Raildock implication:** explain Raildock as an operating model: project topology, desired state, service lifecycle, data/recovery, then ownership boundary.

## What the stronger open-source sites do

### Coolify and Dokploy — direct self-hosting story

Both are explicit about being self-hosted and open source, and both make installation approachable. Their product pages are strongest when they explain ownership and deployment directly; the weaker pattern is long feature inventories that flatten every capability to the same importance.

Sources:
- https://coolify.io/
- https://dokploy.com/self-hosted-paas

**Raildock implication:** preserve the one-line install path and MIT/open-source facts, but avoid turning the homepage into an exhaustive checklist. The docs can carry breadth; marketing should carry the product model.

## Design rules adopted for Raildock

1. **Crop to the claim.** Never use a whole-window screenshot when only one region proves the point.
2. **At most one dominant product capture in a chapter.** A page can contain several captures over its full length, but the user should not be confronted with a gallery wall.
3. **Use actual UI only when it adds credibility.** Abstract architecture, reconciliation, and ownership are better explained by diagrams derived from Raildock's own geometry.
4. **The logo geometry is a system, not a watermark.** Rails, station diamonds, dock bars, converging paths, and angled cuts become dividers, motion paths, masks, and architecture diagrams.
5. **Purple means Raildock state.** Use it for brand, selection, active paths, primary action, and reconciliation. Keep the base graphite/neutral so the product UI retains contrast.
6. **Motion must explain change.** Signals can travel along a lifecycle path; a context viewer can switch between operator tasks; a reconciliation path can animate. Generic scroll-reveal animation is excluded.
7. **No marketing copy about the design itself.** Public copy describes Raildock capabilities and outcomes, never phrases such as "not a mockup", "real screenshot", or commentary about the website treatment.
8. **Do not invent proof.** No fake customer marks, usage numbers, benchmark claims, compliance marks, uptime figures, or unsupported product states.

## Screenshot map for this implementation

- `topology-focus.webp` — hero and project model: service relationships and private links.
- `manifest-focus.webp` — desired state: editor, drift indicator, format/reference surface.
- `deployments-focus.webp` — service lifecycle: deploy/restart/rebuild/processes/revisions.
- `database-focus.webp` — data operations: schema/table browsing inside the service context.
- `activity-focus.webp` — recovery/operations: backups, snapshots, restores and deploy events.
- `integrations-focus.webp` — platform extensibility: builders, databases, caches and services.

The source screenshots remain unmodified outside the marketing folder; marketing assets are presentation crops only.
