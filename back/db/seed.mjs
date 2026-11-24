import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { getNeonClient, parseCsvFile } from './env-utils.mjs';
import {
  STATIC_ML_METRICS,
  STATIC_NUMERICAL_SERIES,
} from '../supabase/functions/_shared/static-catalog.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

function resolveDatasetFile(fileName) {
  const candidates = [
    path.resolve(__dirname, '..', 'dataset', fileName),
    path.resolve(__dirname, '..', '..', 'dataset', fileName),
  ];
  for (const p of candidates) {
    if (fs.existsSync(p)) return p;
  }
  throw new Error(`No se encontró ${fileName} en ninguna ruta esperada.`);
}

const num = (v) => {
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
};

async function insertBatch(sql, table, columns, rows, conflictClause, batchSize = 100) {
  for (let start = 0; start < rows.length; start += batchSize) {
    const chunk = rows.slice(start, start + batchSize);
    const params = [];
    const valueGroups = chunk.map((row) => {
      const placeholders = row.map((val) => {
        params.push(val);
        return `$${params.length}`;
      });
      return `(${placeholders.join(', ')})`;
    });
    const query = `INSERT INTO ${table} (${columns.join(', ')}) VALUES ${valueGroups.join(', ')} ${conflictClause}`;
    await sql.query(query, params);
  }
}

async function runSeed() {
  const sql = await getNeonClient();

  const integradoPath = resolveDatasetFile('dataset_integrado.csv');
  const reducidoPath = resolveDatasetFile('dataset_reducido.csv');

  const rowsIntegrado = parseCsvFile(integradoPath);
  const rowsReducido = parseCsvFile(reducidoPath);

  console.log(`[db:seed] Cargando ${rowsIntegrado.length} registros integrados en NeonDB (por lotes)...`);
  await insertBatch(
    sql,
    'registros_integrados',
    [
      'anio', 'mes', 'tipo_vehiculo',
      'volumen_trafico', 'vehiculos_evasores', 'vehiculos_exentos',
      'tarifa_promedio', 'recaudo_peajes', 'servicios_taller',
      'costo_total_taller', 'costo_promedio_taller', 'horas_servicio_promedio',
      'millaje_promedio', 'distancia_grua_total', 'accidentes_totales',
      'accidentes_registrados', 'tasa_evasion_pct', 'tasa_exencion_pct',
    ],
    rowsIntegrado.map((r) => [
      Math.trunc(num(r['AÑO'])),
      Math.trunc(num(r['MES'])),
      String(r['TIPO_VEHICULO'] || 'OTRO').trim(),
      num(r['VOLUMEN_TRAFICO']),
      num(r['VEHICULOS_EVASORES']),
      num(r['VEHICULOS_EXENTOS']),
      num(r['TARIFA_PROMEDIO']),
      num(r['RECAUDO_PEAJES']),
      num(r['SERVICIOS_TALLER']),
      num(r['COSTO_TOTAL_TALLER']),
      num(r['COSTO_PROMEDIO_TALLER']),
      num(r['HORAS_SERVICIO_PROMEDIO']),
      num(r['MILLAJE_PROMEDIO']),
      num(r['DISTANCIA_GRUA_TOTAL']),
      Math.trunc(num(r['ACCIDENTES_TOTALES'])),
      num(r['ACCIDENTES_REGISTRADOS']),
      num(r['TASA_EVASION_PCT']),
      num(r['TASA_EXENCION_PCT']),
    ]),
    `ON CONFLICT (anio, mes, tipo_vehiculo) DO UPDATE SET
      volumen_trafico = EXCLUDED.volumen_trafico,
      vehiculos_evasores = EXCLUDED.vehiculos_evasores,
      vehiculos_exentos = EXCLUDED.vehiculos_exentos,
      tarifa_promedio = EXCLUDED.tarifa_promedio,
      recaudo_peajes = EXCLUDED.recaudo_peajes,
      servicios_taller = EXCLUDED.servicios_taller,
      costo_total_taller = EXCLUDED.costo_total_taller,
      costo_promedio_taller = EXCLUDED.costo_promedio_taller,
      horas_servicio_promedio = EXCLUDED.horas_servicio_promedio,
      millaje_promedio = EXCLUDED.millaje_promedio,
      distancia_grua_total = EXCLUDED.distancia_grua_total,
      accidentes_totales = EXCLUDED.accidentes_totales,
      accidentes_registrados = EXCLUDED.accidentes_registrados,
      tasa_evasion_pct = EXCLUDED.tasa_evasion_pct,
      tasa_exencion_pct = EXCLUDED.tasa_exencion_pct`,
    100
  );

  console.log(`[db:seed] Cargando ${rowsReducido.length} componentes PCA en NeonDB (por lotes)...`);
  await insertBatch(
    sql,
    'componentes_pca',
    ['anio', 'mes', 'tipo_vehiculo', 'pc1', 'pc2', 'pc3', 'pc4', 'pc5', 'accidentes_registrados'],
    rowsReducido.map((r) => [
      Math.trunc(num(r['AÑO'])),
      Math.trunc(num(r['MES'])),
      String(r['TIPO_VEHICULO'] || 'OTRO').trim(),
      num(r['PC1']),
      num(r['PC2']),
      num(r['PC3']),
      num(r['PC4']),
      num(r['PC5']),
      num(r['ACCIDENTES_REGISTRADOS']),
    ]),
    `ON CONFLICT (anio, mes, tipo_vehiculo) DO UPDATE SET
      pc1 = EXCLUDED.pc1,
      pc2 = EXCLUDED.pc2,
      pc3 = EXCLUDED.pc3,
      pc4 = EXCLUDED.pc4,
      pc5 = EXCLUDED.pc5,
      accidentes_registrados = EXCLUDED.accidentes_registrados`,
    100
  );

  console.log(`[db:seed] Cargando ${STATIC_ML_METRICS.length} métricas de modelos ML...`);
  await insertBatch(
    sql,
    'metricas_modelos_ml',
    ['categoria', 'clave', 'payload', 'orden'],
    STATIC_ML_METRICS.map((m) => [m.categoria, m.clave, JSON.stringify(m.payload), m.orden]),
    `ON CONFLICT (categoria, clave) DO UPDATE SET
      payload = EXCLUDED.payload,
      orden = EXCLUDED.orden`,
    50
  );

  console.log(`[db:seed] Cargando ${STATIC_NUMERICAL_SERIES.length} series de Métodos Numéricos...`);
  await insertBatch(
    sql,
    'series_metodos_numericos',
    ['serie', 'etiqueta', 'x_valor', 'y_valor', 'es_parcial', 'nota'],
    STATIC_NUMERICAL_SERIES.map((s) => [
      s.serie,
      s.etiqueta,
      s.x_valor,
      s.y_valor,
      s.es_parcial,
      s.nota,
    ]),
    `ON CONFLICT (serie, etiqueta) DO UPDATE SET
      x_valor = EXCLUDED.x_valor,
      y_valor = EXCLUDED.y_valor,
      es_parcial = EXCLUDED.es_parcial,
      nota = EXCLUDED.nota`,
    50
  );

  const [cReg] = await sql`SELECT COUNT(*)::int AS total FROM registros_integrados`;
  const [cPca] = await sql`SELECT COUNT(*)::int AS total FROM componentes_pca`;
  const [cMl] = await sql`SELECT COUNT(*)::int AS total FROM metricas_modelos_ml`;
  const [cMn] = await sql`SELECT COUNT(*)::int AS total FROM series_metodos_numericos`;

  console.log('[db:seed] Carga finalizada en NeonDB:', {
    registros_integrados: cReg.total,
    componentes_pca: cPca.total,
    metricas_modelos_ml: cMl.total,
    series_metodos_numericos: cMn.total,
  });
}

runSeed().catch((err) => {
  console.error('[db:seed] Error:', err.message);
  process.exit(1);
});
