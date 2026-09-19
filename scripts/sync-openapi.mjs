import { copyFileSync, mkdirSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(fileURLToPath(new URL('..', import.meta.url)))
const source = resolve(root, 'openapi', 'raildock.openapi.yaml')
const target = resolve(root, 'api-reference', 'public', 'openapi.yaml')

mkdirSync(dirname(target), { recursive: true })
copyFileSync(source, target)
console.log(`[sync:openapi] ${source} -> ${target}`)
