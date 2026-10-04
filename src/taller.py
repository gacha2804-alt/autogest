import pandas as pd
#clase para manejar el dataset de accidentes
class Taller:
    def __init__(self, ruta):
        self.ruta = ruta
        self.df = None

    def cargar(self):
        self.df = pd.read_csv(self.ruta, encoding="utf-8-sig")
        return self.df

    def diagnosticar(self):
        if self.df is None:
            raise ValueError("Primero debe cargar el dataset.")
        print("Dimensiones:", self.df.shape)
        print("\nColumnas:")
        print(self.df.columns.tolist())
        print("\nTipos de datos:")
        print(self.df.dtypes)
        print("\nValores nulos:")
        print(self.df.isnull().sum())
        print("\nDuplicados:", self.df.duplicated().sum())

    def limpiar(self):
        if self.df is None:
            raise ValueError("Primero debe cargar el dataset.")

        self.df.columns = self.df.columns.str.strip()

        self.df["FECHA"] = pd.to_datetime(
            self.df["Repair Date"],
            errors="coerce"
        )

        numericas = [
            "Total Cost",
            "Service Duration Hours",
            "Estimated Cost",
            "Mileage at Service",
            "Technician Rating",
            "Tow Distance Miles"
        ]

        for columna in numericas:
            self.df[columna] = pd.to_numeric(
                self.df[columna], errors="coerce"
            )

        self.df = self.df.dropna(subset=["FECHA"])
        self.df = self.df.drop_duplicates()

        return self.df

    def guardar(self, ruta):
        self.df.to_csv(ruta, index=False, encoding="utf-8-sig")
