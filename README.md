# 🚗 AutoGest — Sistema Integrador de Minería de Datos (CRISP-DM)

> **Asignatura:** Minería de Datos — 8vo Semestre (UNIMINUTO Ibagué)  
> **Metodología:** CRISP-DM (Sesiones 1 a 4: Comprensión del Negocio, Ingesta Multifuente, Limpieza MAR/IQR y Transformación/PCA)  
> **Volumen de Datos Procesado:** 2,000,000 de registros automotrices + Clima histórico Ibagué (OpenMeteo API)  
---

## 📌 Visión General del Proyecto

**AutoGest** es una plataforma orientada al análisis avanzado de servicios de taller automotriz, auxilio mecánico y mantenimientos preventivos. El proyecto aplica la metodología **CRISP-DM** sobre un dataset de **2,000,000 de registros reales** de reparación y remolque, relacionándolos de forma relacional con la serie temporal meteorológica de la estación Perales en Ibagué (`COM00080214` OpenMeteo) para estudiar el impacto de eventos de clima extremo (>7.5 mm de lluvia) en la demanda de servicios y costos anómalos.

---

## 🛠️ Flujo Metodológico CRISP-DM (Sesiones 1 a 4)

El procesamiento opera bajo una arquitectura basada en archivos ejecutables desacoplada de bases de datos relacionales:

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                          DATOS SUCIOS / RAW                             │
│ ├─ enhanced_motor_vehicle_repair_towing_dataset.csv (2M filas x 28 cols) │
│ ├─ clima_ibague_openmeteo.csv (1,827 días - Perales Ibagué)            │
│ ├─ accidentes_vehiculares.csv.csv (633k filas)                          │
│ └─ trafico_vehicular.csv.csv (149k filas)                               │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    SESIÓN 1: EXPLORACIÓN & CRISP-DM                     │
│  Diagnóstico de 8.85M nulos crudos, detección de columnas vacías        │
│  (Customer Feedback) y truncadas (Service Status). Definición del problema.│
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   SESIÓN 2: INGESTA MULTIFUENTE & JOIN                  │
│  Carga de 4 fuentes heterogéneas. Left Join relacional entre Servicios   │
│  y Clima por fecha (190,414 servicios en días de lluvia extrema).        │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                SESIÓN 3: LIMPIEZA MAR & REGLAS IQR SEGMENTADAS          │
│  • Tratamiento MAR (RNF-03): "No aplica" a 1.71M vacíos de grúa.         │
│  • IQR Segmentado: 14 reglas por tipo de servicio (11,830 outliers).     │
│  • Imputación Mediana/Moda (0 nulos finales).                           │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              SESIÓN 4: TRANSFORMACIÓN, PCA & FEATURE STORE              │
│  • Escalado StandardScaler + One-Hot Encoding (27 cols).                 │
│  • PCA: 4 componentes principales explican el 85.0% de la varianza.     │
│  • Generación de Feature Store: X_features.csv e y_objetivo.csv.        │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Métricas Reales de Ejecución

| Métrica | Valor Real Verificado |
| :--- | :--- |
| **Dimensiones Dataset Crudo** | 2,000,000 filas × 28 columnas |
| **Nulos Totales Crudos** | 8,857,048 nulos |
| **Columnas Irrecuperables Eliminadas** | 2 (`Customer Feedback` 100% nula, `Service Status` corrupta) |
| **Tratamiento MAR (RNF-03) en Grúa** | 1,714,262 nulos etiquetados explícitamente como `"No aplica"` |
| **Duplicados Exactos** | 0 duplicados |
| **Outliers de Costo Detectados (IQR)** | 11,830 registros (0.592%) etiquetados mediante 14 reglas por servicio |
| **Días de Clima Analizados (OpenMeteo)** | 1,827 días (2020-01-01 a 2024-12-31) |
| **Días con Lluvia Extrema (>7.5 mm)** | 174 días en la estación Perales (Ibagué) |
| **Servicios en Días de Lluvia Extrema** | 190,414 servicios automotrices |
| **Reducción de Dimensionalidad PCA** | 4 componentes principales explican el **85.0% de la varianza** |
| **Dimensiones Feature Store Final** | $X$: 2,000,000 filas × 27 columnas \| $y$: 2,000,000 filas (Target 50% pos) |
| **Tiempo de Ejecución del Pipeline** | **151.43 segundos** sobre el total de los 2 millones de registros |

---

## 📂 Estructura del Repositorio

```text
AutoGest/
├── datos_sucios/                          # Datasets crudos (excluidos en .gitignore)
│   ├── enhanced_motor_vehicle_repair_towing_dataset.csv
│   ├── clima_ibague_openmeteo.csv
│   ├── accidentes_vehiculares.csv.csv
│   └── trafico_vehicular.csv.csv
├── data_pipeline/
│   ├── data/
│   │   └── processed/                     # Datasets procesados (excluidos en .gitignore)
│   │       ├── motor_vehicle_limpio_propio.csv
│   │       ├── X_features.csv
│   │       └── y_objetivo.csv
│   ├── outputs/                           # Artefactos de reglas y trazabilidad
│   │   ├── reglas_iqr_servicio.csv
│   │   └── bitacora_limpieza.csv
│   └── scripts/                           # Módulos Python por Sesión CRISP-DM
│       ├── s1_exploracion.py              # Sesión 1: Diagnóstico inicial
│       ├── s2_fuentes.py                  # Sesión 2: Ingesta Multifuente & Join
│       ├── s3_limpieza.py                 # Sesión 3: Limpieza MAR & Reglas IQR
│       └── s4_transformacion.py           # Sesión 4: Escalado, PCA & Feature Store
├── docs/                                  # Documentación técnica por fases
│   ├── REGISTRO_EJECUCION_CRISP_DM.md    # Registro completo de hallazgos y ejecución
│   ├── FASE_1_Planificacion_y_Requisitos.md
│   ├── FASE_2_Arquitectura_e_Infraestructura.md
│   └── FASE_3_Datos_y_Backend_Base.md
├── run_pipeline.py                        # Orquestador maestro ejecutable por CLI
└── README.md
```

---

## ⚡ Guía de Ejecución Rápida

### Prerrequisitos
- Python 3.10+
- Pandas, NumPy, Scikit-learn

### 1. Ejecutar Todo el Pipeline CRISP-DM
Procesa secuencialmente los 2M de datos y genera el reporte completo en terminal:
```bash
python run_pipeline.py
```

### 2. Ejecutar Sesiones Individualmente
```bash
# Sesión 1: Exploración Inicial y Diagnóstico de Calidad
python run_pipeline.py --s1

# Sesión 2: Ingesta Multifuente y Join con Clima
python run_pipeline.py --s2

# Sesión 3: Limpieza MAR y Reglas IQR Segmentadas
python run_pipeline.py --s3

# Sesión 4: Escalado, PCA y Feature Store
python run_pipeline.py --s4
```

---

## 📄 Documentación Adicional

Para consultar el informe técnico detallado sobre los hallazgos y la arquitectura de datos, revisa la carpeta `docs/`:
- 📄 [Registro de Ejecución CRISP-DM (docs/REGISTRO_EJECUCION_CRISP_DM.md)](docs/REGISTRO_EJECUCION_CRISP_DM.md)
- 📄 [Especificación de la Fase 3 (docs/FASE_3_Datos_y_Backend_Base.md)](docs/FASE_3_Datos_y_Backend_Base.md)

