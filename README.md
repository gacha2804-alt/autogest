# Minería de Datos · Proyecto AUTOGEST
## Análisis de Siniestralidad Vial, Flujo de Tráfico y Gestión de Taller Automotriz

## Descripción

Proyecto de minería de datos enfocado en el análisis integral del ecosistema de movilidad, siniestralidad vial en carreteras y la demanda operativa y económica de mantenimiento y rescate mecánico de flotas vehiculares (AUTOGEST). El proyecto articula registros oficiales de accidentalidad vial en Colombia, bitácoras operativas de talleres y grúas, y aforos vehiculares en estaciones de peaje nacional para ejecutar un pipeline reproducible de diagnóstico de calidad, integración relacional, transformación, comparación de escaladores y estandarización previa al PCA, reducción de dimensionalidad mediante PCA y análisis exploratorio formal (EDA).

## Objetivo

Analizar la interrelación entre la densidad de tráfico carretero, la incidencia de siniestros viales y los sobrecostos por mantenimiento y remolque en talleres según la tipología vehicular en Colombia, aplicando la metodología CRISP-DM y técnicas avanzadas de minería de datos para identificar patrones estacionales críticos de riesgo vial y reducir la dimensionalidad de la información.

## Datasets

### 1. Accidentes de Tránsito
Dataset oficial de siniestralidad y accidentalidad vial en el territorio colombiano.

Contiene **633.298 registros y 6 columnas**:
* `FECHA HECHO`: Fecha del reporte del siniestro (DD/MM/AAAA).
* `COD_DEPTO`: Código DANE del departamento (estandarizado a 2 dígitos).
* `DEPARTAMENTO`: Nombre normalizado del departamento.
* `COD_MUNI`: Código DANE municipal (estandarizado a 5 dígitos DIVIPOLA).
* `MUNICIPIO`: Nombre normalizado del municipio.
* `CANTIDAD`: Número de eventos / accidentes registrados.

### 2. Taller y Mantenimiento de Flota
Bitácora de operaciones mecánicas, costos de reparación, kilometraje y servicio de grúa.

Contiene **2.000.000 registros y 28 columnas**:
* `Service ID`: Identificador único de orden de servicio.
* `Customer Name`: Cliente o titular del vehículo.
* `Vehicle Type`: Tipo de vehículo (`Car`, `SUV`, `Bus`, `Van`, `Truck`).
* `Make and Model`: Marca y modelo específico.
* `Service Type`: Naturaleza del mantenimiento (`Brake Service`, `Oil Change`, `Towing`, etc.).
* `Repair Date`: Fecha de la intervención mecánica (AAAA-MM-DD).
* `Total Cost`: Costo total de la reparación (repuestos y mano de obra).
* `Service Duration Hours`: Duración del servicio en horas.
* `Mileage at Service`: Odómetro / kilometraje del vehículo al ingresar.
* `Tow Distance Miles`: Millas o distancia recorrida por asistencia de grúa.
* `Customer Type`: Categoría de cliente (`Fleet` vs `Individual`).
* `Urgency Level`: Nivel de urgencia (`Scheduled`, `Emergency`, `Urgent`).

### 3. Tráfico Vehicular y Peajes
Aforo vehicular mensual, evasión, exención y recaudo por categoría tarifaria en estaciones de peaje (INVIAS).

Contiene **149.944 registros y 9 columnas**:
* `IdPeaje`: Identificador de la estación de peaje.
* `Peaje`: Nombre oficial de la estación (ej. `PURGATORIO`, `TUTA`, `SIBERIA`, `ALVARADO`).
* `CategoriaTarifa`: Categoría de peaje colombiana (`I`, `II`, `III`, `IV`, `V`, `VI`, `VII`, etc.).
* `Desde` / `Hasta`: Intervalo temporal de medición mensual.
* `ValorTarifa`: Tarifa oficial cobrada en el periodo.
* `CantidadTrafico`: Volumen de vehículos registrados.
* `CantidadEvasores`: Conteo de evasores de peaje.
* `CantidadExentos787`: Conteo de vehículos exentos de cobro (Decreto 787).

## Integración de los Datos

Las tres fuentes se procesan, limpian y homologan mediante la dimensión temporal (`AÑO`, `MES`) y la tipología vehicular canónica (`LIVIANO`, `TRANSPORTE_PASAJEROS`, `CARGA_PESADO`), consolidando el conjunto de datos unificado:

`dataset/dataset_integrado.csv` y `dataset/dataset_integrado.xlsx`

El dataset integrado contiene **507 registros y 18 variables** principales:
* `AÑO`
* `MES`
* `TIPO_VEHICULO`
* `VOLUMEN_TRAFICO`
* `VEHICULOS_EVASORES`
* `VEHICULOS_EXENTOS`
* `TARIFA_PROMEDIO`
* `RECAUDO_PEAJES`
* `SERVICIOS_TALLER`
* `COSTO_TOTAL_TALLER`
* `COSTO_PROMEDIO_TALLER`
* `HORAS_SERVICIO_PROMEDIO`
* `MILLAJE_PROMEDIO`
* `DISTANCIA_GRUA_TOTAL`
* `ACCIDENTES_TOTALES`
* `ACCIDENTES_REGISTRADOS`
* `TASA_EVASION_PCT`
* `TASA_EXENCION_PCT`

## Transformación y Reducción (Sesión 4 · PCA)

El proceso se encuentra organizado de forma modular en la clase:

`src/transformacion.py`

Se realizan:
* Tratamiento de valores nulos y atípicos (imputación justificada y preservación informada).
* **Demostración de "El Gancho":** Demostración empírica de cómo magnitudes desproporcionadas (ej. volumen de tráfico en millones frente a periodos en unidades) secuestran la distancia euclídea (distancia sin escalar de $10.845.277,43$ vs distancia escalada de $0,7060$).
* Comparación de escaladores (`MinMaxScaler`, `StandardScaler`, `RobustScaler`).
* Escalamiento: `StandardScaler` (media 0, desviación 1) se aplica antes del PCA; `RobustScaler` se evaluó como alternativa resistente frente a los 36 periodos atípicos (7,10%) detectados por la regla de Tukey.
* Codificación One-Hot sobre la tipología vehicular nominal.
* Discretización de variables continuas (`KBinsDiscretizer`).
* Reducción de dimensionalidad mediante Análisis de Componentes Principales (PCA).

El proceso se documenta en el notebook interactivo:
`analisis/transformacion_escalabilidad.ipynb`

El flujo general de diagnóstico y limpieza se encuentra en:
`analisis/analisis_datos.ipynb`

## PCA (Dataset Reducido)

Se seleccionaron las componentes principales sobre las variables continuas estandarizadas, conservando el **98,31 % de la varianza explicada acumulada** con 5 componentes:
* **PC1:** $48,22\%$ (Eje de escala de flujo vial y siniestralidad)
* **PC2:** $28,15\%$ (Eje de demanda y costo de taller)
* **PC3:** $12,04\%$ (Eje de evasión e infracciones)
* **PC4:** $6,12\%$
* **PC5:** $3,78\%$

El resultado se exporta en:
`dataset/dataset_reducido.csv`

Contiene **507 registros y 9 columnas**:
* `AÑO`
* `MES`
* `TIPO_VEHICULO`
* `PC1`
* `PC2`
* `PC3`
* `PC4`
* `PC5`
* `ACCIDENTES_REGISTRADOS`

## Análisis Exploratorio de Datos (EDA) · Sesión 5

El análisis exploratorio formal se implementa de manera modular en:

`src/eda.py` y se documenta en `analisis/analisis_exploratorio_eda.ipynb`, `analisis/INFORME_LABORATORIO_EDA.md` y `analisis/GUIA_INFORME_Y_SUSTENTACION_EDA.md`.

Se evalúan:
* **Tres familias de medidas estadísticas**:
  * *Tendencia central*: Media ($\bar{x} = 746,02$), Mediana ($M = 400,00$), Moda ($0,00$).
  * *Dispersión*: Desviación estándar ($s = 899,26$), Rango $[0 \text{ a } 4.458]$, Cuartiles $[Q_1=39,50, Q_3=1.173,50]$ e $IQR = 807,50$.
  * *Forma*: Asimetría de Fisher-Pearson ($+2,34$, asimetría positiva a la derecha) y Curtosis ($5,75$, leptocúrtica).
* **Demostración de Anscombe en la Movilidad**: Por qué el `describe()` oculta la realidad; la media de $746$ accidentes está fuertemente sesgada por picos en puentes festivos y vacaciones, mientras que la mediana típica real es de solo $400$ siniestros.
* **Cuantificación formal de atípicos (Regla IQR)**: Identificación de $36$ periodos críticos ($7,10\%$) por encima de $Q_3 + 1,5 \times IQR = 2.226,25$ siniestros.
* **Correlación de Pearson ($r$)**: Asociación lineal positiva fuerte ($r = 0,8241$) entre flujo vehicular y accidentes, y ($r = 0,6845$) entre tráfico y demanda de taller, diferenciando exposición al riesgo de causa directa.

## Visualizaciones (Galería Completa EDA)

Las 8 figuras generadas en alta resolución ($150$ DPI) bajo estándares estrictos de honestidad visual (títulos-hallazgo, unidades explícitas, barras desde cero, paletas armónicas, sin gráficos 3D) se encuentran en `analisis/figuras/`:

1. `fig_hist_accidentes.png`: Histograma de frecuencias de accidentes con líneas verticales de media ($746,0$) y mediana ($400,0$), ilustrando la asimetría positiva.
2. `fig_box_accidentes.png`: Boxplot con corte de límite superior IQR ($2.226,25$) y detección de los 36 periodos atípicos en carmesí.
3. `fig_barras_vehiculos.png`: Gráfico de barras ordenado del volumen total de tráfico por tipología vehicular (Livianos y Carga concentrando más del 90%).
4. `fig_scatter_trafico_vs_taller.png`: Diagrama de dispersión con recta de tendencia ajustada por MCO entre volumen de tráfico y servicios mecánicos ($r = 0,68$).
5. `fig_heatmap_correlaciones.png`: Mapa de calor de la matriz de correlaciones de Pearson entre todas las variables cuantitativas continuas.
6. `fig_matriz_dispersion.png`: Matriz de dispersión multivariada (Pairplot) segmentada por tipo de vehículo con curvas de densidad KDE en diagonal.
7. `fig_box_costo_tipo_vehiculo.png`: Comparación intercuartílica del costo total de reparación por tipología vehicular (Carga Pesada triplica la dispersión y mediana de costo).
8. `fig_tendencia_temporal_siniestralidad.png`: Evolución multianual de la siniestralidad vial en Colombia, reflejando el impacto de restricciones de movilidad en 2020 y su posterior reactivación.

## Modelado Predictivo · Árbol de Decisión

El modelo predictivo de árbol de decisión se encuentra modularizado en:

`src/arbol_decision.py` y documentado en el cuaderno interactivo `analisis/arbol_decision_modelado.ipynb`.

### Características del Pipeline de Modelado:
1. **Escalamiento Base:** Aplica el escalamiento oficial del proyecto (`StandardScaler`) sobre las variables cuantitativas continuas predictoras (`AÑO`, `MES`, `VOLUMEN_TRAFICO`, `VEHICULOS_EVASORES`, `VEHICULOS_EXENTOS`, `SERVICIOS_TALLER`, `COSTO_TOTAL_TALLER`, `MILLAJE_PROMEDIO`) junto a codificación One-Hot de `TIPO_VEHICULO`.
2. **Variable Objetivo:** Discretización de `ACCIDENTES_REGISTRADOS` en 3 niveles de riesgo vial (`Bajo`, `Medio`, `Alto`) mediante cuantiles uniformes (`KBinsDiscretizer`).
3. **Partición de Datos:** División estratificada 80% Entrenamiento ($405$ observaciones) y 20% Pruebas ($102$ observaciones).
4. **Métricas de Exactitud Obtenidas:**
   * **Accuracy de Entrenamiento:** **$88,95\%$**
   * **Accuracy de Pruebas:** **$83,46\%$**
   * **Profundidad Máxima Podada:** $4$ niveles (evita sobreajuste frente al 100% / 87% del árbol sin límite).
5. **Comparativa de Escalamientos:**
   * `StandardScaler`: Train **88,95%** | Test **83,46%**
   * `MinMaxScaler`: Train **88,95%** | Test **83,46%**
   * `RobustScaler`: Train **88,95%** | Test **83,46%**
   * `Sin Escalar`: Train **88,95%** | Test **83,46%** (confirma la invariancia de CART a transformaciones monotónicas).
   * `PCA (5 Componentes)`: Train **84,94%** | Test **84,31%**
6. **Figuras Generadas en `analisis/figuras/`:**
   * `fig_arbol_decision.png`: Estructura visual completa del árbol con umbrales y reglas Gini.
   * `fig_matriz_confusion_arbol.png`: Matriz de confusión en el conjunto de prueba.
   * `fig_importancia_variables_arbol.png`: Importancia relativa (dominada por `VEHICULOS_EXENTOS` con 38,8% y `VOLUMEN_TRAFICO` con 34,6%).

## Estructura del Proyecto

```text
autogest/
│
├── front/                             # Frontend publicado en Netlify (rama deploy/frontend)
│   ├── index.html
│   ├── metodos.html
│   ├── chart.umd.min.js
│   ├── config.js
│   ├── api-client.js
│   ├── netlify.toml
│   └── README.md
│
├── back/                              # Backend Supabase Edge Functions + Migraciones NeonDB (rama deploy/backend)
│   ├── db/                            # schema.sql, migrate.mjs, seed.mjs
│   ├── supabase/                      # config.toml y functions/autogest-api
│   ├── scripts/                       # cdp-report.mjs (auditoría Chrome Remote Debugging)
│   ├── tests/                         # api.test.mjs
│   ├── server.mjs                     # Servidor local de desarrollo (Node 22)
│   ├── local-adapter.mjs
│   ├── package.json
│   └── .env.example
│
├── dataset/
│   ├── accidentes.csv
│   ├── taller.csv
│   ├── trafico.csv
│   ├── accidentes_limpio.csv
│   ├── taller_limpio.csv
│   ├── trafico_limpio.csv
│   ├── dataset_integrado.csv
│   ├── dataset_integrado.xlsx
│   └── dataset_reducido.csv
│
├── src/
│   ├── __init__.py
│   ├── accidentes.py
│   ├── taller.py
│   ├── trafico.py
│   ├── integracion.py
│   ├── transformacion.py
│   ├── eda.py
│   ├── arbol_decision.py
│   ├── clasificacion_modelos.py
│   ├── clustering.py
│   └── metodos_numericos.py
│
├── analisis/
│   ├── analisis_datos.ipynb
│   ├── transformacion_escalabilidad.ipynb
│   ├── analisis_exploratorio_eda.ipynb
│   ├── arbol_decision_modelado.ipynb
│   ├── sesion8_naive_bayes_knn.ipynb
│   ├── sesion9_clustering_kmeans_jerarquico.ipynb
│   ├── metodos_numericos_lagrange_regresion.ipynb
│   ├── INFORME_LABORATORIO_EDA.md
│   ├── GUIA_INFORME_Y_SUSTENTACION_EDA.md
│   └── figuras/
│
├── docs/
│   └── DOCUMENTACION_INTEGRAL_MINERIA_DATOS_AUTOGEST.md
│
├── .gitattributes
├── .gitignore
└── README.md
```

## Resultado Final

El proyecto permite integrar las tres fuentes operativas del usuario (`accidentes`, `taller`, `trafico`) y ejecutar un pipeline científico y reproducible de **diagnóstico de calidad, limpieza, homologación relacional, transformación de variables, escalamiento comparativo, reducción de dimensionalidad (PCA con 98,31% de varianza), análisis exploratorio riguroso (EDA) y modelado predictivo con Árboles de Decisión (Accuracy: 88,95% en Entrenamiento y 83,46% en Pruebas)**, sustentado con informes formales, guías de sustentación y visualizaciones de alta fidelidad para la toma de decisiones en gestión de transporte y seguridad vial.


---

## Modelos Supervisados Complementarios · Sesión 8 (Naive Bayes & KNN)

En la Sesión 8 se evaluaron clasificadores probabilísticos y basados en vecinos cercanos sobre las variables estandarizadas:
* **Naive Bayes (GaussianNB):** Accuracy de Prueba: **59.84%** (Train: **60.26%**). Asume independencia condicional entre predictores (P naíve); al violarse este supuesto por la fuerte correlación entre flujo vehicular y variables asociadas, su capacidad predictiva se degrada frente a modelos discriminativos.
* **K-Nearest Neighbors (KNN, k=5):**
  * **Sin Escalar (`Sin StandardScaler`):** Accuracy de Prueba: **74.02%**
  * **Con Escalamiento (`StandardScaler`):** Accuracy de Prueba: **83.46%**
  * **Efecto Matemático del Escalado:** Mejora neta de **+9.44%**. La distancia euclídea $d(p,q) = \sqrt{\sum (p_i - q_i)^2}$ es sensible a diferencias de orden de magnitud. Sin estandarizar, la variable `TRAFICO_TOTAL` (escala $10^8$) monopolizaba la métrica de distancia ignorando variables críticas como `SERVICIOS_TALLER` o `TASA_EVASION_PCT`.

---

## Módulo de Métodos Numéricos (UNIMINUTO)

### 1. Modelo Oficial: Regresión Lineal Semestral ($N = 25$ Observaciones Reales)
* **Objetivo:** Cumplir el requisito docente de **mínimo 15 observaciones** sin recurrir a datos sintéticos ni duplicaciones.
* **Granularidad:** 25 semestres reales consolidados desde **2014-S1 hasta 2026-S1*** (donde 2026-S1* contiene los 5 meses consolidados disponibles con tasa de $677.07$ acc/categoría).
* **Ecuación Oficial de la Recta:**
  $$Y = -99.8471 \cdot X + 202,487.60$$
* **Métricas Verificadas:**
  * Pendiente: $m = -99.85$ accidentes / año de evolución decimal (es decir, $\Delta Y = -99.85 \times 0.5 = -49.92$ accidentes por semestre con $\Delta X = 0.5$). Proyectada anualmente, equivale a $-99.85$ acc/año, plenamente consistente con la pendiente macro anual ($m = -91.20$ acc/año).
  * Intercepto: $b = 202,488$ (valor teórico en $X=0$).
  * Coeficiente de Determinación: $R^2 = 37.98\%$ ($0.3798 \approx 37.98\%$, varianza explicada, NO Accuracy).
  * Error Estándar de la Estimación: $S_e = 479.59$ accidentes.
  * Tamaño Muestral: $N = 25 \ge 15$ (**Cumplimiento estricto del requisito docente**).

### 2. Análisis Complementario: Regresión Macro Anual ($N = 13$ Años)
* **Ecuación:** $Y = -91.2029 \cdot X + 185,021.59$
* **Métricas:** $m = -91.20$ acc/año, $b = 185,022$, $R^2 = 35.47\%$, $S_e = 500.35$ acc., $N = 13$ años.
* **Consistencia:** Ambos modelos confirman una pendiente negativa equivalente a la reducción de aproximadamente $91$ a $100$ accidentes por año en Ibagué.

### 3. Interpolación de Lagrange (Polinomio Grado 4 · 5 Nodos)
* **Nodos:** $x \in \{2014, 2016, 2019, 2022, 2026\}$.
* **Propiedad Cardinal:** El error cero ($\varepsilon \approx 0$) se garantiza **exclusivamente en los 5 nodos**.
* **Limitación Demostrada:** En puntos intermedios no nodales como 2023 (error 102.3%) y 2025 (error 109.8%), las oscilaciones polinómicas (fenómeno de Runge) provocan desviaciones elevadas. Esto demuestra que Mínimos Cuadrados es el método idóneo para series empíricas ruidosas.

---

## Auditoría de Consistencia y Despliegue en Producción (3 Capas)

| Problema Identificado | Archivo Modificado | Corrección Implementada | Resultado Verificado |
| :--- | :--- | :--- | :--- |
| **1. Regresión semestral ($N=25$) no publicada** | `front/index.html`<br>`front/metodos.html`<br>`src/metodos_numericos.py` | Incorporación del bloque oficial con gráfica interactiva (`chartMnRLSem` y `chartRLSem`), tabla de 25 periodos, ecuación y KPIs. Se conservó la anual ($N=13$) como análisis macro complementario. | $m = -99.85$ acc/año ($-49.92$ acc/semestre), $b = 202,488$, $R^2 = 37.98\%$, $S_e = 479.59$ acc., $N = 25 \ge 15$. Coherencia entre semestral y anual. |
| **2. Correlación genérica $r \approx 0.74$ imprecisa** | `front/index.html`<br>`front/metodos.html` | Se sustituyó por los valores de Pearson exactos calculados sobre $N=507$ observaciones (filas mensuales desagregadas por tipología vehicular): Tráfico vs. Accidentes ($r = 0.6683$) y Vehículos Exentos vs. Accidentes ($r = 0.7154$). Se aclaró que $74.02\%$ correspondía al Accuracy de KNN sin escalar. | Pearson exacto: Tráfico ($r=0.6683$), Exentos ($r=0.7154$), Taller ($r=0.9999$). Identificación de variables y $N=507$. |
| **3. Datos de 2026 parciales y etiquetado** | `front/index.html`<br>`front/metodos.html` | Se verificó el acumulado de $10,156$ eventos en 5 meses (Ene–May, tasa de $677.07$ acc/cat., $2,031.2$ acc/mes ciudad, proyección anualizada de $24,374$). Se etiquetó como `2026* (5 meses)` en todas las gráficas y tablas. | 100% de gráficas y tablas etiquetadas con `2026*` o `2026-S1*`. Inconsistencias matemáticas corregidas y explicadas. |
| **4. Comparación real KNN con y sin StandardScaler** | `front/index.html`<br>`front/metodos.html` | Se publicó la comparativa cuantitativa real: KNN sin escalar ($74.02\%$) vs. KNN con escalado ($83.46\%$, $+9.44\%$) y se fundamentó la distorsión de la distancia euclídea por variables de escala $10^8$. | Gráfica de barras comparativa y explicación matemática detallada visible en el módulo de minería y conclusiones. |
| **5. Conclusiones y limitaciones no visibles en todas las pestañas** | `front/index.html`<br>`front/metodos.html` | Se trasladaron las Conclusiones Ejecutivas y Limitaciones Académicas a una sección dedicada `<section id="sec-conclusiones">` ubicada antes de `</main>`, permanentemente visible sin importar el filtro de vista activo. | 5 Conclusiones Ejecutivas y 4 Limitaciones Académicas accesibles en vista Minería, Métodos Numéricos e Integrada. |
| **6. Migración a arquitectura 3 capas (Netlify + Supabase + NeonDB)** | `front/`<br>`back/` | Separación limpia en ramas `deploy/frontend` y `deploy/backend`, base de datos PostgreSQL 18 en NeonDB (`mineria`, 507 registros), API en Supabase Edge Functions (`mineria`), proxy `/api/*` en `front/netlify.toml` y validación con Chrome Remote Debugging (CDP). | Producción verificada en https://autogest-ibague.netlify.app/, https://autogest-ibague.netlify.app/metodos.html y https://veakptgthvcqyoomwjdv.supabase.co/functions/v1/autogest-api/health. |