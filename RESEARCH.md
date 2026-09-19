# RailDock website research brief

Research date: **2026-09-19**

## Product definition

RailDock presents itself as a self-hosted PaaS for deploying applications and databases to servers the operator controls. The current project goes materially beyond a thin Dokku UI: the repository describes declarative manifests, dependency ordering, desired-state reconciliation, project-scoped networking, organizations/roles, backup and PITR workflows, server provisioning, realtime deployment state, and an HTTP API.

Primary repository: `https://github.com/mona-chen/raildock`

## Architecture observed

The current README describes a single application image containing nginx, Puma, and background workers. The React frontend uses same-origin `/api` and `/cable`; the Rails backend talks to deployment targets over SSH through host/Dokku execution layers.

Notable backend concepts visible in the repository include:

- manifest parser, generator and reconciler;
- deployment sequence and deployment jobs;
- project network management;
- external proxy / Traefik configuration;
- Action Cable channels;
- backup, PITR, snapshot and recovery-drill jobs;
- GitHub App and Git-source integration;
- server validation/provisioning and host metrics.

Current stack observed from package manifests: Rails 8.x, React 19.x, Vite, PostgreSQL, Puma, Solid Queue/Cache/Cable, net-ssh/net-scp, JWT, Lockbox, Octokit, rack-attack, aws-sdk-s3, TanStack Query, Radix UI, Framer Motion, xterm, Recharts and Zustand.

## Deployment / install behavior

The README's standard installer is:

```bash
curl -sSL https://raw.githubusercontent.com/mona-chen/raildock/main/install.sh | bash
```

The documented installer checks/installs Docker and Dokku, generates RailDock SSH identity and environment material, starts RailDock on port 8888, and creates a local Dokku server record. The existing documentation warns operators to preserve `.env` and `backend/config/master.key`.

## Declarative state

The README currently names `raildock.toml`, `railway.toml`, and `app.json`. The reconciliation architecture is the most important product-level story discovered during research:

1. parse desired state;
2. compare desired versus current state;
3. build a dependency-aware delta;
4. classify changes by severity;
5. apply the minimum operation needed;
6. report status/drift.

This is why the new website gives manifests their own top-level product page rather than presenting them as a minor configuration format.

Exact manifest field syntax is intentionally not asserted as canonical in the generated docs because the public repository does not currently publish a standalone, versioned manifest schema. Illustrative snippets are marked accordingly and should eventually be replaced by examples exported from parser tests/fixtures.

## API research

The current Rails routing surface includes health/setup/auth, webhooks, modules/plugins, projects, environments, repository import, manifests, shallow service resources, deployments, service configuration, database browsing, recovery/PITR, servers, Docker imports, unmanaged datastore adoption, organizations, Git sources, members/invitations, deploy keys, backup destinations, templates, activity, builders/config, admin/update paths, and GitHub App lifecycle routes.

Controller behavior inspected during research established several concrete details used in the reference:

- login returns a JWT and user payload;
- bearer JWTs are verified using HS256;
- health returns `status` and ISO-8601 time;
- project deletion can return HTTP 428 for confirmation/snapshot preconditions;
- project-wide deploy resolves dependencies and queues a sequence;
- process scaling rejects inappropriate one-shot process types;
- run-command requires a `command` field;
- manifest update parses/validates and creates a preview;
- manifest apply can stop when removals need confirmation;
- server validation refreshes observed host/proxy/runtime fields.

The repository does not currently expose a canonical OpenAPI artifact. The website's OpenAPI file is therefore explicitly marked as derived and keeps uncertain payloads permissive.

## Current limitations worth stating

The existing README documents current scope limitations including:

- no password-reset flow;
- no preview environments;
- no multi-host orchestration for a single project, even though the control plane can manage multiple servers;
- read-only data browser rather than a built-in advanced database query console.

The new `/compare/` page surfaces these constraints so the site does not oversell the system.

## Docs technology research

Holocron is a Mintlify-compatible open-source Vite docs plugin. Current documentation confirms:

- `@holocron.so/vite` is installed with React/React DOM/Vite;
- `docs.json` controls navigation, theme, navbar and other documentation settings;
- Vite `base: '/docs/'` is the supported self-hosted subpath configuration;
- `vite build` produces an SSR Node bundle started with `node dist/rsc/index.js`;
- AI-readable `.md` routes, `/llms.txt`, `/llms-full.txt`, `/docs.zip`, and agent-skill discovery are generated by Holocron;
- Holocron asks sites to retain the “Powered by Holocron” footer link;
- Holocron-managed `/docs` subpath deployment is a Pro feature, while the open-source self-hosted Node build can be reverse-proxied at `/docs/`.

Sources: `https://holocron.so/`, `https://holocron.so/docs/quickstart`, `https://holocron.so/docs/deploy/base-path`, `https://holocron.so/docs/deploy/node`, `https://holocron.so/docs/organize/docs-json`.

## API reference technology research

Scalar's current API Reference supports OpenAPI 3.0/3.1, a modern/classic layout, live request clients, custom themes/CSS, server selection and bearer authentication from the source document. The package used by this site is pinned to `@scalar/api-reference@1.69.0`, the current package version observed during research.

The website uses the ESM package integration rather than an unpinned CDN script so production assets can be built and served with the rest of the site.

Sources: `https://scalar.com/products/api-references/getting-started`, `https://scalar.com/products/api-references/configuration`, `https://www.npmjs.com/package/@scalar/api-reference`.
