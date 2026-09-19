import { createReadStream, existsSync, statSync } from 'node:fs'
import { extname, join, resolve, sep } from 'node:path'

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.mjs': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.yaml': 'application/yaml; charset=utf-8',
  '.yml': 'application/yaml; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.avif': 'image/avif',
  '.ico': 'image/x-icon',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.txt': 'text/plain; charset=utf-8',
  '.webmanifest': 'application/manifest+json',
  '.map': 'application/json; charset=utf-8',
}

export function contentType(filePath) {
  return MIME[extname(filePath).toLowerCase()] || 'application/octet-stream'
}

export function normalizedPath(pathname) {
  const clean = pathname.replace(/\/+/, '/')
  return clean.startsWith('/') ? clean : `/${clean}`
}

export function safeJoin(baseDir, urlPath) {
  let decoded
  try {
    decoded = decodeURIComponent(urlPath.split('?')[0])
  } catch {
    return null
  }
  const target = resolve(baseDir, `.${normalizedPath(decoded)}`)
  if (target !== baseDir && !target.startsWith(baseDir + sep)) return null
  return target
}

export function fileFor(dir, urlPath, { directoryIndex = true } = {}) {
  const target = safeJoin(dir, urlPath)
  if (!target) return null
  try {
    const info = statSync(target)
    if (info.isFile()) return target
    if (info.isDirectory() && directoryIndex) {
      const index = join(target, 'index.html')
      if (existsSync(index)) return index
    }
  } catch {
    return null
  }
  return null
}

export function sendFile(req, res, filePath, { status = 200, cache = 'no-cache' } = {}) {
  const info = statSync(filePath)
  res.writeHead(status, {
    'Content-Type': contentType(filePath),
    'Content-Length': info.size,
    'Cache-Control': cache,
  })
  if (req.method === 'HEAD') return res.end()
  createReadStream(filePath)
    .on('error', () => res.end())
    .pipe(res)
}

export function sendText(res, status, body, type = 'text/plain; charset=utf-8') {
  res.writeHead(status, { 'Content-Type': type, 'Cache-Control': 'no-store' })
  res.end(body)
}
