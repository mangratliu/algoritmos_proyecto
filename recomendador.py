import csv
from collections import defaultdict

class Grafo:
    def _init_(self):
        self.nodos = {}  # Almacena los nodos con su información
        self.aristas = defaultdict(list)  # Almacena las conexiones entre nodos
        self.titulo_a_indice = {}  # Diccionario de título a índice
        self.indice_a_titulo = {}  # Diccionario de índice a título
        self.contador_nodos = 0  # Contador para asignar índices

    def agregar_pelicula(self, titulo, rating, votos, duracion, director, genero, año):
        if titulo in self.nodos:
          #print(f"El título '{titulo}' ya está en el grafo, no se agregará de nuevo.")
          return
        """Agrega una película al grafo."""
        self.nodos[titulo] = {
            "rating": rating,
            "votos": votos,
            "duracion": duracion,
            "director": director,
            "genero": genero,
            "año": año
        }
        self.titulo_a_indice[titulo] = self.contador_nodos
        self.indice_a_titulo[self.contador_nodos] = titulo
        self.contador_nodos += 1

    def agregar_arista(self, titulo1, titulo2, peso):
        """Conecta dos películas con un peso que indica la similitud."""
        if titulo1 in self.nodos and titulo2 in self.nodos:
            self.aristas[titulo1].append((titulo2, peso))
            self.aristas[titulo2].append((titulo1, peso))  # Como es no dirigido, también conectamos en el sentido inverso
        else:
            raise ValueError("Ambas películas deben existir en el grafo.")

    def cargar_desde_txt(self, archivo_txt):
        """Carga películas desde un archivo TXT delimitado por punto y coma."""
        with open(archivo_txt, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')  # Establecemos el delimitador como punto y coma
            print("Encabezados encontrados:", reader.fieldnames)  # Para depurar los encabezados
            for row in reader:
                # Extraer los valores de las columnas y validar que no estén vacíos
                try:
                    titulo = row["Título"]
                    rating = float(row["Rating"])
                    votos = self.validar_numero(row["Votos"])
                    duracion = self.validar_numero(row["Duración"])
                    director = row["Director"]
                    genero = row["Género"].split(",")  # Divide géneros por comas
                    año = self.validar_numero(row["Año"])

                    # Agregar la película al grafo
                    self.agregar_pelicula(titulo, rating, votos, duracion, director, genero, año)

                except ValueError as e:
                    print(f"Error al procesar la película: {row['Título']} - {e}")

        # Ahora que hemos cargado las películas, generamos las conexiones
        self.generar_conexiones()

    def validar_numero(self, valor):
        """Devuelve el número si es válido, o 0 si es vacío o inválido."""
        try:
            return int(valor) if valor.strip() != "" else 0
        except ValueError:
            return 0  # Si no se puede convertir, retorna 0 (o algún valor predeterminado)

    def generar_conexiones(self):
        """Genera conexiones entre películas basadas en sus atributos."""
        for p1 in self.nodos:
            for p2 in self.nodos:
                if p1 != p2:
                    peso = 0

                    # Conexión por Género común
                    if set(self.nodos[p1]["genero"]) & set(self.nodos[p2]["genero"]):
                        peso += 2  # Un medio bajo para las conexiones por género

                    # Conexión por Director común
                    if self.nodos[p1]["director"] == self.nodos[p2]["director"]:
                        peso += 3  # Un peso mayor para las conexiones por director

                    # Conexión por Año común
                    if self.nodos[p1]["año"] == self.nodos[p2]["año"]:
                        peso += 2  # Un peso intermedio para las conexiones por año
                    elif abs(self.nodos[p1]["año"] - self.nodos[p2]["año"]) <= 10:
                        peso += 1  # Un peso bajo para las conexiones por año cercano

                    # Conexión por Rating similar
                    if abs(self.nodos[p1]["rating"] - self.nodos[p2]["rating"]) < 0.5:  # Diferencia menor a 0.5
                        peso += 2  # Peso bajo para rating similar

                    # Conexión por Duración similar
                    if abs(self.nodos[p1]["duracion"] - self.nodos[p2]["duracion"]) < 10:  # Diferencia menor a 10 minutos
                        peso += 1  # Peso bajo para duración similar

                    # Conexión por Votos similares
                    if abs(self.nodos[p1]["votos"] - self.nodos[p2]["votos"]) < 50:  # Diferencia menor a 50 votos
                        peso += 1  # Peso bajo para votos similares

                    # Si el peso es mayor que 0, agregamos la conexión
                    if peso > 0:
                        self.agregar_arista(p1, p2, peso)

    def obtener_vecinos(self, titulo):
        """Devuelve las películas conectadas a la película dada."""
        return self.aristas.get(titulo, [])

    def mostrar_menu(self):
        """Método que muestra el menú y maneja las opciones del usuario"""
        while True:
            print("\n===== Menú de Búsqueda de Películas =====")
            print("1. Buscar película por criterios")
            print("2. Buscar películas similares")
            print("3. Mostrar grafo de películas")
            print("4. Salir")

            opcion = input("Elige una opción: ").strip()

            if opcion == "1":
                self.buscar_peliculas()  # Search for a movie by criteria
            elif opcion == "2":
                titulo = input("Ingresa el título de la película: ").strip()
                print(self.busqueda_por_similitud(titulo) ) # Search for similar movies
            elif opcion == "3":
                self.mostrar_matriz_adyacencia()  # Show the graph of movies
            elif opcion == "4":
                print("¡Hasta luego!")
                break
            else:
                print("Opción no válida, intenta de nuevo.")

    def buscar_pelicula(self, titulo):
        """Devuelve la información de una película."""
        return self.nodos.get(titulo, None)

    def mostrar_grafo(self):
        """Muestra el grafo completo en una sola línea."""
        for titulo, vecinos in self.aristas.items():
            # Creamos una lista para almacenar todas las conexiones
            conexiones = []
            for vecino, peso in vecinos:
                # Añadimos las conexiones en formato "titulo -> vecino (peso)"
                conexiones.append(f"{titulo} -> {vecino} (peso: {peso})")

            # Imprimimos todas las conexiones de ese nodo en una sola línea
            if conexiones:
                print(", ".join(conexiones))

    def busqueda_avanzada(self, **criterios):
        """Permite buscar películas que cumplan ciertos criterios."""
        resultados = []

        for titulo, info in self.nodos.items():
            coincide = True
            for campo, valor in criterios.items():
                if campo in info:
                    if isinstance(info[campo], list):  # Para atributos como género
                        if isinstance(valor, list):
                            if not any(v.lower() in [x.lower() for x in valor] for v in info[campo]):
                                coincide = False
                                break
                        elif not any(v.lower() == valor.lower() for v in info[campo]):
                            coincide = False
                            break
                    elif isinstance(info[campo], str):
                        if info[campo].lower() != valor.lower():
                            coincide = False
                            break
                    elif info[campo] != valor:
                        coincide = False
                        break
                else:
                    coincide = False
                    break
            if coincide:
                resultados.append((titulo, info["rating"]))

        # Ordenar por rating en orden descendente
        resultados.sort(key=lambda x: x[1], reverse=True)

        # Retornar solo los 5 mejores títulos por rating
        return [titulo for titulo, _ in resultados[:5]]

    def buscar_peliculas(self):
        print("¿Qué criterio quieres utilizar para la búsqueda? (Puedes dejar en blanco para omitir)")
        director_input = input("¿Directores en particular? (Deja en blanco si no te importa): ").strip()
        generos_input = input("¿Qué géneros te interesan? (Puedes poner hasta tres, separados por coma): ").strip().split(',')
        año_input = input("¿Algún año en particular? ").strip()

        generos_input = [g.strip() for g in generos_input if g.strip()]
        if len(generos_input) > 3:
            print("Has ingresado más de tres géneros, se tomarán solo los primeros tres.")
            generos_input = generos_input[:3]

        criterios = {}
        if director_input:
            criterios["director"] = director_input
        if generos_input:
            criterios["genero"] = generos_input
        if año_input:
            try:
                criterios["año"] = int(año_input)
            except ValueError:
                print("Año no válido. Se omite el filtro por año.")

        peliculas_encontradas = self.busqueda_avanzada(**criterios)

        if peliculas_encontradas:
            print("\nTop 5 películas encontradas por rating:")
            for pelicula in peliculas_encontradas:
                print(pelicula)
        else:
            print("No se encontraron películas con los criterios dados.")

    def busqueda_por_similitud(self, titulo, umbral_peso=1):
        """
        Busca películas similares a la dada, considerando las aristas y sus pesos.
        Sólo considera aristas cuyo peso sea mayor o igual a umbral_peso.
        """
        if titulo not in self.nodos:
            return []

        similares = set()  # Usamos un conjunto para evitar duplicados
        # Obtener las películas vecinas y sus pesos
        for vecino, peso in self.obtener_vecinos(titulo):
            if peso >= umbral_peso:  # Filtramos por el peso mínimo
                similares.add((vecino, peso))  # Añadimos como tupla para ordenar posteriormente

        # Ordenamos las películas similares por el peso de la arista (similitud) y limitamos a 5 resultados
        similares_ordenados = sorted(similares, key=lambda x: x[1], reverse=True)[:5]
        
        # Devolvemos solo los títulos de las películas similares
        return [titulo for titulo, _ in similares_ordenados]

    # Representación matricial del grafo
    def matriz_adyacencia(self):
        """Genera la matriz de adyacencia del grafo."""
        # Inicializamos una matriz NxN llena de ceros
        n = len(self.nodos)
        matriz = [[0] * n for _ in range(n)]

        # Llenamos la matriz con los pesos de las aristas
        for p1 in self.nodos:  # Iterate through nodes present in self.nodos
            if p1 in self.titulo_a_indice:  # Ensure p1 is in titulo_a_indice
                indice1 = self.titulo_a_indice[p1]
                for p2, peso in self.aristas[p1]:
                    if p2 in self.titulo_a_indice:  # Ensure p2 is in titulo_a_indice
                        indice2 = self.titulo_a_indice[p2]
                        # Check if indices are within bounds before assignment
                        if 0 <= indice1 < n and 0 <= indice2 < n:
                            matriz[indice1][indice2] = peso
                            matriz[indice2][indice1] = peso  # Como es no dirigido, rellenamos también la simétrica


        return matriz

    # Mostrar la matriz de adyacencia
    def mostrar_matriz_adyacencia(self):
        """Muestra la matriz de adyacencia del grafo."""
        matriz = self.matriz_adyacencia()
        for fila in matriz:
            print(fila)

    def num_nodos(self):
        """Devuelve el número de nodos en el grafo."""
        return len(self.nodos)

    def obtener_indice_pelicula(self, titulo):
        """Devuelve el índice de la película dado su título, o None si no se encuentra."""
        return self.titulo_a_indice.get(titulo, None)

def main():
    # Crear el grafo
    grafo = Grafo()

    # Cargar las películas desde el archivo
    #archivo = input("Ingrese el nombre del archivo CSV de películas: ").strip() or "muestra.csv"
    grafo.cargar_desde_txt("muestra.txt")
    #print(grafo.busqueda_avanzada(director="nm2736117", genero="Family"))

    # Mostrar el menú para interactuar con el sistema
    grafo.mostrar_menu()

if _name_ == "_main_":
    main()