import os
import pandas as pd

UNZIPPED_DIR = "imdb_data_unzipped"

def load_data(file_name, usecols=None, dtypes=None, filters=None):
    """Carga y filtra datos de un archivo TSV."""
    file_path = os.path.join(UNZIPPED_DIR, file_name)
    print(f"Cargando {file_name}...")
    try:
        # Carga inicial con las columnas seleccionadas
        chunks = pd.read_csv(
            file_path, 
            sep="\t", 
            low_memory=False, 
            usecols=usecols, 
            dtype=dtypes, 
            chunksize=500000  # Carga en partes
        )
        
        # Filtrar los datos si hay condiciones
        if filters:
            data = pd.concat(chunk.query(filters) for chunk in chunks)
        else:
            data = pd.concat(chunks)
        
        print(f"{file_name} cargado con éxito: {data.shape[0]} filas, {data.shape[1]} columnas.")
        return data
    except FileNotFoundError:
        print(f"Archivo no encontrado: {file_name}.")
        return None
    except Exception as e:
        print(f"Error al cargar {file_name}: {e}")
        return None

def process_data():
    # Cargar title.basics con filtrado inicial (solo películas no adultas)
    title_basics = load_data(
        "title.basics.tsv",
        usecols=["tconst", "titleType", "primaryTitle", "isAdult", "startYear", "genres"],
        filters="titleType == 'movie' and isAdult == '0'"
    )
    
    # Cargar title.ratings con todas las filas
    title_ratings = load_data(
        "title.ratings.tsv",
        usecols=["tconst", "averageRating", "numVotes"]
    )

    # Cargar otros archivos necesarios
    title_principals = load_data(
        "title.principals.tsv",
        usecols=["tconst", "nconst", "category"],
    )

    name_basics = load_data(
        "name.basics.tsv",
        usecols=["nconst", "primaryName", "primaryProfession"]
    )

    if title_basics is not None and title_ratings is not None:
        # Unir title.basics y title.ratings
        print("Uniendo title.basics y title.ratings...")
        merged_data = pd.merge(title_basics, title_ratings, on="tconst", how="inner")

        # Filtrar películas con más de 1000 votos y calificación > 8
        filtered_movies = merged_data[
            (merged_data["numVotes"] >= 1000) & 
            (merged_data["averageRating"] >= 8)
        ]
        print(f"Películas filtradas: {filtered_movies.shape[0]}")

        # Mostrar películas con mayor calificación
        print("\nPelículas con mayor calificación:")
        print(filtered_movies.sort_values(by="averageRating", ascending=False).head(10))

        # Resumen por género
        genres_count = filtered_movies["genres"].str.split(",").explode().value_counts()
        print("\nCantidad de películas por género:")
        print(genres_count)

    # Procesar relaciones de personas si los archivos están disponibles
    if title_principals is not None and name_basics is not None:
        principals_with_names = pd.merge(title_principals, name_basics, on="nconst", how="inner")
        print(f"\nDatos combinados (personas y títulos): {principals_with_names.shape[0]} filas.")

        # Analizar directores
        directors = principals_with_names[principals_with_names["category"] == "director"]
        top_directors = directors["primaryName"].value_counts().head(10)
        print("\nDirectores más frecuentes:")
        print(top_directors)

    print("\nProcesamiento completado.")

if __name__ == "__main__":
    process_data()
