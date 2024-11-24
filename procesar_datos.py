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
            encoding="utf-8",  # Cambia a 'latin1' si persiste el problema
            chunksize=500000
        )
        if filters:
            data = pd.concat(chunk.query(filters) for chunk in chunks)
        else:
            data = pd.concat(chunks)
        print(f"{file_name} cargado: {data.shape[0]} filas, {data.shape[1]} columnas.")
        return data
    except UnicodeDecodeError:
        print(f"Error de codificación al cargar {file_name}. Prueba con otra codificación.")
        return None
    except Exception as e:
        print(f"Error al cargar {file_name}: {e}")
        return None

def process_data():
    # Cargar title.basics
    title_basics = load_data(
        "title.basics.tsv",
        usecols=["tconst", "primaryTitle", "startYear", "runtimeMinutes", "genres"],
        filters="startYear != '\\N' and runtimeMinutes != '\\N'",
        dtypes={"tconst": str, "primaryTitle": str, "startYear": str, "runtimeMinutes": str, "genres": str}
    )

    # Cargar title.ratings
    title_ratings = load_data(
        "title.ratings.tsv",
        usecols=["tconst", "averageRating"],
        dtypes={"tconst": str, "averageRating": float}
    )

    # Cargar title.principals
    title_principals = load_data(
        "title.principals.tsv",
        usecols=["tconst", "nconst", "category"],
        filters="category == 'director'",
        dtypes={"tconst": str, "nconst": str, "category": str}
    )

    # Cargar name.basics
    name_basics = load_data(
        "name.basics.tsv",
        usecols=["nconst", "primaryName"],
        dtypes={"nconst": str, "primaryName": str}
    )

    if title_basics is not None and title_ratings is not None:
        print("Uniendo title.basics y title.ratings...")
        movies = pd.merge(title_basics, title_ratings, on="tconst", how="inner")

        # Agregar directores si los archivos están disponibles
        if title_principals is not None and name_basics is not None:
            print("Agregando directores...")
            movies = pd.merge(movies, title_principals, on="tconst", how="left")
            movies = pd.merge(movies, name_basics, on="nconst", how="left")
            movies.rename(columns={"primaryName": "Director"}, inplace=True)

        # Filtrar columnas finales
        movies = movies[["primaryTitle", "averageRating", "runtimeMinutes", "Director", "genres", "startYear"]]
        movies.rename(columns={
            "primaryTitle": "Título",
            "averageRating": "Rating",
            "runtimeMinutes": "Duración",
            "genres": "Género",
            "startYear": "Año"
        }, inplace=True)

        # Convertir columnas
        movies["Duración"] = pd.to_numeric(movies["Duración"], errors="coerce")
        movies["Año"] = pd.to_numeric(movies["Año"], errors="coerce")

        # Guardar datos
        output_file = "peliculas_procesadas.csv"
        movies.to_csv(output_file, index=False)
        print(f"Datos guardados en {output_file}.")
    else:
        print("Error: No se pudieron cargar title.basics o title.ratings correctamente.")

if __name__ == "__main__":
    process_data()
