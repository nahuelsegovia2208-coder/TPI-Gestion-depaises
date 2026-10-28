import csv
from pathlib import Path

ARCHIVO_CSV = Path(__file__).with_name("paises.csv")
CAMPOS = ["nombre", "poblacion", "superficie", "continente"]


def cargar_paises():
    """Lee los países del CSV y devuelve una lista de diccionarios."""
    if not ARCHIVO_CSV.exists():
        with ARCHIVO_CSV.open("w", newline="", encoding="utf-8") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=CAMPOS)
            escritor.writeheader()
        return []

    paises = []
    try:
        with ARCHIVO_CSV.open("r", newline="", encoding="utf-8-sig") as archivo:
            lector = csv.DictReader(archivo)
            if lector.fieldnames is None or not all(campo in lector.fieldnames for campo in CAMPOS):
                raise ValueError("El CSV no contiene las columnas requeridas.")
            for numero_fila, fila in enumerate(lector, start=2):
                try:
                    nombre = (fila.get("nombre") or "").strip()
                    continente = (fila.get("continente") or "").strip()
                    poblacion = int(fila.get("poblacion", ""))
                    superficie = int(fila.get("superficie", ""))
                    if not nombre or not continente or poblacion < 0 or superficie <= 0:
                        raise ValueError
                    paises.append({
                        "nombre": nombre,
                        "poblacion": poblacion,
                        "superficie": superficie,
                        "continente": continente
                    })
                except (ValueError, TypeError):
                    print(f"Aviso: se omitió la fila {numero_fila} del CSV por tener datos inválidos.")
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        print(f"Error al leer el CSV: {error}")
    return paises


def guardar_paises(paises):
    """Guarda la lista completa en el archivo CSV."""
    try:
        with ARCHIVO_CSV.open("w", newline="", encoding="utf-8") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=CAMPOS)
            escritor.writeheader()
            escritor.writerows(paises)
        return True
    except OSError as error:
        print(f"No se pudieron guardar los datos: {error}")
        return False


def mostrar_paises(paises):
    if not paises:
        print("No se encontraron países.")
        return
    print(f'{"Nombre":<20} {"Población":>15} {"Superficie km²":>18} {"Continente":<15}')
    print("-" * 72)
    for pais in paises:
        print(f'{pais["nombre"]:<20} {pais["poblacion"]:>15,} {pais["superficie"]:>18,} {pais["continente"]:<15}')


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
    nombre = input("Nombre: ").strip()
    continente = input("Continente: ").strip()
    if not nombre or not continente:
        print("Error: nombre y continente no pueden estar vacíos.")
        return
    if any(p["nombre"].casefold() == nombre.casefold() for p in paises):
        print("Ya existe un país con ese nombre.")
        return
    poblacion = leer_entero("Población: ", 0)
    superficie = leer_entero("Superficie en km² (debe ser mayor que 0): ", 1)
    paises.append({"nombre": nombre, "poblacion": poblacion,
                   "superficie": superficie, "continente": continente})
    if guardar_paises(paises):
        print("País agregado correctamente.")


def actualizar_pais(paises):
    nombre = input("Nombre del país que querés actualizar: ").strip()
    pais = next((p for p in paises if p["nombre"].casefold() == nombre.casefold()), None)
    if pais is None:
        print("No se encontró ese país.")
        return
    print("Dejá el valor actual como referencia y escribí el nuevo valor.")
    pais["poblacion"] = leer_entero(f'Nueva población (actual {pais["poblacion"]}): ', 0)
    pais["superficie"] = leer_entero(f'Nueva superficie en km² (actual {pais["superficie"]}): ', 1)
    if guardar_paises(paises):
        print("Datos actualizados correctamente.")


def buscar_pais(paises):
    texto = input("Ingresá el nombre completo o una parte: ").strip().casefold()
    if not texto:
        print("La búsqueda no puede estar vacía.")
        return
    resultados = [p for p in paises if texto in p["nombre"].casefold()]
    mostrar_paises(resultados)


def filtrar_paises(paises):
    print("\n1. Por continente\n2. Por rango de población\n3. Por rango de superficie")
    opcion = input("Elegí un filtro: ").strip()
    if opcion == "1":
        continente = input("Continente: ").strip().casefold()
        resultados = [p for p in paises if p["continente"].casefold() == continente]
    elif opcion in ("2", "3"):
        minimo = leer_entero("Valor mínimo: ", 0 if opcion == "2" else 1)
        maximo = leer_entero("Valor máximo: ", minimo)
        campo = "poblacion" if opcion == "2" else "superficie"
        resultados = [p for p in paises if minimo <= p[campo] <= maximo]
    else:
        print("Opción inválida.")
        return
    mostrar_paises(resultados)


def ordenar_paises(paises):
    print("\n1. Nombre A-Z\n2. Población ascendente\n3. Población descendente")
    print("4. Superficie ascendente\n5. Superficie descendente")
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
    mostrar_paises(sorted(paises, key=lambda p: p[campo].casefold() if campo == "nombre" else p[campo],
                          reverse=reverso))


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
        por_continente[pais["continente"]] = por_continente.get(pais["continente"], 0) + 1

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
            guardar_paises(paises)
            print("Datos guardados. ¡Hasta luego!")
            break
        else:
            print("Opción inválida. Elegí una opción del menú.")


if __name__ == "__main__":
    menu()
