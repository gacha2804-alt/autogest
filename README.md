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

## Estructura del Proyecto

```text
autogest/
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
│   └── eda.py
│
├── analisis/
│   ├── analisis_datos.ipynb
│   ├── transformacion_escalabilidad.ipynb
│   ├── analisis_exploratorio_eda.ipynb
│   ├── INFORME_LABORATORIO_EDA.md
│   ├── GUIA_INFORME_Y_SUSTENTACION_EDA.md
│   └── figuras/
│       ├── fig_hist_accidentes.png
│       ├── fig_box_accidentes.png
│       ├── fig_barras_vehiculos.png
│       ├── fig_scatter_trafico_vs_taller.png
│       ├── fig_heatmap_correlaciones.png
│       ├── fig_matriz_dispersion.png
│       ├── fig_box_costo_tipo_vehiculo.png
│       └── fig_tendencia_temporal_siniestralidad.png
│
├── .gitignore
└── README.md
```

## Resultado Final

El proyecto permite integrar las tres fuentes operativas del usuario (`accidentes`, `taller`, `trafico`) y ejecutar un pipeline científico y reproducible de **diagnóstico de calidad, limpieza, homologación relacional, transformación de variables, escalamiento comparativo, reducción de dimensionalidad (PCA con 98,31% de varianza) y análisis exploratorio riguroso (EDA)**, sustentado con informes formales, guías de sustentación y visualizaciones de alta fidelidad para la toma de decisiones en gestión de transporte y seguridad vial.
