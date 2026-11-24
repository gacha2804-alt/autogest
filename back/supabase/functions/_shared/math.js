/**
 * Núcleo matemático y de agregación analítica de AutoGest.
 * Implementado desde cero en JS puro (compatible con Node 22 y Deno Edge).
 */

export function regresionLineal(xs, ys) {
  const n = xs.length;
  if (n !== ys.length || n < 2) {
    throw new Error('Se requieren al menos 2 pares (x, y) de igual longitud.');
  }

  let sx = 0;
  let sy = 0;
  let sxy = 0;
  let sx2 = 0;
  let sy2 = 0;

  for (let i = 0; i < n; i++) {
    const x = Number(xs[i]);
    const y = Number(ys[i]);
    sx += x;
    sy += y;
    sxy += x * y;
    sx2 += x * x;
    sy2 += y * y;
  }

  const xm = sx / n;
  const ym = sy / n;
  const num_m = n * sxy - sx * sy;
  const den_m = n * sx2 - sx * sx;
  if (Math.abs(den_m) < 1e-12) {
    throw new Error('Denominador nulo: todos los valores X son constantes.');
  }

  const m = num_m / den_m;
  const b = ym - m * xm;
  const yp = xs.map((x) => m * Number(x) + b);

  let ss_tot = 0;
  let ss_res = 0;
  const err_abs = [];
  const err_pct = [];

  for (let i = 0; i < n; i++) {
    const y = Number(ys[i]);
    const pred = yp[i];
    ss_tot += (y - ym) ** 2;
    ss_res += (y - pred) ** 2;
    const ea = Math.abs(y - pred);
    err_abs.push(ea);
    err_pct.push(y !== 0 ? (ea / Math.abs(y)) * 100 : 0);
  }

  const r2 = ss_tot > 0 ? 1 - ss_res / ss_tot : 0;
  const err_std = n > 2 ? Math.sqrt(ss_res / (n - 2)) : 0;

  return {
    n,
    sx,
    sy,
    sxy,
    sx2,
    sy2,
    xm,
    ym,
    num_m,
    den_m,
    m,
    b,
    yp,
    ss_tot,
    ss_res,
    r2,
    err_std,
    err_abs,
    err_pct,
  };
}

export function lagrangeBase(i, x, xs) {
  let result = 1.0;
  for (let j = 0; j < xs.length; j++) {
    if (j !== i) {
      result *= (x - xs[j]) / (xs[i] - xs[j]);
    }
  }
  return result;
}

export function lagrangeEvaluar(x, xs, ys) {
  let sum = 0;
  for (let i = 0; i < xs.length; i++) {
    sum += ys[i] * lagrangeBase(i, x, xs);
  }
  return sum;
}

export function pearson(xs, ys) {
  const n = Math.min(xs.length, ys.length);
  if (n < 2) return 0;
  let sx = 0;
  let sy = 0;
  for (let i = 0; i < n; i++) {
    sx += xs[i];
    sy += ys[i];
  }
  const mx = sx / n;
  const my = sy / n;
  let num = 0;
  let dx2 = 0;
  let dy2 = 0;
  for (let i = 0; i < n; i++) {
    const dx = xs[i] - mx;
    const dy = ys[i] - my;
    num += dx * dy;
    dx2 += dx * dx;
    dy2 += dy * dy;
  }
  const den = Math.sqrt(dx2 * dy2);
  return den > 0 ? num / den : 0;
}

/**
 * Construye el payload agregado del dashboard a partir de las filas de `registros_integrados`.
 */
export function buildDashboardPayload(rows, mlMetrics = []) {
  const totalRegistros = rows.length;
  let totalAccidentes = 0;
  let totalTrafico = 0;
  let totalRecaudo = 0;
  let totalServiciosTaller = 0;
  let millajeSum = 0;
  let millajeCount = 0;

  const porAnio = new Map();
  const porTipo = new Map();
  const porMes = new Map();
  const acc2024 = Array(12).fill(0);

  const trafArr = [];
  const exentosArr = [];
  const accArr = [];

  for (const r of rows) {
    const anio = Number(r.anio);
    const mes = Number(r.mes);
    const tipo = String(r.tipo_vehiculo || 'OTRO');
    const acc = Number(r.accidentes_registrados || 0);
    const traf = Number(r.volumen_trafico || 0);
    const rec = Number(r.recaudo_peajes || 0);
    const srv = Number(r.servicios_taller || 0);
    const evas = Number(r.vehiculos_evasores || 0);
    const exen = Number(r.vehiculos_exentos || 0);
    const tasaEv = Number(r.tasa_evasion_pct || 0);
    const millaje = Number(r.millaje_promedio || 0);

    totalAccidentes += acc;
    totalTrafico += traf;
    totalRecaudo += rec;
    totalServiciosTaller += srv;
    if (millaje > 0) {
      millajeSum += millaje;
      millajeCount += 1;
    }

    trafArr.push(traf);
    exentosArr.push(exen);
    accArr.push(acc);

    if (!porAnio.has(anio)) {
      porAnio.set(anio, {
        anio,
        accidentes: 0,
        trafico: 0,
        evasores_sum: 0,
        tasa_evasion_sum: 0,
        count: 0,
      });
    }
    const aObj = porAnio.get(anio);
    aObj.accidentes += acc;
    aObj.trafico += traf;
    aObj.evasores_sum += evas;
    aObj.tasa_evasion_sum += tasaEv;
    aObj.count += 1;

    if (!porTipo.has(tipo)) {
      porTipo.set(tipo, { tipo_vehiculo: tipo, accidentes: 0, recaudo: 0, trafico: 0 });
    }
    const tObj = porTipo.get(tipo);
    tObj.accidentes += acc;
    tObj.recaudo += rec;
    tObj.trafico += traf;

    if (!porMes.has(mes)) {
      porMes.set(mes, { mes, acc_sum: 0, count: 0 });
    }
    const mObj = porMes.get(mes);
    mObj.acc_sum += acc;
    mObj.count += 1;

    if (anio === 2024 && mes >= 1 && mes <= 12) {
      acc2024[mes - 1] += acc;
    }
  }

  const aniosOrdenados = [...porAnio.values()].sort((a, b) => a.anio - b.anio);
  const maxTraf = Math.max(...aniosOrdenados.map((a) => a.trafico), 1);
  const minTraf = Math.min(...aniosOrdenados.map((a) => a.trafico), 0);
  const maxAcc = Math.max(...aniosOrdenados.map((a) => a.accidentes), 1);
  const minAcc = Math.min(...aniosOrdenados.map((a) => a.accidentes), 0);

  const serieAnual = aniosOrdenados.map((a) => ({
    anio: a.anio,
    etiqueta: a.anio === 2026 ? '2026* (5 meses)' : String(a.anio),
    accidentes: Math.round(a.accidentes),
    trafico: Math.round(a.trafico),
    evasores_promedio: Math.round(a.evasores_sum / Math.max(a.count, 1)),
    tasa_evasion_pct: Number((a.tasa_evasion_sum / Math.max(a.count, 1)).toFixed(2)),
    trafico_norm: Number(((a.trafico - minTraf) / Math.max(maxTraf - minTraf, 1)).toFixed(2)),
    accidentes_norm: Number(((a.accidentes - minAcc) / Math.max(maxAcc - minAcc, 1)).toFixed(2)),
  }));

  const ordenTipos = ['LIVIANO', 'CARGA_PESADO', 'TRANSPORTE_PASAJEROS', 'OTRO'];
  const porTipoVehiculo = ordenTipos
    .map((clave) => {
      const found = porTipo.get(clave) || {
        tipo_vehiculo: clave,
        accidentes: 0,
        recaudo: 0,
        trafico: 0,
      };
      return {
        tipo_vehiculo: found.tipo_vehiculo,
        accidentes: Math.round(found.accidentes),
        recaudo_mm_cop: Number((found.recaudo / 1e9).toFixed(2)),
        trafico: Math.round(found.trafico),
      };
    })
    .filter((t) => t.accidentes > 0 || t.tipo_vehiculo !== 'OTRO' || porTipo.has('OTRO'));

  const estacionalidadMensual = Array.from({ length: 12 }, (_, idx) => {
    const m = porMes.get(idx + 1);
    return {
      mes: idx + 1,
      promedio_accidentes: m && m.count > 0 ? Number((m.acc_sum / m.count).toFixed(2)) : 0,
    };
  });

  // Agrupar métricas ML por categoría
  const mlAgrupado = {};
  for (const item of mlMetrics) {
    if (!mlAgrupado[item.categoria]) mlAgrupado[item.categoria] = [];
    mlAgrupado[item.categoria].push(item.payload);
  }

  return {
    kpis: {
      total_registros: totalRegistros,
      total_accidentes: Math.round(totalAccidentes),
      volumen_trafico_total: Math.round(totalTrafico),
      recaudo_total_cop: Math.round(totalRecaudo),
      servicios_taller_total: Math.round(totalServiciosTaller),
      promedio_accidentes_periodo: totalRegistros > 0 ? Math.round(totalAccidentes / totalRegistros) : 0,
      millaje_promedio: millajeCount > 0 ? Math.round(millajeSum / millajeCount) : 0,
      anios_cubiertos: aniosOrdenados.length,
      r_trafico_accidentes: Number(pearson(trafArr, accArr).toFixed(4)),
      r_exentos_accidentes: Number(pearson(exentosArr, accArr).toFixed(4)),
    },
    serie_anual: serieAnual,
    por_tipo_vehiculo: porTipoVehiculo,
    estacionalidad_mensual: estacionalidadMensual,
    accidentes_2024_mensual: acc2024.map((v) => Math.round(v)),
    modelos_ml: mlAgrupado,
  };
}
