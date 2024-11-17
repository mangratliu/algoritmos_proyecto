import os
import requests
import gzip
import shutil
import pandas as pd

# Ruta base para guardar los archivos
BASE_DIR = "imdb_data"
UNZIPPED_DIR = os.path.join(BASE_DIR, "unzipped")

# URLs y nombres de los archivos IMDb
FILES = [
    "https://datasets.imdbws.com/title.basics.tsv.gz",
    "https://datasets.imdbws.com/title.ratings.tsv.gz",
    "https://datasets.imdbws.com/name.basics.tsv.gz",
    "https://datasets.imdbws.com/title.akas.tsv.gz",
    "https://datasets.imdbws.com/title.episode.tsv.gz",
    "https://datasets.imdbws.com/title.principals.tsv.gz",
    "https://datasets.imdbws.com/title.crew.tsv.gz",
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

def process_large_file(file_path, usecols=None, chunksize=100000):
    print(f"Procesando archivo grande: {file_path}...")
    total_rows = 0
    try:
        for chunk in pd.read_csv(file_path, sep="\t", low_memory=False, usecols=usecols, chunksize=chunksize):
            print(chunk.head())  # Muestra algunas filas como ejemplo
            total_rows += len(chunk)
    except Exception as e:
        print(f"Error al procesar {file_path}: {e}")
    print(f"Archivo procesado: {total_rows} filas en total.")

def process_title_principals(file_path):
    print(f"Procesando archivo grande: {file_path}...")
    dtypes = {
        "tconst": "category",
        "ordering": "int8",
        "nconst": "category",
        "category": "category",
        "job": "string",
        "characters": "string",
    }
    chunksize = 500000
    total_rows = 0
    relevant_rows = 0
    try:
        for chunk in pd.read_csv(file_path, sep="\t", low_memory=False, chunksize=chunksize, dtype=dtypes):
            # Filtrar filas relevantes (ejemplo: solo actores)
            filtered_chunk = chunk[chunk['category'] == 'actor']
            relevant_rows += len(filtered_chunk)
            total_rows += len(chunk)
            print(filtered_chunk.head())  # Mostrar algunas filas filtradas
    except Exception as e:
        print(f"Error al procesar {file_path}: {e}")
    print(f"Archivo procesado: {total_rows} filas en total, {relevant_rows} filas relevantes.")

def main():
    for file_url in FILES:
        # Descargar y descomprimir
        downloaded_path = download_file(file_url)
        decompressed_path = decompress_file(downloaded_path)

        # Procesar archivos según sus columnas específicas
        file_name = os.path.basename(file_url)
        if file_name == "title.basics.tsv.gz":
            process_large_file(decompressed_path, usecols=["tconst", "titleType", "primaryTitle"])
        elif file_name == "title.ratings.tsv.gz":
            process_large_file(decompressed_path, usecols=["tconst", "averageRating", "numVotes"])
        elif file_name == "name.basics.tsv.gz":
            process_large_file(decompressed_path, usecols=["nconst", "primaryName", "birthYear", "deathYear", "primaryProfession", "knownForTitles"])
        elif file_name == "title.akas.tsv.gz":
            process_large_file(decompressed_path, usecols=["titleId", "title", "region", "language", "isOriginalTitle"])
        elif file_name == "title.episode.tsv.gz":
            process_large_file(decompressed_path, usecols=["tconst", "parentTconst", "seasonNumber", "episodeNumber"])
        elif file_name == "title.principals.tsv.gz":
            process_title_principals(decompressed_path)  # Optimización para este archivo grande
        elif file_name == "title.crew.tsv.gz":
            process_large_file(decompressed_path, usecols=["tconst", "directors", "writers"])

if __name__ == "__main__":
    main()
