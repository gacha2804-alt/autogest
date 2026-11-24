import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { parseCsvFile } from './db/env-utils.mjs';
import {
  STATIC_ML_METRICS,
  STATIC_NUMERICAL_SERIES,
} from './supabase/functions/_shared/static-catalog.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const PREDICTIONS_FILE = path.join(__dirname, '.local-predictions.json');

function resolveIntegratedCsv() {
  const candidates = [
    path.resolve(__dirname, 'dataset', 'dataset_integrado.csv'),
    path.resolve(__dirname, '..', 'dataset', 'dataset_integrado.csv'),
  ];
  return candidates.find((p) => fs.existsSync(p)) || candidates[0];
}

const num = (v) => {
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
};

/**
 * Adaptador local que lee los CSV consolidados reales (507 filas) y persiste predicciones
 * en back/.local-predictions.json cuando NEON_DATABASE_URL todavía no está configurada.
 */
export function createLocalFallbackAdapter() {
  const csvPath = resolveIntegratedCsv();
  const rawRows = fs.existsSync(csvPath) ? parseCsvFile(csvPath) : [];

  const registros = rawRows.map((r, idx) => ({
    id: idx + 1,
    anio: Math.trunc(num(r['AÑO'])),
    mes: Math.trunc(num(r['MES'])),
    tipo_vehiculo: String(r['TIPO_VEHICULO'] || 'OTRO').trim(),
    volumen_trafico: num(r['VOLUMEN_TRAFICO']),
    vehiculos_evasores: num(r['VEHICULOS_EVASORES']),
    vehiculos_exentos: num(r['VEHICULOS_EXENTOS']),
    tarifa_promedio: num(r['TARIFA_PROMEDIO']),
    recaudo_peajes: num(r['RECAUDO_PEAJES']),
    servicios_taller: num(r['SERVICIOS_TALLER']),
    costo_total_taller: num(r['COSTO_TOTAL_TALLER']),
    costo_promedio_taller: num(r['COSTO_PROMEDIO_TALLER']),
    horas_servicio_promedio: num(r['HORAS_SERVICIO_PROMEDIO']),
    millaje_promedio: num(r['MILLAJE_PROMEDIO']),
    distancia_grua_total: num(r['DISTANCIA_GRUA_TOTAL']),
    accidentes_totales: Math.trunc(num(r['ACCIDENTES_TOTALES'])),
    accidentes_registrados: num(r['ACCIDENTES_REGISTRADOS']),
    tasa_evasion_pct: num(r['TASA_EVASION_PCT']),
    tasa_exencion_pct: num(r['TASA_EXENCION_PCT']),
  }));

  function readPredictions() {
    if (!fs.existsSync(PREDICTIONS_FILE)) return [];
    try {
      const parsed = JSON.parse(fs.readFileSync(PREDICTIONS_FILE, 'utf8'));
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  }

  function writePredictions(list) {
    fs.writeFileSync(PREDICTIONS_FILE, JSON.stringify(list, null, 2), 'utf8');
  }

  function filterRows({ anioInicio, anioFin, anio, tipoVehiculo } = {}) {
    return registros.filter((r) => {
      if (Number.isInteger(anio) && r.anio !== anio) return false;
      if (Number.isInteger(anioInicio) && r.anio < anioInicio) return false;
      if (Number.isInteger(anioFin) && r.anio > anioFin) return false;
      if (tipoVehiculo && tipoVehiculo !== 'TODOS' && r.tipo_vehiculo !== tipoVehiculo) {
        return false;
      }
      return true;
    });
  }

  return {
    source: 'local-csv-fallback',

    async healthCheck() {
      return {
        connected: true,
        server_time: new Date().toISOString(),
        total_registros: registros.length,
        hint: 'Define NEON_DATABASE_URL en back/.env para conectar con NeonDB en vivo.',
      };
    },

    async getRegistros(filters = {}) {
      const filtered = filterRows(filters);
      const start = Number.isInteger(filters.offset) ? Math.max(filters.offset, 0) : 0;
      if (Number.isInteger(filters.limit)) {
        const safeLimit = Math.min(Math.max(filters.limit, 1), 1000);
        return filtered.slice(start, start + safeLimit);
      }
      return filtered;
    },

    async countRegistros(filters = {}) {
      return filterRows(filters).length;
    },

    async getMlMetrics() {
      return STATIC_ML_METRICS;
    },

    async getNumericalSeries() {
      return STATIC_NUMERICAL_SERIES;
    },

    async savePrediction({ modelo, anio_entrada, valor_predicho, tipo_evaluacion }) {
      const list = readPredictions();
      const nextId = list.length > 0 ? Math.max(...list.map((p) => Number(p.id) || 0)) + 1 : 1;
      const item = {
        id: nextId,
        modelo,
        anio_entrada,
        valor_predicho,
        tipo_evaluacion,
        creado_en: new Date().toISOString(),
      };
      list.unshift(item);
      writePredictions(list.slice(0, 200));
      return item;
    },

    async listPredictions(limit = 20) {
      const safeLimit = Math.min(Math.max(Number(limit) || 20, 1), 100);
      return readPredictions().slice(0, safeLimit);
    },
  };
}
