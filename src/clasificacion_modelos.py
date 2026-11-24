"""
clasificacion_modelos.py
========================
Sesión 8 · Clasificación II: Naive Bayes y K-Vecinos Más Cercanos (KNN)
Minería de Datos · UNIMINUTO Ibagué · 2026-2
Docente: Esteban Ernesto Morales Castro

Implementa GaussianNB y KNeighborsClassifier sobre el dataset AUTOGEST,
los compara con el Árbol de Decisión (sesión 7) y genera todas las
figuras y tablas exigidas por el taller práctico de la sesión.

Referencia pedagógica:
  - Naive Bayes: supone independencia condicional entre features (P naíve).
  - KNN: modelo perezoso (lazy); REQUIERE escalado con StandardScaler.
  - Regla mnemotécnica: "distancia manda a escalar".
"""

from pathlib import Path
import time
import warnings

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings("ignore")

from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)
from sklearn.preprocessing import KBinsDiscretizer

from src.transformacion import Transformacion, resolver_ruta


# ──────────────────────────────────────────────────────────────────────────────
# Clase principal
# ──────────────────────────────────────────────────────────────────────────────

class ClasificacionModelos:
    """
    Torneo de Clasificación II: Árbol de Decisión vs. Naive Bayes vs. KNN.

    Reproduce el flujo pedagógico de la Sesión 8 sobre el dataset AUTOGEST
    (accidentes viales de Ibagué) en lugar del dataset TelecomUNO de la demo:
    la variable objetivo es ACCIDENTES_REGISTRADOS discretizada en 3 niveles
    (Bajo / Medio / Alto) con la misma partición 75-25 estratificada que usan
    los tres modelos, garantizando comparabilidad (misma semilla, mismo split).

    Uso rápido
    ----------
    >>> from src.clasificacion_modelos import ClasificacionModelos
    >>> cm = ClasificacionModelos()
    >>> cm.cargar()
    >>> resultados = cm.torneo()
    >>> cm.generar_figuras()
    """

    # Columnas numéricas del proyecto AUTOGEST (Sesión 4)
    NUMERICAS = [
        "AÑO", "MES", "VOLUMEN_TRAFICO", "VEHICULOS_EVASORES",
        "VEHICULOS_EXENTOS", "SERVICIOS_TALLER", "COSTO_TOTAL_TALLER",
        "MILLAJE_PROMEDIO",
    ]
    CATEGORICAS = ["TIPO_VEHICULO"]
    OBJETIVO = "ACCIDENTES_REGISTRADOS"

    def __init__(self, ruta="dataset/dataset_integrado.csv", df=None):
        self.ruta = resolver_ruta(ruta)
        self.df = df
        self.trans = None
        self.feature_names: list[str] = []

        # Partición compartida (se fija en preparar_datos)
        self.X_train = self.X_test = None
        self.y_train = self.y_test = None

        # Modelos listos para entrenar / consultar
        self.modelos: dict = {}
        self._resultados: list[dict] = []

    # ──────────────────────────────────────────────────────────────────────────
    # 1. Carga de datos
    # ──────────────────────────────────────────────────────────────────────────

    def cargar(self) -> pd.DataFrame:
        """Carga el dataset integrado AUTOGEST (delega en Transformacion)."""
        if self.df is None:
            self.trans = Transformacion(self.ruta)
            self.df = self.trans.cargar()
        else:
            self.trans = Transformacion(df=self.df)
            self.trans.cargar()
        # Ajusta dinámicamente si alguna columna no existe
        self.NUMERICAS = [c for c in self.NUMERICAS if c in self.df.columns]
        self.CATEGORICAS = [c for c in self.CATEGORICAS if c in self.df.columns]
        return self.df

    # ──────────────────────────────────────────────────────────────────────────
    # 2. Preparación del tablero compartido
    # ──────────────────────────────────────────────────────────────────────────

    def _discretizar_objetivo(self, n_clases: int = 3) -> pd.Series:
        """
        Discretiza ACCIDENTES_REGISTRADOS en n_clases niveles ordenados.

        n_clases=3  →  Bajo / Medio / Alto  (quantile, distribución equitativa)
        n_clases=2  →  Normal / Crítico     (umbral IQR Q3+1.5*IQR = 2226.25)
        """
        serie = self.df[self.OBJETIVO]
        if n_clases == 2:
            umbral = 2226.25
            return (serie > umbral).map({False: "Normal", True: "Crítico"})
        disc = KBinsDiscretizer(n_bins=n_clases, encode="ordinal", strategy="quantile")
        bins = disc.fit_transform(self.df[[self.OBJETIVO]]).ravel()
        mapa = {0: "Bajo", 1: "Medio", 2: "Alto"} if n_clases == 3 else {
            i: f"Clase_{i+1}" for i in range(n_clases)
        }
        return pd.Series(bins, index=self.df.index).map(mapa)

    def preparar_datos(
        self,
        n_clases: int = 3,
        test_size: float = 0.25,
        random_state: int = 42,
    ) -> None:
        """
        Construye X/y y hace el split único estratificado.

        Todos los modelos del torneo usarán EXACTAMENTE esta misma partición
        para garantizar comparabilidad (principio de laboratorio de la Sesión 8).

        Parámetros
        ----------
        n_clases : int
            Número de clases del target (2 o 3).
        test_size : float
            Proporción del conjunto de prueba (0.25 → 75/25).
        random_state : int
            Semilla de aleatoriedad (42 en toda la asignatura).
        """
        if self.df is None:
            self.cargar()

        # ── Matriz de predictores X ──────────────────────────────────────────
        # Variables numéricas (crudas; KNN las escalará internamente via Pipeline)
        X_num = self.df[self.NUMERICAS].copy()

        # One-Hot Encoding de TIPO_VEHICULO
        if self.CATEGORICAS:
            df_dummies = pd.get_dummies(
                self.df[self.CATEGORICAS], drop_first=False
            )
            X = pd.concat([X_num, df_dummies], axis=1)
        else:
            X = X_num.copy()

        self.feature_names = list(X.columns)

        # ── Variable objetivo y ──────────────────────────────────────────────
        y = self._discretizar_objetivo(n_clases=n_clases)

        # ── Split estratificado único ────────────────────────────────────────
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=random_state,
            stratify=y,
        )

        # ── Definición del diccionario de modelos (Código 1 y 2 de la demo) ─
        self.modelos = {
            "Árbol (prof=4)": DecisionTreeClassifier(
                max_depth=4,
                min_samples_split=10,
                min_samples_leaf=5,
                criterion="gini",
                random_state=random_state,
            ),
            "Naive Bayes": GaussianNB(),
            "KNN (k=5) escalado": make_pipeline(
                StandardScaler(),
                KNeighborsClassifier(n_neighbors=5),
            ),
        }

    # ──────────────────────────────────────────────────────────────────────────
    # 3. Torneo de los tres modelos
    # ──────────────────────────────────────────────────────────────────────────

    def torneo(
        self,
        n_clases: int = 3,
        test_size: float = 0.25,
        random_state: int = 42,
        verbose: bool = True,
    ) -> pd.DataFrame:
        """
        Entrena Árbol, Naive Bayes y KNN sobre la misma partición y devuelve
        una tabla comparativa con accuracy de entrenamiento y prueba y el
        tiempo de fit (segundos), como en el Código 2 de la demo guiada.

        Parámetros
        ----------
        n_clases : int
            Clases del target (2 o 3).
        test_size : float
            Proporción de test (default 0.25 → 75/25 estratificado).
        random_state : int
            Semilla de aleatoriedad (42).
        verbose : bool
            Imprime la tabla al estilo de la presentación si es True.

        Retorna
        -------
        pd.DataFrame con columnas: Modelo, entrena_s, acc_train, acc_test.
        """
        self.preparar_datos(n_clases=n_clases, test_size=test_size,
                            random_state=random_state)

        filas: list[dict] = []
        self._resultados = []

        if verbose:
            print(f"\n{'─'*60}")
            print(f"{'TORNEO DE CLASIFICACIÓN · AUTOGEST · Sesión 8':^60}")
            print(f"{'─'*60}")
            print(
                f"{'Modelo':<25} {'fit(s)':>8} {'acc_train':>10} {'acc_test':>10}"
            )
            print(f"{'─'*60}")

        for nombre, modelo in self.modelos.items():
            t0 = time.perf_counter()
            modelo.fit(self.X_train, self.y_train)
            dt = time.perf_counter() - t0

            acc_train = modelo.score(self.X_train, self.y_train)
            acc_test  = modelo.score(self.X_test,  self.y_test)

            fila = {
                "Modelo":     nombre,
                "fit_s":      round(dt, 4),
                "acc_train":  round(acc_train, 4),
                "acc_test":   round(acc_test, 4),
                "acc_train_%": f"{acc_train*100:.2f}%",
                "acc_test_%":  f"{acc_test*100:.2f}%",
            }
            filas.append(fila)
            self._resultados.append({**fila, "modelo_obj": modelo})

            if verbose:
                print(
                    f"{nombre:<25} {dt:>8.4f} {acc_train:>10.3f} {acc_test:>10.3f}"
                )

        if verbose:
            print(f"{'─'*60}")
            print(
                "\n[Nota] KNN sin escalar → ver self.efecto_escalado_knn()\n"
            )

        return pd.DataFrame(filas)[
            ["Modelo", "fit_s", "acc_train", "acc_test",
             "acc_train_%", "acc_test_%"]
        ]

    # ──────────────────────────────────────────────────────────────────────────
    # 4. Exploración del parámetro k (Paso 3 del taller)
    # ──────────────────────────────────────────────────────────────────────────

    def explorar_k(
        self,
        valores_k: list[int] | None = None,
        verbose: bool = True,
    ) -> pd.DataFrame:
        """
        Entrena KNN con diferentes valores de k (dentro de Pipeline con
        StandardScaler) y documenta el efecto sobre train/test.

        Permite reproducir los pasos:
          k=1  → sobreajuste evidente (train=1.0)
          k=11 → equilibrio
          k=51 → subajuste suave (vecindario demasiado amplio)

        Parámetros
        ----------
        valores_k : list[int]
            Lista de valores de k a evaluar.
            Por defecto [1, 5, 11, 31, 51].
        verbose : bool
            Imprime la tabla si es True.

        Retorna
        -------
        pd.DataFrame con columnas: k, acc_train, acc_test, Diagnóstico.
        """
        if self.X_train is None:
            self.preparar_datos()

        if valores_k is None:
            valores_k = [1, 5, 11, 31, 51]

        diagnosticos = {
            1:   "Memoriza cada punto → sobreajuste evidente",
            3:   "Vecindario pequeño → aún inestable",
            5:   "Buen equilibrio bias-varianza",
            11:  "Estable, buena generalización",
            31:  "Vecindario amplio, suaviza fronteras",
            51:  "Consulta ~10% de los datos → subajuste suave",
        }

        pipeline_k = make_pipeline(StandardScaler(), KNeighborsClassifier())
        filas: list[dict] = []

        if verbose:
            print(f"\n{'─'*62}")
            print(f"{'EXPLORACIÓN DEL PARÁMETRO k · KNN escalado':^62}")
            print(f"{'─'*62}")
            print(f"{'k':>5} {'acc_train':>12} {'acc_test':>10}  Diagnóstico")
            print(f"{'─'*62}")

        for k in valores_k:
            pipeline_k.set_params(kneighborsclassifier__n_neighbors=k)
            pipeline_k.fit(self.X_train, self.y_train)
            acc_tr = pipeline_k.score(self.X_train, self.y_train)
            acc_te = pipeline_k.score(self.X_test,  self.y_test)
            diag = diagnosticos.get(k, "—")
            filas.append({
                "k":          k,
                "acc_train":  round(acc_tr, 4),
                "acc_test":   round(acc_te, 4),
                "Diagnóstico": diag,
            })
            if verbose:
                print(
                    f"{k:>5} {acc_tr:>12.3f} {acc_te:>10.3f}  {diag}"
                )

        if verbose:
            print(f"{'─'*62}\n")

        return pd.DataFrame(filas)

    # ──────────────────────────────────────────────────────────────────────────
    # 5. Efecto del escalado sobre KNN (slide 12 de la presentación)
    # ──────────────────────────────────────────────────────────────────────────

    def efecto_escalado_knn(self, k: int = 5) -> dict:
        """
        Compara KNN con y sin StandardScaler para demostrar por qué
        "distancia manda a escalar" (Sesión 8, diapositiva 12).

        Retorna
        -------
        dict con claves 'sin_escalar' y 'escalado' (accuracy de test).
        """
        if self.X_train is None:
            self.preparar_datos()

        # Sin escalar
        knn_crudo = KNeighborsClassifier(n_neighbors=k)
        knn_crudo.fit(self.X_train, self.y_train)
        acc_crudo = knn_crudo.score(self.X_test, self.y_test)

        # Con StandardScaler dentro de Pipeline
        knn_pipe = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=k))
        knn_pipe.fit(self.X_train, self.y_train)
        acc_pipe = knn_pipe.score(self.X_test, self.y_test)

        resultado = {
            "sin_escalar": round(acc_crudo, 4),
            "escalado":    round(acc_pipe,  4),
            "diferencia":  round(acc_pipe - acc_crudo, 4),
        }

        print(f"\n── Efecto del escalado en KNN (k={k}) ──────────────────")
        print(f"  Sin StandardScaler : acc_test = {resultado['sin_escalar']:.3f}")
        print(f"  Con StandardScaler : acc_test = {resultado['escalado']:.3f}")
        print(f"  Diferencia         : {resultado['diferencia']:+.3f}")
        print(f"  → 'distancia manda a escalar' ✓")
        print("─" * 56)

        return resultado

    # ──────────────────────────────────────────────────────────────────────────
    # 6. Reporte detallado por modelo
    # ──────────────────────────────────────────────────────────────────────────

    def reporte_modelo(self, nombre_modelo: str) -> dict:
        """
        Devuelve la matriz de confusión y el classification_report completo
        del modelo indicado (debe estar ya entrenado por torneo()).

        Parámetros
        ----------
        nombre_modelo : str
            Clave exacta del modelo en self.modelos
            ('Árbol (prof=4)', 'Naive Bayes', 'KNN (k=5) escalado').

        Retorna
        -------
        dict con claves 'confusion_matrix' (DataFrame) y 'report' (DataFrame).
        """
        if nombre_modelo not in self.modelos:
            raise ValueError(
                f"Modelo '{nombre_modelo}' no encontrado. "
                f"Opciones: {list(self.modelos.keys())}"
            )
        modelo = self.modelos[nombre_modelo]
        y_pred = modelo.predict(self.X_test)
        etiquetas = sorted(self.y_test.unique())

        cm = confusion_matrix(self.y_test, y_pred, labels=etiquetas)
        df_cm = pd.DataFrame(
            cm,
            index=[f"Real_{e}"  for e in etiquetas],
            columns=[f"Pred_{e}" for e in etiquetas],
        )
        report_dict = classification_report(
            self.y_test, y_pred, output_dict=True
        )
        df_report = pd.DataFrame(report_dict).transpose().round(4)

        return {"confusion_matrix": df_cm, "report": df_report}

    # ──────────────────────────────────────────────────────────────────────────
    # 7. Generación de figuras (taller práctico)
    # ──────────────────────────────────────────────────────────────────────────

    def generar_figuras(
        self,
        carpeta_salida: str = "analisis/figuras",
    ) -> dict[str, str]:
        """
        Genera y exporta en alta resolución (150 DPI) las figuras diagnósticas
        del torneo de clasificación de la Sesión 8:

        1. fig_torneo_accuracy_comparado.png
           Barras comparativas de accuracy test de los 3 modelos.

        2. fig_knn_efecto_k.png
           Curva de acc_train vs acc_test para k ∈ {1, 3, 5, 11, 21, 31, 51, 71}.

        3. fig_knn_efecto_escalado.png
           Barras: KNN sin escalar vs. KNN escalado (k=5).

        4. fig_matrices_confusion.png
           Panel 1×3 con la matriz de confusión de cada modelo.

        Retorna
        -------
        dict {nombre_figura: ruta_absoluta}.
        """
        if not self._resultados:
            self.torneo(verbose=False)

        carpeta = resolver_ruta(carpeta_salida)
        carpeta.mkdir(parents=True, exist_ok=True)
        rutas: dict[str, str] = {}

        colores_modelo = {
            "Árbol (prof=4)":        "#1d4ed8",
            "Naive Bayes":           "#7c3aed",
            "KNN (k=5) escalado":    "#059669",
        }

        # ── FIGURA 1: Accuracy comparado (torneo) ────────────────────────────
        nombres  = [r["Modelo"]   for r in self._resultados]
        acc_tr   = [r["acc_train"] for r in self._resultados]
        acc_te   = [r["acc_test"]  for r in self._resultados]
        colores  = [colores_modelo.get(n, "#6b7280") for n in nombres]

        fig1, (ax1a, ax1b) = plt.subplots(1, 2, figsize=(13, 5.5), dpi=150)

        x = np.arange(len(nombres))
        ancho = 0.35
        bars_tr = ax1a.bar(x - ancho/2, [v*100 for v in acc_tr],
                           ancho, label="Entrenamiento", color=colores, alpha=0.55,
                           edgecolor="black", linewidth=0.8)
        bars_te = ax1a.bar(x + ancho/2, [v*100 for v in acc_te],
                           ancho, label="Pruebas",        color=colores,
                           edgecolor="black", linewidth=0.8)
        ax1a.set_xticks(x)
        ax1a.set_xticklabels(nombres, fontsize=10)
        ax1a.set_ylim(0, 110)
        ax1a.set_ylabel("Accuracy (%)", fontweight="bold")
        ax1a.set_title(
            "Torneo de Clasificación · Accuracy Train vs. Test\n"
            "AUTOGEST · Sesión 8 · Árbol vs. Naive Bayes vs. KNN",
            fontsize=11, fontweight="bold",
        )
        ax1a.legend(fontsize=9)
        for b in list(bars_tr) + list(bars_te):
            h = b.get_height()
            ax1a.text(
                b.get_x() + b.get_width() / 2, h + 0.8,
                f"{h:.1f}%", ha="center", va="bottom", fontsize=8.5, fontweight="bold",
            )

        # Panel derecho: ranking por acc_test
        orden = sorted(range(len(nombres)), key=lambda i: acc_te[i], reverse=True)
        nombres_ord = [nombres[i] for i in orden]
        acc_te_ord  = [acc_te[i]*100  for i in orden]
        colores_ord = [colores[i]      for i in orden]
        bars_rank = ax1b.barh(nombres_ord, acc_te_ord, color=colores_ord,
                              edgecolor="black", linewidth=0.8)
        ax1b.set_xlim(0, 110)
        ax1b.set_xlabel("Accuracy de Prueba (%)", fontweight="bold")
        ax1b.set_title("Ranking por Accuracy de Prueba", fontsize=11, fontweight="bold")
        for b in bars_rank:
            w = b.get_width()
            ax1b.text(w + 0.5, b.get_y() + b.get_height()/2,
                      f"{w:.2f}%", va="center", fontsize=10, fontweight="bold")

        fig1.tight_layout()
        ruta_f1 = carpeta / "fig_torneo_accuracy_comparado.png"
        fig1.savefig(ruta_f1, bbox_inches="tight")
        plt.close(fig1)
        rutas["fig_torneo"] = str(ruta_f1)
        print(f"[OK] {ruta_f1.name}")

        # ── FIGURA 2: Efecto de k en KNN ─────────────────────────────────────
        valores_k = [1, 3, 5, 11, 21, 31, 51, 71]
        df_k = self.explorar_k(valores_k=valores_k, verbose=False)

        fig2, ax2 = plt.subplots(figsize=(10, 5.5), dpi=150)
        ax2.plot(df_k["k"], df_k["acc_train"]*100, "o-", color="#1d4ed8",
                 linewidth=2.5, label="Entrenamiento (Train)", markersize=7)
        ax2.plot(df_k["k"], df_k["acc_test"]*100,  "s-", color="#059669",
                 linewidth=2.5, label="Pruebas (Test)",         markersize=7)
        ax2.axvline(5, color="#dc2626", linestyle="--", linewidth=1.5, label="k=5 (referencia)")
        idx5 = df_k[df_k["k"] == 5].index
        if not idx5.empty:
            ax2.scatter([5], [df_k.loc[idx5[0], "acc_test"]*100],
                        color="#dc2626", s=120, zorder=5)
        ax2.fill_betweenx([0, 110], 0, 2.5,  alpha=0.08, color="orange", label="k muy pequeño")
        ax2.fill_betweenx([0, 110], 55, 80,  alpha=0.08, color="red",    label="k muy grande")
        ax2.text(1.3,  ax2.get_ylim()[0]+1, "Sobreajuste", fontsize=8.5,
                 color="#b45309", fontweight="bold")
        ax2.text(60,   ax2.get_ylim()[0]+1, "Subajuste",   fontsize=8.5,
                 color="#b91c1c", fontweight="bold")
        ax2.set_xlabel("Valor de k (número de vecinos)", fontsize=11, fontweight="bold")
        ax2.set_ylabel("Accuracy (%)", fontsize=11, fontweight="bold")
        ax2.set_title(
            "Efecto del Parámetro k en KNN · Compromiso Sesgo–Varianza\n"
            "AUTOGEST · Sesión 8 · StandardScaler aplicado en Pipeline",
            fontsize=11, fontweight="bold",
        )
        ax2.legend(fontsize=9)
        fig2.tight_layout()
        ruta_f2 = carpeta / "fig_knn_efecto_k.png"
        fig2.savefig(ruta_f2, bbox_inches="tight")
        plt.close(fig2)
        rutas["fig_knn_efecto_k"] = str(ruta_f2)
        print(f"[OK] {ruta_f2.name}")

        # ── FIGURA 3: Efecto del escalado ─────────────────────────────────────
        ef = self.efecto_escalado_knn(k=5)
        fig3, ax3 = plt.subplots(figsize=(6, 4.5), dpi=150)
        etiq_esc = ["Sin StandardScaler\n(distancias sesgadas)",
                    "Con StandardScaler\n(en Pipeline)"]
        vals_esc = [ef["sin_escalar"]*100, ef["escalado"]*100]
        bars_esc = ax3.bar(etiq_esc, vals_esc,
                           color=["#ef4444", "#059669"],
                           edgecolor="black", linewidth=1, width=0.45)
        ax3.set_ylim(0, 115)
        ax3.set_ylabel("Accuracy de Prueba (%)", fontweight="bold")
        ax3.set_title(
            f"KNN k=5 · Efecto del Escalado en Distancia Euclidiana\n"
            f"Diferencia: {ef['diferencia']*100:+.2f}% · 'distancia manda a escalar'",
            fontsize=11, fontweight="bold",
        )
        for b, v in zip(bars_esc, vals_esc):
            ax3.text(b.get_x() + b.get_width()/2, v + 1.5,
                     f"{v:.2f}%", ha="center", fontsize=12, fontweight="bold")
        fig3.tight_layout()
        ruta_f3 = carpeta / "fig_knn_efecto_escalado.png"
        fig3.savefig(ruta_f3, bbox_inches="tight")
        plt.close(fig3)
        rutas["fig_knn_efecto_escalado"] = str(ruta_f3)
        print(f"[OK] {ruta_f3.name}")

        # ── FIGURA 4: Panel de matrices de confusión ──────────────────────────
        fig4, axes4 = plt.subplots(1, 3, figsize=(16, 5.5), dpi=150)
        for ax, nombre in zip(axes4, self.modelos.keys()):
            modelo  = self.modelos[nombre]
            y_pred  = modelo.predict(self.X_test)
            etiquetas = sorted(self.y_test.unique())
            cm_arr  = confusion_matrix(self.y_test, y_pred, labels=etiquetas)
            cm_pct  = (cm_arr.astype(float)
                       / cm_arr.sum(axis=1)[:, np.newaxis] * 100)
            annot   = np.empty_like(cm_arr, dtype=object)
            for i in range(len(etiquetas)):
                for j in range(len(etiquetas)):
                    annot[i, j] = f"{cm_arr[i, j]}\n({cm_pct[i, j]:.0f}%)"
            sns.heatmap(
                cm_arr, annot=annot, fmt="",
                cmap="Blues", ax=ax,
                xticklabels=[f"P:{e}" for e in etiquetas],
                yticklabels=[f"R:{e}" for e in etiquetas],
                linewidths=0.8, linecolor="#e2e8f0", cbar=False,
            )
            acc = accuracy_score(self.y_test, y_pred)
            ax.set_title(
                f"{nombre}\nAcc = {acc*100:.2f}%",
                fontsize=11, fontweight="bold",
            )
            ax.set_xlabel("Predicho", fontsize=9, fontweight="bold")
            ax.set_ylabel("Real",     fontsize=9, fontweight="bold")

        fig4.suptitle(
            "Matrices de Confusión · Torneo de Clasificación\n"
            "AUTOGEST · Sesión 8 · Árbol vs. Naive Bayes vs. KNN (k=5, escalado)",
            fontsize=12, fontweight="bold", y=1.02,
        )
        fig4.tight_layout()
        ruta_f4 = carpeta / "fig_matrices_confusion_sesion8.png"
        fig4.savefig(ruta_f4, bbox_inches="tight")
        plt.close(fig4)
        rutas["fig_matrices_confusion"] = str(ruta_f4)
        print(f"[OK] {ruta_f4.name}")

        print(f"\n[OK] Figuras de la Sesión 8 guardadas en: {carpeta}")
        return rutas

    # ──────────────────────────────────────────────────────────────────────────
    # 8. Veredicto técnico (Paso 4 del taller)
    # ──────────────────────────────────────────────────────────────────────────

    def veredicto_tecnico(self) -> str:
        """
        Genera un veredicto técnico escrito (≤ 8 líneas) recomendando el
        modelo más adecuado para AUTOGEST, ponderando accuracy, interpretabilidad
        y costos de operación (criterios del taller de la Sesión 8).

        Retorna
        -------
        str con el texto del veredicto.
        """
        if not self._resultados:
            self.torneo(verbose=False)

        filas_txt = sorted(
            self._resultados, key=lambda r: r["acc_test"], reverse=True
        )

        lineas = [
            "═" * 62,
            "VEREDICTO TÉCNICO · AUTOGEST · Torneo de Clasificación",
            "Sesión 8 · Minería de Datos · UNIMINUTO Ibagué · 2026-2",
            "═" * 62,
            "",
        ]
        lineas.append(
            f"{'Modelo':<25} {'acc_train':>10} {'acc_test':>10}"
        )
        lineas.append("─" * 50)
        for r in filas_txt:
            lineas.append(
                f"{r['Modelo']:<25} {r['acc_train']:>10.3f} {r['acc_test']:>10.3f}"
            )

        mejor = filas_txt[0]
        lineas += [
            "",
            f"► Ganador en accuracy de prueba: {mejor['Modelo']} "
            f"({mejor['acc_test']*100:.2f}%)",
            "",
            "RECOMENDACIÓN PARA AUTOGEST:",
            "  • Árbol de Decisión (prof=4): modelo PRINCIPAL para producción.",
            "    Ofrece reglas IF-THEN legibles para inspectores y directivos viales,",
            "    requisito crítico en gestión pública de siniestralidad.",
            "  • Naive Bayes: línea base permanente. Reentrenar diario es trivial;",
            "    si NB supera al árbol, el problema se simplificó o hay fuga de datos.",
            "  • KNN (k=5 escalado): útil para análisis exploratorio local,",
            "    pero lento en predicción sobre el histórico completo de Ibagué.",
            "",
            "Criterios ponderados: accuracy de prueba, interpretabilidad regulatoria,",
            "costo computacional de predicción y facilidad de reentrenamiento.",
            "═" * 62,
        ]

        texto = "\n".join(lineas)
        print(texto)
        return texto
