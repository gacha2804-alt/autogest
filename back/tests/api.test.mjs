import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  lagrangeEvaluar,
  regresionLineal,
} from '../supabase/functions/_shared/math.js';
import { STATIC_NUMERICAL_SERIES } from '../supabase/functions/_shared/static-catalog.js';
import { createLocalFallbackAdapter } from '../local-adapter.mjs';
import { handleApiRequest } from '../supabase/functions/_shared/handlers.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const LOCAL_PRED_FILE = path.resolve(__dirname, '..', '.local-predictions.json');
const FRONT_DIR = path.resolve(__dirname, '..', '..', 'front');

test('Regresión lineal semestral (N=25) reproduce ecuación oficial AutoGest', () => {
  const sem = STATIC_NUMERICAL_SERIES.filter((s) => s.serie === 'semestral');
  assert.equal(sem.length, 25);

  const rl = regresionLineal(
    sem.map((s) => s.x_valor),
    sem.map((s) => s.y_valor)
  );

  assert.ok(Math.abs(rl.m - -99.8471) < 0.01, `Pendiente inesperada: ${rl.m}`);
  assert.ok(Math.abs(rl.b - 202487.6) < 2, `Intercepto inesperado: ${rl.b}`);
  assert.ok(Math.abs(rl.r2 * 100 - 37.98) < 0.1, `R2 inesperado: ${rl.r2 * 100}`);
  assert.ok(Math.abs(rl.err_std - 479.59) < 0.5, `Error estándar inesperado: ${rl.err_std}`);
});

test('Regresión lineal anual (N=13) e Interpolación Lagrange (5 nodos) cumplen propiedad cardinal', () => {
  const anual = STATIC_NUMERICAL_SERIES.filter((s) => s.serie === 'anual');
  const nodos = STATIC_NUMERICAL_SERIES.filter((s) => s.serie === 'lagrange_nodo');

  assert.equal(anual.length, 13);
  assert.equal(nodos.length, 5);

  const rl = regresionLineal(
    anual.map((s) => s.x_valor),
    anual.map((s) => s.y_valor)
  );
  assert.ok(Math.abs(rl.m - -91.2029) < 0.01);
  assert.ok(Math.abs(rl.b - 185021.59) < 2);

  const xs = nodos.map((n) => n.x_valor);
  const ys = nodos.map((n) => n.y_valor);
  for (let i = 0; i < xs.length; i++) {
    const val = lagrangeEvaluar(xs[i], xs, ys);
    assert.ok(Math.abs(val - ys[i]) < 1e-6, `Propiedad cardinal falló en nodo ${xs[i]}`);
  }
});

test('API router (handleApiRequest) responde correctamente en todos los endpoints y validaciones', async () => {
  const hadPredFile = fs.existsSync(LOCAL_PRED_FILE);
  const previousPred = hadPredFile ? fs.readFileSync(LOCAL_PRED_FILE, 'utf8') : null;

  const adapter = createLocalFallbackAdapter();
  const baseUrl = 'http://localhost:3000';
  const callApi = (route, init) => handleApiRequest(new Request(`${baseUrl}${route}`, init), adapter);

  try {
    // 1. GET /api/health
    const rHealth = await callApi('/api/health');
    assert.equal(rHealth.status, 200);
    const jHealth = await rHealth.json();
    assert.equal(jHealth.status, 'ok');
    assert.equal(jHealth.total_registros, 507);

    // 2. GET /api/dashboard (sin filtros y con filtros)
    const rDash = await callApi('/api/dashboard');
    assert.equal(rDash.status, 200);
    const jDash = await rDash.json();
    assert.equal(jDash.kpis.total_registros, 507);
    assert.equal(jDash.kpis.total_accidentes, 378234);
    assert.equal(jDash.serie_anual.length, 13);

    const rDashFiltered = await callApi(
      '/api/dashboard?anio_inicio=2020&anio_fin=2024&tipo_vehiculo=LIVIANO'
    );
    assert.equal(rDashFiltered.status, 200);
    const jDashFiltered = await rDashFiltered.json();
    assert.ok(jDashFiltered.kpis.total_registros > 0 && jDashFiltered.kpis.total_registros < 507);
    assert.equal(jDashFiltered.serie_anual.length, 5);

    // 3. GET /api/registros paginado (también probando prefijo Supabase Edge Function)
    const rReg = await callApi('/functions/v1/autogest-api/registros?anio=2024&limit=10&offset=0');
    assert.equal(rReg.status, 200);
    const jReg = await rReg.json();
    assert.equal(jReg.items.length, 10);
    assert.ok(jReg.total >= 10);

    // 4. GET /api/metodos-numericos
    const rMn = await callApi('/api/metodos-numericos');
    assert.equal(rMn.status, 200);
    const jMn = await rMn.json();
    assert.equal(jMn.semestral.puntos.length, 25);
    assert.equal(jMn.anual.puntos.length, 13);
    assert.equal(jMn.lagrange.nodos.length, 5);

    // 5. POST /api/predicciones + GET /api/predicciones
    const rPost = await callApi('/api/predicciones', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ modelo: 'regresion_anual', anio_entrada: 2027 }),
    });
    assert.equal(rPost.status, 201);
    const jPost = await rPost.json();
    assert.equal(jPost.prediccion.modelo, 'regresion_anual');
    assert.equal(jPost.prediccion.tipo_evaluacion, 'extrapolacion');

    const rList = await callApi('/api/predicciones?limit=5');
    assert.equal(rList.status, 200);
    const jList = await rList.json();
    assert.ok(jList.items.length >= 1);
    assert.equal(jList.items[0].anio_entrada, 2027);

    // 6. CORS preflight + Validaciones 400 y 404
    const rOpt = await callApi('/api/dashboard', { method: 'OPTIONS' });
    assert.equal(rOpt.status, 204);

    const rBad = await callApi('/api/predicciones', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ modelo: 'invalido', anio_entrada: 2027 }),
    });
    assert.equal(rBad.status, 400);

    const rNotFound = await callApi('/api/no-existe');
    assert.equal(rNotFound.status, 404);

    // 7. Integridad de archivos de front/ (cuando corre dentro del monorepo)
    if (fs.existsSync(FRONT_DIR)) {
      for (const file of ['index.html', 'metodos.html', 'chart.umd.min.js', 'config.js', 'api-client.js', 'netlify.toml']) {
        assert.ok(fs.existsSync(path.join(FRONT_DIR, file)), `Falta front/${file}`);
      }
      const indexHtml = fs.readFileSync(path.join(FRONT_DIR, 'index.html'), 'utf8');
      assert.ok(indexHtml.includes('/api-client.js'));
      assert.ok(indexHtml.includes('filtroTipoVehiculo'));
      assert.ok(!indexHtml.includes('18.83.46%'));
    }
  } finally {
    if (hadPredFile && previousPred !== null) {
      fs.writeFileSync(LOCAL_PRED_FILE, previousPred, 'utf8');
    } else if (!hadPredFile && fs.existsSync(LOCAL_PRED_FILE)) {
      fs.unlinkSync(LOCAL_PRED_FILE);
    }
  }
});

test('Control de vigencia hasta el 5 de diciembre de 2026 (23:59 COT)', async () => {
  let dbCalls = 0;
  const spyAdapter = {
    source: 'neondb',
    async healthCheck() {
      dbCalls += 1;
      return { connected: true, total_registros: 507 };
    },
  };

  // 1 minuto antes del cierre (5 dic 2026, 23:59:00 COT) -> 200 OK
  const rBefore = await handleApiRequest(
    new Request('http://localhost:3000/api/health'),
    spyAdapter,
    { nowMs: Date.parse('2026-12-05T23:59:00-05:00') }
  );
  assert.equal(rBefore.status, 200);
  const jBefore = await rBefore.json();
  assert.equal(jBefore.status, 'ok');
  assert.equal(jBefore.active_until, '2026-12-05T23:59:59-05:00');
  assert.equal(dbCalls, 1);

  // 1 minuto después del cierre (6 dic 2026, 00:01:00 COT) -> 503 sin tocar la BD
  const rAfter = await handleApiRequest(
    new Request('http://localhost:3000/api/health'),
    spyAdapter,
    { nowMs: Date.parse('2026-12-06T00:01:00-05:00') }
  );
  assert.equal(rAfter.status, 503);
  const jAfter = await rAfter.json();
  assert.equal(jAfter.status, 'closed');
  assert.equal(dbCalls, 1, 'No debe consultar NeonDB después de la fecha límite');
});
