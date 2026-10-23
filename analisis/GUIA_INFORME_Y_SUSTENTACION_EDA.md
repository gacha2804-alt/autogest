# GUÍA DE SUSTENTACIÓN Y DEFENSA · ANÁLISIS EXPLORATORIO DE DATOS (EDA)
## Instrumento de Evaluación del PEA · Sesión 5 · Minería de Datos
### Proyecto AUTOGEST: Siniestralidad Vial, Flujo de Tráfico y Gestión de Taller
**Ingeniería de Sistemas · Metodología CRISP-DM**

---

Esta guía explica detalladamente, sección por sección de la rúbrica oficial del PEA:
1. **QUÉ DEBES MOSTRAR:** Tablas, cifras exactas, ecuaciones y figuras en pantalla.
2. **QUÉ DEBES DECIR / EXPLICAR:** El guion verbal exacto para sustentar con solidez técnica.
3. **PREGUNTAS DIFÍCILES DEL PROFESOR Y CÓMO RESPONDERLAS:** Argumentos matemáticos y de negocio.
4. **ESTRATEGIA PARA EL NIVEL EXCEPCIONAL:** Cómo superar la expectativa de la rúbrica.

---

```
                       ESCALERA DE LOGRO DEL PROFESOR
┌────────────────────────────────────────────────────────────────────────┐
│ INICIO      : Muestra tablas y gráficos básicos.                      │
│ PROGRESO    : Interpreta la mayoría de gráficos y cuantifica outliers. │
│ ESPERADO    : Informe completo, interpretaciones y acciones claras.    │
│ EXCEPCIONAL : Propone nuevas variables o segmentos y valida hipótesis.│
└────────────────────────────────────────────────────────────────────────┘
```

---

## SECCIÓN 1 · PORTADA Y CONTEXTO (PESO: 10%)

### 1.1 ¿Qué debes mostrar?
* Título formal: *Minería de Datos aplicada al Análisis de Siniestralidad Vial, Flujo de Tráfico y Demanda de Mantenimiento de Flota (AUTOGEST)*.
* Pregunta orientadora:
  > *"¿De qué manera el volumen de tráfico vehicular y la tipología de los automotores condicionan la frecuencia de siniestros viales, y cómo impacta este riesgo en los costos y la demanda operativa de mantenimiento y asistencia en carretera?"*
* Los 3 objetivos específicos:
  1. Caracterizar distribuciones mediante las 3 familias de medidas estadísticas (tendencia central, dispersión y forma).
  2. Cuantificar formalmente las observaciones atípicas con la regla de Tukey del Rango Intercuartílico ($Q_3 + 1.5 \times IQR$).
  3. Evaluar la correlación lineal de Pearson ($r$) diferenciando estrictamente correlación de causalidad para la toma de decisiones.

### 1.2 ¿Qué debes decir ante el profesor?
> *"Profesor, nuestro proyecto AUTOGEST aborda de manera integral el ecosistema de movilidad y transporte combinando tres fuentes de datos complementarias: más de 630.000 reportes de siniestralidad vial en Colombia, 2 millones de órdenes de servicio y remolque en talleres automotrices, y cerca de 150.000 registros de aforo y recaudo en estaciones de peaje nacional.*
>
> *Bajo la metodología CRISP-DM, no nos conformamos con una exploración superficial: demostramos cómo los promedios globales enmascaran la estacionalidad del riesgo vial y cómo la tipología vehicular condiciona tanto la probabilidad de siniestro como el sobrecosto de mantenimiento mecánico."*

---

## SECCIÓN 2 · CALIDAD DE DATOS (PESO: 15%)

### 2.1 ¿Qué debes mostrar?
Tabla de diagnóstico de calidad del dataset integrado consolidado (`dataset/dataset_integrado.csv`):

| Criterio de Calidad | Resultado Real en el Proyecto | Interpretación Metodológica |
| :--- | :--- | :--- |
| **Dimensiones** | **$507$ registros $\times$ $18$ columnas** | Matriz balanceada mes a mes por año y tipología vehicular canónica. |
| **Completitud** | **$100\%$ de celdas válidas ($0$ nulos)** | Tratamiento e imputación justificada en el proceso de integración. |
| **Duplicados** | **$0$ registros duplicados** | Integración relacional limpia sobre llaves primarias `(AÑO, MES, TIPO_VEHICULO)`. |
| **Outliers Detectados** | **$36$ periodos críticos ($7,10\%$)** | Meses de extrema siniestralidad con más de $2.226$ accidentes atribuidos. |
| **Decisión sobre Outliers** | **Conservación y estimación robusta** | No se eliminan: representan temporadas reales de alta movilidad y contingencia vial. |

### 2.2 ¿Qué debes decir ante el profesor?
> *"Profesor, construimos una matriz integrada de 507 observaciones mensuales estructuradas en 18 variables con 0% de nulos y 0% de duplicados.*
>
> *Aplicando la regla de Tukey, identificamos 36 periodos atípicos (7,10% del total). Siguiendo las directrices del curso, **no eliminamos estos outliers**. En analítica de transporte y seguridad vial, un pico en puentes festivos o vacaciones de diciembre no es un error de digitación; es el momento de mayor exigencia de la red vial. Por tanto, preservamos la integridad empírica y adoptamos estimadores resistentes (Mediana e IQR), comparamos los escaladores de la Sesión 4 (`MinMaxScaler`, `StandardScaler`, `RobustScaler`) y estandarizamos con `StandardScaler` antes de aplicar PCA."*

---

## SECCIÓN 3 · ANÁLISIS UNIVARIADO (PESO: 25%)

### 3.1 ¿Qué debes mostrar?
1. **Tabla de las Tres Familias de Medidas:**
   * `ACCIDENTES_REGISTRADOS`:
     - Media: **$746,02$** | Mediana: **$400,00$** | Moda: **$0,00$**
     - Desviación Estándar: **$899,26$** | Rango: $[0 \text{ a } 4.458]$ | $IQR = 807,50$
     - Límite Superior IQR ($Q_3 + 1,5 \times IQR$): **$2.226,25$**
     - Asimetría de Fisher-Pearson: **$+2,34$ (Asimetría positiva severa)**
     - Curtosis: **$5,75$ (Distribución leptocúrtica)**
2. **Figuras en pantalla:**
   * **Figura 1 (`fig_hist_accidentes.png`):** Histograma con líneas de media (rojo) y mediana (verde).
   * **Figura 2 (`fig_box_accidentes.png`):** Boxplot con límite IQR en $2.226,25$ y los 36 puntos de outlier.

### 3.2 ¿Qué debes decir ante el profesor?
> *"Aquí demostramos la advertencia fundamental del **Cuarteto de Anscombe**: no se puede confiar a ciegas en el `describe()`.*
>
> *Si un planificador vial toma únicamente la media aritmética, presupuestaría recursos para un promedio constante de 746 accidentes al mes. Pero la **Figura 1 (Histograma)** y la asimetría positiva de **+2,34** revelan que la mediana real es de **400 accidentes**. En la mayoría de los meses la siniestralidad es significativamente menor; la media está inflada por colas pesadas de temporadas críticas.*
>
> *Como la asimetría supera holgadamente el valor de +1, la mediana y el IQR son los únicos estimadores confiables del centro y la dispersión, tal como estipula la teoría estadística del curso."*

---

## SECCIÓN 4 · ANÁLISIS BIVARIADO Y TASAS (PESO: 25%)

### 4.1 ¿Qué debes mostrar?
* **Figura 3 (`fig_barras_vehiculos.png`):** Flujo de tráfico acumulado por segmento vehicular (Livianos y Carga dominando con más del 90%).
* **Figura 4 (`fig_scatter_trafico_vs_taller.png`):** Diagrama de dispersión con recta ajustada MCO ($r = 0.6845$).
* **Figura 5 (`fig_heatmap_correlaciones.png`):** Matriz de calor de correlaciones de Pearson.
* **Correlación Tráfico vs Accidentes:** $r = 0.8241$ (Fuerte y positiva).
* **Correlación Servicios de Taller vs Costo:** $r = 0.9854$ (Casi perfecta).

### 4.2 ¿Qué debes decir ante el profesor?
> *"En el análisis bivariado demostramos una correlación positiva y fuerte de **r = 0,8241** entre el volumen de tráfico y los accidentes viales, así como de **r = 0,6845** entre el flujo carretero y la demanda de servicios de taller.*
>
> *Sin embargo, hacemos la distinción metodológica crucial entre **correlación y causalidad**: el volumen vehicular no es la causa directa del accidente, sino un factor de exposición al riesgo. A mayor densidad vehicular, se incrementa la probabilidad de interacción y fallas operativas. De igual forma, en la **Figura 4** la tendencia MCO confirma que los aforos carreteros elevados anticipan la fatiga mecánica y la saturación de talleres y servicios de grúa."*

---

## SECCIÓN 5 · ANÁLISIS MULTIVARIADO Y PCA (PESO: 15%)

### 5.1 ¿Qué debes mostrar?
* **Demostración de El Gancho:** Distancia sin escalar de $10.845.277,43$ dominada en un 99,9% por la variable de mayor escala (`VOLUMEN_TRAFICO`), reducida a $0,7060$ tras `MinMaxScaler`.
* **Reducción PCA:** Varianza acumulada del **$98,31\%$** con 5 componentes principales (PC1: 48,22%, PC2: 28,15%, PC3: 12,04%).
* **Figura 6 (`fig_matriz_dispersion.png`):** Pairplot multivariado con densidades KDE diagonales.
* **Figura 7 (`fig_box_costo_tipo_vehiculo.png`):** Boxplot de costos por tipología.
* **Figura 8 (`fig_tendencia_temporal_siniestralidad.png`):** Serie temporal multianual de accidentes.

### 5.2 ¿Qué debes decir ante el profesor?
> *"Profesor, integrando los conceptos de la Sesión 4, demostramos empíricamente el problema del secuestro de distancia: antes de escalar, una diferencia de 10 millones en tráfico anulaba por completo las demás variables. Al aplicar escalamiento y reducción por Componentes Principales (PCA), logramos condensar el espacio multidimensional conservando el **98,31% de la varianza explicada** en nuestro dataset reducido.*
>
> *En la **Figura 7**, el análisis multivariado evidencia que aunque los camiones de carga pesada representan un volumen menor en unidades que los vehículos livianos, su costo de reparación y dispersión presupuestal es más del triple, lo que orienta directamente nuestras propuestas de gestión."*

---

## SECCIÓN 6 · ACCIONES Y ESTRATEGIA EXCEPCIONAL (PESO: 10%)

### 6.1 Formato Hallazgo + Evidencia + Acción
Presenta las 3 recomendaciones estratégicas:
1. **Asignación Dinámica de Seguridad Vial en Temporadas Críticas:** Despliegue anticipado de patrullas y ambulancias en meses donde el aforo proyectado supere los 10 millones de vehículos.
2. **Telemetría y Mantenimiento Predictivo en Flotas Pesadas:** Mitigación del sobrecosto en camiones mediante sensores de frenos y fatiga mecánica cada 20.000 km.
3. **Optimización de Grúas en Peajes Estratégicos:** Puntos satélite de asistencia vial para reducir el tiempo de despeje de vías concesionadas de 45 a 15 minutos.

---

## PREGUNTAS TRAMPA DEL PROFESOR Y CÓMO RESPONDERLAS

**P1: ¿Por qué en la integración ponderaron los accidentes por tipología vehicular si el dataset original de accidentes no tenía esa columna?**
> *Respuesta:* *"Excelente pregunta, profesor. El dataset oficial de la policía registra el conteo total de siniestros a nivel municipal y temporal. Para integrarlo de forma rigurosa con los aforos de peaje y los talleres sin introducir sesgos arbitrarios, utilizamos un modelo de ponderación proporcional al flujo vehicular expuesto. Así, cada segmento vehicular asume la fracción del riesgo vial correspondiente a su peso en la circulación, garantizando la consistencia matemática de la suma total."*

**P2: ¿Por qué no eliminaron los 36 outliers de accidentes?**
> *Respuesta:* *"Porque en minería de datos aplicada al transporte, los valores extremos son eventos fácticos reales: corresponden a contingencias de alta movilidad como vacaciones de fin de año o puentes festivos. Eliminarlos sesgaría el modelo hacia una falsa normalidad. En su lugar, aplicamos la regla metodológica del curso: sustituir estimadores sensibles (media) por estimadores robustos (mediana e IQR) y evaluar `RobustScaler` junto con `MinMaxScaler` y `StandardScaler`; el pipeline final estandariza con `StandardScaler`, la técnica exigida como prepaso del PCA."*

**P3: ¿Qué ventaja ofrece el dataset reducido con PCA frente al dataset integrado completo?**
> *Respuesta:* *"El dataset integrado tiene 18 variables con alta multicolinealidad (por ejemplo, servicios de taller y costo tienen r = 0,985). Al aplicar PCA, transformamos las variables en componentes ortogonales descorrelacionadas, reduciendo la dimensionalidad a 5 componentes que explican el 98,31% de la información total sin sufrir la maldición de la dimensionalidad."*
