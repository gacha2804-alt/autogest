import unicodedata
from pathlib import Path
import pandas as pd


def resolver_ruta(ruta):
    """Resuelve la ruta del archivo de forma defensiva desde cualquier directorio de trabajo."""
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


def sin_tildes(texto):
    """Elimina acentos y tildes preservando los caracteres base."""
    if pd.isna(texto):
        return texto
    texto = str(texto)
    return "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )


def normalizar_texto(texto):
    """Limpia espacios en blanco, remueve tildes y convierte a mayúsculas consistentes."""
    if pd.isna(texto):
        return texto
    texto = sin_tildes(texto)
    texto = texto.strip().upper()
    while "  " in texto:
        texto = texto.replace("  ", " ")
    return texto


class Trafico:
    """Clase modular para diagnóstico, limpieza y exportación del dataset de Tráfico y Peajes."""

    def __init__(self, ruta="dataset/trafico.csv"):
        self.ruta = resolver_ruta(ruta)
        self.df = None

    def cargar(self):
        """Carga el dataset de tráfico vehicular en peajes."""
        self.ruta = resolver_ruta(self.ruta)
        self.df = pd.read_csv(self.ruta, low_memory=False)
        return self.df

    def diagnosticar(self):
        """Presenta un diagnóstico de dimensiones, nulos y duplicados."""
        if self.df is None:
            raise ValueError("Debe cargar los datos primero con .cargar()")
        print("=" * 80)
        print("DIAGNÓSTICO INICIAL · TRÁFICO VEHICULAR Y PEAJES")
        print("=" * 80)
        print("Filas:", f"{len(self.df):,}")
        print("Columnas:", len(self.df.columns))
        print("\nValores nulos por columna:")
        print(self.df.isnull().sum())
        print("\nDuplicados exactos:", f"{self.df.duplicated().sum():,}")

    def limpiar(self):
        """Ejecuta el pipeline de limpieza y estandarización del dataset de tráfico."""
        if self.df is None:
            raise ValueError("Debe cargar los datos primero con .cargar()")

        self.df = self.df.copy()

        # 1. Deduplicación
        self.df = self.df.drop_duplicates().reset_index(drop=True)

        # 2. Normalización de texto en estaciones de peaje
        if "Peaje" in self.df.columns:
            self.df["Peaje"] = self.df["Peaje"].apply(normalizar_texto)

        # 3. Limpieza de columnas numéricas (remoción de separadores de miles)
        cols_numericas = ["CantidadTrafico", "CantidadEvasores", "CantidadExentos787", "ValorTarifa"]
        for c in cols_numericas:
            if c in self.df.columns:
                limpio = (
                    self.df[c]
                    .astype(str)
                    .str.replace(",", "", regex=False)
                    .str.replace(".", "", regex=False)
                    .str.strip()
                )
                self.df[c] = pd.to_numeric(limpio, errors="coerce").fillna(0)

        # 4. Homologación de CategoriaTarifa a tipología vehicular estándar
        def homologar_tarifa(cat):
            cat_str = str(cat).strip().upper()
            if cat_str in [
                "I", "IE", "IEE", "IEEE", "IE1", "IE2", "IE3",
                "IE4", "IE10", "IE1A", "IE1B", "IE2A", "IE2B", "UNICA", "EXCI"
            ]:
                return "LIVIANO"
            elif cat_str in ["II", "IIE", "IIIE", "IIE1", "IIE2", "IIA", "POLCA", "EXCII"]:
                return "TRANSPORTE_PASAJEROS"
            else:
                return "CARGA_PESADO"

        if "CategoriaTarifa" in self.df.columns:
            self.df["TIPO_VEHICULO"] = self.df["CategoriaTarifa"].apply(homologar_tarifa)

        # 5. Formateo temporal desde columna 'Desde'
        if "Desde" in self.df.columns:
            fechas_desde = pd.to_datetime(self.df["Desde"], errors="coerce")
            self.df["FECHA"] = fechas_desde
            self.df["AÑO"] = self.df["FECHA"].dt.year
            self.df["MES"] = self.df["FECHA"].dt.month

            mediana_anio = int(self.df["AÑO"].dropna().median())
            mediana_mes = int(self.df["MES"].dropna().median())

            self.df["AÑO"] = self.df["AÑO"].fillna(mediana_anio).astype(int)
            self.df["MES"] = self.df["MES"].fillna(mediana_mes).astype(int)

        # 6. Recaudo estimado del registro (Tráfico × Valor Tarifa)
        self.df["RECAUDO_ESTIMADO"] = self.df["CantidadTrafico"] * self.df["ValorTarifa"]

        return self.df

    def guardar(self, ruta_salida="dataset/trafico_limpio.csv"):
        """Guarda el archivo de tráfico limpio en disco."""
        if self.df is None:
            raise ValueError("No hay datos limpios para guardar.")
        salida = Path(ruta_salida)
        salida.parent.mkdir(parents=True, exist_ok=True)
        self.df.to_csv(salida, index=False, encoding="utf-8-sig")
        print("[OK] Archivo de tráfico limpio guardado correctamente en:", salida)
        print(f"Dimensiones finales: {self.df.shape[0]:,} filas × {self.df.shape[1]} columnas")
