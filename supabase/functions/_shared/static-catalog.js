/**
 * Catálogo consolidado de métricas ML y series oficiales de Métodos Numéricos
 * de AutoGest (UNIMINUTO Ibagué · 2014–2026*).
 * Compartido entre el seed de NeonDB, el servidor local y Supabase Edge Functions.
 */

export const STATIC_ML_METRICS = [
  // Torneo de clasificación · Sesión 8
  {
    categoria: 'torneo_clasificacion',
    clave: 'arbol_decision',
    orden: 1,
    payload: {
      modelo: 'Árbol Decisión (prof=4)',
      accuracy_train: 88.95,
      accuracy_test: 83.46,
      tiempo_fit_s: 0.062,
      requiere_escala: false,
      recomendacion: 'Principal',
    },
  },
  {
    categoria: 'torneo_clasificacion',
    clave: 'naive_bayes',
    orden: 2,
    payload: {
      modelo: 'Naive Bayes (GaussianNB)',
      accuracy_train: 60.26,
      accuracy_test: 59.84,
      tiempo_fit_s: 0.003,
      requiere_escala: false,
      recomendacion: 'Línea base',
    },
  },
  {
    categoria: 'torneo_clasificacion',
    clave: 'knn_escalado',
    orden: 3,
    payload: {
      modelo: 'KNN k=5 (escalado StandardScaler)',
      accuracy_train: 91.58,
      accuracy_test: 83.46,
      tiempo_fit_s: 0.012,
      requiere_escala: true,
      recomendacion: 'Alta precisión',
    },
  },
  {
    categoria: 'torneo_clasificacion',
    clave: 'knn_sin_escalar',
    orden: 4,
    payload: {
      modelo: 'KNN k=5 (sin escalar)',
      accuracy_train: 84.74,
      accuracy_test: 74.02,
      tiempo_fit_s: 0.01,
      requiere_escala: false,
      recomendacion: '-9.44% sin escala',
    },
  },

  // Efecto de k en KNN
  ...[
    [1, 100.0, 73.5],
    [3, 87.2, 81.0],
    [5, 85.3, 82.0],
    [11, 83.8, 82.8],
    [21, 83.1, 83.0],
    [31, 83.1, 82.8],
    [51, 83.0, 83.0],
    [71, 83.0, 83.0],
  ].map(([k, train, test], idx) => ({
    categoria: 'knn_k',
    clave: `k_${k}`,
    orden: idx + 1,
    payload: { k, accuracy_train: train, accuracy_test: test },
  })),

  // Método del codo y silueta (K-Means · Sesión 9)
  ...[
    [2, 12583, 0.128],
    [3, 11332, 0.129],
    [4, 10404, 0.122],
    [5, 9647, 0.126],
    [6, 9047, 0.127],
    [7, 8549, 0.127],
    [8, 8176, 0.124],
  ].map(([k, inercia, silueta], idx) => ({
    categoria: 'codo_silueta',
    clave: `k_${k}`,
    orden: idx + 1,
    payload: { k, inercia, silueta },
  })),

  // Importancia de variables (Árbol de decisión · Criterio Gini)
  ...[
    ['VEHICULOS_EXENTOS', 0.42],
    ['VOLUMEN_TRAFICO', 0.24],
    ['MILLAJE_PROMEDIO', 0.16],
    ['COSTO_TOTAL_TALLER', 0.09],
    ['SERVICIOS_TALLER', 0.06],
    ['VEHICULOS_EVASORES', 0.03],
  ].map(([variable, importancia], idx) => ({
    categoria: 'feature_importance',
    clave: variable,
    orden: idx + 1,
    payload: { variable, importancia },
  })),

  // Perfiles de clústeres K-Means (k=3)
  {
    categoria: 'cluster_perfil',
    clave: 'cluster_0',
    orden: 1,
    payload: {
      nombre: 'Período de Tráfico Habitual',
      volumen_trafico: '~3.5M veh/mes',
      accidentes_prom: '~430',
      evasores: 'Bajo',
      accion: 'Mantenimiento preventivo',
    },
  },
  {
    categoria: 'cluster_perfil',
    clave: 'cluster_1',
    orden: 2,
    payload: {
      nombre: 'Período de Alta Siniestralidad',
      volumen_trafico: '~7.2M veh/mes',
      accidentes_prom: '~2,100',
      evasores: 'Alto',
      accion: 'Alerta inmediata · refuerzo señalización',
    },
  },
  {
    categoria: 'cluster_perfil',
    clave: 'cluster_2',
    orden: 3,
    payload: {
      nombre: 'Período de Baja Actividad',
      volumen_trafico: '~1.2M veh/mes',
      accidentes_prom: '~260',
      evasores: 'Muy bajo',
      accion: 'Análisis causas de baja demanda',
    },
  },
];

export const STATIC_NUMERICAL_SERIES = [
  // Serie oficial semestral (N = 25 >= 15)
  ...[
    ['2014-S1', 2014.0, 1113.72, false, null],
    ['2014-S2', 2014.5, 1124.33, false, null],
    ['2015-S1', 2015.0, 1143.22, false, null],
    ['2015-S2', 2015.5, 1214.39, false, null],
    ['2016-S1', 2016.0, 2104.39, false, null],
    ['2016-S2', 2016.5, 2109.44, false, 'Máximo semestral'],
    ['2017-S1', 2017.0, 1854.33, false, null],
    ['2017-S2', 2017.5, 1813.0, false, null],
    ['2018-S1', 2018.0, 530.0, false, null],
    ['2018-S2', 2018.5, 458.11, false, null],
    ['2019-S1', 2019.0, 448.78, false, null],
    ['2019-S2', 2019.5, 412.06, false, null],
    ['2020-S1', 2020.0, 251.17, false, 'Mínimo semestral (COVID-19)'],
    ['2020-S2', 2020.5, 268.79, false, null],
    ['2021-S1', 2021.0, 318.58, false, null],
    ['2021-S2', 2021.5, 298.04, false, null],
    ['2022-S1', 2022.0, 377.29, false, null],
    ['2022-S2', 2022.5, 396.38, false, null],
    ['2023-S1', 2023.0, 418.17, false, null],
    ['2023-S2', 2023.5, 406.58, false, null],
    ['2024-S1', 2024.0, 443.79, false, null],
    ['2024-S2', 2024.5, 468.08, false, null],
    ['2025-S1', 2025.0, 610.11, false, null],
    ['2025-S2', 2025.5, 650.39, false, null],
    ['2026-S1*', 2026.0, 677.07, true, 'Parcial (Ene–May, 5 meses)'],
  ].map(([etiqueta, x_valor, y_valor, es_parcial, nota]) => ({
    serie: 'semestral',
    etiqueta,
    x_valor,
    y_valor,
    es_parcial,
    nota,
  })),

  // Serie macro anual (N = 13 años)
  ...[
    ['2014', 2014, 1119.03, false, 'Inicio del rango (mín X)'],
    ['2015', 2015, 1178.81, false, null],
    ['2016', 2016, 2106.92, false, 'Pico máximo histórico'],
    ['2017', 2017, 1833.67, false, null],
    ['2018', 2018, 494.06, false, null],
    ['2019', 2019, 430.42, false, null],
    ['2020', 2020, 259.98, false, 'Mínimo — pandemia COVID-19'],
    ['2021', 2021, 308.31, false, null],
    ['2022', 2022, 386.83, false, null],
    ['2023', 2023, 412.38, false, null],
    ['2024', 2024, 455.94, false, null],
    ['2025', 2025, 630.25, false, null],
    ['2026*', 2026, 677.07, true, 'Año parcial (Ene–May, 5 meses)'],
  ].map(([etiqueta, x_valor, y_valor, es_parcial, nota]) => ({
    serie: 'anual',
    etiqueta,
    x_valor,
    y_valor,
    es_parcial,
    nota,
  })),

  // 5 Nodos estratégicos de Lagrange (grado 4)
  ...[
    ['Nodo 0 (2014)', 2014, 1119.03, false, 'Inicio del rango (mín X)'],
    ['Nodo 1 (2016)', 2016, 2106.92, false, 'Pico máximo histórico'],
    ['Nodo 2 (2019)', 2019, 430.42, false, 'Punto intermedio descendente'],
    ['Nodo 3 (2022)', 2022, 386.83, false, 'Recuperación post-pandemia'],
    ['Nodo 4 (2026)', 2026, 677.07, true, 'Fin del rango (máx X)'],
  ].map(([etiqueta, x_valor, y_valor, es_parcial, nota]) => ({
    serie: 'lagrange_nodo',
    etiqueta,
    x_valor,
    y_valor,
    es_parcial,
    nota,
  })),
];
