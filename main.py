import csv
import unicodedata
from pathlib import Path

# El CSV se guarda en la misma carpeta que este archivo main.py.
ARCHIVO_CSV = Path(__file__).with_name("paises.csv")
CAMPOS = ["nombre", "poblacion", "superficie", "continente"]


def normalizar(texto):
    """Pasa a minúsculas y quita tildes para comparar textos."""
    texto = unicodedata.normalize("NFD", str(texto))
    texto = "".join(caracter for caracter in texto if unicodedata.category(caracter) != "Mn")
    return texto.strip().casefold()


def cargar_paises():
    """Lee el CSV y devuelve una lista de diccionarios válidos."""
    if not ARCHIVO_CSV.exists():
        guardar_paises([])
        return []

    paises = []
    nombres = set()

    try:
        with ARCHIVO_CSV.open("r", newline="", encoding="utf-8-sig") as archivo:
            lector = csv.DictReader(archivo)

            if lector.fieldnames is None or lector.fieldnames != CAMPOS:
                print("Error: el CSV debe tener estos encabezados:")
                print(",".join(CAMPOS))
                return []

            for numero_fila, fila in enumerate(lector, start=2):
                try:
                    nombre = (fila.get("nombre") or "").strip()
                    continente = (fila.get("continente") or "").strip()
                    poblacion_texto = (fila.get("poblacion") or "").strip()
                    superficie_texto = (fila.get("superficie") or "").strip()

                    if not nombre or not continente or not poblacion_texto or not superficie_texto:
                        raise ValueError("hay campos vacíos")

                    poblacion = int(poblacion_texto)
                    superficie = int(superficie_texto)

                    if poblacion < 0:
                        raise ValueError("la población no puede ser negativa")
                    if superficie <= 0:
                        raise ValueError("la superficie debe ser mayor que cero")
                    if normalizar(nombre) in nombres:
                        raise ValueError("el país está repetido")

                    paises.append({
                        "nombre": nombre,
                        "poblacion": poblacion,
                        "superficie": superficie,
                        "continente": continente
                    })
                    nombres.add(normalizar(nombre))

                except (ValueError, TypeError) as error:
                    print(f"Aviso: se omitió la fila {numero_fila}: {error}.")

    except (OSError, UnicodeError, csv.Error) as error:
        print(f"Error al leer el archivo CSV: {error}")

    return paises


def guardar_paises(paises):
    """Guarda todos los registros en paises.csv."""
    try:
        with ARCHIVO_CSV.open("w", newline="", encoding="utf-8-sig") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=CAMPOS)
            escritor.writeheader()
            escritor.writerows(paises)
        return True
    except OSError as error:
        print(f"Error al guardar los datos: {error}")
        return False


def mostrar_paises(paises):
    if not paises:
        print("No se encontraron países.")
        return

    print(f'{"Nombre":<18} {"Población":>15} {"Superficie km²":>18} {"Continente":<18}')
    print("-" * 75)
    for pais in paises:
        print(
            f'{pais["nombre"]:<18} '
            f'{pais["poblacion"]:>15,} '
            f'{pais["superficie"]:>18,} '
            f'{pais["continente"]:<18}'
        )


def leer_texto(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("Este campo no puede quedar vacío.")


def leer_entero(mensaje, minimo=0):
    while True:
        try:
            valor = int(input(mensaje).strip())
            if valor < minimo:
                print(f"El valor debe ser mayor o igual a {minimo}.")
                continue
            return valor
        except ValueError:
            print("Ingresá un número entero válido.")


def agregar_pais(paises):
    print("\n--- Agregar país ---")
    nombre = leer_texto("Nombre: ")

    if any(normalizar(p["nombre"]) == normalizar(nombre) for p in paises):
        print("Error: ya existe un país con ese nombre.")
        return

    poblacion = leer_entero("Población (habitantes): ", 0)
    superficie = leer_entero("Superficie en km²: ", 1)
    continente = leer_texto("Continente: ")

    paises.append({
        "nombre": nombre,
        "poblacion": poblacion,
        "superficie": superficie,
        "continente": continente
    })

    if guardar_paises(paises):
        print("País agregado y guardado correctamente en paises.csv.")


def actualizar_pais(paises):
    print("\n--- Actualizar país ---")
    nombre = leer_texto("Nombre del país que querés actualizar: ")
    pais = next(
        (p for p in paises if normalizar(p["nombre"]) == normalizar(nombre)),
        None
    )

    if pais is None:
        print("No se encontró ese país.")
        return

    print(f'País: {pais["nombre"]}')
    pais["poblacion"] = leer_entero("Nueva población: ", 0)
    pais["superficie"] = leer_entero("Nueva superficie en km²: ", 1)

    if guardar_paises(paises):
        print("Datos actualizados y guardados correctamente en paises.csv.")


def buscar_pais(paises):
    texto = leer_texto("Ingresá el nombre completo o una parte: ")
    resultados = [
        p for p in paises
        if normalizar(texto) in normalizar(p["nombre"])
    ]
    mostrar_paises(resultados)


def filtrar_paises(paises):
    print("\n1. Por continente")
    print("2. Por rango de población")
    print("3. Por rango de superficie")
    opcion = input("Elegí un filtro: ").strip()

    if opcion == "1":
        continente = leer_texto("Continente: ")
        resultados = [
            p for p in paises
            if normalizar(p["continente"]) == normalizar(continente)
        ]
    elif opcion in ("2", "3"):
        if opcion == "2":
            campo = "poblacion"
            minimo = leer_entero("Población mínima: ", 0)
            maximo = leer_entero("Población máxima: ", minimo)
        else:
            campo = "superficie"
            minimo = leer_entero("Superficie mínima en km²: ", 1)
            maximo = leer_entero("Superficie máxima en km²: ", minimo)

        resultados = [p for p in paises if minimo <= p[campo] <= maximo]
    else:
        print("Opción inválida.")
        return

    mostrar_paises(resultados)


def ordenar_paises(paises):
    print("\n1. Nombre A-Z")
    print("2. Población ascendente")
    print("3. Población descendente")
    print("4. Superficie ascendente")
    print("5. Superficie descendente")
    opcion = input("Elegí cómo ordenar: ").strip()

    opciones = {
        "1": ("nombre", False),
        "2": ("poblacion", False),
        "3": ("poblacion", True),
        "4": ("superficie", False),
        "5": ("superficie", True)
    }

    if opcion not in opciones:
        print("Opción inválida.")
        return

    campo, reverso = opciones[opcion]
    if campo == "nombre":
        ordenados = sorted(paises, key=lambda p: normalizar(p[campo]), reverse=reverso)
    else:
        ordenados = sorted(paises, key=lambda p: p[campo], reverse=reverso)

    mostrar_paises(ordenados)


def mostrar_estadisticas(paises):
    if not paises:
        print("No hay datos suficientes para calcular estadísticas.")
        return

    mayor = max(paises, key=lambda p: p["poblacion"])
    menor = min(paises, key=lambda p: p["poblacion"])
    promedio_poblacion = sum(p["poblacion"] for p in paises) / len(paises)
    promedio_superficie = sum(p["superficie"] for p in paises) / len(paises)

    por_continente = {}
    for pais in paises:
        continente = pais["continente"]
        por_continente[continente] = por_continente.get(continente, 0) + 1

    print("\n--- Estadísticas ---")
    print(f'País con mayor población: {mayor["nombre"]} ({mayor["poblacion"]:,})')
    print(f'País con menor población: {menor["nombre"]} ({menor["poblacion"]:,})')
    print(f"Promedio de población: {promedio_poblacion:,.2f}")
    print(f"Promedio de superficie: {promedio_superficie:,.2f} km²")
    print("Cantidad de países por continente:")
    for continente, cantidad in sorted(por_continente.items()):
        print(f"  {continente}: {cantidad}")


def menu():
    paises = cargar_paises()

    while True:
        print("\n===== GESTIÓN DE DATOS DE PAÍSES =====")
        print("1. Mostrar todos los países")
        print("2. Agregar un país")
        print("3. Actualizar población y superficie")
        print("4. Buscar un país")
        print("5. Filtrar países")
        print("6. Ordenar países")
        print("7. Mostrar estadísticas")
        print("0. Guardar y salir")

        opcion = input("Elegí una opción: ").strip()

        if opcion == "1":
            mostrar_paises(paises)
        elif opcion == "2":
            agregar_pais(paises)
        elif opcion == "3":
            actualizar_pais(paises)
        elif opcion == "4":
            buscar_pais(paises)
        elif opcion == "5":
            filtrar_paises(paises)
        elif opcion == "6":
            ordenar_paises(paises)
        elif opcion == "7":
            mostrar_estadisticas(paises)
        elif opcion == "0":
            if guardar_paises(paises):
                print("Datos guardados en paises.csv. ¡Hasta luego!")
            break
        else:
            print("Opción inválida. Elegí una opción del menú.")


if __name__ == "__main__":
    menu()
