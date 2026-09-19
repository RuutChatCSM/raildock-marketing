import { createApiReference } from '@scalar/api-reference'
import '@scalar/api-reference/style.css'
import './shell.css'

createApiReference('#app', {
  url: '/api-reference/openapi.yaml',
  theme: 'elysiajs',
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
    ogDescription: 'Automate projects, services, deployments, servers, manifests, organizations and recovery workflows.',
    ogImage: 'https://raildock.xyz/assets/og.png',
    twitterImage: 'https://raildock.xyz/assets/og.png',
    twitterCard: 'summary_large_image'
  },
})
