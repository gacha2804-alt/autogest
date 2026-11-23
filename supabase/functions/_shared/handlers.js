/**
 * Router y handlers HTTP de AutoGest API (Web Standard Request/Response).
 * Compatible tanto con Supabase Edge Functions (Deno) como con el servidor local Node 22.
 */

import {
  buildDashboardPayload,
  lagrangeBase,
  lagrangeEvaluar,
  regresionLineal,
} from './math.js';
import { STATIC_ML_METRICS, STATIC_NUMERICAL_SERIES } from './static-catalog.js';

const VALID_VEHICLES = new Set(['TODOS', 'LIVIANO', 'CARGA_PESADO', 'TRANSPORTE_PASAJEROS', 'OTRO']);
const VALID_MODELS = new Set(['regresion_anual', 'regresion_semestral', 'lagrange']);

// Vigencia oficial: hasta el 5 de diciembre de 2026 a las 23:59:59 hora Colombia (UTC-5)
export const DEFAULT_ACTIVE_UNTIL = '2026-12-06T04:59:59.000Z';
const ACTIVE_UNTIL_LABEL = '2026-12-05T23:59:59-05:00';

function corsHeaders(origin = '*') {
  return {
    'Access-Control-Allow-Origin': origin,
    'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, apikey, x-client-info',
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
  };
}

function jsonResponse(body, status = 200, corsOrigin = '*') {
  return new Response(JSON.stringify(body), {
    status,
    headers: corsHeaders(corsOrigin),
  });
}

function normalizePath(pathname) {
  let clean = pathname.replace(/\/+$/, '') || '/';
  // Soporta invocación directa en Supabase (/functions/v1/autogest-api/... o /autogest-api/...) y proxy Netlify (/api/...)
  clean = clean
    .replace(/^\/functions\/v1\/autogest-api/, '')
    .replace(/^\/autogest-api/, '')
    .replace(/^\/api/, '');
  return clean || '/';
}

function parseIntOrNull(val) {
  if (val === null || val === undefined || val === '') return null;
  const n = Number(val);
  return Number.isInteger(n) ? n : NaN;
}

export async function handleApiRequest(request, adapter, options = {}) {
  const corsOrigin = options.corsOrigin || '*';
  const method = request.method.toUpperCase();

  if (method === 'OPTIONS') {
    return new Response(null, { status: 204, headers: corsHeaders(corsOrigin) });
  }

  // Verificar vigencia antes de consultar la base de datos (0 consumo en NeonDB tras el cierre)
  const cutoffIso = options.activeUntil === undefined ? DEFAULT_ACTIVE_UNTIL : options.activeUntil;
  const nowMs = typeof options.nowMs === 'number' ? options.nowMs : Date.now();
  if (cutoffIso && Number.isFinite(Date.parse(cutoffIso)) && nowMs > Date.parse(cutoffIso)) {
    return jsonResponse(
      {
        status: 'closed',
        service: 'autogest-api',
        active_until: ACTIVE_UNTIL_LABEL,
        message: 'La demostración académica AutoGest estuvo disponible hasta el 5 de diciembre de 2026.',
      },
      503,
      corsOrigin
    );
  }

  const url = new URL(request.url);
  const route = normalizePath(url.pathname);

  try {
    // 1. GET /health
    if (method === 'GET' && (route === '/' || route === '/health')) {
      const health = await adapter.healthCheck();
      return jsonResponse(
        {
          status: 'ok',
          service: 'autogest-api',
          db: adapter.source,
          active_until: ACTIVE_UNTIL_LABEL,
          ...health,
          timestamp: new Date().toISOString(),
        },
        200,
        corsOrigin
      );
    }

    // 2. GET /dashboard
    if (method === 'GET' && route === '/dashboard') {
      const anioInicio = parseIntOrNull(url.searchParams.get('anio_inicio'));
      const anioFin = parseIntOrNull(url.searchParams.get('anio_fin'));
      const tipoVehiculo = (url.searchParams.get('tipo_vehiculo') || 'TODOS').toUpperCase();

      if (Number.isNaN(anioInicio) || Number.isNaN(anioFin)) {
        return jsonResponse({ error: 'anio_inicio y anio_fin deben ser enteros válidos.' }, 400, corsOrigin);
      }
      if (!VALID_VEHICLES.has(tipoVehiculo)) {
        return jsonResponse({ error: `tipo_vehiculo inválido: ${tipoVehiculo}` }, 400, corsOrigin);
      }

      const [rows, mlMetrics] = await Promise.all([
        adapter.getRegistros({ anioInicio, anioFin, tipoVehiculo }),
        adapter.getMlMetrics(),
      ]);

      const payload = buildDashboardPayload(
        rows,
        mlMetrics.length > 0 ? mlMetrics : STATIC_ML_METRICS
      );

      return jsonResponse(
        {
          source: adapter.source,
          filtros: {
            anio_inicio: anioInicio,
            anio_fin: anioFin,
            tipo_vehiculo: tipoVehiculo,
          },
          ...payload,
        },
        200,
        corsOrigin
      );
    }

    // 3. GET /registros
    if (method === 'GET' && route === '/registros') {
      const anio = parseIntOrNull(url.searchParams.get('anio'));
      const tipoVehiculo = (url.searchParams.get('tipo_vehiculo') || 'TODOS').toUpperCase();
      const limit = parseIntOrNull(url.searchParams.get('limit')) ?? 50;
      const offset = parseIntOrNull(url.searchParams.get('offset')) ?? 0;

      if (Number.isNaN(anio) || Number.isNaN(limit) || Number.isNaN(offset)) {
        return jsonResponse({ error: 'Parámetros numéricos inválidos.' }, 400, corsOrigin);
      }
      if (!VALID_VEHICLES.has(tipoVehiculo)) {
        return jsonResponse({ error: `tipo_vehiculo inválido: ${tipoVehiculo}` }, 400, corsOrigin);
      }

      const [items, total] = await Promise.all([
        adapter.getRegistros({ anio, tipoVehiculo, limit, offset }),
        adapter.countRegistros({ anio, tipoVehiculo }),
      ]);

      return jsonResponse(
        {
          source: adapter.source,
          total,
          limit: Math.min(Math.max(limit, 1), 1000),
          offset: Math.max(offset, 0),
          items,
        },
        200,
        corsOrigin
      );
    }

    // 4. GET /metodos-numericos
    if (method === 'GET' && route === '/metodos-numericos') {
      const seriesRaw = await adapter.getNumericalSeries();
      const series = seriesRaw.length > 0 ? seriesRaw : STATIC_NUMERICAL_SERIES;

      const semestral = series.filter((s) => s.serie === 'semestral');
      const anual = series.filter((s) => s.serie === 'anual');
      const nodosLagrange = series.filter((s) => s.serie === 'lagrange_nodo');

      const rlSemestral = regresionLineal(
        semestral.map((s) => Number(s.x_valor)),
        semestral.map((s) => Number(s.y_valor))
      );
      const rlAnual = regresionLineal(
        anual.map((s) => Number(s.x_valor)),
        anual.map((s) => Number(s.y_valor))
      );

      return jsonResponse(
        {
          source: adapter.source,
          semestral: {
            puntos: semestral,
            regresion: rlSemestral,
          },
          anual: {
            puntos: anual,
            regresion: rlAnual,
          },
          lagrange: {
            grado: nodosLagrange.length - 1,
            nodos: nodosLagrange,
          },
        },
        200,
        corsOrigin
      );
    }

    // 5. GET /predicciones
    if (method === 'GET' && route === '/predicciones') {
      const limit = parseIntOrNull(url.searchParams.get('limit')) ?? 20;
      const items = await adapter.listPredictions(Number.isNaN(limit) ? 20 : limit);
      return jsonResponse({ source: adapter.source, items }, 200, corsOrigin);
    }

    // 6. POST /predicciones
    if (method === 'POST' && route === '/predicciones') {
      let body;
      try {
        body = await request.json();
      } catch {
        return jsonResponse({ error: 'El cuerpo de la petición debe ser JSON válido.' }, 400, corsOrigin);
      }

      const modelo = String(body?.modelo || '').trim();
      const anioEntrada = Number(body?.anio_entrada);

      if (!VALID_MODELS.has(modelo)) {
        return jsonResponse(
          { error: 'modelo debe ser regresion_anual, regresion_semestral o lagrange.' },
          400,
          corsOrigin
        );
      }
      if (!Number.isFinite(anioEntrada) || anioEntrada < 1900 || anioEntrada > 2150) {
        return jsonResponse(
          { error: 'anio_entrada debe ser un número válido entre 1900 y 2150.' },
          400,
          corsOrigin
        );
      }

      const seriesRaw = await adapter.getNumericalSeries();
      const series = seriesRaw.length > 0 ? seriesRaw : STATIC_NUMERICAL_SERIES;

      let valorPredicho = 0;
      let tipoEvaluacion = 'extrapolacion';
      let detalle = {};

      if (modelo === 'regresion_anual') {
        const pts = series.filter((s) => s.serie === 'anual');
        const xs = pts.map((p) => Number(p.x_valor));
        const ys = pts.map((p) => Number(p.y_valor));
        const rl = regresionLineal(xs, ys);
        valorPredicho = rl.m * anioEntrada + rl.b;
        tipoEvaluacion =
          anioEntrada >= Math.min(...xs) && anioEntrada <= Math.max(...xs)
            ? 'interpolacion'
            : 'extrapolacion';
        detalle = { m: rl.m, b: rl.b, r2: rl.r2 };
      } else if (modelo === 'regresion_semestral') {
        const pts = series.filter((s) => s.serie === 'semestral');
        const xs = pts.map((p) => Number(p.x_valor));
        const ys = pts.map((p) => Number(p.y_valor));
        const rl = regresionLineal(xs, ys);
        valorPredicho = rl.m * anioEntrada + rl.b;
        tipoEvaluacion =
          anioEntrada >= Math.min(...xs) && anioEntrada <= Math.max(...xs)
            ? 'interpolacion'
            : 'extrapolacion';
        detalle = { m: rl.m, b: rl.b, r2: rl.r2 };
      } else {
        const pts = series.filter((s) => s.serie === 'lagrange_nodo');
        const xs = pts.map((p) => Number(p.x_valor));
        const ys = pts.map((p) => Number(p.y_valor));
        valorPredicho = lagrangeEvaluar(anioEntrada, xs, ys);
        tipoEvaluacion =
          anioEntrada >= Math.min(...xs) && anioEntrada <= Math.max(...xs)
            ? 'interpolacion'
            : 'extrapolacion';
        detalle = {
          bases: xs.map((_, i) => Number(lagrangeBase(i, anioEntrada, xs).toFixed(4))),
          rango_nodos: [Math.min(...xs), Math.max(...xs)],
        };
      }

      const saved = await adapter.savePrediction({
        modelo,
        anio_entrada: anioEntrada,
        valor_predicho: Number(valorPredicho.toFixed(4)),
        tipo_evaluacion: tipoEvaluacion,
      });

      return jsonResponse(
        {
          source: adapter.source,
          prediccion: saved,
          detalle,
        },
        201,
        corsOrigin
      );
    }

    return jsonResponse({ error: `Ruta no encontrada: ${route}` }, 404, corsOrigin);
  } catch (err) {
    console.error('[autogest-api] Error:', err);
    return jsonResponse(
      { error: 'Error interno en el servidor.', detail: err?.message || String(err) },
      500,
      corsOrigin
    );
  }
}
