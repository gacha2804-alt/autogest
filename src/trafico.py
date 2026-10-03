import pandas as pd

class Trafico:
    def __init__(self, ruta):
        self.ruta = ruta
        self.df = None

    def cargar(self):
        self.df = pd.read_csv(
            self.ruta,
            encoding="utf-8-sig",
            thousands=","
        )
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

        self.df["DESDE"] = pd.to_datetime(
            self.df["Desde"].astype(str).str.strip(),
            errors="coerce"
        )
        self.df["HASTA"] = pd.to_datetime(
            self.df["Hasta"].astype(str).str.strip(),
            errors="coerce"
        )

        numericas = [
            "ValorTarifa",
            "CantidadTrafico",
            "CantidadEvasores",
            "CantidadExentos787"
        ]

        for columna in numericas:
            self.df[columna] = pd.to_numeric(
                self.df[columna], errors="coerce"
            )

        self.df = self.df.dropna(subset=["DESDE", "HASTA"])
        self.df[numericas] = self.df[numericas].fillna(0)
        self.df = self.df.drop_duplicates()

        # Mes de referencia para relacionarlo con accidentes y taller.
        self.df["MES"] = self.df["DESDE"].dt.to_period("M").astype(str)

        return self.df

    def guardar(self, ruta):
        self.df.to_csv(ruta, index=False, encoding="utf-8-sig")
