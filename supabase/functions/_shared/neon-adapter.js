/**
 * Adaptador PostgreSQL para NeonDB usando @neondatabase/serverless (HTTPS).
 * Todas las consultas usan templates parametrizados para prevenir inyección SQL.
 */

export function createNeonAdapter(sql) {
  return {
    source: 'neondb',

    async healthCheck() {
      const rows = await sql`SELECT NOW() AS server_time, COUNT(*)::int AS total_registros FROM registros_integrados`;
      return {
        connected: true,
        server_time: rows[0]?.server_time ?? null,
        total_registros: rows[0]?.total_registros ?? 0,
      };
    },

    async getRegistros({ anioInicio, anioFin, anio, tipoVehiculo, limit, offset } = {}) {
      const conditions = [];
      const params = [];

      if (Number.isInteger(anio)) {
        params.push(anio);
        conditions.push(`anio = $${params.length}`);
      } else {
        if (Number.isInteger(anioInicio)) {
          params.push(anioInicio);
          conditions.push(`anio >= $${params.length}`);
        }
        if (Number.isInteger(anioFin)) {
          params.push(anioFin);
          conditions.push(`anio <= $${params.length}`);
        }
      }

      if (tipoVehiculo && tipoVehiculo !== 'TODOS') {
        params.push(tipoVehiculo);
        conditions.push(`tipo_vehiculo = $${params.length}`);
      }

      const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';
      const limitClause = Number.isInteger(limit) ? `LIMIT ${Math.min(Math.max(limit, 1), 1000)}` : '';
      const offsetClause = Number.isInteger(offset) ? `OFFSET ${Math.max(offset, 0)}` : '';

      const queryText = `
        SELECT
          id, anio, mes, tipo_vehiculo,
          volumen_trafico, vehiculos_evasores, vehiculos_exentos,
          tarifa_promedio, recaudo_peajes, servicios_taller,
          costo_total_taller, costo_promedio_taller, horas_servicio_promedio,
          millaje_promedio, distancia_grua_total, accidentes_totales,
          accidentes_registrados, tasa_evasion_pct, tasa_exencion_pct
        FROM registros_integrados
        ${whereClause}
        ORDER BY anio ASC, mes ASC, tipo_vehiculo ASC
        ${limitClause} ${offsetClause}
      `;

      const res = await sql.query(queryText, params);
      return Array.isArray(res) ? res : res.rows || [];
    },

    async countRegistros({ anio, tipoVehiculo } = {}) {
      const conditions = [];
      const params = [];
      if (Number.isInteger(anio)) {
        params.push(anio);
        conditions.push(`anio = $${params.length}`);
      }
      if (tipoVehiculo && tipoVehiculo !== 'TODOS') {
        params.push(tipoVehiculo);
        conditions.push(`tipo_vehiculo = $${params.length}`);
      }
      const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';
      const res = await sql.query(
        `SELECT COUNT(*)::int AS total FROM registros_integrados ${whereClause}`,
        params
      );
      const rows = Array.isArray(res) ? res : res.rows || [];
      return rows[0]?.total ?? 0;
    },

    async getMlMetrics() {
      const rows = await sql`
        SELECT categoria, clave, payload, orden
        FROM metricas_modelos_ml
        ORDER BY categoria ASC, orden ASC
      `;
      return rows;
    },

    async getNumericalSeries() {
      const rows = await sql`
        SELECT serie, etiqueta, x_valor, y_valor, es_parcial, nota
        FROM series_metodos_numericos
        ORDER BY serie ASC, x_valor ASC
      `;
      return rows;
    },

    async savePrediction({ modelo, anio_entrada, valor_predicho, tipo_evaluacion }) {
      const rows = await sql`
        INSERT INTO historial_predicciones (modelo, anio_entrada, valor_predicho, tipo_evaluacion)
        VALUES (${modelo}, ${anio_entrada}, ${valor_predicho}, ${tipo_evaluacion})
        RETURNING id, modelo, anio_entrada, valor_predicho, tipo_evaluacion, creado_en
      `;
      return rows[0];
    },

    async listPredictions(limit = 20) {
      const safeLimit = Math.min(Math.max(Number(limit) || 20, 1), 100);
      const rows = await sql`
        SELECT id, modelo, anio_entrada, valor_predicho, tipo_evaluacion, creado_en
        FROM historial_predicciones
        ORDER BY creado_en DESC, id DESC
        LIMIT ${safeLimit}
      `;
      return rows;
    },
  };
}
