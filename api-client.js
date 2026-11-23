/**
 * Cliente HTTP del Frontend AutoGest para consumir la API (Local / Supabase Edge Functions -> NeonDB).
 * Maneja estado de conexión, filtros dinámicos del dashboard e historial de predicciones.
 */
(function () {
  'use strict';

  const cfg = window.AUTOGEST_CONFIG || { API_BASE_URL: '/api' };
  const API_BASE = String(cfg.API_BASE_URL || '/api').replace(/\/+$/, '');

  async function apiFetch(endpoint, options = {}) {
    const res = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
      ...options,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(data.error || `HTTP ${res.status}`);
    }
    return data;
  }

  function formatCompact(value, suffix = '') {
    if (value >= 1e9) return `${(value / 1e9).toFixed(1)}B${suffix}`;
    if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M${suffix}`;
    if (value >= 1e3) return `${(value / 1e3).toFixed(0)}K${suffix}`;
    return `${Math.round(value).toLocaleString('es-CO')}${suffix}`;
  }

  function updateStatusBadge(state, text) {
    const el = document.getElementById('apiStatusBadge');
    if (!el) return;
    el.textContent = text;
    if (state === 'neondb') {
      el.style.background = '#10b98125';
      el.style.color = '#34d399';
      el.style.borderColor = '#10b98160';
    } else if (state === 'local') {
      el.style.background = '#0ea5e925';
      el.style.color = '#38bdf8';
      el.style.borderColor = '#0ea5e960';
    } else {
      el.style.background = '#f9731625';
      el.style.color = '#fb923c';
      el.style.borderColor = '#f9731660';
    }
  }

  function applyDashboardData(data) {
    if (!data || !data.kpis) return;
    const k = data.kpis;

    const setTxt = (id, val) => {
      const node = document.getElementById(id);
      if (node) node.textContent = val;
    };

    setTxt('kpiValAccidentes', Number(k.total_accidentes).toLocaleString('es-CO'));
    setTxt('kpiValTrafico', `${(Number(k.volumen_trafico_total) / 1e6).toLocaleString('es-CO', { maximumFractionDigits: 0 })}M`);
    setTxt('kpiValRecaudo', `$${(Number(k.recaudo_total_cop) / 1e12).toFixed(1)}B`);
    setTxt('kpiValTaller', formatCompact(Number(k.servicios_taller_total)));
    setTxt('kpiValPromedio', Number(k.promedio_accidentes_periodo).toLocaleString('es-CO'));
    setTxt('kpiValMillaje', Number(k.millaje_promedio).toLocaleString('es-CO'));
    setTxt('kpiValAnios', `${k.anios_cubiertos} años`);
    setTxt('badgeTotalRegistros', `📊 ${k.total_registros} registros`);

    const charts = window.AUTOGEST_CHARTS || {};
    const serie = data.serie_anual || [];
    const labels = serie.map((s) => s.etiqueta);

    if (charts.accAnio && serie.length > 0) {
      charts.accAnio.data.labels = labels;
      charts.accAnio.data.datasets[0].data = serie.map((s) => s.accidentes);
      charts.accAnio.update();
    }

    if (charts.trafico && serie.length > 0) {
      charts.trafico.data.labels = labels;
      charts.trafico.data.datasets[0].data = serie.map((s) => s.trafico);
      charts.trafico.update();
    }

    if (charts.correlacion && serie.length > 0) {
      charts.correlacion.data.labels = labels;
      charts.correlacion.data.datasets[0].label = `Volumen Tráfico (norm.) · r = ${k.r_trafico_accidentes}`;
      charts.correlacion.data.datasets[0].data = serie.map((s) => s.trafico_norm);
      charts.correlacion.data.datasets[1].data = serie.map((s) => s.accidentes_norm);
      charts.correlacion.update();
    }

    if (charts.evasion && serie.length > 0) {
      charts.evasion.data.labels = labels;
      charts.evasion.data.datasets[0].data = serie.map((s) => s.tasa_evasion_pct);
      charts.evasion.update();
    }

    if (charts.evasores && serie.length > 0) {
      charts.evasores.data.labels = labels;
      charts.evasores.data.datasets[0].data = serie.map((s) => s.evasores_promedio);
      charts.evasores.update();
    }

    const tipos = data.por_tipo_vehiculo || [];
    const labelMap = {
      LIVIANO: 'Liviano',
      CARGA_PESADO: 'Carga Pesado',
      TRANSPORTE_PASAJEROS: 'Transporte Pasajeros',
      OTRO: 'Otro',
    };

    if (charts.tipoVeh && tipos.length > 0) {
      charts.tipoVeh.data.labels = tipos.map((t) => labelMap[t.tipo_vehiculo] || t.tipo_vehiculo);
      charts.tipoVeh.data.datasets[0].data = tipos.map((t) => t.accidentes);
      charts.tipoVeh.update();
    }

    if (charts.recaudo && tipos.length > 0) {
      charts.recaudo.data.labels = tipos.map((t) => labelMap[t.tipo_vehiculo] || t.tipo_vehiculo);
      charts.recaudo.data.datasets[0].data = tipos.map((t) => t.recaudo_mm_cop);
      charts.recaudo.update();
    }

    const est = data.estacionalidad_mensual || [];
    if (charts.meses && est.length === 12) {
      charts.meses.data.datasets[0].data = est.map((m) => m.promedio_accidentes);
      charts.meses.update();
    }

    const filterMeta = document.getElementById('filterMetaInfo');
    if (filterMeta) {
      filterMeta.textContent = `Mostrando ${k.total_registros} observaciones · Fuente: ${data.source} · Pearson r(Tráfico,Acc) = ${k.r_trafico_accidentes}`;
    }
  }

  function renderPredictionHistory(items) {
    const tbody = document.getElementById('tbodyHistorialPredicciones');
    if (!tbody) return;
    if (!items || items.length === 0) {
      tbody.innerHTML =
        '<tr><td colspan="5" style="text-align:center;color:var(--muted)">Aún no hay cálculos guardados. Usa la calculadora para registrar una predicción en la BD.</td></tr>';
      return;
    }

    const modelLabels = {
      regresion_anual: 'Regresión Anual (MCO)',
      regresion_semestral: 'Regresión Semestral (N=25)',
      lagrange: 'Interpolación Lagrange (g=4)',
    };

    tbody.innerHTML = items
      .slice(0, 10)
      .map((item) => {
        const fecha = item.creado_en
          ? new Date(item.creado_en).toLocaleString('es-CO', {
              dateStyle: 'short',
              timeStyle: 'short',
            })
          : '—';
        const badgeCls =
          item.tipo_evaluacion === 'interpolacion' ? 'pill-green b-verde' : 'pill-orange b-naranja';
        const valFmt = Number(item.valor_predicho).toLocaleString('es-CO', {
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        });
        return `<tr>
          <td><strong>${modelLabels[item.modelo] || item.modelo}</strong></td>
          <td>${item.anio_entrada}</td>
          <td style="text-align:right"><strong>${valFmt}</strong></td>
          <td><span class="pill badge ${badgeCls}">${item.tipo_evaluacion}</span></td>
          <td style="color:var(--muted);font-size:.75rem">${fecha}</td>
        </tr>`;
      })
      .join('');
  }

  async function loadPredictions() {
    try {
      const data = await apiFetch('/predicciones?limit=10');
      renderPredictionHistory(data.items || []);
      return data;
    } catch {
      return null;
    }
  }

  async function savePrediction(modelo, anioEntrada) {
    try {
      const res = await apiFetch('/predicciones', {
        method: 'POST',
        body: JSON.stringify({ modelo, anio_entrada: Number(anioEntrada) }),
      });
      await loadPredictions();
      return res;
    } catch (err) {
      console.warn('[AutoGest API] No se pudo guardar la predicción:', err.message);
      return null;
    }
  }

  async function applyDashboardFilters() {
    const anioInicio = document.getElementById('filtroAnioInicio')?.value || '';
    const anioFin = document.getElementById('filtroAnioFin')?.value || '';
    const tipoVehiculo = document.getElementById('filtroTipoVehiculo')?.value || 'TODOS';
    const qs = new URLSearchParams();
    if (anioInicio) qs.set('anio_inicio', anioInicio);
    if (anioFin) qs.set('anio_fin', anioFin);
    if (tipoVehiculo) qs.set('tipo_vehiculo', tipoVehiculo);

    const data = await apiFetch(`/dashboard?${qs.toString()}`);
    applyDashboardData(data);
    return data;
  }

  async function resetDashboardFilters() {
    const s1 = document.getElementById('filtroAnioInicio');
    const s2 = document.getElementById('filtroAnioFin');
    const s3 = document.getElementById('filtroTipoVehiculo');
    if (s1) s1.value = '2014';
    if (s2) s2.value = '2026';
    if (s3) s3.value = 'TODOS';
    return await applyDashboardFilters();
  }

  async function initAutogestApi() {
    if (window.location.protocol === 'file:') {
      updateStatusBadge('offline', '🟡 Modo Estático Local (file://)');
      return;
    }

    try {
      const health = await apiFetch('/health');
      const isNeon = health.db === 'neondb';
      updateStatusBadge(
        isNeon ? 'neondb' : 'local',
        isNeon
          ? `🟢 NeonDB en vivo (${health.total_registros} reg.)`
          : `🟢 API Local activa (${health.total_registros} reg.)`
      );

      if (document.getElementById('chartAccAnio')) {
        const dash = await apiFetch('/dashboard');
        applyDashboardData(dash);
      }

      // Validar carga del endpoint de métodos numéricos e historial de predicciones
      await Promise.all([apiFetch('/metodos-numericos'), loadPredictions()]);
    } catch (err) {
      console.warn('[AutoGest API] Fallback a datos embebidos:', err.message);
      updateStatusBadge('offline', '🟡 Respaldo Estático (API offline)');
    }
  }

  window.AutoGestAPI = {
    apiFetch,
    savePrediction,
    loadPredictions,
    applyDashboardFilters,
    resetDashboardFilters,
    initAutogestApi,
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAutogestApi);
  } else {
    initAutogestApi();
  }
})();
