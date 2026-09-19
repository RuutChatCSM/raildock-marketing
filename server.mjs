import { spawn } from 'node:child_process'
import { existsSync } from 'node:fs'
import { createServer, request as httpRequest } from 'node:http'
import { join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { fileFor, normalizedPath, sendFile, sendText } from './scripts/http-util.mjs'

const ROOT = resolve(fileURLToPath(new URL('.', import.meta.url)))
const MARKETING_DIR = join(ROOT, 'marketing')
const API_DIR = join(ROOT, 'api-reference', 'dist')
const DOCS_ENTRY = join(ROOT, 'docs', 'dist', 'rsc', 'index.js')

const HOST = process.env.HOST || '0.0.0.0'
const PORT = Number(process.env.PORT || 3000)
const DOCS_PORT = Number(process.env.DOCS_PORT || 3001)

function proxyDocs(req, res) {
  const upstream = httpRequest(
    {
      host: '127.0.0.1',
      port: DOCS_PORT,
      method: req.method,
      path: req.url,
      headers: {
        ...req.headers,
        host: `127.0.0.1:${DOCS_PORT}`,
        'x-forwarded-host': req.headers.host || '',
        'x-forwarded-proto': req.headers['x-forwarded-proto'] || 'http',
      },
    },
    (docsRes) => {
      res.writeHead(docsRes.statusCode || 502, docsRes.headers)
      docsRes.pipe(res)
    },
  )
  upstream.on('error', () => {
    if (!res.headersSent) sendText(res, 502, 'Documentation server unavailable')
    else res.end()
  })
  req.pipe(upstream)
}

function health(req, res) {
  const body = JSON.stringify({ status: 'ok', docs: existsSync(DOCS_ENTRY), time: new Date().toISOString() })
  res.writeHead(200, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' })
  res.end(req.method === 'HEAD' ? undefined : body)
}

const server = createServer((req, res) => {
  const pathname = normalizedPath((req.url || '/').split('?')[0])

  if (pathname === '/_up' || pathname === '/up' || pathname === '/healthz') {
    return health(req, res)
  }

  if (pathname === '/docs' || pathname.startsWith('/docs/')) {
    return proxyDocs(req, res)
  }

  if (pathname === '/api-reference') {
    res.writeHead(308, { Location: '/api-reference/' })
    return res.end()
  }

  if (pathname.startsWith('/api-reference/')) {
    const rel = pathname.slice('/api-reference'.length)
    const asset = fileFor(API_DIR, rel)
    if (asset) {
      const immutable = pathname.startsWith('/api-reference/assets/')
      return sendFile(req, res, asset, { cache: immutable ? 'public, max-age=31536000, immutable' : 'no-cache' })
    }
    const index = join(API_DIR, 'index.html')
    if (existsSync(index)) return sendFile(req, res, index)
    return sendText(res, 404, 'API reference not built')
  }

  const marketingFile = fileFor(MARKETING_DIR, pathname)
  if (marketingFile) {
    const immutable = pathname.startsWith('/assets/')
    return sendFile(req, res, marketingFile, { cache: immutable ? 'public, max-age=604800' : 'no-cache' })
  }
  const notFound = join(MARKETING_DIR, '404.html')
  if (existsSync(notFound)) return sendFile(req, res, notFound, { status: 404 })
  return sendText(res, 404, 'Not found')
})

server.listen(PORT, HOST, () => {
  console.log(`[web] listening on http://${HOST}:${PORT}`)
})

let docsProc = null
if (existsSync(DOCS_ENTRY)) {
  docsProc = spawn(process.execPath, [DOCS_ENTRY], {
    cwd: join(ROOT, 'docs'),
    env: { ...process.env, PORT: String(DOCS_PORT), HOST: '127.0.0.1', NODE_ENV: 'production' },
    stdio: 'inherit',
  })
  docsProc.on('exit', (code, signal) => {
    console.error(`[web] docs server exited code=${code} signal=${signal}`)
  })
} else {
  console.warn(`[web] docs build not found at ${DOCS_ENTRY}; /docs/ will return 502`)
}

function shutdown(signal) {
  console.log(`[web] received ${signal}, shutting down`)
  server.close(() => process.exit(0))
  if (docsProc && !docsProc.killed) docsProc.kill('SIGTERM')
  setTimeout(() => process.exit(0), 5000).unref()
}

process.on('SIGTERM', () => shutdown('SIGTERM'))
process.on('SIGINT', () => shutdown('SIGINT'))
