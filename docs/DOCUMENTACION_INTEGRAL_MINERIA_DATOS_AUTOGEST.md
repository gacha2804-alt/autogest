# DOCUMENTACIÓN TÉCNICA INTEGRAL DEL PROCESO DE MINERÍA DE DATOS
## Proyecto AUTOGEST · Análisis de Siniestralidad Vial, Flujo de Tráfico y Gestión de Taller
### Programa de Ingeniería de Sistemas · Asignatura: Minería de Datos y Métodos Numéricos
**Universidad Minuto de Dios (UNIMINUTO) · Centro Regional Ibagué**  
**Autora:** Gilary Gacha  emelin rubiano
**Periodo Académico:** 2026-2  
**Repositorio Oficial:** `c:\Users\Gilary Gacha\Desktop\autogest`  
**Dashboard Público en Producción (Netlify):** [https://autogest-ibague.netlify.app/](https://autogest-ibague.netlify.app/)  
**Módulo de Métodos Numéricos en Producción:** [https://autogest-ibague.netlify.app/metodos.html](https://autogest-ibague.netlify.app/metodos.html)  
**API Backend en Producción (Supabase Edge Function → NeonDB):** [https://veakptgthvcqyoomwjdv.supabase.co/functions/v1/autogest-api/health](https://veakptgthvcqyoomwjdv.supabase.co/functions/v1/autogest-api/health)

---

## TABLA DE CONTENIDO

1. [Introducción al Proyecto AutoGest](#1-introducción-al-proyecto-autogest)
2. [Búsqueda, Selección y Reconocimiento de las Fuentes de Datos](#2-búsqueda-selección-y-reconocimiento-de-las-fuentes-de-datos)
3. [Exploración Inicial de los Datos](#3-exploración-inicial-de-los-datos)
4. [Limpieza y Preparación de los Datos](#4-limpieza-y-preparación-de-los-datos)
5. [Integración y Unión de los Conjuntos de Datos](#5-integración-y-unión-de-los-conjuntos-de-datos)
6. [Estandarización y Transformación de Variables](#6-estandarización-y-transformación-de-variables)
7. [Análisis Exploratorio de Datos (EDA)](#7-análisis-exploratorio-de-datos-eda)
8. [Análisis de Correlaciones](#8-análisis-de-correlaciones)
9. [Reducción de Dimensionalidad mediante PCA](#9-reducción-de-dimensionalidad-mediante-pca)
10. [Modelos de Aprendizaje Automático](#10-modelos-de-aprendizaje-automático)
11. [Metodología CRISP-DM](#11-metodología-crisp-dm)
12. [Desarrollo de los Métodos Numéricos](#12-desarrollo-de-los-métodos-numéricos)
    - 12.1 [Regresión Lineal por Mínimos Cuadrados (Semestral Oficial vs. Anual Complementario)](#121-regresión-lineal-por-mínimos-cuadrados)
    - 12.2 [Interpolación de Lagrange (Polinomio Cuártico de 5 Nodos)](#122-interpolación-de-lagrange)
    - 12.3 [Comparación y Evaluación Crítica de Métodos Numéricos](#123-comparación-de-métodos-numéricos)
13. [Integración de Resultados en el Dashboard Web](#13-integración-de-los-resultados-en-el-dashboard)
14. [Dificultades Encontradas y Soluciones Técnicas](#14-dificultades-y-soluciones-durante-el-desarrollo)
15. [Resultados y Hallazgos Principales](#15-resultados-y-hallazgos-principales)
16. [Limitaciones del Estudio](#16-limitaciones-del-estudio)
17. [Conclusiones](#17-conclusiones)
18. [Tecnologías y Bibliotecas Utilizadas](#18-tecnologías-y-bibliotecas-utilizadas)

---

## 1. INTRODUCCIÓN AL PROYECTO AUTOGEST

### 1.1 Contexto y Problemática Abordada
La movilidad vehicular y la siniestralidad vial representan dos de los mayores desafíos socioeconómicos y de salud pública en Colombia. En corredores estratégicos de interconexión regional —como el corredor vial de Ibagué, paso obligatorio entre el centro del país, el Eje Cafetero y el puerto de Buenaventura— confluyen diariamente flujos intensivos de vehículos livianos, transporte intermunicipal de pasajeros y transporte pesado de carga.

Tradicionalmente, las entidades territoriales, los concesionarios viales y los operadores logísticos analizan la movilidad de manera fragmentada:
- Las secretarías de tránsito y la Policía Nacional analizan la accidentalidad únicamente como cifras policiales de eventos y fatalidades.
- Los concesionarios de peajes (INVIAS y ANI) monitorean exclusivamente el aforo vehicular y el recaudo financiero.
- Los centros de diagnóstico automotriz y talleres de mantenimiento registran bitácoras de fallas mecánicas, tiempos de parada y costos de reparación sin correlacionarlos con la dinámica de la infraestructura vial.

Esta desconexión genera una brecha analítica: **no se comprende cuantitativamente de qué manera el volumen vehicular y la tipología de los automotores que transitan por la red vial condicionan la ocurrencia de accidentes de tránsito, ni cómo ese riesgo se traduce operativamente en sobrecostos de mantenimiento, horas de reparación y demanda de servicios de grúa.**

### 1.2 Propósito de la Minería de Datos
El proyecto **AutoGest** nace como una iniciativa científico-tecnológica en el marco del programa de Ingeniería de Sistemas de UNIMINUTO para cerrar dicha brecha. Su propósito es consolidar un pipeline automatizado, reproducible y matemáticamente sustentado de minería de datos que integre fuentes heterogéneas de movilidad, aforo carretero y servicio mecánico, permitiendo:
1. Identificar concentraciones temporales de riesgo y anomalías operativas.
2. Descubrir asociaciones estadísticas entre el flujo de tráfico, vehículos exentos y accidentalidad vial.
3. Evaluar modelos de clasificación y agrupamiento para predecir niveles de riesgo vehicular.
4. Aplicar métodos numéricos para modelar tendencias históricas y proyecciones de siniestralidad.

### 1.3 Alcance y Objetivos
- **Alcance Temporal:** Registros históricos desde enero de 2014 hasta mayo de 2026 (149 periodos mensuales cronológicos, subdivididos en 25 semestres completos e incompletos).
- **Alcance Geográfico y Operativo:** Red de transporte nacional con énfasis en los puntos de aforo de peaje, talleres concesionados y la siniestralidad vial urbana e interurbana de Ibagué (Tolima).
- **Objetivo General:** Desarrollar un sistema analítico integral basado en minería de datos y métodos numéricos para la caracterización, modelado y visualización de la siniestralidad vial y la demanda de mantenimiento de flota en el ecosistema AutoGest.

---

## 2. BÚSQUEDA, SELECCIÓN Y RECONOCIMIENTO DE LAS FUENTES DE DATOS

El desarrollo de AutoGest requirió identificar y seleccionar fuentes primarias que cubrieran las tres dimensiones del problema: siniestralidad, flujo vial y soporte mecánico.

### 2.1 Fuentes de Información Seleccionadas

```
┌────────────────────────────────────────────────────────────────────────┐
│                        FUENTES PRIMARIAS AUTOGEST                      │
├─────────────────────┬──────────────────────────┬───────────────────────┤
│ Accidentes de       │ Tráfico Vehicular y      │ Taller Mecánico y     │
│ Tránsito            │ Peajes (INVIAS)          │ Mantenimiento         │
│ (Policía / DANE)    │                          │                       │
│ 633,298 registros   │ 149,944 registros        │ 2,000,000 registros   │
│ 6 columnas (33.3 MB)│ 9 columnas (14.2 MB)     │ 28 columnas (482.8 MB)│
└─────────────────────┴──────────────────────────┴───────────────────────┘
```

#### 2.1.1 Dataset de Accidentes de Tránsito (`dataset/accidentes.csv`)
- **Procedencia:** Datos Abiertos del Gobierno de Colombia / Registros oficiales de siniestralidad vial de la Policía Nacional y codificación DIVIPOLA del DANE.
- **Dimensiones:** $633.298$ filas $\times$ $6$ columnas ($33,29$ MB).
- **Periodo Cubierto:** 2014 a 2026.
- **Variables Originales:**
  - `FECHA HECHO`: Fecha del reporte del siniestro (formato texto `DD/MM/AAAA`).
  - `COD_DEPTO`: Código numérico del departamento según clasificación DANE.
  - `DEPARTAMENTO`: Nombre en texto del departamento.
  - `COD_MUNI`: Código numérico municipal DANE.
  - `MUNICIPIO`: Nombre del municipio donde ocurrió el evento.
  - `CANTIDAD`: Número de eventos o lesionados registrados en el reporte.

#### 2.1.2 Dataset de Tráfico Vehicular y Peajes (`dataset/trafico.csv`)
- **Procedencia:** Instituto Nacional de Vías (INVIAS) / Subdirección de Tránsito y Transporte.
- **Dimensiones:** $149.944$ filas $\times$ $9$ columnas ($14,23$ MB).
- **Periodo Cubierto:** Enero de 2014 a mayo de 2026.
- **Variables Originales:**
  - `IdPeaje`: Identificador único de la estación de peaje.
  - `Peaje`: Nombre oficial de la estación (e.g., PURGATORIO, TUTA, SIBERIA, ALVARADO).
  - `CategoriaTarifa`: Categoría vehicular según cobro tarifario (`I`, `II`, `III`, `IV`, `V`, `VI`, `VII`, `IE`, `UNICA`, etc.).
  - `Desde` / `Hasta`: Intervalo temporal de medición mensual (formato fecha).
  - `ValorTarifa`: Valor unitario cobrado por peaje (almacenado con separadores de miles).
  - `CantidadTrafico`: Conteo mensual de vehículos registrados en la estación.
  - `CantidadEvasores`: Automotores que eludieron el cobro de la tasa vial.
  - `CantidadExentos787`: Automotores con exención de pago (Ley 787 de movilidad especial).

#### 2.1.3 Dataset de Taller y Mantenimiento de Flota (`dataset/taller.csv`)
- **Procedencia:** Bitácora operativa de sistemas de gestión de flota de talleres automotrices y concesionarias de grúas viales.
- **Dimensiones:** $2.000.000$ filas $\times$ $28$ columnas ($482,79$ MB).
- **Periodo Cubierto:** 2014 a 2026.
- **Variables Principales:**
  - `Service ID`: Clave primaria alfanumérica de la orden de trabajo.
  - `Customer Name`: Nombre del propietario o empresa operadora de transporte.
  - `Vehicle Type`: Clasificación del automotor (`Car`, `SUV`, `Bus`, `Van`, `Truck`).
  - `Make and Model`: Marca y modelo comercial del vehículo intervenido.
  - `Service Type`: Tipo de servicio (`Brake Service`, `Oil Change`, `Towing`, `Engine Repair`).
  - `Repair Date`: Fecha del servicio mecánico (`AAAA-MM-DD`).
  - `Total Cost`: Costo final de mano de obra y repuestos en unidades monetarias.
  - `Service Duration Hours`: Duración real de la reparación en taller.
  - `Mileage at Service`: Kilometraje u odómetro acumulado al ingresar al taller.
  - `Tow Distance Miles`: Distancia de remolque en millas asistida por grúa.
  - `Urgency Level`: Nivel de atención (`Scheduled`, `Urgent`, `Emergency`).
  - `Customer Type`: Segmento de cliente (`Fleet` corporativa vs. `Individual`).

#### 2.1.4 Diccionario Geográfico DANE (`dataset/municipios_dane.xlsx`)
- **Procedencia:** Catálogo de División Político-Administrativa de Colombia (DIVIPOLA) del DANE.
- **Uso:** Normalización de códigos departamentales a 2 dígitos y municipales a 5 dígitos (`00000`), resolviendo discrepancias ortográficas y sufijos institucionales.

---

## 3. EXPLORACIÓN INICIAL DE LOS DATOS

La exploración inicial se ejecutó de forma modular mediante clases orientadas a objetos estructuradas en el directorio `src/` y cuadernos de análisis en `analisis/`:
- `src/accidentes.py` $\to$ Clase `Accidentes`
- `src/taller.py` $\to$ Clase `Taller`
- `src/trafico.py` $\to$ Clase `Trafico`
- Cuaderno interactivo: `analisis/analisis_datos.ipynb`

### 3.1 Inspección Estructural y Lectura Defensiva
Debido al volumen de los archivos (especialmente `taller.csv` con cerca de medio gigabyte y 2 millones de filas), se implementó un mecanismo de resolución de rutas dinámico (`resolver_ruta`) para garantizar ejecución tanto desde la raíz del proyecto como desde subcarpetas.

```python
def resolver_ruta(ruta):
    """Resuelve la ruta del archivo de forma defensiva desde cualquier entorno."""
    p = Path(ruta)
    if p.exists():
        return p
    raiz = Path(__file__).resolve().parent.parent
    candidatos = [
        raiz / "dataset" / p.name,
        raiz / p,
        Path.cwd() / "dataset" / p.name,
        Path.cwd() / p,
    ]
    for c in candidatos:
        if c.exists():
            return c
    return p
```

### 3.2 Diagnóstico Inicial de Anomalías y Calidad

| Fuente | Filas Originales | Columnas | Valores Nulos Identificados | Duplicados Exactos | Problemas Detectados en Lectura |
| :--- | :---: | :---: | :--- | :---: | :--- |
| **Accidentes** | $633.298$ | 6 | `FECHA HECHO`: 0<br>`COD_MUNI`: 12 nulos<br>`MUNICIPIO`: 12 nulos | $3.412$ filas | Fechas en formato texto `DD/MM/AAAA`; códigos DANE leídos como números decimales (`float64`) con pérdida de ceros a la izquierda (e.g. `73001.0` en vez de `"73001"`). |
| **Tráfico** | $149.944$ | 9 | `CantidadTrafico`: 0<br>`ValorTarifa`: 0<br>`CantidadEvasores`: 0 | $1.205$ filas | Las columnas numéricas contenían separadores mixtos de miles con comas y puntos (e.g. `"1,250.00"` o `"12.450"`), cargándose como `object` (strings). |
| **Taller** | $2.000.000$ | 28 | `Mileage at Service`: 1.4% nulos<br>`Total Cost`: 0.8% nulos<br>`Tow Distance`: 2.1% nulos | $0$ filas | Costos negativos en registros erróneos; inconsistencia de mayúsculas/minúsculas en tipos de vehículos (`truck`, `Truck`, `TRUCK`). |

---

## 4. LIMPIEZA Y PREPARACIÓN DE LOS DATOS

La limpieza de los datos se ejecutó a través de métodos `.limpiar()` dedicados en cada clase modular, generando versiones intermedias auditables: `accidentes_limpio.csv`, `trafico_limpio.csv` y `taller_limpio.csv`.

### 4.1 Pipeline de Limpieza por Fuente

#### 4.1.1 Limpieza de Accidentes (`src/accidentes.py`)
1. **Deduplicación:** Eliminación de los $3.412$ registros redundantes exactos (`drop_duplicates()`).
2. **Normalización de Texto:** Remoción de tildes mediante descomposición Unicode NFD (`unicodedata`) y eliminación de sufijos institucionales como `(CT)` y `D.C.`:
   ```python
   def normalizar_municipio(texto):
       texto = normalizar_texto(texto)
       texto = texto.replace("(CT)", "").replace(" D.C.", "").strip()
       return texto
   ```
3. **Estandarización DIVIPOLA DANE:** Conversión de códigos a cadenas de longitud fija:
   - `COD_DEPTO`: Relleno con ceros a 2 dígitos (`str.zfill(2)`).
   - `COD_MUNI`: Relleno con ceros a 5 dígitos (`str.zfill(5)`).
4. **Transformación Temporal:** Parseo de `FECHA HECHO` mediante `pd.to_datetime(format="%d/%m/%Y", errors="coerce")`, extrayendo las componentes enteras `AÑO` y `MES`.
5. **Filtrado Operativo:** Imputación de cantidades nulas a $1$ y exclusión de registros con cantidad menor o igual a cero.

#### 4.1.2 Limpieza de Tráfico y Peajes (`src/trafico.py`)
1. **Deduplicación:** Eliminación de $1.205$ duplicados.
2. **Saneamiento Numérico de Strings:** Remoción sistemática de caracteres no numéricos en `CantidadTrafico`, `CantidadEvasores`, `CantidadExentos787` y `ValorTarifa`:
   ```python
   limpio = df[c].astype(str).str.replace(",", "", regex=False).str.replace(".", "", regex=False).str.strip()
   df[c] = pd.to_numeric(limpio, errors="coerce").fillna(0)
   ```
3. **Homologación de Categorías Tarifarias:** Mapeo de más de 20 categorías tarifarias del INVIAS hacia las tres tipologías vehiculares canónicas:
   ```python
   def homologar_tarifa(cat):
       cat_str = str(cat).strip().upper()
       if cat_str in ["I", "IE", "IEE", "IEEE", "IE1", "IE2", "IE3", "IE4", "IE10", "IE1A", "IE1B", "UNICA", "EXCI"]:
           return "LIVIANO"
       elif cat_str in ["II", "IIE", "IIIE", "IIE1", "IIE2", "IIA", "POLCA", "EXCII"]:
           return "TRANSPORTE_PASAJEROS"
       else:
           return "CARGA_PESADO"
   ```
4. **Variable Financiera:** Cálculo de recaudo bruto estimado:
   $$\text{RECAUDO\_ESTIMADO} = \text{CantidadTrafico} \times \text{ValorTarifa}$$

#### 4.1.3 Limpieza de Taller y Mantenimiento (`src/taller.py`)
1. **Homologación Canónica:** Mapeo de los tipos de vehículo del taller (`Vehicle Type`):
   - `CAR`, `SUV` $\to$ `LIVIANO`
   - `BUS`, `VAN` $\to$ `TRANSPORTE_PASAJEROS`
   - `TRUCK` $\to$ `CARGA_PESADO`
2. **Tratamiento de Valores Nulos:** Imputación robusta con la **mediana** de las variables continuas operativas:
   - Mediana de `Total Cost`
   - Mediana de `Service Duration Hours`
   - Mediana de `Mileage at Service`
3. **Control de Rango:** Eliminación estricta de registros con costos negativos ($\text{Total Cost} < 0$).

---

## 5. INTEGRACIÓN Y UNIÓN DE LOS CONJUNTOS DE DATOS

La fase de integración relacional (`src/integracion.py`) constituyó el núcleo técnico para la construcción del `dataset_integrado.csv`.

```
┌──────────────────────────┐       ┌──────────────────────────┐
│   trafico_limpio.csv     │       │     taller_limpio.csv    │
│  Agregado por:           │       │   Agregado por:          │
│  (AÑO, MES, TIPO_VEHICULO│       │   (AÑO, MES, TIPO_VEHICULO   │
└────────────┬─────────────┘       └─────────────┬────────────┘
             │                                   │
             └─────────────► MERGE OUTER ◄───────┘
                                   │
                                   ▼
                      ┌────────────────────────┐
                      │   merged_movilidad     │
                      └────────────┬───────────┘
                                   │
┌──────────────────────────┐       │
│  accidentes_limpio.csv   │       │
│  Agregado por (AÑO, MES) ├───────► MERGE LEFT
└──────────────────────────┘       │
                                   ▼
                      ┌────────────────────────┐
                      │ Ponderación de Riesgo  │
                      │       Flujo Vial       │
                      └────────────┬───────────┘
                                   ▼
                      ┌────────────────────────┐
                      │  dataset_integrado.csv │
                      │  507 filas × 18 cols   │
                      └────────────────────────┘
```

### 5.1 Criterios de Unión y Agregación
Las fuentes originales presentaban diferentes granularidades:
- Tráfico: registro individual por estación de peaje, categoría y mes.
- Taller: registro por cada orden individual de servicio técnico.
- Accidentes: registro por cada siniestro vial georreferenciado con fecha exacta.

Para hacerlas comparables sin distorsión matemática, se definieron como llaves relacionales primarias la terna:
$$\text{Clave Primaria} = (\text{A\~{N}O}, \text{MES}, \text{TIPO\_VEHICULO})$$

### 5.2 El Modelo de Ponderación Proporcional de Siniestralidad
El dataset oficial de la policía registra el conteo total de accidentes a nivel municipal y mensual (`ACCIDENTES_TOTALES`), pero **no desglosa la tipología vehicular culpable o involucrada**. 

Para asignar la accidentalidad de forma científicamente fundamentada y evitar una división arbitraria en partes iguales ($1/3$), se implementó un **modelo de asignación proporcional a la exposición al riesgo**:
1. Se computa el aforo total circulante en el mes sumando todas las tipologías:
   $$\text{Aforo\_Mes}(a, m) = \sum_{v \in \text{Tipologías}} \text{VOLUMEN\_TRAFICO}(a, m, v)$$
2. Se calcula la proporción de flujo de cada categoría:
   $$w(a, m, v) = \begin{cases} \frac{\text{VOLUMEN\_TRAFICO}(a, m, v)}{\text{Aforo\_Mes}(a, m)} & \text{si } \text{Aforo\_Mes} > 0 \\ \frac{1}{3} & \text{en otro caso} \end{cases}$$
3. Se distribuyen los accidentes registrados garantizando la conservación de la suma total:
   $$\text{ACCIDENTES\_REGISTRADOS}(a, m, v) = \text{round}\Big(\text{ACCIDENTES\_TOTALES}(a, m) \times w(a, m, v)\Big)$$

### 5.3 Tabla Comparativa de Dimensiones: Antes vs. Después

| Conjunto de Datos | Archivo Físico | Filas | Columnas | Tamaño en Disco | Nulos (%) | Duplicados |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Accidentes Original** | `dataset/accidentes.csv` | $633.298$ | 6 | $33,29$ MB | $< 0,01\%$ | $3.412$ |
| **Accidentes Limpio** | `dataset/accidentes_limpio.csv` | $629.886$ | 10 | $21,99$ MB | $0,00\%$ | $0$ |
| **Taller Original** | `dataset/taller.csv` | $2.000.000$ | 28 | $482,79$ MB | $4,30\%$ | $0$ |
| **Taller Limpio** | `dataset/taller_limpio.csv` | $1.999.850$ | 29 | $507,05$ MB | $0,00\%$ | $0$ |
| **Tráfico Original** | `dataset/trafico.csv` | $149.944$ | 9 | $14,23$ MB | $0,00\%$ | $1.205$ |
| **Tráfico Limpio** | `dataset/trafico_limpio.csv` | $148.739$ | 14 | $17,16$ MB | $0,00\%$ | $0$ |
| **DATASET INTEGRADO** | `dataset/dataset_integrado.csv` | **$507$** | **18** | **$0,07$ MB** | **$0,00\%$** | **$0$** |
| **DATASET REDUCIDO (PCA)**| `dataset/dataset_reducido.csv` | **$507$** | **9** | **$0,06$ MB** | **$0,00\%$** | **$0$** |

> **Diferencia Metodológica: Unión Relacional vs. Concatenación:**
> - Una **concatenación** (`pd.concat`) simplemente apila vertical u horizontalmente DataFrames sin relacionar su contenido semántico, lo que habría generado una matriz dispersa con millones de filas y múltiples celdas vacías (`NaN`).
> - Una **unión relacional con agregación** (`groupby` + `pd.merge`) alinea conceptualmente la información a través de dimensiones compartidas de tiempo y tipo de automotor, consolidando una base de datos analítica compacta de 507 registros (149 periodos cronológicos $\times$ categorías vehiculares activas).

---

## 6. ESTANDARIZACIÓN Y TRANSFORMACIÓN DE VARIABLES

El preprocesamiento matemático de variables se encuentra implementado en `src/transformacion.py` y se documenta en el cuaderno `analisis/transformacion_escalabilidad.ipynb`.

### 6.1 Demostración Empírica de "El Gancho" (Secuestro de Distancia)
En minería de datos, los algoritmos basados en distancias (como KNN o K-Means) son altamente vulnerables a las diferencias de magnitud entre variables. Si una variable está expresada en millones y otra en unidades, la variable de gran magnitud anula a todas las demás.

Para evidenciar esto ante la comunidad académica, se comparó la distancia euclídea entre el primer y segundo registro del dataset antes y después del escalado:
- **Fórmula de Distancia Euclídea:**
  $$d(p, q) = \sqrt{\sum_{i=1}^{n} (p_i - q_i)^2}$$
- **Distancia sin escalar:**
  $$d_{\text{cruda}} = 10.845.277,43 \text{ unidades}$$
  *(El $99,99\%$ de la distancia estaba determinado exclusivamente por la diferencia en `VOLUMEN_TRAFICO`).*
- **Distancia escalada (`MinMaxScaler`):**
  $$d_{\text{escalada}} = 0,7060 \text{ unidades}$$
  *(Permite que variables como `SERVICIOS_TALLER`, `TASA_EVASION_PCT` y `MILLAJE_PROMEDIO` aporten equilibradamente al espacio métrico).*

### 6.2 Comparación de Escaladores Estadísticos
Se implementaron y compararon tres técnicas de transformación en `Transformacion.comparar_escaladores()`:

1. **StandardScaler (Z-Score):**
   $$z = \frac{x - \mu}{\sigma}$$
   Transforma las variables para que tengan media $\mu = 0$ y desviación estándar $\sigma = 1$. Es el requisito teórico indispensable para la descomposición ortogonal en Componentes Principales (PCA).
2. **MinMaxScaler:**
   $$x' = \frac{x - x_{\min}}{x_{\max} - x_{\min}}$$
   Acota las variables al rango $[0, 1]$. Es sensible a la presencia de valores atípicos severos.
3. **RobustScaler:**
   $$x_{\text{rob}} = \frac{x - \text{Mediana}}{IQR}$$
   Utiliza estadísticos resistentes (mediana y rango intercuartílico), evitando que los valores atípicos distorsionen la escala.

### 6.3 Discretización de la Variable Objetivo
Para los algoritmos de clasificación supervisada, la variable continua `ACCIDENTES_REGISTRADOS` fue transformada en una variable categórica ordinal de **3 niveles de riesgo vial** (`Bajo`, `Medio`, `Alto`) mediante la técnica de cuantiles (`KBinsDiscretizer(n_bins=3, strategy="quantile")`). Esta discretización garantiza balanceo exacto entre clases en el conjunto de entrenamiento:
- **Bajo:** Siniestralidad baja ($0$ a $150$ accidentes/mes-categoría).
- **Medio:** Siniestralidad moderada ($151$ a $850$ accidentes/mes-categoría).
- **Alto:** Siniestralidad crítica ($> 850$ accidentes/mes-categoría).

---

## 7. ANÁLISIS EXPLORATORIO DE DATOS (EDA)

El análisis exploratorio formal (`src/eda.py` y `analisis/analisis_exploratorio_eda.ipynb`) evaluó las propiedades estructurales de las distribuciones.

### 7.1 Las Tres Familias de Medidas Estadísticas

| Familia de Medida | Métrica Estadística | `ACCIDENTES_REGISTRADOS` (Objetivo) | `VOLUMEN_TRAFICO` | `SERVICIOS_TALLER` | `COSTO_TOTAL_TALLER` |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Tendencia Central** | **Media ($\bar{x}$)** | $746,02$ | $6.475.939,78$ | $3.944,77$ | $\$1.476.214,65$ |
| | **Mediana ($M$)** | **$400,00$** | **$3.574.005,00$** | **$0,00$** | **$\$0,00$** |
| | **Moda** | $0,00$ | $0,00$ | $0,00$ | $\$0,00$ |
| **Dispersión** | **Desviación Estándar ($s$)** | $899,26$ | $5.897.085,89$ | $4.587,10$ | $\$1.717.313,56$ |
| | **Rango Mín – Máx** | $[0,00 - 4.458,00]$ | $[0 - 22.371.088]$ | $[0 - 11.516]$ | $[\$0 - \$4.367.279,09]$ |
| | **Cuartil 1 ($Q_1$)** | $39,50$ | $1.730.015,00$ | $0,00$ | $\$0,00$ |
| | **Cuartil 3 ($Q_3$)** | $1.173,50$ | $10.628.735,00$ | $5.741,00$ | $\$2.159.990,52$ |
| | **Rango Intercuartílico ($IQR$)**| **$807,50$** | **$8.898.720,00$** | **$5.741,00$** | **$\$2.159.990,52$** |
| | **Límite Superior IQR** | **$2.226,25$** | **$25.368.570,00$** | **$14.352,50$** | **$\$5.399.976,29$** |
| **Forma** | **Asimetría de Fisher** | **$+2,34$ (Sesgo positivo severo)** | **$+1,01$ (Moderado)** | **$+0,59$** | **$+0,59$** |
| | **Curtosis** | **$5,75$ (Leptocúrtica)** | **$-0,36$ (Platicúrtica)**| **$-1,28$** | **$-1,27$** |
| **Atípicos** | **Outliers Detectados** | **$36$ periodos ($7,10\%$)** | **$0$** | **$0$** | **$0$** |

### 7.2 El Cuarteto de Anscombe y la Falacia de la Media
El resultado de asimetría positiva ($+2,34$) y curtosis leptocúrtica ($5,75$) en la siniestralidad vial demostró la validez práctica de la advertencia de Anscombe:
- Un analista novato que observe únicamente el promedio ($\bar{x} = 746,02$) asumiría que la ciudad presenta una demanda constante de aproximadamente 750 siniestros mensuales por tipología.
- Sin embargo, **la mediana real es de $400,00$ accidentes**, casi la mitad del promedio. La media está inflada artificialmente por $36$ meses de contingencia severa donde los accidentes escalan hasta $4.458$ eventos.
- **Decisión Metodológica:** Los 36 valores atípicos **no son errores de digitación**, sino eventos fácticos de máxima tensión vial (temporadas vacacionales y puentes festivos). Por tanto, **se mantuvieron en el dataset** para no ocultar la realidad operativa.

### 7.3 Galería Visual del EDA (8 Figuras Verificadas)

```
[Fig. 1: Histograma Accidentes]       [Fig. 2: Boxplot IQR Accidentes]
Asimetría Fisher = +2.34             36 Outliers Críticos (> 2,226.25)
Líneas: Media (746) vs Mediana (400) Punto Máximo: 4,458 eventos

[Fig. 3: Tráfico por Tipología]       [Fig. 4: Scatter Tráfico vs Taller]
Livianos (46.3%) y Carga (43.8%)     Tendencia MCO Positiva Ascendente
Pasajeros concentran 9.8%            Asociación r = 0.6845

[Fig. 5: Heatmap Correlaciones]      [Fig. 6: Pairplot Multivariado]
Interdependencia cuantitativa         KDE diagonal y dispersión
Taller vs Costo: r ≈ 0.99            Separación por tipologías

[Fig. 7: Boxplot Costo por Tipo]      [Fig. 8: Tendencia Multianual]
Carga Pesada triplica la dispersión   Impacto pandemia 2020 (valle)
y mediana de gasto mecánico          Reactivación sostenida 2021-2026
```

---

## 8. ANÁLISIS DE CORRELACIONES

El análisis de correlación lineal se evaluó utilizando el coeficiente de correlación de Pearson ($r$):
$$r = \frac{\sum_{i=1}^{n} (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^{n} (x_i - \bar{x})^2} \sqrt{\sum_{i=1}^{n} (y_i - \bar{y})^2}}$$

### 8.1 Resultados Cuantitativos Exactos ($N = 507$ Observaciones)
Evaluadas sobre la matriz completa de 507 observaciones desagregadas por tipología vehicular y periodo cronológico:

1. **Tráfico Vehicular vs. Accidentes Registrados:**
   $$r = +0,6683 \quad (\text{Correlación positiva moderada-fuerte})$$
   A mayor aforo en carreteras y peajes, mayor es la probabilidad de que ocurran colisiones viales.
2. **Vehículos Exentos vs. Accidentes Registrados:**
   $$r = +0,7154 \quad (\text{Correlación positiva fuerte})$$
   Los vehículos exentos corresponden a transporte oficial, ambulancias y residentes locales de corredores periurbanos, cuya presencia coincide con zonas de alta interacción peatonal y vehicular de alto riesgo.
3. **Servicios de Taller vs. Costo Total de Reparación:**
   $$r = +0,9999 \approx 1,0000 \quad (\text{Correlación casi perfecta})$$
   Valida la consistencia contable del sistema: el gasto acumulado en mantenimiento es directamente proporcional a la cantidad de órdenes de servicio ejecutadas.
4. **Vehículos Evasores vs. Accidentes Registrados:**
   $$r = +0,0353 \quad (\text{Correlación prácticamente nula})$$
   La infracción de evasión de peaje ocurre de manera independiente a la accidentalidad masiva en carretera.

### 8.2 Frontera Epistemológica: Correlación vs. Causalidad
En la sustentación académica de AutoGest se hace especial énfasis en delimitar la frontera causal:
> **Una correlación de $r = 0,6683$ no demuestra que el tráfico cause accidentes.**  
> El volumen vehicular actúa como una variable de **exposición al riesgo**: a mayor número de automotores por kilómetro cuadrado, aumenta la probabilidad de que factores causales directos (falla humana, microsueño, exceso de velocidad, lluvia o falla de frenos) desencadenen un siniestro.

---

## 9. REDUCCIÓN DE DIMENSIONALIDAD MEDIANTE PCA

El Análisis de Componentes Principales (PCA) se aplicó sobre las 8 variables continuas estandarizadas con `StandardScaler`.

### 9.1 Varianza Explicada por Componente Principal

$$\text{Varianza Total Explicada} = 98,31\% \quad (\text{con 5 Componentes})$$

| Componente | Varianza Individual | Varianza Acumulada | Interpretación Teórica del Eje |
| :---: | :---: | :---: | :--- |
| **PC1** | **$48,22\%$** | **$48,22\%$** | **Eje de Magnitud Operativa y Siniestralidad:** Condensa el volumen de tráfico y los accidentes viales. |
| **PC2** | **$28,15\%$** | **$76,37\%$** | **Eje de Mantenimiento y Costos:** Asocia servicios de taller, costos y kilometraje de flota. |
| **PC3** | **$12,04\%$** | **$88,41\%$** | **Eje de Infracción y Exención:** Captura evasión de peajes y condiciones especiales de vía. |
| **PC4** | **$6,12\%$** | **$94,53\%$** | **Eje Temporal:** Variaciones residuales de tendencia multianual. |
| **PC5** | **$3,78\%$** | **$98,31\%$** | **Eje Estacional:** Ajustes de estacionalidad mensual. |

El resultado fue exportado en `dataset/dataset_reducido.csv` ($507$ filas $\times$ $9$ columnas: `AÑO`, `MES`, `TIPO_VEHICULO`, `PC1` a `PC5` y `ACCIDENTES_REGISTRADOS`), reduciendo en un $50\%$ la dimensionalidad del espacio predictivo preservando casi la totalidad de la información.

---

## 10. MODELOS DE APRENDIZAJE AUTOMÁTICO

Se implementaron y compararon rigurosamente los modelos predictivos supervisados y no supervisados estructurados en `src/arbol_decision.py`, `src/clasificacion_modelos.py` y `src/clustering.py`.

### 10.1 Torneo de Clasificación Supervisada (Sesión 8)
Para garantizar una comparación metodológica perfecta, los tres modelos fueron entrenados y evaluados bajo un **tablero compartido único**:
- Mismo split estratificado 75% Entrenamiento ($380$ observaciones) y 25% Prueba ($127$ observaciones).
- Misma semilla aleatoria fija: `random_state = 42`.
- Misma variable objetivo discretizada en 3 niveles de riesgo (`Bajo`, `Medio`, `Alto`).

#### Tabla Comparativa Oficial del Torneo de Clasificación

| Modelo de Clasificación | Parámetros Clave | Preprocesamiento | Accuracy Train | Accuracy Test | Tiempo Fit (s) | Diagnóstico Metodológico |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **Árbol de Decisión** | `max_depth=4`, `criterion='gini'` | Invariante (Sin escalar o Escalado) | **$88,95\%$** | **$83,46\%$** | $0,0047$ s | **Modelo Ganador General:** Excelente equilibrio bias-varianza. Altamente interpretable con reglas `if-then`. |
| **K-Nearest Neighbors (KNN)** | $k=5$, métrica euclídea | Con `StandardScaler` (Pipeline) | **$91,58\%$** | **$83,46\%$** | $0,0042$ s | **Excelente clasificador métrico:** Empata la exactitud del árbol, pero requiere almacenamiento de todo el conjunto de entrenamiento. |
| **K-Nearest Neighbors (KNN)** | $k=5$, métrica euclídea | **Sin escalar (Crudo)** | **$84,74\%$** | **$74,02\%$** | $0,0035$ s | **Degradación severa ($-9,44\%$):** Demuestra empíricamente por qué *"distancia manda a escalar"*. |
| **Gaussian Naive Bayes** | Priors empíricos | Distribución Gaussiana | **$60,26\%$** | **$59,84\%$** | $0,0021$ s | **Rendimiento bajo:** Viola el supuesto de independencia condicional debido a la fuerte correlación entre tráfico y accidentalidad. |

### 10.2 Demostración del Efecto del Escalado en KNN
La experimentación con KNN demostró matemáticamente el impacto de estandarizar:
- Sin `StandardScaler`: Accuracy Test = **$74,02\%$**
- Con `StandardScaler`: Accuracy Test = **$83,46\%$**
- **Ganancia Neta por Escalamiento:** **$+9,44\%$** ($+0,0945$)
Al estandarizar con media 0 y varianza 1, la variable `VOLUMEN_TRAFICO` deja de dominar la distancia euclídea, permitiendo que variables determinantes como `MILLAJE_PROMEDIO` y `VEHICULOS_EXENTOS` influyan en la asignación de vecinos cercanos.

### 10.3 Exploración del Hiperparámetro $k$ en KNN

| Vecinos ($k$) | Accuracy Train | Accuracy Test | Diagnóstico Teórico |
| :---: | :---: | :---: | :--- |
| **$k = 1$** | $100,00\%$ | $85,04\%$ | **Sobreajuste evidente (Overfitting):** Memoriza exactamente el punto de entrenamiento; sensible al ruido. |
| **$k = 5$** | **$91,58\%$** | **$83,46\%$** | **Punto óptimo:** Mejor equilibrio de frontera y capacidad de generalización. |
| **$k = 11$** | $84,74\%$ | $85,04\%$ | Fronteras suaves, excelente estabilidad estadística. |
| **$k = 31$** | $75,26\%$ | $81,10\%$ | Vecindario excesivamente amplio, comienza a diluir patrones locales. |
| **$k = 51$** | $72,63\%$ | $79,53\%$ | **Subajuste (Underfitting):** Consulta más del 13% de la muestra total, sesgándose hacia la clase mayoritaria. |

### 10.4 Importancia de Variables en el Árbol de Decisión
El cálculo del índice de impureza Gini reveló que el árbol de decisión toma sus decisiones fundamentado en:
1. `VEHICULOS_EXENTOS`: **$38,8\%$** de importancia relativa.
2. `VOLUMEN_TRAFICO`: **$34,6\%$** de importancia relativa.
3. `MILLAJE_PROMEDIO`: **$11,2\%$** de importancia relativa.
4. `COSTO_TOTAL_TALLER`: **$8,1\%$** de importancia relativa.
5. Otras variables combinadas: **$7,3\%$**.

### 10.5 Clustering No Supervisado: K-Means y Jerárquico (Sesión 9)
Implementado en `src/clustering.py`, aplicando `StandardScaler` sobre las variables de comportamiento excluyendo la variable objetivo:
- **Búsqueda del $k$ óptimo:**
  - $k=2$: Inercia $1682,0$, Silueta $0,5600$
  - $k=3$: Inercia $1165,3$, Silueta $0,6331$
  - $k=4$: Inercia $691,9$, Silueta $0,7659$
  - $k=7$: Inercia $103,4$, Silueta $0,8288$ (Máxima silueta matemática)
- **Selección de $k=3$ para perfilamiento operativo:**
  - **Clúster 0 (Período Habitual - 52.7% obs):** Tráfico medio, millaje bajo, tasa media de siniestros ($1.088,8$ acc).
  - **Clúster 1 (Flota Activa de Bajo Riesgo - 35.9% obs):** Millaje elevado ($155.009$ km/mi), baja accidentalidad ($155,2$ acc).
  - **Clúster 2 (Período Crítico de Siniestralidad - 11.4% obs):** Alto aforo, millaje alto, picos críticos de siniestralidad ($1.022,1$ acc).

---

## 11. METODOLOGÍA CRISP-DM

El proyecto AutoGest se estructuró siguiendo formalmente las seis fases del estándar de facto de la industria: **CRISP-DM (Cross-Industry Standard Process for Data Mining)**.

```
       ┌────────────────────────┐
       │ 1. Comprensión Negocio │
       └───────────┬────────────┘
                   ▼
       ┌────────────────────────┐
  ┌───►│ 2. Comprensión Datos   │
  │    └───────────┬────────────┘
  │                ▼
  │    ┌────────────────────────┐
  └───-┤ 3. Preparación Datos   │◄───┐
       └───────────┬────────────┘    │
                   ▼                 │
       ┌────────────────────────┐    │
       │ 4. Modelado            ├───-┘
       └───────────┬────────────┘
                   ▼
       ┌────────────────────────┐
       │ 5. Evaluación          │
       └───────────┬────────────┘
                   ▼
       ┌────────────────────────┐
       │ 6. Despliegue 3 Capas  │
       │ Netlify+Supabase+Neon  │
       └────────────────────────┘
```

1. **Comprensión del Negocio (Business Understanding):** Definición de la pregunta rectora: ¿cómo incide el aforo y la tipología en la siniestralidad y el costo de flota? Delimitación de objetivos técnicos y métricas de éxito.
2. **Comprensión de los Datos (Data Understanding):** Adquisición de los datasets de siniestralidad, peajes INVIAS y mantenimiento. Ejecución del EDA, cálculo de las 3 familias de medidas, correlaciones de Pearson y detección de outliers IQR.
3. **Preparación de los Datos (Data Preparation):** Limpieza de strings, normalización DIVIPOLA DANE, deduplicación, resolución de nulos con medianas, homologación canónica de tipologías vehiculares, integración relacional por $(\text{Año}, \text{Mes}, \text{Tipo})$ y estandarización con `StandardScaler`.
4. **Modelado (Modeling):** Reducción con PCA ($98,31\%$ varianza), entrenamiento del torneo de clasificación supervisada (Árbol CART, GaussianNB, KNN con y sin escalado), segmentación con K-Means y ajuste de métodos numéricos (Mínimos Cuadrados e Interpolación de Lagrange).
5. **Evaluación (Evaluation):** Comparación empírica mediante matrices de confusión, accuracy en conjunto de prueba independiente (75/25 estratificado), verificación de invariancia de escala en árboles, cálculo de $R^2$ y error estándar de estimación $S_e$ en regresión, y análisis del fenómeno de Runge en interpolación.
6. **Despliegue (Deployment):** Arquitectura moderna en 3 capas: frontend interactivo con Chart.js publicado en **Netlify** (rama `deploy/frontend`), API serverless en **Supabase Edge Functions** (proyecto dedicado `mineria`, rama `deploy/backend`) y base de datos PostgreSQL 18 en **NeonDB** (`mineria`), verificada mediante Chrome Remote Debugging (CDP).

---

## 12. DESARROLLO DE LOS MÉTODOS NUMÉRICOS

Esta sección documenta el componente de computación matemática rigurosa desarrollado para modelar la evolución de la siniestralidad vial en Ibagué. Se implementó de manera modular en `src/metodos_numericos.py` y en el cuaderno `analisis/metodos_numericos_lagrange_regresion.ipynb`.

### 12.1 Regresión Lineal por Mínimos Cuadrados

#### 12.1.1 Fundamento Matemático
El método de Mínimos Cuadrados Ordinarios (MCO) busca encontrar los coeficientes de la recta $Y = mX + b$ que minimizan la suma de los errores cuadráticos:
$$\text{Minimizar } S(m, b) = \sum_{i=1}^{N} (y_i - (mx_i + b))^2$$

Derivando parcialmente respecto a $m$ y $b$ e igualando a cero se obtienen las ecuaciones normales, cuyas soluciones explícitas son:
$$m = \frac{N \sum X Y - \sum X \sum Y}{N \sum X^2 - (\sum X)^2} = \frac{SS_{xy}}{SS_{xx}}$$
$$b = \bar{Y} - m\bar{X}$$

Donde las medidas de variabilidad y ajuste corresponden a:
$$SS_{xx} = \sum (x_i - \bar{x})^2, \quad SS_{yy} = \sum (y_i - \bar{y})^2, \quad SS_{xy} = \sum (x_i - \bar{x})(y_i - \bar{y})$$
$$R^2 = \frac{SS_{xy}^2}{SS_{xx} \cdot SS_{yy}}$$
$$S_e = \sqrt{\frac{\sum_{i=1}^{N} (y_i - \hat{y}_i)^2}{N - 2}}$$

#### 12.1.2 MODELO OFICIAL SEMESTRAL ($N = 25$ Observaciones Reales)
- **Requisito Académico Docente:** Cumplimiento estricto del umbral de **mínimo 15 observaciones** ($N \ge 15$) sin recurrir a datos ficticios ni duplicaciones sintéticas.
- **Definición de Variables:**
  - Variable Independiente ($X$): Tiempo transcurrido en años decimales continuos ($2014.0, 2014.5, 2015.0, \dots, 2026.0$).
  - Variable Dependiente ($Y$): Tasa promedio de accidentes por categoría vehicular.
- **Periodo Cronológico:** 2014-S1 hasta 2026-S1* ($25$ semestres reales).

##### Sumatorias Verificadas del Modelo Semestral ($N = 25$):
- $\sum X = 50.500,00 \quad \implies \quad \bar{X} = 2.020,0000$
- $\sum Y = 19.910,21 \quad \implies \quad \bar{Y} = 796,4084$
- $\sum X^2 = 102.010.325,00$
- $\sum Y^2 = 24.386.857,45$
- $\sum XY = 40.186.173,88$
- $SS_{xx} = 325,0000$
- $SS_{yy} = 8.530.198,9611$
- $SS_{xy} = -32.450,3150$

##### Parámetros y Métricas Oficiales:
$$m = \frac{-32.450,3150}{325,0000} = -99,8471$$
$$b = 796,4084 - (-99,8471 \times 2.020,00) = 202.487,5970 \approx 202.487,60$$
$$\mathbf{Y = -99,8471 \cdot X + 202.487,60}$$

- **Coeficiente de Determinación:** $R^2 = 0,3798$ (**$37,98\%$** de la varianza explicada).
- **Error Estándar de Estimación:** $S_e = 479,5890 \approx \mathbf{479,59}$ accidentes.
- **Coeficiente de Correlación de Pearson:** $r = -0,6163$ (asociación lineal negativa moderada).

##### Interpretación Crítica de la Pendiente y Conversión de Unidades:
> [!IMPORTANT]
> **No confundir la pendiente con una reducción por semestre.**  
> Al formularse $X$ en **años decimales**, un incremento de $\Delta X = 1,0$ representa el transcurso de **un año completo**. Por tanto:
> - Pendiente anual equivalente: **$-99,85$ accidentes/año**.
> - Reducción estimada por cada semestre individual ($\Delta X = 0,5$):
>   $$\Delta Y = -99,8471 \times 0,5 = \mathbf{-49,92 \text{ accidentes/semestre}}$$
> Ambas lecturas son matemáticamente equivalentes y coinciden plenamente con el modelo anual complementario.

##### Tabla Completa de las 25 Observaciones Semestrales Oficiales

| Semestre | $X$ (Año Dec.) | $Y$ Real (acc/cat) | $\hat{Y}$ Estimado (MCO) | Residuo ($e_i = Y - \hat{Y}$) | Error Absoluto | Error Porcentual |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 2014-S1 | $2014,0$ | $1.113,72$ | $1.395,49$ | $-281,77$ | $281,77$ | $25,30\%$ |
| 2014-S2 | $2014,5$ | $1.124,33$ | $1.345,57$ | $-221,24$ | $221,24$ | $19,68\%$ |
| 2015-S1 | $2015,0$ | $1.143,22$ | $1.295,64$ | $-152,42$ | $152,42$ | $13,33\%$ |
| 2015-S2 | $2015,5$ | $1.214,39$ | $1.245,72$ | $-31,33$ | $31,33$ | $2,58\%$ |
| 2016-S1 | $2016,0$ | $2.104,39$ | $1.195,80$ | $+908,59$ | $908,59$ | $43,18\%$ |
| 2016-S2 | $2016,5$ | $2.109,44$ | $1.145,87$ | $+963,57$ | $963,57$ | $45,68\%$ |
| 2017-S1 | $2017,0$ | $1.854,33$ | $1.095,95$ | $+758,38$ | $758,38$ | $40,90\%$ |
| 2017-S2 | $2017,5$ | $1.813,00$ | $1.046,03$ | $+766,97$ | $766,97$ | $42,30\%$ |
| 2018-S1 | $2018,0$ | $530,00$ | $996,10$ | $-466,10$ | $466,10$ | $87,94\%$ |
| 2018-S2 | $2018,5$ | $458,11$ | $946,18$ | $-488,07$ | $488,07$ | $106,54\%$ |
| 2019-S1 | $2019,0$ | $448,78$ | $896,26$ | $-447,48$ | $447,48$ | $99,71\%$ |
| 2019-S2 | $2019,5$ | $412,06$ | $846,33$ | $-434,27$ | $434,27$ | $105,39\%$ |
| 2020-S1 | $2020,0$ | $251,17$ | $796,41$ | $-545,24$ | $545,24$ | $217,08\%$ |
| 2020-S2 | $2020,5$ | $268,79$ | $746,48$ | $-477,69$ | $477,69$ | $177,72\%$ |
| 2021-S1 | $2021,0$ | $318,58$ | $696,56$ | $-377,98$ | $377,98$ | $118,65\%$ |
| 2021-S2 | $2021,5$ | $298,04$ | $646,64$ | $-348,60$ | $348,60$ | $116,96\%$ |
| 2022-S1 | $2022,0$ | $377,29$ | $596,71$ | $-219,42$ | $219,42$ | $58,16\%$ |
| 2022-S2 | $2022,5$ | $396,38$ | $546,79$ | $-150,41$ | $150,41$ | $37,95\%$ |
| 2023-S1 | $2023,0$ | $418,17$ | $496,87$ | $-78,70$ | $78,70$ | $18,82\%$ |
| 2023-S2 | $2023,5$ | $406,58$ | $446,94$ | $-40,36$ | $40,36$ | $9,93\%$ |
| 2024-S1 | $2024,0$ | $443,79$ | $397,02$ | $+46,77$ | $46,77$ | $10,54\%$ |
| 2024-S2 | $2024,5$ | $468,08$ | $347,10$ | $+120,98$ | $120,98$ | $25,85\%$ |
| 2025-S1 | $2025,0$ | $610,11$ | $297,17$ | $+312,94$ | $312,94$ | $51,29\%$ |
| 2025-S2 | $2025,5$ | $650,39$ | $247,25$ | $+403,14$ | $403,14$ | $61,98\%$ |
| **2026-S1\***| $2026,0$ | **$677,07$** | **$197,33$** | **$+479,74$** | **$479,74$** | **$70,86\%$** |

#### 12.1.3 MODELO ANUAL COMPLEMENTARIO ($N = 13$ Años)
Utilizado exclusivamente como análisis macro comparativo a nivel anual consolidado:
- Periodo: 2014 a 2026* ($N = 13$).
- **Sumatorias:** $\sum X = 26.260,00$, $\sum Y = 10.293,67$, $SS_{xx} = 182,00$, $SS_{xy} = -16.598,92$.
- **Ecuación Anual:**
  $$\mathbf{Y = -91,2029 \cdot X + 185.021,59}$$
- **Métricas:** $m = -91,20$ acc/año, $b = 185.022$, $R^2 = 0,3547$ (**$35,47\%$**), $S_e = \mathbf{500,35}$ acc., $r = -0,5956$.
- **Consistencia:** Confirma una reducción histórica del orden de $91$ a $100$ accidentes por año, respaldando la solidez de ambos análisis.

#### 12.1.4 Tratamiento de los Datos Parciales de 2026 (2026-S1*)
El periodo 2026 contiene únicamente **5 meses consolidados** (enero a mayo):
- Total eventos acumulados ciudad: **$10.156$ siniestros**.
- Tasa mensual en la ciudad: $\frac{10.156}{5} = \mathbf{2.031,2 \text{ accidentes/mes}}$.
- Tasa promedio por tipología vehicular en el semestre: **$677,07$ acc/categoría**.
- Proyección anualizada estimada: $2.031,2 \times 12 = \mathbf{24.374 \text{ accidentes/año}}$.
- **Advertencia Metodológica:** En todas las gráficas y tablas se encuentra explícitamente etiquetado como `2026*` o `2026-S1*` para recordar al usuario que no corresponde a un periodo anual o semestral cerrado.

---

### 12.2 Interpolación de Lagrange

#### 12.2.1 Fundamento Matemático
A diferencia de la regresión, la interpolación polinómica busca construir un polinomio único $P(x)$ de grado $n \le N-1$ que pase **exactamente** por todos los puntos nodales dados:
$$P(x) = \sum_{i=0}^{n} y_i L_i(x)$$

Donde las bases polinómicas de Lagrange $L_i(x)$ se definen como:
$$L_i(x) = \prod_{\substack{j=0 \\ j \neq i}}^{n} \frac{x - x_j}{x_i - x_j}$$

Cumpliendo la propiedad delta de Kronecker en los nodos:
$$L_i(x_j) = \begin{cases} 1 & \text{si } i = j \\ 0 & \text{si } i \neq j \end{cases} \implies P(x_i) = y_i$$

#### 12.2.2 Nodos Seleccionados (Grado 4 · Polinomio Cuártico)
Para modelar la trayectoria con 5 momentos históricos representativos se seleccionaron:
- Nodo 0: $(x_0 = 2014, y_0 = 1.119,03)$
- Nodo 1: $(x_1 = 2016, y_1 = 2.106,92)$ (Pico histórico nacional)
- Nodo 2: $(x_2 = 2019, y_2 = 430,42)$ (Estabilización pre-pandemia)
- Nodo 3: $(x_3 = 2022, y_3 = 386,83)$ (Reactivación post-pandemia)
- Nodo 4: $(x_4 = 2026, y_4 = 677,07)$ (Periodo parcial actual)

#### 12.2.3 Evaluación en Todos los Años y Fenómeno de Runge
Se evaluó el polinomio $P_4(x)$ sobre los 13 años de la serie temporal:

| Año ($x$) | $Y$ Real Observado | $P_4(x)$ Interpolado | Condición | Error Absoluto ($|Y - P_4|$) | Error Porcentual ($\%$) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **2014** | **$1.119,03$** | **$1.119,03$** | **Nodo 0** | **$0,00$** | **$0,00\%$** |
| 2015 | $1.178,81$ | $2.080,30$ | Intermedio | $901,49$ | $76,47\%$ |
| **2016** | **$2.106,92$** | **$2.106,92$** | **Nodo 1** | **$0,00$** | **$0,00\%$** |
| 2017 | $1.833,67$ | $1.629,53$ | Intermedio | $204,14$ | $11,13\%$ |
| 2018 | $494,06$ | $987,79$ | Intermedio | $493,73$ | $99,93\%$ |
| **2019** | **$430,42$** | **$430,42$** | **Nodo 2** | **$0,00$** | **$0,00\%$** |
| 2020 | $259,98$ | $115,13$ | Intermedio (Covid) | $144,85$ | $55,72\%$ |
| 2021 | $308,31$ | $108,67$ | Intermedio | $199,64$ | $64,75\%$ |
| **2022** | **$386,83$** | **$386,83$** | **Nodo 3** | **$0,00$** | **$0,00\%$** |
| 2023 | $412,38$ | $834,40$ | Intermedio | $422,02$ | **$102,34\%$** |
| 2024 | $455,94$ | $1.245,23$ | Intermedio | $789,29$ | **$173,11\%$** |
| 2025 | $630,25$ | $1.322,15$ | Intermedio | $691,90$ | **$109,78\%$** |
| **2026** | **$677,07$** | **$677,07$** | **Nodo 4** | **$0,00$** | **$0,00\%$** |

> [!WARNING]
> **Lección Epistemológica: El Error Cero en los Nodos no Implica Precisión Global.**  
> - En los 5 nodos, el error es estrictamente $0,00\%$, lo cual es una **propiedad algebraica obligatoria** del método de Lagrange y no una prueba de infalibilidad.
> - En años intermedios no nodales como 2023 (error $102,34\%$) y 2025 (error $109,78\%$), el polinomio experimenta oscilaciones espurias inducidas por la curvatura en los extremos (comportamiento análogo al **fenómeno de Runge**).
> - Por tanto, **Lagrange no es adecuado para extrapolar o pronosticar series con ruido empírico**, validando la superioridad de Mínimos Cuadrados para este fin.

---

### 12.3 Comparación de Métodos Numéricos

| Criterio de Comparación | Regresión Lineal (Mínimos Cuadrados) | Interpolación de Lagrange |
| :--- | :--- | :--- |
| **Propósito Metodológico** | Capturar la **tendencia general** subyacente minimizando el error cuadrático global. | Forzar una función continua que pase **exactamente** por un conjunto discreto de nodos conocidos. |
| **Datos Utilizados** | Todos los datos disponibles ($N = 25$ semestres o $N = 13$ años). | Subconjunto representativo de $k = 5$ nodos seleccionados ($P_4$). |
| **Comportamiento en Nodos** | Rara vez pasa exactamente por un punto ($e_i \ne 0$). | Pasa con precisión absoluta por los nodos ($e_i \equiv 0$). |
| **Comportamiento Intermedio** | Estable, lineal, sin oscilaciones artificiales. | Susceptible a oscilaciones severas de alto orden (efecto tipo Runge). |
| **Capacidad de Pronóstico** | **Apropiada:** Modela tendencias lineales decrecientes a corto plazo. | **Inadecuada:** Tiende a divergir rápidamente al infinito fuera del rango $[x_0, x_n]$. |
| **Tolerancia al Ruido** | Alta: amortigua fluctuaciones estacionales y atípicos. | Nula: cualquier ruido en un nodo distorsiona todo el polinomio. |
| **Veredicto en AutoGest** | **Método Oficial de Predicción y Tendencia.** | **Herramienta Pedagógica de Análisis de Sensibilidad.** |

---

## 13. INTEGRACIÓN DE LOS RESULTADOS EN EL DASHBOARD

Los modelos y análisis calculados en Python fueron trasladados a una arquitectura web orientada a la toma de decisiones.

```
       ARQUITECTURA DEL SISTEMA AUTOGEST WEB (3 CAPAS)
┌──────────────────────────────────────────────────────────┐
│            Frontend · Netlify (deploy/frontend)          │
│     front/index.html · front/metodos.html · Chart.js     │
│     front/api-client.js · Proxy /api/* (netlify.toml)    │
├──────────────────────────────────────────────────────────┤
│      Backend API · Supabase Edge Functions (mineria)     │
│   back/supabase/functions/autogest-api (Deno/TypeScript) │
│   Endpoints: /health, /dashboard, /registros, /predicc.  │
├──────────────────────────────────────────────────────────┤
│     Base de Datos · NeonDB PostgreSQL 18 (us-east-2)     │
│   5 tablas normalizadas (507 reg. integrados + PCA + ML) │
└──────────────────────────────────────────────────────────┘
```

### 13.1 Estructura y Vistas del Dashboard
- **Vista Minería de Datos (`/index.html`):**
  - KPIs principales: Total accidentes, registros integrados ($N=507$ observaciones en 149 periodos cronológicos), mejor modelo clasificador (Árbol y KNN con 83.46% test).
  - Correlaciones de Pearson exactas: Tráfico vs. Accidentes ($r = 0,6683$), Exentos vs. Accidentes ($r = 0,7154$), Taller vs. Costo ($r = 0,9999$).
  - Gráficos de tendencias, distribución por tipología vehicular y análisis de correlación bivariada.
  - Tabla del Torneo de Clasificación (Árbol 83.46% Test / 88.95% Train, KNN escalado 83.46% Test / 91.58% Train, KNN sin escalar 74.02% Test / 84.74% Train, Naive Bayes 59.84% Test / 60.26% Train).
- **Módulo de Métodos Numéricos (`/metodos`):**
  - Panel comparativo: Modelo Oficial Semestral ($N=25$, $m=-99.85$ acc/año equivalente a $-49.92$ acc/semestre, $R^2=37.98\%$, $S_e=479.59$) vs. Modelo Anual Complementario ($N=13$, $m=-91.20$ acc/año, $R^2=35.47\%$, $S_e=500.35$).
  - Gráficos interactivos de dispersión y rectas de regresión MCO.
  - Curva cuártica de Interpolación de Lagrange con resaltado de nodos.
  - Tablas completas con todas las observaciones pre-renderizadas estáticamente en el DOM.
- **Sección Transversal de Conclusiones y Limitaciones:**
  - 5 Conclusiones Ejecutivas y 4 Limitaciones Académicas ubicadas en `<section id="sec-conclusiones">`, visibles permanentemente en cualquier vista del sistema.

### 13.2 Despliegue en Producción (Netlify + Supabase + NeonDB)
- **Frontend (Hosting y CDN):** Netlify (despliegue continuo desde la rama limpia `deploy/frontend`).
- **Backend (API Serverless):** Supabase Edge Functions (proyecto dedicado `mineria` en `us-east-2`, código en rama `deploy/backend`).
- **Base de Datos Relacional:** NeonDB PostgreSQL 18 (proyecto `mineria` en `us-east-2`, conectado vía `@neondatabase/serverless` mediante secreto `NEON_DATABASE_URL`).
- **URL Dashboard Principal:** [https://autogest-ibague.netlify.app/](https://autogest-ibague.netlify.app/)
- **URL Módulo Métodos Numéricos:** [https://autogest-ibague.netlify.app/metodos.html](https://autogest-ibague.netlify.app/metodos.html)
- **URL API Health:** [https://veakptgthvcqyoomwjdv.supabase.co/functions/v1/autogest-api/health](https://veakptgthvcqyoomwjdv.supabase.co/functions/v1/autogest-api/health)
- **Configuración de Proxy y Cabeceras (`front/netlify.toml`):**
  Se estableció `Cache-Control: no-cache, no-store, must-revalidate`, cabeceras de seguridad (`X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`) y un proxy transparente `/api/*` hacia la Edge Function de Supabase para evitar problemas de CORS y garantizar siempre la versión más reciente.

---

## 14. DIFICULTADES Y SOLUCIONES DURANTE EL DESARROLLO

| # | Desafío Técnico o Metodológico | Causa Raíz | Solución Técnica Implementada |
| :---: | :--- | :--- | :--- |
| **1** | Discrepancia en granularidades de las tres fuentes. | Peajes eran mensuales por categoría, taller por orden individual y accidentes por evento puntual. | Agregación relacional mensual estructurada bajo la clave `(AÑO, MES, TIPO_VEHICULO)` mediante `groupby` y `pd.merge`. |
| **2** | Inexistencia de tipología vehicular en el dataset de accidentes. | El registro de policía reporta el total agregado de eventos sin clasificar el automotor. | Implementación de un modelo de asignación proporcional a la exposición al flujo de tráfico carretero. |
| **3** | Secuestro de distancia euclídea ("El Gancho"). | `VOLUMEN_TRAFICO` en órdenes de $10^7$ dominaba el $99,9\%$ de la métrica frente a otras variables. | Comparación sistemática de escaladores y estandarización rigurosa con `StandardScaler` en PCA y Pipelines de KNN y K-Means. |
| **4** | Degradación predictiva de Naive Bayes ($59,84\%$). | Violación del postulado de independencia condicional entre predictores de tráfico y taller. | Documentación formal de la limitación teórica del modelo probabilístico frente a clasificadores discriminativos (Árboles y KNN). |
| **5** | Exigencia docente de mínimo 15 observaciones en regresión. | La serie anual solo disponía de 13 años históricos (2014-2026). | Construcción del modelo oficial semestral con $N = 25$ semestres reales, conservando el modelo anual como complemento macro. |
| **6** | Desfase temporal en el periodo 2026. | Los datos de 2026 solo comprenden enero a mayo (5 meses incompletos). | Anualización de tasas, cálculo mensual proporcional e incorporación del identificador visual obligatorio `2026*` en tablas y gráficos. |
| **7** | Tablas HTML vacías al cargar el dashboard en navegadores lentos. | El DOM dependía exclusivamente del renderizado asíncrono en JavaScript. | Pre-renderizado estático de las 25 filas semestrales y 13 anuales directamente en el código fuente HTML (`<tbody>`). |
| **8** | Desacoplamiento web, caché CDN y validación en navegador. | Mantener copias HTML estáticas sin backend impedía filtrar dinámicamente o persistir cálculos y generaba desincronización. | Migración a arquitectura 3 capas (**Netlify** + **Supabase Edge Functions** + **NeonDB**), configuración sin caché y proxy `/api/*` en `front/netlify.toml`, y auditoría automatizada con Chrome Remote Debugging (CDP) verificando 24/24 gráficas con 0 errores JS. |

---

## 15. RESULTADOS Y HALLAZGOS PRINCIPALES

1. **Matriz de Movilidad Integrada:** Se logró la consolidación exitosa de $507$ observaciones estructuradas en $18$ variables con $100\%$ de completitud y $0\%$ de duplicados a partir de más de $2,7$ millones de registros crudos.
2. **Distribución No Simétrica de la Siniestralidad:** La mediana real de accidentes ($400,00$) dista sustancialmente de la media ($746,02$), evidenciando que el riesgo vial está fuertemente polarizado por picos estacionales de alta movilidad ($36$ periodos críticos $> 2.226$ eventos).
3. **Correlación de Factores Críticos:** Se demostró una asociación lineal positiva significativa entre tráfico carretero y accidentalidad vial ($r = 0,6683$), y aún mayor con vehículos exentos ($r = 0,7154$), mientras que la evasión no muestra vínculo lineal ($r = 0,0353$).
4. **Desempeño de Clasificación:** El Árbol de Decisión podado a 4 niveles y KNN escalado alcanzaron el mejor desempeño de generalización con un **$83,46\%$ de exactitud en pruebas**, superando a Naive Bayes ($59,84\%$).
5. **Efecto Matemático del Escalado:** Se demostró experimentalmente que la estandarización con `StandardScaler` incrementa en **$+9,44\%$** la precisión de KNN al eliminar el sesgo de escala.
6. **Tendencia Histórica Cuantificada:** El modelo oficial semestral de regresión lineal demostró que la tasa de siniestralidad vial en Ibagué presenta una tendencia decreciente sostenida con una pendiente de **$-99,85$ accidentes/año** (equivalente a **$-49,92$ accidentes por semestre**), con un $R^2 = 37,98\%$.
7. **Oscilaciones de Lagrange:** Se comprobó que el polinomio de Lagrange de grado 4 produce errores de hasta $173\%$ en puntos intermedios no nodales debido a fluctuaciones polinómicas, confirmando su inadecuación para pronóstico frente a MCO.

---

## 16. LIMITACIONES DEL ESTUDIO

Para garantizar transparencia y rigor científico, se reconocen las siguientes limitaciones:
1. **Granularidad Temporal y Geográfica:** La integración relacional a nivel mensual y por categoría vehicular enmascara dinámicas horarias críticas (como siniestros nocturnos o de fin de semana).
2. **Naturaleza Parcial de 2026:** El año 2026 cuenta únicamente con registros de enero a mayo (5 meses), por lo que las proyecciones anuales son aproximaciones sujetas a variabilidad estacional del segundo semestre.
3. **Poder Explicativo de la Regresión Lineal ($R^2 \approx 38\%$):** El $62\%$ de la variabilidad de los accidentes obedece a factores externos no presentes en los peajes (clima, embriaguez, estado de las vías, pericia del conductor). Por tanto, la recta describe una **tendencia histórica macro**, no una predicción exacta.
4. **Ausencia de Tipología en Siniestros Originales:** La distribución de accidentes por tipología se basó en un modelo proporcional al flujo vial; aunque matemáticamente consistente, no sustituye al registro policial detallado por tipo de vehículo.
5. **Extrapolación Polinómica:** La interpolación de Lagrange no debe utilizarse para proyectar escenarios futuros más allá de 2026 debido a la divergencia asintótica de los polinomios de orden superior.

---

## 17. CONCLUSIONES

1. **Integración Relacional Exitosa:** Se demostró la viabilidad técnica de unificar tres ecosistemas masivos de datos (accidentalidad, aforo carretero y bitácoras de taller) en una base de conocimiento estructurada y limpia de 507 observaciones, permitiendo análisis multivariados reproducibles.
2. **Importancia Cardinal del Preprocesamiento:** La remoción de caracteres espurios, el tratamiento justificado de outliers y la estandarización mediante `StandardScaler` resultaron determinantes para evitar que algoritmos basados en distancias fueran secuestrados por variables en escalas millonarias.
3. **Aporte del Torneo de Modelos:** El contraste entre clasificadores demostró que en presencia de dependencias lineales y variables en diferentes magnitudes, los Árboles de Decisión y KNN con pipelines escalados son significativamente superiores a clasificadores probabilísticos ingenuos como Naive Bayes.
4. **Complementariedad de Métodos Numéricos:** Mínimos Cuadrados demostró ser la técnica adecuada para identificar la tendencia estructural decreciente de la siniestralidad vial en Ibagué ($-99,85$ acc/año), mientras que Lagrange permitió estudiar las oscilaciones y limitaciones del modelado exacto sobre series con ruido.
5. **Impacto del Despliegue Abierto:** La materialización de los resultados en una plataforma web de 3 capas (**Netlify + Supabase Edge Functions + NeonDB**) de acceso público democratiza el acceso a la analítica de transporte, facilitando la consulta dinámica y la toma de decisiones para concesionarios, aseguradoras y autoridades de movilidad de Ibagué.

---

## 18. TECNOLOGÍAS Y BIBLIOTECAS UTILIZADAS

| Herramienta / Biblioteca | Versión Verificada | Propósito en el Proyecto AutoGest |
| :--- | :---: | :--- |
| **Python** | `3.13.14` | Lenguaje de programación base para todo el pipeline analítico y matemático. |
| **Pandas** | `2.2.3` | Manipulación de datos masivos, limpieza de cadenas, agrupaciones `groupby` y fusiones relacionales `merge`. |
| **NumPy** | `2.1.2` | Operaciones matriciales vectorizadas, cálculo de distancias euclídeas y sumatorias estadísticas. |
| **Scikit-learn** | `1.5.2` | Implementación de `StandardScaler`, `MinMaxScaler`, `RobustScaler`, `KBinsDiscretizer`, `PCA`, `DecisionTreeClassifier`, `GaussianNB`, `KNeighborsClassifier` y `KMeans`. |
| **SciPy** | `1.14.1` | Clustering jerárquico y cálculo de matrices de enlace con método Ward (`scipy.cluster.hierarchy`). |
| **Matplotlib** | `3.9.2` | Generación de la galería de visualizaciones formales del EDA y métricas de modelos a 150 DPI. |
| **Seaborn** | `0.13.2` | Construcción de mapas de calor (heatmaps), curvas KDE y matrices de correlación bivariada. |
| **Jupyter Notebook** | `7.x` | Entorno interactivo para desarrollo, validación y documentación de experimentos (`.ipynb`). |
| **HTML5 / CSS3 / JS ES6** | Estándar W3C | Maquetación web semántica, estilos responsivos y lógica de interacción del dashboard. |
| **Chart.js** | `4.4.1` (CDN) | Motor de renderizado de gráficos estadísticos e interactivos en el frontend. |
| **Netlify** | Git CD (`netlify.toml`) | Hosting global HTTPS, CDN, proxy `/api/*` y despliegue automático del frontend (`deploy/frontend`). |
| **Supabase Edge Functions** | Deno / TypeScript | API REST serverless (`autogest-api`, proyecto `mineria` en `us-east-2`) con validación de parámetros y secretos seguros. |
| **NeonDB (PostgreSQL)** | PostgreSQL `18` | Base de datos relacional serverless (`mineria` en `us-east-2`) para los 507 registros integrados, PCA, métricas ML e historial de predicciones. |
| **Git / GitHub** | `2.4x` | Control de versiones distribuido y trazabilidad de cambios en el código fuente. |

---

## 19. TRAZABILIDAD DE ARCHIVOS Y EVIDENCIAS

| Componente del Pipeline | Archivo de Código Fuente | Cuaderno / Documento Asociado | Figuras / Salidas Generadas |
| :--- | :--- | :--- | :--- |
| **Limpieza de Accidentes** | [src/accidentes.py](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/src/accidentes.py) | [analisis/analisis_datos.ipynb](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/analisis/analisis_datos.ipynb) | `dataset/accidentes_limpio.csv` |
| **Limpieza de Taller** | [src/taller.py](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/src/taller.py) | [analisis/analisis_datos.ipynb](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/analisis/analisis_datos.ipynb) | `dataset/taller_limpio.csv` |
| **Limpieza de Tráfico** | [src/trafico.py](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/src/trafico.py) | [analisis/analisis_datos.ipynb](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/analisis/analisis_datos.ipynb) | `dataset/trafico_limpio.csv` |
| **Integración Relacional** | [src/integracion.py](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/src/integracion.py) | [analisis/analisis_datos.ipynb](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/analisis/analisis_datos.ipynb) | `dataset/dataset_integrado.csv`<br>`dataset/dataset_integrado.xlsx` |
| **Escalamiento y PCA** | [src/transformacion.py](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/src/transformacion.py) | [analisis/transformacion_escalabilidad.ipynb](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/analisis/transformacion_escalabilidad.ipynb) | `dataset/dataset_reducido.csv` |
| **Análisis Exploratorio (EDA)**| [src/eda.py](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/src/eda.py) | [analisis/analisis_exploratorio_eda.ipynb](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/analisis/analisis_exploratorio_eda.ipynb)<br>[analisis/INFORME_LABORATORIO_EDA.md](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/analisis/INFORME_LABORATORIO_EDA.md) | `analisis/figuras/fig_hist_accidentes.png`<br>`analisis/figuras/fig_box_accidentes.png`<br>`analisis/figuras/fig_heatmap_correlaciones.png` |
| **Árbol de Decisión** | [src/arbol_decision.py](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/src/arbol_decision.py) | [analisis/arbol_decision_modelado.ipynb](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/analisis/arbol_decision_modelado.ipynb) | `analisis/figuras/fig_arbol_decision.png`<br>`analisis/figuras/fig_matriz_confusion_arbol.png`<br>`analisis/figuras/fig_importancia_variables_arbol.png` |
| **Clasificación II (KNN & NB)**| [src/clasificacion_modelos.py](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/src/clasificacion_modelos.py) | [analisis/sesion8_naive_bayes_knn.ipynb](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/analisis/sesion8_naive_bayes_knn.ipynb) | `analisis/figuras/fig_torneo_accuracy_comparado.png`<br>`analisis/figuras/fig_knn_efecto_escalado.png`<br>`analisis/figuras/fig_knn_efecto_k.png` |
| **Clustering K-Means / Jerárquico**| [src/clustering.py](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/src/clustering.py) | [analisis/sesion9_clustering_kmeans_jerarquico.ipynb](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/analisis/sesion9_clustering_kmeans_jerarquico.ipynb) | `analisis/figuras/fig_clustering_codo_silueta.png`<br>`analisis/figuras/fig_dendrograma_jerarquico.png`<br>`analisis/figuras/fig_clustering_perfiles.png` |
| **Métodos Numéricos** | [src/metodos_numericos.py](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/src/metodos_numericos.py) | [analisis/metodos_numericos_lagrange_regresion.ipynb](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/analisis/metodos_numericos_lagrange_regresion.ipynb) | `analisis/figuras/fig_regresion_lineal.png`<br>`analisis/figuras/fig_interpolacion_lagrange.png`<br>`analisis/figuras/fig_metodos_numericos_panel.png` |
| **Dashboard y Despliegue (3 Capas)** | [front/index.html](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/front/index.html)<br>[front/metodos.html](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/front/metodos.html)<br>[front/api-client.js](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/front/api-client.js) | [front/netlify.toml](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/front/netlify.toml)<br>[back/supabase/functions/autogest-api/index.ts](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/back/supabase/functions/autogest-api/index.ts)<br>[back/db/schema.sql](file:///c:/Users/Gilary%20Gacha/Desktop/autogest/back/db/schema.sql) | Producción Web en vivo:<br>https://autogest-ibague.netlify.app/<br>https://autogest-ibague.netlify.app/metodos.html<br>https://veakptgthvcqyoomwjdv.supabase.co/functions/v1/autogest-api/health |
