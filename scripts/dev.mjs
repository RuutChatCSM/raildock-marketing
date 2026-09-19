import { spawn } from 'node:child_process'
import { existsSync } from 'node:fs'
import { createServer, request } from 'node:http'
import { connect } from 'node:net'
import { join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

import { fileFor, normalizedPath, sendFile, sendText } from './http-util.mjs'

const ROOT = resolve(fileURLToPath(new URL('..', import.meta.url)))
const MARKETING_DIR = join(ROOT, 'marketing')

const PORT = Number(process.env.PORT || 8080)
const HOST = process.env.HOST || '0.0.0.0'
const DOCS_PORT = 5173
const API_PORT = 5174

const children = []

function run(name, args, cwd) {
  const child = spawn('npm', args, { cwd, stdio: 'inherit', env: process.env })
  child.on('exit', (code, signal) => {
    console.error(`[dev] ${name} exited code=${code} signal=${signal}`)
    shutdown()
  })
  children.push(child)
}

function forward(port, req, res) {
  const upstream = request(
    { host: '127.0.0.1', port, method: req.method, path: req.url, headers: { ...req.headers, host: `127.0.0.1:${port}` } },
    (upRes) => {
      res.writeHead(upRes.statusCode || 502, upRes.headers)
      upRes.pipe(res)
    },
  )
  upstream.on('error', () => {
    if (!res.headersSent) sendText(res, 502, `Dev server on ${port} unavailable`)
    else res.end()
  })
  req.pipe(upstream)
}

function warmup(port, path, label) {
  let attempts = 0
  const timer = setInterval(() => {
    attempts += 1
    if (attempts > 60) return clearInterval(timer)
    const req = request({ host: '127.0.0.1', port, path, method: 'GET' }, (res) => {
      res.resume()
      if (res.statusCode && res.statusCode < 500) {
        clearInterval(timer)
        console.log(`[dev] ${label} ready (${res.statusCode})`)
      }
    })
    req.on('error', () => {})
    req.end()
  }, 1500)
  timer.unref?.()
}

run('docs', ['run', 'dev', '--', '--port', String(DOCS_PORT), '--strictPort'], join(ROOT, 'docs'))
run('api-reference', ['run', 'dev', '--', '--port', String(API_PORT), '--strictPort'], join(ROOT, 'api-reference'))

warmup(DOCS_PORT, '/docs/', 'docs')
warmup(API_PORT, '/api-reference/', 'api-reference')

const server = createServer((req, res) => {
  const pathname = normalizedPath((req.url || '/').split('?')[0])

  if (pathname === '/_up') {
    return sendText(res, 200, JSON.stringify({ status: 'ok' }), 'application/json; charset=utf-8')
  }
  if (pathname === '/api-reference') {
    res.writeHead(308, { Location: '/api-reference/' })
    return res.end()
  }
  if (pathname === '/docs' || pathname.startsWith('/docs/')) {
    return forward(DOCS_PORT, req, res)
  }
  if (pathname.startsWith('/api-reference/')) {
    return forward(API_PORT, req, res)
  }

  const marketingFile = fileFor(MARKETING_DIR, pathname)
  if (marketingFile) return sendFile(req, res, marketingFile)
  const notFound = join(MARKETING_DIR, '404.html')
  if (existsSync(notFound)) return sendFile(req, res, notFound, { status: 404 })
  return sendText(res, 404, 'Not found')
})

server.on('upgrade', (req, socket, head) => {
  const pathname = normalizedPath((req.url || '/').split('?')[0])
  const port = pathname.startsWith('/api-reference') ? API_PORT : pathname.startsWith('/docs') ? DOCS_PORT : null
  if (!port) return socket.destroy()

  const upstream = connect(port, '127.0.0.1', () => {
    const headers = Object.entries(req.headers)
      .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : value}`)
      .join('\r\n')
    upstream.write(`${req.method} ${req.url} HTTP/1.1\r\n${headers}\r\n\r\n`)
    if (head?.length) upstream.write(head)
    upstream.pipe(socket)
    socket.pipe(upstream)
  })
  upstream.on('error', () => socket.destroy())
  socket.on('error', () => upstream.destroy())
})

server.listen(PORT, HOST, () => {
  console.log(`\n[dev] unified site on http://localhost:${PORT}`)
  console.log('[dev]   /               marketing (static)')
  console.log(`[dev]   /docs/          holocron dev (${DOCS_PORT})`)
  console.log(`[dev]   /api-reference/ scalar dev (${API_PORT})\n`)
})

function shutdown() {
  for (const child of children) {
    if (!child.killed) child.kill('SIGTERM')
  }
  server.close(() => process.exit(0))
  setTimeout(() => process.exit(0), 3000).unref()
}

process.on('SIGTERM', shutdown)
process.on('SIGINT', shutdown)
