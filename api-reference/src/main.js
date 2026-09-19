import { createApiReference } from '@scalar/api-reference'
import './shell.css'

createApiReference('#app', {
  url: '/api-reference/openapi.yaml',
  theme: 'purple',
  layout: 'modern',
  darkMode: true,
  forceDarkModeState: 'dark',
  hideDarkModeToggle: true,
  withDefaultFonts: false,
  agent: { disabled: true },
  showOperationId: false,
  modelsSectionLabel: 'Schemas',
  defaultRequestBodyView: 'form',
  defaultHttpClient: { targetKey: 'shell', clientKey: 'curl' },
  searchHotKey: 'k',
  metaData: {
    title: 'RailDock API Reference',
    description: 'Interactive HTTP API reference for the RailDock control plane.',
    ogTitle: 'RailDock API Reference',
    ogDescription: 'Automate projects, services, deployments, servers, manifests, organizations and recovery workflows.'
  },
  customCss: `
    :root {
      --scalar-color-1: #f5f5f7;
      --scalar-color-2: #a1a1aa;
      --scalar-color-3: #71717a;
      --scalar-color-accent: #a78bfa;
      --scalar-background-1: #0b0b0e;
      --scalar-background-2: #111116;
      --scalar-background-3: #17171d;
      --scalar-background-accent: rgba(139, 92, 246, .12);
      --scalar-border-color: #292932;
    }
    .scalar-app { --scalar-header-height: 0px; }
  `,
})
