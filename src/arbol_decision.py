from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

import warnings
warnings.filterwarnings("ignore")

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import (
    StandardScaler,
    MinMaxScaler,
    RobustScaler,
    KBinsDiscretizer
)
from sklearn.tree import (
    DecisionTreeClassifier,
    DecisionTreeRegressor,
    export_text,
    plot_tree
)
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    r2_score,
    mean_squared_error,
    mean_absolute_error
)

from src.transformacion import Transformacion, resolver_ruta


class ModeloArbolDecision:
    """
    Clase modular para el Modelado con Árboles de Decisión (Clasificación y Regresión)
    según la metodología CRISP-DM y PEA UNIMINUTO para el proyecto AUTOGEST.
    Integra el pipeline de transformación, escalamiento y reducción previamente desarrollado.
    """

    def __init__(self, ruta="../dataset/dataset_integrado.csv", df=None):
        self.ruta = resolver_ruta(ruta)
        self.df = df
        self.trans = None
        self.numericas = [
            "AÑO", "MES", "VOLUMEN_TRAFICO", "VEHICULOS_EVASORES",
            "VEHICULOS_EXENTOS", "SERVICIOS_TALLER", "COSTO_TOTAL_TALLER",
            "MILLAJE_PROMEDIO"
        ]
        self.categoricas = ["TIPO_VEHICULO"]
        self.variable_objetivo = "ACCIDENTES_REGISTRADOS"
        self.scalers = {
            "standard": StandardScaler(),
            "minmax": MinMaxScaler(),
            "robust": RobustScaler()
        }
        self.scaler_ajustado = None
        self.modelo = None
        self.feature_names = []
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None

    def cargar(self):
        """Carga el dataset integrado usando la clase modular Transformacion."""
        if self.df is None:
            self.trans = Transformacion(self.ruta)
            self.df = self.trans.cargar()
        else:
            self.trans = Transformacion(df=self.df)
            self.trans.cargar()
        self.numericas = [c for c in self.numericas if c in self.df.columns]
        self.categoricas = [c for c in self.categoricas if c in self.df.columns]
        return self.df

    def preparar_target_clasificacion(self, n_clases=3, estrategia="quantile"):
        """
        Discretiza la variable objetivo continua ACCIDENTES_REGISTRADOS en categorías ordenadas:
        - n_clases=3: ['Bajo', 'Medio', 'Alto']
        - n_clases=2: ['Normal', 'Crítico'] (usando el umbral IQR de Tukey = 2226.25 de Sesión 5)
        - n_clases=4: Cuartiles ['Q1_Bajo', 'Q2_Medio_Bajo', 'Q3_Medio_Alto', 'Q4_Alto']
        """
        if self.df is None:
            self.cargar()

        serie_y = self.df[self.variable_objetivo]

        if n_clases == 2:
            # Umbral formal de outliers del EDA (Q3 + 1.5 * IQR = 2226.25)
            umbral_outlier = 2226.25
            y_cat = (serie_y > umbral_outlier).map({False: "Normal", True: "Crítico"})
            bordes = [serie_y.min(), umbral_outlier, serie_y.max()]
            return y_cat, bordes

        discretizador = KBinsDiscretizer(n_bins=n_clases, encode="ordinal", strategy=estrategia)
        bins = discretizador.fit_transform(self.df[[self.variable_objetivo]]).ravel()
        bordes = discretizador.bin_edges_[0]

        if n_clases == 3:
            mapeo = {0: "Bajo", 1: "Medio", 2: "Alto"}
        elif n_clases == 4:
            mapeo = {0: "Q1_Bajo", 1: "Q2_Medio_Bajo", 2: "Q3_Medio_Alto", 3: "Q4_Alto"}
        else:
            mapeo = {i: f"Clase_{i+1}" for i in range(n_clases)}

        y_cat = pd.Series(bins, index=self.df.index).map(mapeo)
        return y_cat, bordes

    def preparar_features(self, tipo_escalamiento="standard"):
        """
        Prepara la matriz predictora X aplicando el escalamiento especificado:
        - 'standard': StandardScaler (Estándar del proyecto AUTOGEST y prepaso de PCA).
        - 'minmax'  : MinMaxScaler (Rango [0, 1]).
        - 'robust'  : RobustScaler (Mediana e IQR, resistente a outliers).
        - 'pca'     : 5 Componentes Principales generadas por PCA estandarizado.
        - 'crudo'   : Variables continuas sin transformar.
        Incluye variables dummy (One-Hot Encoding) para TIPO_VEHICULO.
        """
        if self.df is None:
            self.cargar()

        # One-Hot Encoding de variables categóricas
        df_dummies = self.trans.codificar_onehot()

        if tipo_escalamiento == "pca":
            df_pca, _ = self.trans.aplicar_pca(n_componentes=5)
            X = pd.concat([df_pca, df_dummies], axis=1)
            self.feature_names = list(X.columns)
            return X

        X_num = self.df[self.numericas].copy()

        if tipo_escalamiento in self.scalers:
            self.scaler_ajustado = self.scalers[tipo_escalamiento]
            X_scaled_arr = self.scaler_ajustado.fit_transform(X_num)
            df_num_scaled = pd.DataFrame(X_scaled_arr, columns=self.numericas, index=self.df.index)
        elif tipo_escalamiento == "crudo":
            df_num_scaled = X_num
        else:
            raise ValueError(f"Escalamiento desconocido: '{tipo_escalamiento}'. Opciones: 'standard', 'minmax', 'robust', 'pca', 'crudo'.")

        X = pd.concat([df_num_scaled, df_dummies], axis=1)
        self.feature_names = list(X.columns)
        return X

    def entrenar_arbol_clasificacion(
        self,
        tipo_escalamiento="standard",
        n_clases=3,
        estrategia_discretizacion="quantile",
        max_depth=4,
        min_samples_split=10,
        min_samples_leaf=5,
        test_size=0.2,
        random_state=42
    ):
        """
        Entrena el Árbol de Decisión de Clasificación según el escalamiento elegido
        y calcula el accuracy de entrenamiento y pruebas junto a métricas detalladas.
        """
        X = self.preparar_features(tipo_escalamiento=tipo_escalamiento)
        y, bordes = self.preparar_target_clasificacion(n_clases=n_clases, estrategia=estrategia_discretizacion)

        # División Estratificada 80% Train - 20% Test
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        # Construcción del Árbol de Clasificación
        self.modelo = DecisionTreeClassifier(
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            criterion="gini",
            random_state=random_state
        )
        self.modelo.fit(self.X_train, self.y_train)

        # Predicciones
        y_pred_train = self.modelo.predict(self.X_train)
        y_pred_test = self.modelo.predict(self.X_test)

        # Cálculo de Accuracy
        acc_train = accuracy_score(self.y_train, y_pred_train)
        acc_test = accuracy_score(self.y_test, y_pred_test)

        # Importancia de Variables
        importancias = pd.Series(self.modelo.feature_importances_, index=self.feature_names).sort_values(ascending=False)

        # Matriz de Confusión y Reporte
        etiquetas = sorted(list(set(y)))
        cm = confusion_matrix(self.y_test, y_pred_test, labels=etiquetas)
        df_cm = pd.DataFrame(cm, index=[f"Real_{e}" for e in etiquetas], columns=[f"Pred_{e}" for e in etiquetas])
        reporte = classification_report(self.y_test, y_pred_test, output_dict=True)

        resumen = {
            "tipo_modelo": "DecisionTreeClassifier",
            "tipo_escalamiento": tipo_escalamiento,
            "n_clases": n_clases,
            "bordes_clases": bordes.tolist() if isinstance(bordes, np.ndarray) else bordes,
            "max_depth": max_depth,
            "profundidad_real": self.modelo.get_depth(),
            "n_hojas": self.modelo.get_n_leaves(),
            "accuracy_entrenamiento": float(round(acc_train, 4)),
            "accuracy_pruebas": float(round(acc_test, 4)),
            "accuracy_entrenamiento_pct": f"{acc_train * 100:.2f}%",
            "accuracy_pruebas_pct": f"{acc_test * 100:.2f}%",
            "importancia_variables": importancias[importancias > 0].round(4).to_dict(),
            "matriz_confusion": df_cm,
            "reporte_clasificacion": pd.DataFrame(reporte).transpose().round(4),
            "etiquetas": etiquetas
        }
        return resumen

    def entrenar_arbol_regresion(
        self,
        tipo_escalamiento="standard",
        max_depth=4,
        min_samples_split=10,
        min_samples_leaf=5,
        test_size=0.2,
        random_state=42
    ):
        """
        Entrena el Árbol de Decisión de Regresión sobre la variable continua ACCIDENTES_REGISTRADOS,
        calculando R2 de entrenamiento y pruebas, RMSE y MAE.
        """
        X = self.preparar_features(tipo_escalamiento=tipo_escalamiento)
        y = self.df[self.variable_objetivo]

        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )

        modelo_reg = DecisionTreeRegressor(
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state
        )
        modelo_reg.fit(self.X_train, self.y_train)

        y_pred_train = modelo_reg.predict(self.X_train)
        y_pred_test = modelo_reg.predict(self.X_test)

        r2_train = r2_score(self.y_train, y_pred_train)
        r2_test = r2_score(self.y_test, y_pred_test)
        rmse_test = float(np.sqrt(mean_squared_error(self.y_test, y_pred_test)))
        mae_test = float(mean_absolute_error(self.y_test, y_pred_test))

        resumen = {
            "tipo_modelo": "DecisionTreeRegressor",
            "tipo_escalamiento": tipo_escalamiento,
            "max_depth": max_depth,
            "r2_entrenamiento": float(round(r2_train, 4)),
            "r2_pruebas": float(round(r2_test, 4)),
            "r2_entrenamiento_pct": f"{r2_train * 100:.2f}%",
            "r2_pruebas_pct": f"{r2_test * 100:.2f}%",
            "rmse_pruebas": float(round(rmse_test, 2)),
            "mae_pruebas": float(round(mae_test, 2))
        }
        return resumen

    def comparar_escalamientos(self, n_clases=3, max_depth=4):
        """
        Compara empíricamente el desempeño del Árbol de Decisión bajo todos los escaladores
        estudiados en la Sesión 4 (StandardScaler, MinMaxScaler, RobustScaler, Sin Escalar y PCA).
        """
        metodos = [
            ("StandardScaler (Pipeline Oficial)", "standard"),
            ("MinMaxScaler (Normalización [0,1])", "minmax"),
            ("RobustScaler (Resistente a Outliers)", "robust"),
            ("Sin Escalar (Datos Crudos)", "crudo"),
            ("PCA (5 Componentes Reducidas)", "pca")
        ]

        filas = []
        for nombre, tipo in metodos:
            res = self.entrenar_arbol_clasificacion(tipo_escalamiento=tipo, n_clases=n_clases, max_depth=max_depth)
            filas.append({
                "Método de Escalamiento": nombre,
                "Tipo": tipo,
                "Accuracy Entrenamiento": res["accuracy_entrenamiento_pct"],
                "Accuracy Pruebas": res["accuracy_pruebas_pct"],
                "Profundidad Real": res["profundidad_real"],
                "Hojas": res["n_hojas"]
            })

        df_comp = pd.DataFrame(filas)
        return df_comp

    def comparar_profundidades(self, tipo_escalamiento="standard", n_clases=3, profundidades=[2, 3, 4, 5, 6, None]):
        """
        Analiza el impacto del hiperparámetro max_depth en el balance sesgo-varianza,
        demostrando cómo evitar el sobreajuste (overfitting).
        """
        filas = []
        for p in profundidades:
            res = self.entrenar_arbol_clasificacion(tipo_escalamiento=tipo_escalamiento, n_clases=n_clases, max_depth=p)
            nombre_p = "Sin límite (Overfitting)" if p is None else f"Profundidad {p}"
            filas.append({
                "Hiperparámetro": nombre_p,
                "max_depth": str(p),
                "Accuracy Train": res["accuracy_entrenamiento_pct"],
                "Accuracy Test": res["accuracy_pruebas_pct"],
                "Hojas": res["n_hojas"],
                "Diferencia (Train - Test)": f"{(res['accuracy_entrenamiento'] - res['accuracy_pruebas'])*100:.2f}%"
            })
        return pd.DataFrame(filas)

    def exportar_reglas_texto(self, max_depth=3):
        """Genera y retorna la representación textual legible de las reglas del árbol."""
        if self.modelo is None:
            self.entrenar_arbol_clasificacion(max_depth=max_depth)
        return export_text(self.modelo, feature_names=self.feature_names)

    def generar_figuras(self, carpeta_salida="analisis/figuras"):
        """
        Genera y exporta en alta definición (150 DPI) los 3 gráficos diagnósticos del árbol:
        1. Diagrama visual del árbol de decisión (plot_tree).
        2. Mapa de calor de la matriz de confusión (Test Set).
        3. Gráfico de barras de importancia de variables predictoras.
        """
        carpeta = resolver_ruta(carpeta_salida)
        carpeta.mkdir(parents=True, exist_ok=True)

        if self.modelo is None:
            self.entrenar_arbol_clasificacion(tipo_escalamiento="standard", max_depth=4)

        etiquetas = sorted(list(set(self.y_train)))

        # FIGURA 1 · ESTRUCTURA VISUAL DEL ÁRBOL DE DECISIÓN
        fig1, ax1 = plt.subplots(figsize=(16, 7), dpi=150)
        plot_tree(
            self.modelo,
            feature_names=self.feature_names,
            class_names=[str(e) for e in etiquetas],
            filled=True,
            rounded=True,
            fontsize=8,
            ax=ax1
        )
        ax1.set_title(
            f"Árbol de Decisión · Clasificación de Siniestralidad Vial (StandardScaler · Depth={self.modelo.get_depth()})\n"
            f"AUTOGEST · Exactitud Entrenamiento: {self.modelo.score(self.X_train, self.y_train)*100:.2f}% | Pruebas: {self.modelo.score(self.X_test, self.y_test)*100:.2f}%",
            fontsize=11,
            fontweight="bold",
            pad=12
        )
        ruta_fig1 = carpeta / "fig_arbol_decision.png"
        fig1.tight_layout()
        fig1.savefig(ruta_fig1, bbox_inches="tight")
        plt.close(fig1)

        # FIGURA 2 · MATRIZ DE CONFUSIÓN ENRIQUECIDA
        y_pred_test = self.modelo.predict(self.X_test)
        cm = confusion_matrix(self.y_test, y_pred_test, labels=etiquetas)
        cm_pct = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100

        fig2, ax2 = plt.subplots(figsize=(6.8, 5.5), dpi=150)
        annot_matrix = np.empty_like(cm, dtype=object)
        for i in range(len(etiquetas)):
            for j in range(len(etiquetas)):
                annot_matrix[i, j] = f"{cm[i, j]}\n({cm_pct[i, j]:.1f}%)"

        sns.heatmap(
            cm,
            annot=annot_matrix,
            fmt="",
            cmap="Blues",
            xticklabels=[f"Pred: {e}" for e in etiquetas],
            yticklabels=[f"Real: {e}" for e in etiquetas],
            cbar=True,
            cbar_kws={'label': 'Observaciones'},
            linewidths=1,
            linecolor="#e2e8f0",
            ax=ax2
        )
        acc_test_val = accuracy_score(self.y_test, y_pred_test) * 100
        ax2.set_title(
            f"Matriz de Confusión · Árbol de Decisión (StandardScaler)\n"
            f"Exactitud Global (Accuracy de Pruebas): {acc_test_val:.2f}% ({int(np.trace(cm))}/{len(self.y_test)} aciertos)",
            fontsize=11,
            fontweight="bold",
            pad=12
        )
        ax2.set_xlabel("Nivel de Siniestralidad Predicho", fontsize=10.5, fontweight="bold", labelpad=8)
        ax2.set_ylabel("Nivel de Siniestralidad Real (Observado)", fontsize=10.5, fontweight="bold", labelpad=8)
        ruta_fig2 = carpeta / "fig_matriz_confusion_arbol.png"
        fig2.tight_layout()
        fig2.savefig(ruta_fig2, bbox_inches="tight")
        plt.close(fig2)

        # FIGURA 3 · IMPORTANCIA DE VARIABLES
        importancias = pd.Series(self.modelo.feature_importances_, index=self.feature_names).sort_values(ascending=True)
        importancias_utiles = importancias[importancias > 0.01]

        fig3, ax3 = plt.subplots(figsize=(8, 4.5), dpi=150)
        colores = sns.color_palette("mako", len(importancias_utiles))
        importancias_utiles.plot(kind="barh", color=colores, ax=ax3, edgecolor="black", linewidth=0.5)
        ax3.set_title("Importancia Relativa de Variables Predictoras (Criterio Gini)", fontsize=11, fontweight="bold")
        ax3.set_xlabel("Importancia Normalizada (0 a 1)", fontweight="bold")
        ax3.set_ylabel("Variable Predictora", fontweight="bold")
        for i, v in enumerate(importancias_utiles):
            ax3.text(v + 0.01, i, f"{v:.3f}", va="center", fontsize=9, fontweight="bold")
        ax3.set_xlim(0, max(importancias_utiles.max() + 0.08, 0.5))
        ruta_fig3 = carpeta / "fig_importancia_variables_arbol.png"
        fig3.tight_layout()
        fig3.savefig(ruta_fig3, bbox_inches="tight")
        plt.close(fig3)

        # FIGURA 4 · ACCURACY ENTRENAMIENTO VS PRUEBAS
        profundidades = list(range(1, 11))
        acc_train_list = []
        acc_test_list = []
        for d in profundidades:
            t_d = DecisionTreeClassifier(max_depth=d, min_samples_leaf=5, random_state=42)
            t_d.fit(self.X_train, self.y_train)
            acc_train_list.append(accuracy_score(self.y_train, t_d.predict(self.X_train)) * 100)
            acc_test_list.append(accuracy_score(self.y_test, t_d.predict(self.X_test)) * 100)

        fig4, (ax4_1, ax4_2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=150)
        # Panel 1: Barras Comparativas
        etiquetas_barras = ["Entrenamiento\n(Train - 80%)", "Pruebas\n(Test - 20%)"]
        valores_acc = [self.modelo.score(self.X_train, self.y_train) * 100, acc_test_val]
        barras = ax4_1.bar(etiquetas_barras, valores_acc, color=["#1d4ed8", "#059669"], width=0.45, edgecolor="black", linewidth=1)
        ax4_1.set_ylim(0, 105)
        ax4_1.set_ylabel("Exactitud / Accuracy (%)", fontsize=11, fontweight="bold")
        ax4_1.set_title("Comparación de Accuracy: Entrenamiento vs. Pruebas\n(StandardScaler · max_depth=4)", fontsize=11, fontweight="bold", pad=10)
        for b in barras:
            h = b.get_height()
            ax4_1.text(b.get_x() + b.get_width() / 2, h + 1.5, f"{h:.2f}%", ha="center", va="bottom", fontsize=12, fontweight="bold")
        ax4_1.text(0, 40, f"Muestras: {len(self.X_train)}\nAciertos: {int(len(self.X_train)*valores_acc[0]/100)}\nError: {100-valores_acc[0]:.2f}%", ha="center", fontsize=9.5, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#1d4ed8", alpha=0.9))
        ax4_1.text(1, 40, f"Muestras: {len(self.X_test)}\nAciertos: {int(len(self.X_test)*valores_acc[1]/100)}\nError: {100-valores_acc[1]:.2f}%", ha="center", fontsize=9.5, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#059669", alpha=0.9))
        ax4_1.text(0.5, 93, f"Diferencia: {valores_acc[0]-valores_acc[1]:.2f}%\n(Sin Sobreajuste)", ha="center", fontsize=9.5, fontweight="bold", color="#374151", bbox=dict(boxstyle="round,pad=0.4", facecolor="#f3f4f6", edgecolor="#9ca3af"))

        # Panel 2: Curva de Complejidad
        ax4_2.plot(profundidades, acc_train_list, marker="o", color="#1d4ed8", linewidth=2.5, label="Entrenamiento (Train)")
        ax4_2.plot(profundidades, acc_test_list, marker="s", color="#059669", linewidth=2.5, label="Pruebas (Test)")
        ax4_2.axvline(4, color="#dc2626", linestyle="--", linewidth=1.5, label="Seleccionada (max_depth=4)")
        ax4_2.scatter([4], [acc_test_list[3]], color="#dc2626", s=100, zorder=5)
        ax4_2.annotate(f"Punto Óptimo\nTest: {acc_test_list[3]:.2f}%\nTrain: {acc_train_list[3]:.2f}%", xy=(4, acc_test_list[3]), xytext=(5.2, 75),
                     arrowprops=dict(facecolor="#dc2626", shrink=0.08, width=1.5, headwidth=6),
                     fontsize=9.5, fontweight="bold", bbox=dict(boxstyle="round,pad=0.4", facecolor="#fef2f2", edgecolor="#dc2626"))
        ax4_2.set_title("Curva de Aprendizaje y Sobreajuste por Profundidad\n(Compromiso Sesgo - Varianza)", fontsize=11, fontweight="bold", pad=10)
        ax4_2.set_xlabel("Profundidad Máxima del Árbol (max_depth)", fontsize=11, fontweight="bold")
        ax4_2.set_ylabel("Accuracy (%)", fontsize=11, fontweight="bold")
        ax4_2.set_xticks(profundidades)
        ax4_2.set_ylim(65, 102)
        ax4_2.legend(loc="lower right", frameon=True, fontsize=9.5)
        ax4_2.axvspan(1, 2.5, alpha=0.1, color="orange")
        ax4_2.axvspan(5.5, 10, alpha=0.1, color="red")
        ax4_2.text(1.75, 67, "Subajuste", ha="center", fontsize=8, color="#b45309", fontweight="bold")
        ax4_2.text(7.5, 67, "Sobreajuste (Overfitting)", ha="center", fontsize=8, color="#b91c1c", fontweight="bold")

        fig4.tight_layout()
        ruta_fig4 = carpeta / "fig_accuracy_train_test.png"
        fig4.savefig(ruta_fig4, bbox_inches="tight")
        plt.close(fig4)

        print("[OK] Figuras del Árbol de Decisión generadas exitosamente en:", carpeta)
        return {
            "fig_arbol": str(ruta_fig1),
            "fig_matriz": str(ruta_fig2),
            "fig_importancia": str(ruta_fig3),
            "fig_accuracy": str(ruta_fig4)
        }

    def generar_arboles_divididos(self, carpeta_salida="analisis/figuras"):
        """
        Divide la estructura del árbol de decisión en 2 subárboles altamente legibles
        a partir de la partición raíz óptima (VEHICULOS_EXENTOS <= 1.21 vs > 1.21):
        1. Subárbol Izquierdo (Régimen Habitual: 80.7% de los datos).
        2. Subárbol Derecho (Régimen de Picos Críticos: 19.3% de los datos).
        3. Vista Macro (Nivel 1 y 2).
        4. Panel Consolidado con los 2 subárboles ordenados verticalmente.
        """
        carpeta = resolver_ruta(carpeta_salida)
        carpeta.mkdir(parents=True, exist_ok=True)

        if self.modelo is None:
            self.entrenar_arbol_clasificacion(tipo_escalamiento="standard", max_depth=4)

        feat_idx = self.modelo.tree_.feature[0]
        threshold = self.modelo.tree_.threshold[0]
        feat_name = self.feature_names[feat_idx]

        mask_left = self.X_train[feat_name] <= threshold
        mask_right = self.X_train[feat_name] > threshold

        tree_left = DecisionTreeClassifier(max_depth=3, min_samples_split=10, min_samples_leaf=5, random_state=42)
        tree_left.fit(self.X_train[mask_left], self.y_train[mask_left])

        tree_right = DecisionTreeClassifier(max_depth=3, min_samples_split=10, min_samples_leaf=5, random_state=42)
        tree_right.fit(self.X_train[mask_right], self.y_train[mask_right])

        etiquetas = sorted(list(set(self.y_train)))

        # 1. Subárbol Izquierdo
        fig_l, ax_l = plt.subplots(figsize=(13, 6.5), dpi=150)
        plot_tree(tree_left, feature_names=self.feature_names, class_names=[str(e) for e in etiquetas],
                  filled=True, rounded=True, fontsize=9, ax=ax_l)
        ax_l.set_title(f"PARTE 1: Subárbol Rama Izquierda · Régimen de Tráfico Habitual ({feat_name} <= {threshold:.2f})\n"
                       f"AUTOGEST · Muestras: {mask_left.sum()} (80.7% del entrenamiento) | Predominio: Niveles Bajo y Medio",
                       fontsize=11, fontweight="bold", pad=12)
        fig_l.tight_layout()
        ruta_l = carpeta / "fig_arbol_rama_izquierda.png"
        fig_l.savefig(ruta_l, bbox_inches="tight")
        plt.close(fig_l)

        # 2. Subárbol Derecho
        fig_r, ax_r = plt.subplots(figsize=(10, 5.5), dpi=150)
        plot_tree(tree_right, feature_names=self.feature_names, class_names=[str(e) for e in etiquetas],
                  filled=True, rounded=True, fontsize=10, ax=ax_r)
        ax_r.set_title(f"PARTE 2: Subárbol Rama Derecha · Régimen de Alta Contingencia ({feat_name} > {threshold:.2f})\n"
                       f"AUTOGEST · Muestras: {mask_right.sum()} (19.3% del entrenamiento) | Predominio: Nivel Alto de Siniestralidad",
                       fontsize=11, fontweight="bold", pad=12)
        fig_r.tight_layout()
        ruta_r = carpeta / "fig_arbol_rama_derecha.png"
        fig_r.savefig(ruta_r, bbox_inches="tight")
        plt.close(fig_r)

        # 3. Vista Macro
        tree_macro = DecisionTreeClassifier(max_depth=2, random_state=42)
        tree_macro.fit(self.X_train, self.y_train)
        fig_m, ax_m = plt.subplots(figsize=(10, 4.8), dpi=150)
        plot_tree(tree_macro, feature_names=self.feature_names, class_names=[str(e) for e in etiquetas],
                  filled=True, rounded=True, fontsize=10, ax=ax_m)
        ax_m.set_title("Árbol de Decisión General (Estructura Macro · Niveles 1 y 2)\n"
                       "División Raíz Inicial que Segmenta el Comportamiento de Siniestralidad",
                       fontsize=11, fontweight="bold", pad=12)
        fig_m.tight_layout()
        ruta_m = carpeta / "fig_arbol_macro_nivel2.png"
        fig_m.savefig(ruta_m, bbox_inches="tight")
        plt.close(fig_m)

        # 4. Panel Consolidado
        fig_div, (ax_d1, ax_d2) = plt.subplots(2, 1, figsize=(14, 11), dpi=150)
        plot_tree(tree_left, feature_names=self.feature_names, class_names=[str(e) for e in etiquetas],
                  filled=True, rounded=True, fontsize=8, ax=ax_d1)
        ax_d1.set_title(f"SUBÁRBOL 1 (Rama Izquierda · Régimen Habitual): VEHICULOS_EXENTOS <= {threshold:.2f} (80.7% de los datos)",
                        fontsize=11, fontweight="bold", color="#1e3a8a")

        plot_tree(tree_right, feature_names=self.feature_names, class_names=[str(e) for e in etiquetas],
                  filled=True, rounded=True, fontsize=9, ax=ax_d2)
        ax_d2.set_title(f"SUBÁRBOL 2 (Rama Derecha · Régimen de Contingencia/Pico): VEHICULOS_EXENTOS > {threshold:.2f} (19.3% de los datos)",
                        fontsize=11, fontweight="bold", color="#991b1b")

        fig_div.tight_layout()
        ruta_div = carpeta / "fig_arbol_dividido_2_ramas.png"
        fig_div.savefig(ruta_div, bbox_inches="tight")
        plt.close(fig_div)

        print("[OK] Figuras del árbol dividido generadas exitosamente en:", carpeta)
        return {
            "fig_macro": str(ruta_m),
            "fig_subarbol_izq": str(ruta_l),
            "fig_subarbol_der": str(ruta_r),
            "fig_consolidada": str(ruta_div)
        }
