import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadLocalEnv } from './db/env-utils.mjs';
import { createLocalFallbackAdapter } from './local-adapter.mjs';
import { createNeonAdapter } from './supabase/functions/_shared/neon-adapter.js';
import { handleApiRequest } from './supabase/functions/_shared/handlers.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const FRONT_DIR = path.resolve(__dirname, '..', 'front');

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.mjs': 'application/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
};

export async function createDataAdapter() {
  loadLocalEnv();
  const databaseUrl = process.env.NEON_DATABASE_URL;
  if (databaseUrl && databaseUrl.trim().length > 0) {
    try {
      const { neon } = await import('@neondatabase/serverless');
      const sql = neon(databaseUrl.trim());
      return createNeonAdapter(sql);
    } catch (err) {
      console.warn(
        '[autogest-server] No se pudo inicializar @neondatabase/serverless, usando respaldo CSV local:',
        err.message
      );
    }
  }
  return createLocalFallbackAdapter();
}

export async function createAppServer({ adapter } = {}) {
  const resolvedAdapter = adapter || (await createDataAdapter());
  const corsOrigin = process.env.CORS_ORIGIN || '*';

  const server = http.createServer(async (req, res) => {
    const reqUrl = new URL(req.url || '/', `http://${req.headers.host || 'localhost'}`);

    // 1. Rutas de API (/api o /api/* — sin interceptar archivos estáticos como /api-client.js)
    if (reqUrl.pathname === '/api' || reqUrl.pathname.startsWith('/api/')) {
      const chunks = [];
      for await (const chunk of req) chunks.push(chunk);
      const bodyBuffer = chunks.length > 0 ? Buffer.concat(chunks) : undefined;

      const webReq = new Request(reqUrl.toString(), {
        method: req.method,
        headers: req.headers,
        body: req.method === 'GET' || req.method === 'HEAD' ? undefined : bodyBuffer,
      });

      const webRes = await handleApiRequest(webReq, resolvedAdapter, { corsOrigin });
      res.writeHead(webRes.status, Object.fromEntries(webRes.headers.entries()));
      const resBuf = Buffer.from(await webRes.arrayBuffer());
      res.end(resBuf);
      return;
    }

    // 2. Archivos estáticos de front/
    let relPath = decodeURIComponent(reqUrl.pathname);
    if (relPath === '/' || relPath === '') relPath = '/index.html';
    if (relPath === '/metodos') relPath = '/metodos.html';

    const safeTarget = path.normalize(path.join(FRONT_DIR, relPath));
    if (!safeTarget.startsWith(FRONT_DIR)) {
      res.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('Acceso denegado');
      return;
    }

    if (!fs.existsSync(safeTarget) || fs.statSync(safeTarget).isDirectory()) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end(`Archivo no encontrado: ${relPath}`);
      return;
    }

    const ext = path.extname(safeTarget).toLowerCase();
    res.writeHead(200, {
      'Content-Type': MIME_TYPES[ext] || 'application/octet-stream',
      'Cache-Control': 'no-cache, no-store, must-revalidate',
    });
    fs.createReadStream(safeTarget).pipe(res);
  });

  return { server, adapter: resolvedAdapter };
}

// Ejecutar directamente cuando se invoca `node server.mjs`
if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  loadLocalEnv();
  const port = Number(process.env.PORT || 3000);
  const { server, adapter } = await createAppServer();
  server.listen(port, '127.0.0.1', () => {
    console.log('===============================================================');
    console.log(` AutoGest Local Server activo en http://127.0.0.1:${port}`);
    console.log(`   Frontend : ${FRONT_DIR}`);
    console.log(`   API      : http://127.0.0.1:${port}/api/health`);
    console.log(`   Datos    : ${adapter.source}`);
    console.log('===============================================================');
  });
}
