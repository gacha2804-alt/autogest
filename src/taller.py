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


class Taller:
    """Clase modular para diagnóstico, limpieza y exportación del dataset de Taller y Mantenimiento."""

    def __init__(self, ruta="dataset/taller.csv"):
        self.ruta = resolver_ruta(ruta)
        self.df = None

    def cargar(self, chunksize=None):
        """Carga el dataset de taller y servicio vehicular."""
        self.ruta = resolver_ruta(self.ruta)
        self.df = pd.read_csv(self.ruta, low_memory=False)
        return self.df

    def diagnosticar(self):
        """Presenta un diagnóstico de dimensiones, nulos y duplicados."""
        if self.df is None:
            raise ValueError("Debe cargar los datos primero con .cargar()")
        print("=" * 80)
        print("DIAGNÓSTICO INICIAL · TALLER Y MANTENIMIENTO DE FLOTA")
        print("=" * 80)
        print("Filas:", f"{len(self.df):,}")
        print("Columnas:", len(self.df.columns))
        print("\nValores nulos por columna:")
        print(self.df.isnull().sum())
        print("\nDuplicados exactos:", f"{self.df.duplicated().sum():,}")

    def limpiar(self):
        """Ejecuta el pipeline de limpieza y estandarización del dataset de taller."""
        if self.df is None:
            raise ValueError("Debe cargar los datos primero con .cargar()")

        self.df = self.df.copy()

        # 1. Deduplicación
        self.df = self.df.drop_duplicates().reset_index(drop=True)

        # 2. Normalización de campos de texto
        cols_texto = [
            "Vehicle Type", "Service Type", "Urgency Level",
            "Customer Type", "Payment Method", "Service Status"
        ]
        for col in cols_texto:
            if col in self.df.columns:
                self.df[col] = self.df[col].apply(normalizar_texto)

        # 3. Clasificación canónica de vehículo homologable a peajes y movilidad
        def clasificar_vehiculo(v):
            v_str = str(v).strip().upper()
            if v_str in ["CAR", "SUV"]:
                return "LIVIANO"
            elif v_str in ["BUS", "VAN"]:
                return "TRANSPORTE_PASAJEROS"
            elif v_str in ["TRUCK"]:
                return "CARGA_PESADO"
            return "OTRO"

        if "Vehicle Type" in self.df.columns:
            self.df["TIPO_VEHICULO"] = self.df["Vehicle Type"].apply(clasificar_vehiculo)

        # 4. Formateo de fecha de reparación y extracción temporal
        if "Repair Date" in self.df.columns:
            self.df["FECHA"] = pd.to_datetime(self.df["Repair Date"], errors="coerce")
            self.df["AÑO"] = self.df["FECHA"].dt.year
            self.df["MES"] = self.df["FECHA"].dt.month

            mediana_anio = int(self.df["AÑO"].dropna().median())
            mediana_mes = int(self.df["MES"].dropna().median())

            self.df["AÑO"] = self.df["AÑO"].fillna(mediana_anio).astype(int)
            self.df["MES"] = self.df["MES"].fillna(mediana_mes).astype(int)

        # 5. Limpieza y conversión de métricas cuantitativas
        metricas_float = [
            "Total Cost", "Estimated Cost", "Service Duration Hours",
            "Mileage at Service", "Technician Rating", "Tow Distance Miles"
        ]
        for m in metricas_float:
            if m in self.df.columns:
                self.df[m] = pd.to_numeric(self.df[m], errors="coerce")
                if m in ["Total Cost", "Service Duration Hours", "Mileage at Service"]:
                    mediana = float(self.df[m].dropna().median())
                    self.df[m] = self.df[m].fillna(mediana)
                else:
                    self.df[m] = self.df[m].fillna(0)

        # Garantizar que costos y tiempos no sean negativos
        if "Total Cost" in self.df.columns:
            self.df = self.df[self.df["Total Cost"] >= 0].copy()

        return self.df

    def guardar(self, ruta_salida="dataset/taller_limpio.csv"):
        """Guarda el dataset de taller limpio en disco."""
        if self.df is None:
            raise ValueError("No hay datos limpios para guardar.")
        salida = Path(ruta_salida)
        salida.parent.mkdir(parents=True, exist_ok=True)
        self.df.to_csv(salida, index=False, encoding="utf-8-sig")
        print("[OK] Archivo de taller limpio guardado correctamente en:", salida)
        print(f"Dimensiones finales: {self.df.shape[0]:,} filas × {self.df.shape[1]} columnas")
