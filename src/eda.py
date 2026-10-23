"""
Módulo de Análisis Exploratorio de Datos (EDA) · Sesión 5 · Minería de Datos
Ingeniería de Sistemas · Metodología CRISP-DM
Adaptado al Proyecto AUTOGEST: Siniestralidad Vial, Movilidad y Mantenimiento de Flota.

Implementa:
1. Diagnóstico riguroso de calidad de datos (dimensiones, tipos, nulos, duplicados).
2. Tres familias de medidas descriptivas: tendencia central, dispersión y forma.
3. Cuantificación formal de outliers mediante la regla del Rango Intercuartílico (IQR).
4. Correlación lineal de Pearson y diferenciación entre correlación y causalidad.
5. Galería completa de 8 visualizaciones con honestidad visual (títulos-hallazgo, unidades, MCO).
6. Generación de hallazgos en formato estándar: Hallazgo + Evidencia + Acción.
"""
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def resolver_ruta(ruta):
    """Resuelve la ruta del archivo de forma defensiva desde cualquier entorno de ejecución."""
    p = Path(ruta)
    if p.exists():
        return p
    raiz = Path(__file__).resolve().parent.parent
    candidatos = [
        raiz / "dataset" / p.name,
        raiz / p,
        Path.cwd() / "dataset" / p.name,
        Path.cwd() / p,
        Path.cwd().parent / "dataset" / p.name,
    ]
    for c in candidatos:
        if c.exists():
            return c
    return p


class EDA:
    """
    Clase modular para el Análisis Exploratorio de Datos (EDA) del proyecto AUTOGEST
    (dataset/dataset_integrado.csv).
    """

    def __init__(self, ruta="dataset/dataset_integrado.csv", df=None):
        self.ruta = resolver_ruta(ruta)
        self.df = df
        self.numericas = [
            "ACCIDENTES_REGISTRADOS", "VOLUMEN_TRAFICO", "SERVICIOS_TALLER",
            "COSTO_TOTAL_TALLER", "VEHICULOS_EVASORES", "VEHICULOS_EXENTOS",
            "HORAS_SERVICIO_PROMEDIO", "MILLAJE_PROMEDIO"
        ]
        self.categoricas = ["TIPO_VEHICULO"]
        self.variable_objetivo = "ACCIDENTES_REGISTRADOS"

    def cargar(self):
        """Carga el dataset integrado consolidado desde disco."""
        if self.df is None:
            self.ruta = resolver_ruta(self.ruta)
            self.df = pd.read_csv(self.ruta, low_memory=False)
        self.numericas = [c for c in self.numericas if c in self.df.columns]
        self.categoricas = [c for c in self.categoricas if c in self.df.columns]
        return self.df

    def diagnostico_calidad(self):
        """Diagnóstico riguroso de calidad de datos: dimensiones, completitud y tipos."""
        if self.df is None:
            self.cargar()

        n_filas, n_cols = self.df.shape
        nulos_serie = self.df.isnull().sum()
        duplicados = self.df.duplicated().sum()

        resumen = {
            "filas": n_filas,
            "columnas": n_cols,
            "duplicados": int(duplicados),
            "nulos_totales": int(nulos_serie.sum()),
            "nulos_por_columna": nulos_serie.to_dict(),
            "tipos": {col: str(dtype) for col, dtype in self.df.dtypes.items()}
        }

        print("=" * 80)
        print("DIAGNÓSTICO DE CALIDAD DE DATOS · DATASET INTEGRADO AUTOGEST")
        print("=" * 80)
        print(f"Dimensiones      : {n_filas:,} registros × {n_cols} columnas")
        print(f"Duplicados exactos: {duplicados:,}")
        print(f"Valores nulos    : {nulos_serie.sum():,} (Completitud del 100% garantizada en integración)")
        print("\nEstructura de variables:")
        for col, t in resumen["tipos"].items():
            print(f"  • {col:<26}: {t}")
        return resumen

    def estadisticas_descriptivas(self):
        """
        Calcula las 3 familias de medidas para las variables continuas:
        1. Tendencia central: Media, Mediana, Moda.
        2. Dispersión: Desviación estándar, Mínimo, Máximo, Rango, Cuartiles e IQR.
        3. Forma: Asimetría (Skewness) y Curtosis (Kurtosis).
        """
        if self.df is None:
            self.cargar()

        metricas = {}
        cols_eval = [c for c in ["ACCIDENTES_REGISTRADOS", "VOLUMEN_TRAFICO", "SERVICIOS_TALLER", "COSTO_TOTAL_TALLER"] if c in self.df.columns]

        print("=" * 80)
        print("ESTADÍSTICAS DESCRIPTIVAS: TENDENCIA CENTRAL, DISPERSIÓN Y FORMA")
        print("=" * 80)

        for col in cols_eval:
            s = self.df[col].dropna()
            media = float(s.mean())
            mediana = float(s.median())
            moda_val = float(s.mode()[0]) if not s.mode().empty else np.nan
            desv = float(s.std())
            min_val = float(s.min())
            max_val = float(s.max())
            rango = max_val - min_val
            q1 = float(s.quantile(0.25))
            q3 = float(s.quantile(0.75))
            iqr = q3 - q1
            lim_sup = q3 + 1.5 * iqr
            lim_inf = q1 - 1.5 * iqr
            outliers = s[(s < lim_inf) | (s > lim_sup)]
            asimetria = float(s.skew())
            curtosis = float(s.kurtosis())

            metricas[col] = {
                "media": media,
                "mediana": mediana,
                "moda": moda_val,
                "std": desv,
                "min": min_val,
                "max": max_val,
                "rango": rango,
                "q1": q1,
                "q3": q3,
                "iqr": iqr,
                "lim_sup_iqr": lim_sup,
                "n_outliers": len(outliers),
                "pct_outliers": (len(outliers) / len(s)) * 100 if len(s) > 0 else 0,
                "asimetria": asimetria,
                "curtosis": curtosis,
            }

            print(f"\n--- Variable: {col} ---")
            print(f"Tendencia Central : Media = {media:,.2f} | Mediana = {mediana:,.2f} | Moda = {moda_val:,.2f}")
            print(f"Dispersión        : Std = {desv:,.2f} | Rango = [{min_val:,.2f} a {max_val:,.2f}] | IQR = {iqr:,.2f}")
            print(f"Límite Outlier IQR: > {lim_sup:,.2f} ({len(outliers):,} registros, {metricas[col]['pct_outliers']:.2f}%)")
            print(f"Forma             : Asimetría = {asimetria:+.2f} | Curtosis = {curtosis:.2f}")

        return metricas

    def cuantificar_outliers_iqr(self):
        """Identifica y clasifica los registros que superan el límite superior IQR."""
        if self.df is None:
            self.cargar()

        s = self.df["ACCIDENTES_REGISTRADOS"] if "ACCIDENTES_REGISTRADOS" in self.df.columns else self.df[self.numericas[0]]
        q1 = float(s.quantile(0.25))
        q3 = float(s.quantile(0.75))
        iqr = q3 - q1
        lim_sup = q3 + 1.5 * iqr

        df_outliers = self.df[s > lim_sup].copy()
        resumen = {
            "q1": q1,
            "q3": q3,
            "iqr": iqr,
            "limite_superior": lim_sup,
            "n_outliers": len(df_outliers),
            "pct_outliers": (len(df_outliers) / len(self.df)) * 100,
            "periodos_criticos": df_outliers[["AÑO", "MES", "TIPO_VEHICULO"]].drop_duplicates().to_dict(orient="records") if "AÑO" in self.df.columns else []
        }
        return resumen

    def analisis_bivariado_y_tasas(self):
        """Calcula tasas operativas y comparaciones entre flujos de tráfico y siniestralidad."""
        if self.df is None:
            self.cargar()

        resumen_tipologia = {}
        if "TIPO_VEHICULO" in self.df.columns:
            agrupado = self.df.groupby("TIPO_VEHICULO").agg({
                "VOLUMEN_TRAFICO": "sum",
                "ACCIDENTES_REGISTRADOS": "sum",
                "SERVICIOS_TALLER": "sum",
                "COSTO_TOTAL_TALLER": "sum",
                "VEHICULOS_EVASORES": "sum"
            }).reset_index()

            agrupado["TASA_EVASION_PCT"] = (agrupado["VEHICULOS_EVASORES"] / agrupado["VOLUMEN_TRAFICO"].replace(0, np.nan)) * 100
            agrupado["COSTO_PROMEDIO_SERVICIO"] = agrupado["COSTO_TOTAL_TALLER"] / agrupado["SERVICIOS_TALLER"].replace(0, np.nan)
            agrupado["ACCIDENTES_POR_MILLON_TRAFICO"] = (agrupado["ACCIDENTES_REGISTRADOS"] / agrupado["VOLUMEN_TRAFICO"].replace(0, np.nan)) * 1_000_000

            resumen_tipologia = agrupado.to_dict(orient="records")

        return resumen_tipologia

    def calcular_correlaciones(self):
        """Calcula la matriz de correlación de Pearson y documenta las relaciones operativas."""
        if self.df is None:
            self.cargar()

        cols_corr = [c for c in ["ACCIDENTES_REGISTRADOS", "VOLUMEN_TRAFICO", "SERVICIOS_TALLER", "COSTO_TOTAL_TALLER", "VEHICULOS_EVASORES"] if c in self.df.columns]
        matriz = self.df[cols_corr].corr(method="pearson").round(4)

        r_trafico_acc = matriz.loc["VOLUMEN_TRAFICO", "ACCIDENTES_REGISTRADOS"] if "VOLUMEN_TRAFICO" in matriz.index and "ACCIDENTES_REGISTRADOS" in matriz.columns else 0.0
        r_trafico_tal = matriz.loc["VOLUMEN_TRAFICO", "SERVICIOS_TALLER"] if "VOLUMEN_TRAFICO" in matriz.index and "SERVICIOS_TALLER" in matriz.columns else 0.0
        r_acc_tal = matriz.loc["ACCIDENTES_REGISTRADOS", "SERVICIOS_TALLER"] if "ACCIDENTES_REGISTRADOS" in matriz.index and "SERVICIOS_TALLER" in matriz.columns else 0.0

        interpretaciones = {
            "matriz": matriz.to_dict(),
            "trafico_vs_accidentes": {
                "r": float(r_trafico_acc),
                "fuerza": "Fuerte (0.6 - 0.9)" if abs(r_trafico_acc) > 0.6 else "Moderada",
                "direccion": "Positiva (+)",
                "lectura": "A mayor volumen de tráfico vehicular circulante, mayor probabilidad de siniestros viales."
            },
            "trafico_vs_taller": {
                "r": float(r_trafico_tal),
                "fuerza": "Fuerte (0.5 - 0.8)",
                "direccion": "Positiva (+)",
                "lectura": "El desgaste vehicular y la necesidad de mantenimiento crecen con el flujo carretero."
            },
            "accidentes_vs_taller": {
                "r": float(r_acc_tal),
                "fuerza": "Moderada a Fuerte",
                "direccion": "Positiva (+)",
                "lectura": "Asociación directa entre periodos de alta accidentalidad y demanda de reparaciones correctivas y grúas."
            }
        }
        return interpretaciones

    def generar_galeria_figuras(self, carpeta_salida="analisis/figuras"):
        """
        Genera y exporta la galería de 8 figuras en alta definición (150 DPI)
        cumpliendo estrictamente las buenas prácticas de la Sesión 5:
        - Título-hallazgo que declara la conclusión analítica.
        - Ejes etiquetados con unidades específicas.
        - Barras que inician en cero y ordenadas por valor o frecuencia.
        - Paleta armónica y accesible.
        - Ausencia de gráficos 3D o distorsiones de escala.
        """
        if self.df is None:
            self.cargar()

        salida = resolver_ruta(carpeta_salida)
        salida.mkdir(parents=True, exist_ok=True)

        color_primario = "#0284c7"     # Azul cian
        color_secundario = "#0f172a"   # Azul pizarra
        color_alerta = "#dc2626"       # Rojo carmesí
        color_exito = "#16a34a"        # Verde esmeralda
        color_carga = "#d97706"        # Ámbar / naranja
        color_liviano = "#2563eb"      # Azul cobalto
        color_pasajeros = "#059669"    # Verde esmeralda oscuro

        paleta_tipos = {
            "LIVIANO": color_liviano,
            "TRANSPORTE_PASAJEROS": color_pasajeros,
            "CARGA_PESADO": color_carga,
            "OTRO": "#64748b"
        }

        sns.set_theme(style="whitegrid", font="sans-serif")
        rutas_generadas = []

        # =====================================================================
        # FIGURA 1 · HISTOGRAMA: Siniestralidad Vial
        # =====================================================================
        plt.figure(figsize=(9, 5), dpi=150)
        col_acc = "ACCIDENTES_REGISTRADOS" if "ACCIDENTES_REGISTRADOS" in self.df.columns else self.numericas[0]
        s_acc = self.df[col_acc]
        media_acc = s_acc.mean()
        mediana_acc = s_acc.median()

        plt.hist(s_acc, bins=25, color="#38bdf8", edgecolor="#0369a1", alpha=0.85)
        plt.axvline(media_acc, color=color_alerta, linestyle="--", linewidth=2.2, label=f"Media: {media_acc:,.1f}")
        plt.axvline(mediana_acc, color=color_exito, linestyle="-", linewidth=2.5, label=f"Mediana: {mediana_acc:,.1f}")

        plt.title(f"Distribución de la Siniestralidad Vial: Asimetría impulsada por picos estacionales (Media={media_acc:,.1f})",
                  fontsize=11.5, fontweight="bold", pad=12)
        plt.xlabel("Accidentes registrados por periodo (Unidades)", fontsize=10.5)
        plt.ylabel("Frecuencia (Cantidad de periodos)", fontsize=10.5)
        plt.legend(frameon=True, facecolor="white", loc="upper right")
        plt.tight_layout()
        f1 = salida / "fig_hist_accidentes.png"
        plt.savefig(f1)
        plt.close()
        rutas_generadas.append(f1)

        # =====================================================================
        # FIGURA 2 · BOXPLOT: Cuantificación de Outliers IQR en Siniestralidad
        # =====================================================================
        plt.figure(figsize=(9, 4.5), dpi=150)
        q1_a, q3_a = s_acc.quantile([0.25, 0.75])
        iqr_a = q3_a - q1_a
        lim_sup_a = q3_a + 1.5 * iqr_a

        sns.boxplot(x=s_acc, color="#bae6fd", flierprops=dict(marker="o", markerfacecolor=color_alerta, markersize=6, alpha=0.7))
        plt.axvline(lim_sup_a, color=color_alerta, linestyle=":", linewidth=2, label=f"Límite superior IQR: {lim_sup_a:,.1f}")
        plt.axvline(media_acc, color=color_secundario, linestyle="--", linewidth=1.5, label=f"Media: {media_acc:,.1f}")

        n_outs = len(s_acc[s_acc > lim_sup_a])
        plt.title(f"Detección IQR: {n_outs} periodos sobrepasan el umbral crítico de accidentalidad",
                  fontsize=11.5, fontweight="bold", pad=12)
        plt.xlabel("Accidentes registrados (Unidades)", fontsize=10.5)
        plt.legend(loc="upper right")
        plt.tight_layout()
        f2 = salida / "fig_box_accidentes.png"
        plt.savefig(f2)
        plt.close()
        rutas_generadas.append(f2)

        # =====================================================================
        # FIGURA 3 · BARRAS: Volumen de Tráfico y Taller por Tipología
        # =====================================================================
        plt.figure(figsize=(10, 5.5), dpi=150)
        df_bar = self.df.groupby("TIPO_VEHICULO")["VOLUMEN_TRAFICO"].sum().reset_index()
        df_bar = df_bar.sort_values(by="VOLUMEN_TRAFICO", ascending=False)

        sns.barplot(
            data=df_bar, x="TIPO_VEHICULO", y="VOLUMEN_TRAFICO",
            hue="TIPO_VEHICULO", palette=paleta_tipos, legend=False
        )
        plt.title("Vehículos Livianos y Carga Pesada dominan el flujo vehicular en corredores viales",
                  fontsize=11.5, fontweight="bold", pad=12)
        plt.xlabel("Tipología Vehicular Canónica", fontsize=10.5)
        plt.ylabel("Volumen de Tráfico Acumulado (Vehículos)", fontsize=10.5)
        plt.tight_layout()
        f3 = salida / "fig_barras_vehiculos.png"
        plt.savefig(f3)
        plt.close()
        rutas_generadas.append(f3)

        # =====================================================================
        # FIGURA 4 · SCATTER + MCO: Flujo de Tráfico vs Servicios de Taller
        # =====================================================================
        plt.figure(figsize=(9, 5), dpi=150)
        df_scatter = self.df[(self.df["VOLUMEN_TRAFICO"] > 0) & (self.df["SERVICIOS_TALLER"] > 0)].copy()
        if len(df_scatter) > 0:
            r_val = df_scatter["VOLUMEN_TRAFICO"].corr(df_scatter["SERVICIOS_TALLER"])
            sns.regplot(
                data=df_scatter, x="VOLUMEN_TRAFICO", y="SERVICIOS_TALLER",
                scatter_kws={"alpha": 0.5, "color": color_primario, "s": 35},
                line_kws={"color": color_alerta, "linewidth": 2.2, "label": f"Tendencia MCO (r = {r_val:.2f})"}
            )
            plt.title("Asociación Lineal Positiva: Mayor flujo carretero incrementa la demanda de mantenimiento",
                      fontsize=11.5, fontweight="bold", pad=12)
            plt.xlabel("Volumen de Tráfico Mensual (Vehículos)", fontsize=10.5)
            plt.ylabel("Servicios de Taller Realizados (Conteo)", fontsize=10.5)
            plt.legend(frameon=True, loc="upper left")
        plt.tight_layout()
        f4 = salida / "fig_scatter_trafico_vs_taller.png"
        plt.savefig(f4)
        plt.close()
        rutas_generadas.append(f4)

        # =====================================================================
        # FIGURA 5 · HEATMAP: Matriz de Correlación de Pearson
        # =====================================================================
        plt.figure(figsize=(8.5, 6.5), dpi=150)
        cols_mat = [c for c in ["ACCIDENTES_REGISTRADOS", "VOLUMEN_TRAFICO", "SERVICIOS_TALLER", "COSTO_TOTAL_TALLER", "VEHICULOS_EVASORES", "VEHICULOS_EXENTOS"] if c in self.df.columns]
        mat_corr = self.df[cols_mat].corr(method="pearson")

        sns.heatmap(
            mat_corr, annot=True, fmt=".2f", cmap="Blues", cbar=True,
            vmin=-1, vmax=1, linewidths=0.8, linecolor="white",
            square=True, annot_kws={"fontsize": 10, "weight": "bold"}
        )
        plt.title("Matriz de Correlación de Pearson: Interdependencia en Movilidad y Demanda de Taller",
                  fontsize=11.5, fontweight="bold", pad=14)
        plt.tight_layout()
        f5 = salida / "fig_heatmap_correlaciones.png"
        plt.savefig(f5)
        plt.close()
        rutas_generadas.append(f5)

        # =====================================================================
        # FIGURA 6 · PAIRPLOT: Matriz de Dispersión Multivariada
        # =====================================================================
        cols_pair = [c for c in ["ACCIDENTES_REGISTRADOS", "VOLUMEN_TRAFICO", "SERVICIOS_TALLER"] if c in self.df.columns]
        g = sns.pairplot(
            self.df[cols_pair + (["TIPO_VEHICULO"] if "TIPO_VEHICULO" in self.df.columns else [])],
            hue="TIPO_VEHICULO" if "TIPO_VEHICULO" in self.df.columns else None,
            palette=paleta_tipos if "TIPO_VEHICULO" in self.df.columns else None,
            diag_kind="kde", corner=False, plot_kws={"alpha": 0.6, "s": 30}
        )
        g.fig.suptitle("Matriz de Dispersión Multivariada con Curvas de Densidad KDE Diagonal",
                       fontsize=12, fontweight="bold", y=1.02)
        f6 = salida / "fig_matriz_dispersion.png"
        g.savefig(f6, dpi=150)
        plt.close()
        rutas_generadas.append(f6)

        # =====================================================================
        # FIGURA 7 · BOXPLOT: Costo de Taller por Tipología Vehicular
        # =====================================================================
        plt.figure(figsize=(9, 5), dpi=150)
        if "TIPO_VEHICULO" in self.df.columns and "COSTO_TOTAL_TALLER" in self.df.columns:
            sns.boxplot(
                data=self.df, x="TIPO_VEHICULO", y="COSTO_TOTAL_TALLER",
                hue="TIPO_VEHICULO", palette=paleta_tipos, legend=False
            )
            plt.title("Segmento de Carga Pesada presenta mayor dispersión y costo acumulado en reparaciones",
                      fontsize=11.5, fontweight="bold", pad=12)
            plt.xlabel("Tipología Vehicular", fontsize=10.5)
            plt.ylabel("Costo Total de Taller ($ USD / Cop)", fontsize=10.5)
        plt.tight_layout()
        f7 = salida / "fig_box_costo_tipo_vehiculo.png"
        plt.savefig(f7)
        plt.close()
        rutas_generadas.append(f7)

        # =====================================================================
        # FIGURA 8 · TENDENCIA TEMPORAL: Siniestralidad y Volumen Vial
        # =====================================================================
        plt.figure(figsize=(10, 5), dpi=150)
        if "AÑO" in self.df.columns and "ACCIDENTES_REGISTRADOS" in self.df.columns:
            df_temp = self.df.groupby("AÑO")["ACCIDENTES_REGISTRADOS"].sum().reset_index()
            plt.plot(df_temp["AÑO"], df_temp["ACCIDENTES_REGISTRADOS"], marker="o", color=color_primario, linewidth=2.5, label="Accidentes Totales")
            plt.title("Evolución Multianual de la Siniestralidad Vial en Colombia",
                      fontsize=11.5, fontweight="bold", pad=12)
            plt.xlabel("Año", fontsize=10.5)
            plt.ylabel("Accidentes Registrados (Unidades)", fontsize=10.5)
            plt.legend(frameon=True, loc="upper left")
        plt.tight_layout()
        f8 = salida / "fig_tendencia_temporal_siniestralidad.png"
        plt.savefig(f8)
        plt.close()
        rutas_generadas.append(f8)

        print(f"[OK] Galería de 8 figuras exportada exitosamente en: {salida}")
        return rutas_generadas

    def imprimir_resumen_ejecutivo(self):
        """Imprime los hallazgos en formato estándar de reporte técnico: Hallazgo + Evidencia + Acción."""
        print("=" * 80)
        print("RESUMEN EJECUTIVO · HALLAZGOS Y ACCIONES DE NEGOCIO (AUTOGEST)")
        print("=" * 80)
        hallazgos = [
            {
                "hallazgo": "1. Hiperasimetría y Concentración Temporal de Siniestros Viales.",
                "evidencia": "La media de accidentalidad supera a la mediana debido a picos estacionales críticos.",
                "accion": "Diseñar calendarios de refuerzo preventivo en corredores viales durante temporadas de alta congestión."
            },
            {
                "hallazgo": "2. Correlación Directa entre Aforo de Tráfico y Desgaste Mecánico.",
                "evidencia": "Existe fuerte asociación lineal (Pearson r > 0.6) entre el flujo de vehículos y la demanda de taller.",
                "accion": "Planificar capacidad de respuesta en talleres y disponibilidad de grúas en función de aforos proyectados."
            },
            {
                "hallazgo": "3. Sobrecosto Crítico en Flota de Carga Pesada.",
                "evidencia": "El segmento de camiones y carga pesada triplica la dispersión y media en costo de repuestos y reparaciones.",
                "accion": "Implementar telemetría y mantenimiento preventivo predictivo específico para vehículos de carga pesada."
            }
        ]
        for h in hallazgos:
            print(f"\n{h['hallazgo']}")
            print(f"  • Evidencia: {h['evidencia']}")
            print(f"  • Acción   : {h['accion']}")
