"""
clustering.py
=============
Sesión 9 · Clustering: K-means y Clustering Jerárquico
Minería de Datos · UNIMINUTO Ibagué · 2026-2
Docente: Esteban Ernesto Morales Castro

Implementa sobre el dataset AUTOGEST (siniestralidad vial de Ibagué):
  - Búsqueda del k óptimo: método del codo (inercia) + coeficiente de silueta
  - K-means con StandardScaler + perfilamiento con groupby
  - Nomenclatura comercial de segmentos y campañas de retención
  - Clustering jerárquico (linkage ward) + dendrograma sobre muestra
  - Generación de figuras diagnósticas (150 DPI) listas para el Avance 2

Principios pedagógicos aplicados:
  • "Siempre escalar antes de KMeans" (misma regla que KNN, Sesión 8).
  • Los centroides en km.cluster_centers_ están estandarizados:
    para narrar se usan las medias REALES del groupby sobre datos originales.
  • La variable objetivo (ACCIDENTES_REGISTRADOS) NO entra en X:
    se usa solo DESPUÉS para perfilar los grupos (evitar contaminación).
  • K-means SIEMPRE produce grupos; el juicio humano decide si son útiles.

Uso rápido
----------
>>> from src.clustering import Clustering
>>> cl = Clustering()
>>> cl.cargar()
>>> cl.buscar_k(k_min=2, k_max=8)   # método del codo + silueta
>>> cl.ajustar(k=3)                  # modelo final
>>> cl.perfilar()                    # groupby con medias reales + tasa obj
>>> cl.nombrar_segmentos({0: "Período habitual", 1: "Período crítico alto",
...                       2: "Período de baja actividad"})
>>> cl.dendrograma(n_muestra=60)
>>> cl.generar_figuras()
"""

from pathlib import Path
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

warnings.filterwarnings("ignore")

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from scipy.cluster.hierarchy import dendrogram, linkage

from src.transformacion import Transformacion, resolver_ruta


# ──────────────────────────────────────────────────────────────────────────────
# Clase principal
# ──────────────────────────────────────────────────────────────────────────────

class Clustering:
    """
    Segmentación no supervisada del dataset AUTOGEST con K-means y jerárquico.

    La variable objetivo ACCIDENTES_REGISTRADOS no entra en X durante el
    clustering: se usa únicamente para enriquecer el perfil de cada segmento
    (tasa de siniestralidad) después de ajustar el modelo.

    Atributos principales
    ---------------------
    df          : DataFrame original cargado.
    X_scaled    : Matriz escalada (StandardScaler) usada por KMeans.
    km          : Objeto KMeans ajustado (None hasta llamar ajustar()).
    df_perfil   : DataFrame de perfiles por clúster (None hasta perfilar()).
    nombres_seg : dict {cluster_id: nombre_comercial}.
    """

    # Variables de comportamiento del proyecto AUTOGEST
    # (excluye el objetivo y columnas de identificación)
    VARIABLES_CLUSTERING: list[str] = [
        "VOLUMEN_TRAFICO",
        "VEHICULOS_EVASORES",
        "VEHICULOS_EXENTOS",
        "SERVICIOS_TALLER",
        "COSTO_TOTAL_TALLER",
        "MILLAJE_PROMEDIO",
    ]
    OBJETIVO: str = "ACCIDENTES_REGISTRADOS"
    CATEGORICA: str = "TIPO_VEHICULO"

    def __init__(self, ruta: str = "dataset/dataset_integrado.csv", df=None):
        self.ruta = resolver_ruta(ruta)
        self.df = df
        self.trans = None

        # Estado interno
        self._vars: list[str] = []          # variables efectivamente usadas
        self.scaler: StandardScaler | None = None
        self.X_scaled: np.ndarray | None = None
        self.km: KMeans | None = None
        self.k_elegido: int | None = None
        self.df_perfil: pd.DataFrame | None = None
        self.nombres_seg: dict[int, str] = {}

        # Tabla de búsqueda de k
        self._tabla_k: pd.DataFrame | None = None

    # ──────────────────────────────────────────────────────────────────────────
    # 1. Carga y preparación
    # ──────────────────────────────────────────────────────────────────────────

    def cargar(self) -> pd.DataFrame:
        """Carga el dataset AUTOGEST (delega en Transformacion)."""
        if self.df is None:
            self.trans = Transformacion(self.ruta)
            self.df = self.trans.cargar()
        else:
            self.trans = Transformacion(df=self.df)
            self.trans.cargar()

        # Ajusta la lista de variables al dataset real
        self._vars = [c for c in self.VARIABLES_CLUSTERING if c in self.df.columns]
        return self.df

    def preparar_x(self) -> np.ndarray:
        """
        Escala las variables de comportamiento con StandardScaler.

        Solo variables de comportamiento entran en X (sin ACCIDENTES ni IDs).
        El scaler se ajusta aquí y se reutiliza en ajustar() y dendrograma().

        Retorna
        -------
        np.ndarray : matriz escalada (n_muestras × n_variables).
        """
        if self.df is None:
            self.cargar()

        X_raw = self.df[self._vars].copy()
        self.scaler = StandardScaler()
        self.X_scaled = self.scaler.fit_transform(X_raw)
        return self.X_scaled

    # ──────────────────────────────────────────────────────────────────────────
    # 2. Búsqueda del k óptimo (Código 1 de la demo)
    # ──────────────────────────────────────────────────────────────────────────

    def buscar_k(
        self,
        k_min: int = 2,
        k_max: int = 8,
        n_init: int = 10,
        random_state: int = 42,
        verbose: bool = True,
    ) -> pd.DataFrame:
        """
        Calcula inercia y coeficiente de silueta para k ∈ [k_min, k_max].

        Reproduce el Código 1 de la demo guiada (diapositiva 11):
          - Inercia: suma de distancias al cuadrado a su centroide (menos = mejor).
          - Silueta: cohesión interna vs separación inter-clúster (-1 a +1).

        Parámetros
        ----------
        k_min, k_max : int
            Rango de valores de k a explorar.
        n_init : int
            Intentos de inicialización de KMeans (conserva el mejor).
        random_state : int
            Semilla de aleatoriedad (42 en toda la asignatura).
        verbose : bool
            Imprime la tabla estilo presentación.

        Retorna
        -------
        pd.DataFrame con columnas: k, inercia, silueta, Lectura.
        """
        if self.X_scaled is None:
            self.preparar_x()

        filas: list[dict] = []

        if verbose:
            print(f"\n{'─'*62}")
            print(f"{'BÚSQUEDA DEL K ÓPTIMO · AUTOGEST · Sesión 9':^62}")
            print(f"{'─'*62}")
            print(f"{'k':>4}  {'inercia':>12}  {'silueta':>8}  Lectura")
            print(f"{'─'*62}")

        for k in range(k_min, k_max + 1):
            km_tmp = KMeans(n_clusters=k, n_init=n_init, random_state=random_state)
            etiquetas = km_tmp.fit_predict(self.X_scaled)
            inercia   = km_tmp.inertia_
            silueta   = silhouette_score(self.X_scaled, etiquetas)

            # Lectura automática
            if k == k_min:
                lectura = "Referencia mínima de k"
            elif silueta == max(
                [silhouette_score(
                    self.X_scaled,
                    KMeans(n_clusters=kk, n_init=n_init,
                           random_state=random_state).fit_predict(self.X_scaled)
                ) for kk in range(k_min, k_max + 1)]
            ):
                lectura = "← MÁXIMA silueta"
            else:
                lectura = ""

            filas.append({
                "k":       k,
                "inercia": round(inercia, 1),
                "silueta": round(silueta, 4),
                "Lectura": lectura,
            })
            if verbose:
                print(f"{k:>4}  {inercia:>12.1f}  {silueta:>8.3f}  {lectura}")

        if verbose:
            print(f"{'─'*62}\n")

        self._tabla_k = pd.DataFrame(filas)

        # Marcar la silueta máxima en la tabla
        idx_max_sil = self._tabla_k["silueta"].idxmax()
        self._tabla_k.loc[idx_max_sil, "Lectura"] = "← MÁXIMA silueta"

        return self._tabla_k

    # ──────────────────────────────────────────────────────────────────────────
    # 3. Modelo K-means final (Código 2 de la demo, parte 1)
    # ──────────────────────────────────────────────────────────────────────────

    def ajustar(
        self,
        k: int = 3,
        n_init: int = 10,
        random_state: int = 42,
    ) -> "Clustering":
        """
        Ajusta KMeans con el k elegido y agrega la columna 'cluster' al df.

        Parámetros
        ----------
        k : int
            Número de clústeres (elegido con codo + silueta + viabilidad comercial).
        n_init : int
            Intentos de inicialización (10 en la asignatura).
        random_state : int
            Semilla (42).

        Retorna
        -------
        self (para encadenamiento: cl.ajustar(3).perfilar()).
        """
        if self.X_scaled is None:
            self.preparar_x()

        self.k_elegido = k
        self.km = KMeans(n_clusters=k, n_init=n_init, random_state=random_state)
        self.df["cluster"] = self.km.fit_predict(self.X_scaled)

        print(f"\n── KMeans ajustado con k={k} ──────────────────────────")
        conteo = self.df["cluster"].value_counts().sort_index()
        for cid, n in conteo.items():
            print(f"  Clúster {cid}: {n:>5} observaciones ({n/len(self.df)*100:.1f}%)")
        print(f"  Inercia total: {self.km.inertia_:.1f}")
        sil = silhouette_score(self.X_scaled, self.df["cluster"])
        print(f"  Silueta global: {sil:.4f}")
        print("─" * 56)

        return self

    # ──────────────────────────────────────────────────────────────────────────
    # 4. Perfilamiento con groupby (Código 2 de la demo, parte 2)
    # ──────────────────────────────────────────────────────────────────────────

    def perfilar(self, incluir_objetivo: bool = True) -> pd.DataFrame:
        """
        Calcula el perfil de cada clúster con medias REALES (escala original).

        Parámetros
        ----------
        incluir_objetivo : bool
            Si True, incluye la media de ACCIDENTES_REGISTRADOS por clúster.

        Retorna
        -------
        pd.DataFrame con una fila por clúster y columnas de comportamiento.
        """
        if self.km is None:
            raise RuntimeError("Llame ajustar() antes de perfilar().")

        cols_perfil = self._vars[:]
        if incluir_objetivo and self.OBJETIVO in self.df.columns:
            cols_perfil.append(self.OBJETIVO)

        perfil = self.df.groupby("cluster")[cols_perfil].mean().round(2)

        # Añadir conteo y porcentaje
        conteo = self.df["cluster"].value_counts().sort_index()
        perfil.insert(0, "n_obs",   conteo)
        perfil.insert(1, "pct_obs", (conteo / len(self.df) * 100).round(1))

        self.df_perfil = perfil
        return perfil

    # ──────────────────────────────────────────────────────────────────────────
    # 5. Nomenclatura comercial de segmentos
    # ──────────────────────────────────────────────────────────────────────────

    def nombrar_segmentos(
        self,
        nombres: dict[int, str] | None = None,
        campanas: dict[int, str] | None = None,
    ) -> pd.DataFrame:
        """
        Asigna nombres comerciales a cada clúster y genera una columna
        'segmento' en self.df con la etiqueta de cada fila.

        Si no se proveen nombres, se generan automáticamente basados en el
        nivel de ACCIDENTES_REGISTRADOS del perfil.

        Parámetros
        ----------
        nombres : dict {cluster_id: nombre_string}
            Nombres comerciales para cada segmento.
        campanas : dict {cluster_id: accion_string}
            Acciones de retención / intervención por segmento.

        Retorna
        -------
        pd.DataFrame con columnas: cluster, nombre, n_obs, pct_obs, campaña.
        """
        if self.df_perfil is None:
            self.perfilar()

        # Generación automática de nombres si no se proveen
        if nombres is None:
            # Ordena por nivel de accidentes
            if self.OBJETIVO in self.df_perfil.columns:
                orden = self.df_perfil[self.OBJETIVO].rank(method="first").astype(int)
                etiquetas = {
                    cid: f"Segmento_Nivel{orden[cid]}" for cid in self.df_perfil.index
                }
            else:
                etiquetas = {
                    cid: f"Segmento_{cid}" for cid in self.df_perfil.index
                }
            nombres = etiquetas

        self.nombres_seg = nombres
        self.df["segmento"] = self.df["cluster"].map(nombres)

        # Campañas por defecto si no se proveen
        if campanas is None:
            campanas = {cid: "— campaña por definir —" for cid in nombres}

        # Tabla resumen
        filas = []
        for cid, nombre in sorted(nombres.items()):
            fila = {
                "cluster":  cid,
                "nombre":   nombre,
                "n_obs":    int(self.df_perfil.loc[cid, "n_obs"])
                            if cid in self.df_perfil.index else 0,
                "pct_obs":  float(self.df_perfil.loc[cid, "pct_obs"])
                            if cid in self.df_perfil.index else 0.0,
                "campaña":  campanas.get(cid, "—"),
            }
            filas.append(fila)

        df_nombres = pd.DataFrame(filas)

        print("\n── Segmentos nombrados ─────────────────────────────────")
        for _, row in df_nombres.iterrows():
            print(f"  [{row['cluster']}] {row['nombre']}"
                  f" · {row['n_obs']} obs ({row['pct_obs']}%)")
            print(f"       Campaña: {row['campaña']}")
        print("─" * 56)

        return df_nombres

    # ──────────────────────────────────────────────────────────────────────────
    # 6. Clustering jerárquico y dendrograma (Código 3 de la demo)
    # ──────────────────────────────────────────────────────────────────────────

    def dendrograma(
        self,
        n_muestra: int = 60,
        random_state: int = 42,
        carpeta_salida: str = "analisis/figuras",
        verbose: bool = True,
    ) -> str:
        """
        Genera un dendrograma jerárquico (linkage ward) sobre una muestra
        de n_muestra filas del dataset escalado.

        El uso de muestra es la práctica estándar con bases grandes:
        la complejidad O(n²) del clustering jerárquico lo vuelve impracticable
        sobre decenas de miles de filas.

        Parámetros
        ----------
        n_muestra : int
            Tamaño de la muestra (default 60, igual que la demo de la sesión).
        random_state : int
            Semilla para la muestra aleatoria.
        carpeta_salida : str
            Directorio donde se guarda el PNG.
        verbose : bool
            Imprime información de fusiones si True.

        Retorna
        -------
        str : ruta absoluta del PNG generado.
        """
        if self.X_scaled is None:
            self.preparar_x()

        carpeta = resolver_ruta(carpeta_salida)
        carpeta.mkdir(parents=True, exist_ok=True)

        # Muestra aleatoria estratificada
        muestra_idx = (
            self.df[self._vars]
            .sample(n=min(n_muestra, len(self.df)), random_state=random_state)
            .index
        )
        X_muestra = self.scaler.transform(self.df.loc[muestra_idx, self._vars])

        # Linkage ward
        Z = linkage(X_muestra, method="ward")

        if verbose:
            print(f"\n── Dendrograma jerárquico (ward) · muestra n={len(muestra_idx)} ──")
            print(f"  Primeras 5 fusiones (distancia): {Z[:5, 2].round(2).tolist()}")
            print(f"  Última fusión (distancia total): {Z[-1, 2]:.2f}")
            if self.k_elegido:
                print(
                    f"  Una línea horizontal a ~{Z[-self.k_elegido, 2]:.1f} "
                    f"cruzaría {self.k_elegido} ramas → coherente con k={self.k_elegido}"
                )
            print("─" * 56)

        # Figura
        fig, ax = plt.subplots(figsize=(14, 6), dpi=150)
        dendrogram(
            Z,
            ax=ax,
            leaf_rotation=90,
            leaf_font_size=7,
            color_threshold=0.7 * max(Z[:, 2]),
        )
        # Línea de corte sugerida
        if self.k_elegido and self.k_elegido >= 2:
            corte = Z[-self.k_elegido, 2]
            ax.axhline(
                y=corte, color="#dc2626", linestyle="--", linewidth=1.5,
                label=f"Corte sugerido k={self.k_elegido} (dist ≈ {corte:.1f})"
            )
            ax.legend(fontsize=9)

        ax.set_title(
            f"Dendrograma Jerárquico (Ward) · Muestra n={len(muestra_idx)}\n"
            f"AUTOGEST · Sesión 9 · Variables: {', '.join(self._vars[:4])}...",
            fontsize=11, fontweight="bold",
        )
        ax.set_xlabel("Índice de observación en la muestra", fontsize=10)
        ax.set_ylabel("Distancia de fusión (Ward)", fontsize=10)

        fig.tight_layout()
        ruta_png = carpeta / "fig_dendrograma_jerarquico.png"
        fig.savefig(ruta_png, bbox_inches="tight")
        plt.close(fig)
        print(f"[OK] {ruta_png.name}")

        return str(ruta_png)

    # ──────────────────────────────────────────────────────────────────────────
    # 7. Generación completa de figuras
    # ──────────────────────────────────────────────────────────────────────────

    def generar_figuras(
        self,
        carpeta_salida: str = "analisis/figuras",
    ) -> dict[str, str]:
        """
        Genera y exporta en alta resolución (150 DPI) las figuras del clustering:

        1. fig_clustering_codo_silueta.png
           Panel doble: curva de inercia (codo) + curva de silueta.

        2. fig_clustering_scatter_pca.png
           Dispersión de los clústeres proyectados en 2 componentes PCA.

        3. fig_clustering_perfiles.png
           Mapa de calor (heatmap) de los centroides en escala original.

        4. fig_clustering_barras_perfil.png
           Barras comparativas de cada variable por segmento.

        5. fig_dendrograma_jerarquico.png
           Dendrograma jerárquico sobre muestra de 60 filas.

        Retorna
        -------
        dict {nombre_figura: ruta_absoluta}.
        """
        if self.km is None:
            raise RuntimeError("Llame ajustar() antes de generar_figuras().")
        if self.df_perfil is None:
            self.perfilar()
        if self._tabla_k is None:
            self.buscar_k(verbose=False)

        carpeta = resolver_ruta(carpeta_salida)
        carpeta.mkdir(parents=True, exist_ok=True)
        rutas: dict[str, str] = {}

        palette = sns.color_palette("Set2", self.k_elegido)

        # ── FIGURA 1: Codo + Silueta ──────────────────────────────────────────
        fig1, (ax1a, ax1b) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=150)

        ax1a.plot(self._tabla_k["k"], self._tabla_k["inercia"],
                  "o-", color="#1d4ed8", linewidth=2.5, markersize=8)
        if self.k_elegido:
            row = self._tabla_k[self._tabla_k["k"] == self.k_elegido]
            if not row.empty:
                ax1a.scatter([self.k_elegido], [row["inercia"].values[0]],
                             color="#dc2626", s=120, zorder=5,
                             label=f"k elegido = {self.k_elegido}")
                ax1a.axvline(self.k_elegido, color="#dc2626",
                             linestyle="--", linewidth=1.2)
                ax1a.legend(fontsize=9)
        ax1a.set_xlabel("Número de clústeres (k)", fontsize=11, fontweight="bold")
        ax1a.set_ylabel("Inercia (WCSS)", fontsize=11, fontweight="bold")
        ax1a.set_title("Método del Codo · Inercia vs k\nBuscar el \"doblez\" de la curva",
                        fontsize=11, fontweight="bold")
        ax1a.set_xticks(self._tabla_k["k"])

        ax1b.plot(self._tabla_k["k"], self._tabla_k["silueta"],
                  "s-", color="#059669", linewidth=2.5, markersize=8)
        idx_max = self._tabla_k["silueta"].idxmax()
        k_max_sil = self._tabla_k.loc[idx_max, "k"]
        sil_max   = self._tabla_k.loc[idx_max, "silueta"]
        ax1b.scatter([k_max_sil], [sil_max], color="#dc2626", s=120, zorder=5,
                     label=f"Máx silueta k={k_max_sil} ({sil_max:.3f})")
        ax1b.axvline(k_max_sil, color="#dc2626", linestyle="--", linewidth=1.2)
        ax1b.set_xlabel("Número de clústeres (k)", fontsize=11, fontweight="bold")
        ax1b.set_ylabel("Coeficiente de Silueta", fontsize=11, fontweight="bold")
        ax1b.set_title("Coeficiente de Silueta vs k\nMáximo = mejor cohesión/separación",
                        fontsize=11, fontweight="bold")
        ax1b.set_xticks(self._tabla_k["k"])
        ax1b.legend(fontsize=9)

        fig1.suptitle(
            "Selección de k · Clustering AUTOGEST · Sesión 9\n"
            "Método del Codo (inercia) + Coeficiente de Silueta",
            fontsize=12, fontweight="bold",
        )
        fig1.tight_layout()
        ruta_f1 = carpeta / "fig_clustering_codo_silueta.png"
        fig1.savefig(ruta_f1, bbox_inches="tight")
        plt.close(fig1)
        rutas["fig_codo_silueta"] = str(ruta_f1)
        print(f"[OK] {ruta_f1.name}")

        # ── FIGURA 2: Scatter PCA ─────────────────────────────────────────────
        pca = PCA(n_components=2, random_state=42)
        X_pca = pca.fit_transform(self.X_scaled)
        clusters = self.df["cluster"].values

        fig2, ax2 = plt.subplots(figsize=(9, 6.5), dpi=150)
        for cid in range(self.k_elegido):
            mask = clusters == cid
            nombre = self.nombres_seg.get(cid, f"Clúster {cid}")
            color  = palette[cid]
            ax2.scatter(
                X_pca[mask, 0], X_pca[mask, 1],
                c=[color], alpha=0.55, s=35, label=nombre, edgecolors="none",
            )
        # Centroides en espacio PCA
        centroides_pca = pca.transform(self.km.cluster_centers_)
        for cid, (cx, cy) in enumerate(centroides_pca):
            nombre = self.nombres_seg.get(cid, f"C{cid}")
            ax2.scatter(cx, cy, c=[palette[cid]], s=250, marker="*",
                        edgecolors="black", linewidths=1, zorder=5)
            ax2.annotate(
                nombre, (cx, cy),
                textcoords="offset points", xytext=(8, 6),
                fontsize=8.5, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.25", fc="white", alpha=0.75),
            )

        var_exp = pca.explained_variance_ratio_ * 100
        ax2.set_xlabel(f"PC1 ({var_exp[0]:.1f}% var. explicada)", fontsize=10, fontweight="bold")
        ax2.set_ylabel(f"PC2 ({var_exp[1]:.1f}% var. explicada)", fontsize=10, fontweight="bold")
        ax2.set_title(
            f"Clústeres K-means proyectados en 2 Componentes PCA\n"
            f"AUTOGEST · Sesión 9 · k={self.k_elegido} · "
            f"Varianza total explicada: {sum(var_exp):.1f}%",
            fontsize=11, fontweight="bold",
        )
        ax2.legend(title="Segmento", fontsize=9, title_fontsize=9)
        fig2.tight_layout()
        ruta_f2 = carpeta / "fig_clustering_scatter_pca.png"
        fig2.savefig(ruta_f2, bbox_inches="tight")
        plt.close(fig2)
        rutas["fig_scatter_pca"] = str(ruta_f2)
        print(f"[OK] {ruta_f2.name}")

        # ── FIGURA 3: Heatmap de perfiles ─────────────────────────────────────
        cols_heat = [c for c in self._vars if c in self.df_perfil.columns]
        df_heat = self.df_perfil[cols_heat].copy()

        # Normalizar cada columna a [0,1] para comparar variables de distinta escala
        df_heat_norm = (df_heat - df_heat.min()) / (df_heat.max() - df_heat.min() + 1e-9)
        df_heat_norm.index = [
            self.nombres_seg.get(i, f"Clúster {i}") for i in df_heat_norm.index
        ]

        fig3, ax3 = plt.subplots(figsize=(11, 4 + self.k_elegido * 0.5), dpi=150)
        sns.heatmap(
            df_heat_norm,
            annot=df_heat.round(1),
            fmt=".1f",
            cmap="YlOrRd",
            ax=ax3,
            linewidths=0.5,
            linecolor="#e2e8f0",
            cbar_kws={"label": "Valor normalizado [0–1]"},
        )
        ax3.set_title(
            "Perfil de Clústeres · Medias Reales (escala original)\n"
            f"AUTOGEST · Sesión 9 · k={self.k_elegido} · Mapa de calor normalizado",
            fontsize=11, fontweight="bold",
        )
        ax3.set_xlabel("Variable de comportamiento", fontsize=10, fontweight="bold")
        ax3.set_ylabel("Segmento", fontsize=10, fontweight="bold")
        ax3.tick_params(axis="x", rotation=30, labelsize=9)
        ax3.tick_params(axis="y", rotation=0,  labelsize=9)
        fig3.tight_layout()
        ruta_f3 = carpeta / "fig_clustering_perfiles.png"
        fig3.savefig(ruta_f3, bbox_inches="tight")
        plt.close(fig3)
        rutas["fig_perfiles"] = str(ruta_f3)
        print(f"[OK] {ruta_f3.name}")

        # ── FIGURA 4: Barras comparativas por variable ────────────────────────
        n_vars = len(cols_heat)
        n_cols = 3
        n_rows = (n_vars + n_cols - 1) // n_cols
        fig4, axes4 = plt.subplots(n_rows, n_cols,
                                    figsize=(14, 4 * n_rows), dpi=150)
        axes4_flat = axes4.flatten() if n_rows > 1 else [axes4] if n_cols == 1 else axes4.flatten()

        for i, var in enumerate(cols_heat):
            ax = axes4_flat[i]
            valores = self.df_perfil[var].values
            etiquetas_seg = [
                self.nombres_seg.get(cid, f"C{cid}")
                for cid in self.df_perfil.index
            ]
            barras = ax.bar(
                etiquetas_seg, valores,
                color=palette[:self.k_elegido],
                edgecolor="black", linewidth=0.6,
            )
            ax.set_title(var, fontsize=10, fontweight="bold")
            ax.tick_params(axis="x", rotation=20, labelsize=8)
            ax.set_ylabel("Media", fontsize=9)
            for b, v in zip(barras, valores):
                ax.text(b.get_x() + b.get_width()/2, v * 1.01,
                        f"{v:,.1f}", ha="center", fontsize=8)

        # Ocultar ejes sobrantes
        for j in range(i + 1, len(axes4_flat)):
            axes4_flat[j].set_visible(False)

        fig4.suptitle(
            f"Comparación de Variables por Segmento · AUTOGEST · Sesión 9 · k={self.k_elegido}",
            fontsize=12, fontweight="bold",
        )
        fig4.tight_layout()
        ruta_f4 = carpeta / "fig_clustering_barras_perfil.png"
        fig4.savefig(ruta_f4, bbox_inches="tight")
        plt.close(fig4)
        rutas["fig_barras_perfil"] = str(ruta_f4)
        print(f"[OK] {ruta_f4.name}")

        # ── FIGURA 5: Dendrograma ─────────────────────────────────────────────
        ruta_dend = self.dendrograma(
            n_muestra=60, carpeta_salida=carpeta_salida, verbose=False
        )
        rutas["fig_dendrograma"] = ruta_dend

        print(f"\n[OK] Todas las figuras de la Sesión 9 guardadas en: {carpeta}")
        return rutas

    # ──────────────────────────────────────────────────────────────────────────
    # 8. Resumen ejecutivo para el Avance 2
    # ──────────────────────────────────────────────────────────────────────────

    def resumen_avance2(self) -> str:
        """
        Genera un texto estructurado listo para incluir en el documento
        del Avance 2: descripción del k elegido, perfiles y campañas.

        Retorna
        -------
        str : texto del resumen ejecutivo.
        """
        if self.df_perfil is None:
            self.perfilar()

        lineas = [
            "═" * 65,
            "RESUMEN DE SEGMENTACIÓN · AUTOGEST · Sesión 9",
            "Minería de Datos · UNIMINUTO Ibagué · 2026-2",
            "═" * 65,
            f"\nk elegido: {self.k_elegido} clústeres",
            f"Variables de clustering ({len(self._vars)}): {', '.join(self._vars)}",
            f"Método: KMeans (n_init=10, random_state=42) + StandardScaler",
            f"Silueta global: "
            f"{silhouette_score(self.X_scaled, self.df['cluster']):.4f}",
            f"\nTamaño de la base: {len(self.df):,} observaciones",
            "",
        ]

        lineas.append("PERFILES POR SEGMENTO (medias en escala original):")
        lineas.append("─" * 65)
        lineas.append(str(self.df_perfil.to_string()))

        if self.nombres_seg:
            lineas += ["", "NOMENCLATURA COMERCIAL:", "─" * 65]
            for cid, nombre in sorted(self.nombres_seg.items()):
                n_obs = int(self.df_perfil.loc[cid, "n_obs"]) \
                        if cid in self.df_perfil.index else "?"
                pct   = float(self.df_perfil.loc[cid, "pct_obs"]) \
                        if cid in self.df_perfil.index else 0
                lineas.append(f"  [{cid}] {nombre}  —  {n_obs} obs ({pct}%)")

        lineas += ["", "═" * 65]
        texto = "\n".join(lineas)
        print(texto)
        return texto
