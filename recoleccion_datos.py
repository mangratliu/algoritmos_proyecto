import os
import requests
import gzip
import shutil
import pandas as pd

# Ruta base para guardar los archivos
BASE_DIR = "imdb_data"
UNZIPPED_DIR = os.path.join(BASE_DIR, "unzipped")

# URLs y nombres de los archivos IMDb necesarios
FILES = [
    "https://datasets.imdbws.com/title.basics.tsv.gz",
    "https://datasets.imdbws.com/title.ratings.tsv.gz",
    "https://datasets.imdbws.com/title.principals.tsv.gz",
]

def download_file(url, download_dir=BASE_DIR):
    os.makedirs(download_dir, exist_ok=True)
    file_name = os.path.join(download_dir, os.path.basename(url))
    print(f"Descargando {os.path.basename(url)}...")
    with requests.get(url, stream=True) as response:
        if response.status_code == 200:
            with open(file_name, "wb") as f:
                shutil.copyfileobj(response.raw, f)
            print(f"{os.path.basename(url)} descargado correctamente.")
        else:
            print(f"Error al descargar {os.path.basename(url)}: {response.status_code}")
    return file_name

def decompress_file(file_path, unzipped_dir=UNZIPPED_DIR):
    os.makedirs(unzipped_dir, exist_ok=True)
    decompressed_path = os.path.join(unzipped_dir, os.path.splitext(os.path.basename(file_path))[0])
    print(f"Descomprimiendo {file_path}...")
    with gzip.open(file_path, "rb") as f_in:
        with open(decompressed_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    print(f"{file_path} descomprimido en {decompressed_path}.")
    return decompressed_path

def process_title_basics(file_path):
    print("Procesando title.basics.tsv...")
    usecols = ["tconst", "primaryTitle", "startYear", "runtimeMinutes", "genres"]
    try:
        df = pd.read_csv(file_path, sep="\t", usecols=usecols, na_values="\\N", dtype=str)
        print(f"title.basics.tsv procesado: {len(df)} filas.")
        return df
    except Exception as e:
        print(f"Error al procesar title.basics.tsv: {e}")
        return pd.DataFrame()

def process_title_ratings(file_path):
    print("Procesando title.ratings.tsv...")
    usecols = ["tconst", "averageRating", "numVotes"]
    try:
        df = pd.read_csv(file_path, sep="\t", usecols=usecols, na_values="\\N", dtype={"tconst": str, "averageRating": float, "numVotes": int})
        print(f"title.ratings.tsv procesado: {len(df)} filas.")
        return df
    except Exception as e:
        print(f"Error al procesar title.ratings.tsv: {e}")
        return pd.DataFrame()

def process_title_principals(file_path):
    print("Procesando title.principals.tsv para directores...")
    usecols = ["tconst", "category", "nconst"]
    try:
        df = pd.read_csv(file_path, sep="\t", usecols=usecols, na_values="\\N", dtype=str)
        # Filtrando solo los directores
        directors_df = df[df["category"] == "director"]
        print(f"title.principals.tsv procesado: {len(directors_df)} filas de directores.")
        return directors_df
    except Exception as e:
        print(f"Error al procesar title.principals.tsv: {e}")
        return pd.DataFrame()

def main():
    dataframes = {}

    # Descargar y descomprimir archivos
    for file_url in FILES:
        downloaded_path = download_file(file_url)
        decompressed_path = decompress_file(downloaded_path)
        
        # Procesar archivos según sus características
        file_name = os.path.basename(file_url)
        if file_name == "title.basics.tsv.gz":
            dataframes["basics"] = process_title_basics(decompressed_path)
        elif file_name == "title.ratings.tsv.gz":
            dataframes["ratings"] = process_title_ratings(decompressed_path)
        elif file_name == "title.principals.tsv.gz":
            dataframes["principals"] = process_title_principals(decompressed_path)
    
    # Unir datasets
    print("Uniendo datasets...")
    basics = dataframes.get("basics", pd.DataFrame())
    ratings = dataframes.get("ratings", pd.DataFrame())
    principals = dataframes.get("principals", pd.DataFrame())

    if not basics.empty and not ratings.empty:
        merged_df = basics.merge(ratings, on="tconst", how="inner")
        print("Unión de title.basics y title.ratings completada.")
    else:
        print("Error: No se pudo unir basics y ratings.")
        return

    if not principals.empty:
        merged_df = merged_df.merge(principals, on="tconst", how="left")
        print("Unión con directores completada.")
    else:
        print("Advertencia: No se encontraron datos de directores.")
    
    # Filtrar columnas relevantes
    final_df = merged_df[["primaryTitle", "averageRating", "numVotes", "runtimeMinutes", "nconst", "genres", "startYear"]]
    final_df.rename(columns={
        "primaryTitle": "Título",
        "averageRating": "Rating",
        "numVotes": "Votos",
        "runtimeMinutes": "Duración",
        "nconst": "Director",
        "genres": "Género",
        "startYear": "Año"
    }, inplace=True)

    print(f"Datos procesados: {len(final_df)} filas.")
    print(final_df.head())

    # Guardar datos finales en un archivo CSV completo
    final_df.to_csv("peliculas_procesadas.csv", index=False)
    print("Datos guardados en peliculas_procesadas.csv.")

    # Crear una muestra de 3,000 datos y guardar en un archivo separado
    muestra = final_df.sample(n=3000, random_state=42) if len(final_df) > 3000 else final_df
    muestra.to_csv("muestra.csv", index=False)
    print("Muestra de 3,000 filas guardada en muestra.csv.")

if __name__ == "__main__":
    main()
