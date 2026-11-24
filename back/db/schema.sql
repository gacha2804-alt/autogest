-- ============================================================================
-- AutoGest · Esquema Relacional PostgreSQL para NeonDB
-- Diseñado bajo mejores prácticas Postgres (< 5 MB, apto para Neon Free Tier)
-- ============================================================================

-- 1. Dataset integrado oficial (507 filas · 2014–2026)
CREATE TABLE IF NOT EXISTS registros_integrados (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  anio SMALLINT NOT NULL CHECK (anio BETWEEN 2000 AND 2100),
  mes SMALLINT NOT NULL CHECK (mes BETWEEN 1 AND 12),
  tipo_vehiculo TEXT NOT NULL,
  volumen_trafico DOUBLE PRECISION NOT NULL DEFAULT 0,
  vehiculos_evasores DOUBLE PRECISION NOT NULL DEFAULT 0,
  vehiculos_exentos DOUBLE PRECISION NOT NULL DEFAULT 0,
  tarifa_promedio DOUBLE PRECISION NOT NULL DEFAULT 0,
  recaudo_peajes DOUBLE PRECISION NOT NULL DEFAULT 0,
  servicios_taller DOUBLE PRECISION NOT NULL DEFAULT 0,
  costo_total_taller DOUBLE PRECISION NOT NULL DEFAULT 0,
  costo_promedio_taller DOUBLE PRECISION NOT NULL DEFAULT 0,
  horas_servicio_promedio DOUBLE PRECISION NOT NULL DEFAULT 0,
  millaje_promedio DOUBLE PRECISION NOT NULL DEFAULT 0,
  distancia_grua_total DOUBLE PRECISION NOT NULL DEFAULT 0,
  accidentes_totales INTEGER NOT NULL DEFAULT 0,
  accidentes_registrados DOUBLE PRECISION NOT NULL DEFAULT 0,
  tasa_evasion_pct DOUBLE PRECISION NOT NULL DEFAULT 0,
  tasa_exencion_pct DOUBLE PRECISION NOT NULL DEFAULT 0,
  CONSTRAINT uq_registros_anio_mes_tipo UNIQUE (anio, mes, tipo_vehiculo)
);

CREATE INDEX IF NOT EXISTS idx_registros_anio_mes
  ON registros_integrados (anio, mes);

CREATE INDEX IF NOT EXISTS idx_registros_tipo_anio
  ON registros_integrados (tipo_vehiculo, anio);

-- 2. Componentes principales PCA (507 filas · 98.31% varianza acumulada)
CREATE TABLE IF NOT EXISTS componentes_pca (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  anio SMALLINT NOT NULL CHECK (anio BETWEEN 2000 AND 2100),
  mes SMALLINT NOT NULL CHECK (mes BETWEEN 1 AND 12),
  tipo_vehiculo TEXT NOT NULL,
  pc1 DOUBLE PRECISION NOT NULL,
  pc2 DOUBLE PRECISION NOT NULL,
  pc3 DOUBLE PRECISION NOT NULL,
  pc4 DOUBLE PRECISION NOT NULL,
  pc5 DOUBLE PRECISION NOT NULL,
  accidentes_registrados DOUBLE PRECISION NOT NULL,
  CONSTRAINT uq_pca_anio_mes_tipo UNIQUE (anio, mes, tipo_vehiculo)
);

CREATE INDEX IF NOT EXISTS idx_pca_anio_tipo
  ON componentes_pca (anio, tipo_vehiculo);

-- 3. Métricas consolidadas de Minería de Datos (Clasificación, KNN, Clustering, Gini)
CREATE TABLE IF NOT EXISTS metricas_modelos_ml (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  categoria TEXT NOT NULL,
  clave TEXT NOT NULL,
  payload JSONB NOT NULL,
  orden SMALLINT NOT NULL DEFAULT 0,
  CONSTRAINT uq_ml_categoria_clave UNIQUE (categoria, clave)
);

CREATE INDEX IF NOT EXISTS idx_ml_categoria_orden
  ON metricas_modelos_ml (categoria, orden);

-- 4. Series oficiales de Métodos Numéricos (25 semestres, 13 años, 5 nodos Lagrange)
CREATE TABLE IF NOT EXISTS series_metodos_numericos (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  serie TEXT NOT NULL CHECK (serie IN ('semestral', 'anual', 'lagrange_nodo')),
  etiqueta TEXT NOT NULL,
  x_valor DOUBLE PRECISION NOT NULL,
  y_valor DOUBLE PRECISION NOT NULL,
  es_parcial BOOLEAN NOT NULL DEFAULT FALSE,
  nota TEXT,
  CONSTRAINT uq_mn_serie_etiqueta UNIQUE (serie, etiqueta)
);

CREATE INDEX IF NOT EXISTS idx_mn_serie_x
  ON series_metodos_numericos (serie, x_valor);

-- 5. Historial interactivo de predicciones (escritura real desde calculadora web)
CREATE TABLE IF NOT EXISTS historial_predicciones (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  modelo TEXT NOT NULL CHECK (modelo IN ('regresion_anual', 'regresion_semestral', 'lagrange')),
  anio_entrada DOUBLE PRECISION NOT NULL CHECK (anio_entrada BETWEEN 1900 AND 2150),
  valor_predicho DOUBLE PRECISION NOT NULL,
  tipo_evaluacion TEXT NOT NULL CHECK (tipo_evaluacion IN ('interpolacion', 'extrapolacion')),
  creado_en TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_predicciones_creado
  ON historial_predicciones (creado_en DESC);
