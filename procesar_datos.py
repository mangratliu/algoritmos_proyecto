import os
import pandas as pd

UNZIPPED_DIR = "imdb_data_unzipped"

def load_data(file_name, usecols=None, filters=None, dtypes=None):
    """Carga y filtra datos de un archivo TSV."""
    file_path = os.path.join(UNZIPPED_DIR, file_name)
    if not os.path.exists(file_path):
        print(f"Archivo no encontrado: {file_name}.")
        return None

    print(f"Cargando {file_name}...")
    try:
        chunks = pd.read_csv(
            file_path,
            sep="\t",
            usecols=usecols,
            dtype=dtypes,
            na_values="\\N",  # Manejo de valores nulos
            encoding="utf-8", 
            chunksize=500000
        )
        if filters:
            data = pd.concat(chunk.query(filters) for chunk in chunks)
        else:
            data = pd.concat(chunks)
        print(f"{file_name} cargado: {data.shape[0]} filas, {data.shape[1]} columnas.")
        return data
    except Exception as e:
        print(f"Error al cargar {file_name}: {e}")
        return None

def process_data():
    # Cargar y filtrar datos necesarios
    title_basics = load_data(
        "title.basics.tsv",
        usecols=["tconst", "primaryTitle", "startYear", "runtimeMinutes", "genres"],
        filters="startYear != '\\N' and runtimeMinutes != '\\N'",
        dtypes={"tconst": str, "primaryTitle": str, "startYear": str, "runtimeMinutes": str, "genres": str}
    )

    title_ratings = load_data(
        "title.ratings.tsv",
        usecols=["tconst", "averageRating"],
        dtypes={"tconst": str, "averageRating": float}
    )

    if title_basics is not None and title_ratings is not None:
        print("Uniendo datasets...")
        movies = pd.merge(title_basics, title_ratings, on="tconst", how="inner")

        # Filtrar columnas relevantes
        movies = movies[["primaryTitle", "averageRating", "runtimeMinutes", "genres", "startYear"]]
        movies.rename(columns={
            "primaryTitle": "Título",
            "averageRating": "Rating",
            "runtimeMinutes": "Duración",
            "genres": "Género",
            "startYear": "Año"
        }, inplace=True)

        # Convertir columnas a tipo numérico
        movies["Duración"] = pd.to_numeric(movies["Duración"], errors="coerce")
        movies["Año"] = pd.to_numeric(movies["Año"], errors="coerce")

        # Mostrar resumen de los datos
        print("Datos procesados:")
        print(movies.head())  # Mostrar primeras filas
        print(f"Total de películas procesadas: {len(movies)}")
        return movies
    else:
        print("Error: No se pudieron cargar los archivos necesarios.")
        return None

if __name__ == "__main__":
    processed_data = process_data()
