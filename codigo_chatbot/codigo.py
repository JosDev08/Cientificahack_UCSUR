import unicodedata
# Con "Path" se puede trabar con rutas de archivos y carpetas
from pathlib import Path 

import pandas as pd # Sirve para trabajar con tablas de datos

# Averigua en qué carpeta está el archivo "codigo.py" y la guarda en la variable "CARPETA"
CARPETA = Path(__file__).resolve().parent

# Ruta CSV
ARCHIVO_CSV = CARPETA / "reto2_finanzas_transacciones_billetera.csv"

df = pd.read_csv(ARCHIVO_CSV)
# print(df.head())

# print(f"Primer vistazo, {df.shape[0]}")

# Quitamos filas repetidas
df_limpio = df.drop_duplicates() # ---> Elimina filas repetidas y lo guardamos en una varible
# print(f"Segundo vistazo, {df_limpio.shape[0]}") # ---> "shape" da (filas y columnas) con shape[0] solo me da filas

# Asignacion de nombres a distritos 
df_limpio["distrito"] = df_limpio["distrito"].str.strip().str.upper() # ---> "strip()" quita los espacion de los bordes, mientras que str hace que trate cada linea como texto.

# Comprobacion de distritos

# print(df_limpio["distrito"].unique()) # ---> "unique()" da lista de valores distintos que quedaron

# Entrada 

def entrada(texto):
    """
    Funciona como una maquina, donde entra una pregunta y la procesamos de manera que sale una pregunta mas limpia de la inicialmente entro.
    """
    texto = texto.lower().strip()  # Quitamos espacios y pasamos a minusculas.
    texto = unicodedata.normalize("NFD", texto) # Quitamos acentos "NFD" separa las letras de las tildes.
    return "".join(c for c in texto if unicodedata.category(c) != "Mn") # Rearma el texto, pero sin tildes.

# print(entrada("¿Que operación tiene más fraudes?"))

# EL vocabulario del bot, creamos un diccionario con la siguiente logica:
# palabra del usuario ---> columna real en la tabla

CLASES = {
    "distrito" : "distrito",
    "zona" : "distrito",                  # NUEVO: sinonimo
    "negocio" : "tipo_negocio",
    "operacion" : "tipo_operacion",
    "pago" : "tipo_operacion",            # NUEVO: sinonimo
    "hora" : "hora",
    "fecha" : "fecha",
    "dispositivo" : "dispositivo_nuevo"
}

# AHORA cada medida guarda 3 datos: (columna, calculo, nombre para mostrar)
# OJO AL ORDEN: gana la PRIMERA coincidencia. Por eso "tasa" va antes que "fraude"
# y "maximo" / "minimo" van antes que "monto".
MEDIDA = {
    "tasa" : ("es_fraude", "mean", "Tasa de fraude (%)"),             # NUEVO
    "porcentaje" : ("es_fraude", "mean", "Tasa de fraude (%)"),       # NUEVO
    "fraude" : ("es_fraude", "sum", "Total de fraudes"),
    "estafa" : ("es_fraude", "sum", "Total de fraudes"),              # NUEVO: sinonimo
    "cuant" : ("id_transaccion", "count", "Cantidad de operaciones"), # NUEVO: cuantas / cuantos
    "transaccion" : ("id_transaccion", "count", "Cantidad de operaciones"), # NUEVO
    "maximo" : ("monto_soles", "max", "Monto maximo (S/)"),           # NUEVO
    "minimo" : ("monto_soles", "min", "Monto minimo (S/)"),           # NUEVO
    "monto" : ("monto_soles", "mean", "Monto promedio (S/)"),
    "dinero" : ("monto_soles", "mean", "Monto promedio (S/)"),        # NUEVO: sinonimo
    "antiguedad" : ("antiguedad_cuenta_dias", "mean", "Antiguedad promedio (dias)")
}

# print(MEDIDA["fraude"])

def busqueda(texto, diccionario):
    """
    Recorre un diccionario y devuelve el valor de la primera palabra que aparezca en la pregunta
    """
    for palabra, valor in diccionario.items(): # ---> "items()" hagarra tanto la clave como el valor
        if palabra in texto: # Si la palabra aparece dentro de la frase entonces devuelve "valor"
            return valor
    return None

# NUEVO: comando "ayuda" que muestra las clases que conoce el bot y ejemplos
def ayuda():
    clases = ", ".join(CLASES.keys()) # ---> "join" pega todas las claves separadas por coma
    return (
        f"Puedes agrupar por: {clases}\n"
        "Ejemplos:\n"
        "  - fraudes por distrito\n"
        "  - tasa de fraude por dispositivo\n"
        "  - cuantas operaciones por negocio\n"
        "  - monto maximo por distrito\n"
        "  - fraudes (solo la medida, da el total)\n"
        "  - fraudes por hora menos (con 'menos' ordena de menor a mayor)"
    )

def respuesta(pregunta):
    texto = entrada(pregunta)

    # NUEVO: comando especial
    if texto == "ayuda":
        return ayuda()

    columna = busqueda(texto, CLASES)
    medida = busqueda(texto, MEDIDA)

    # NUEVO: si solo pidio la clase (ej. "distritos"), asumimos que quiere fraudes
    if medida is None and columna is not None:
        medida = MEDIDA["fraude"]

    # Si no se encontro QUE medir, solicitamos un nuevo ingreso.
    if medida is None:
        return "No entendi. Escribe 'ayuda' para ver ejemplos."

    col_medida, calculo, nombre_medida = medida

    # La tasa de fraude es un promedio de 0 y 1 (ej. 0.05), asi que la pasamos a porcentaje
    factor = 1
    if col_medida == "es_fraude" and calculo == "mean":
        factor = 100

    # NUEVO: si solo pidio la medida (ej. "fraudes"), damos el valor de toda la tabla
    if columna is None:
        valor = round(df_limpio[col_medida].agg(calculo) * factor, 2)
        return f"{nombre_medida}: {valor}"

    # Si la pregunta trae "menos", ordenamos de menor a mayor
    de_menor_a_mayor = "menos" in texto

    resultado = df_limpio.groupby(columna)[col_medida].agg(calculo) * factor
    resultado = resultado.sort_values(ascending = de_menor_a_mayor).round(2)

    # Armamos la lista completa, una linea por cada elemento
    lista = ""
    for nombre, valor in resultado.items():
        lista += f"  {nombre}: {valor}\n"

    nombre_clase = columna.replace("_", " ")
    orden = "de menor a mayor" if de_menor_a_mayor else "de mayor a menor"
    return f"{nombre_medida} por {nombre_clase} ({orden}):\n{lista}"

pregunta = entrada("¿Que distrito tiene mas fraudes?") # Esto hace que el texto quede limpio
#pregunta = entrada("A?")
# print(pregunta)
# print(busqueda(pregunta, CLASES)) # Procesa la pregunta
# print(busqueda(pregunta, MEDIDA)) # Procesa la pregunta

# OPERACIONES 
## Aqrupamos las filas por distrito
# Este es un primer modelo : "resultado = df_limpio.groupby("distrito")["es_fraude"].sum() # "sum()" suma esa columna, con esto contamos el numero de fraudes."

resultado = (
    df_limpio.groupby("distrito")["es_fraude"]
    .sum()
    .sort_values(ascending = False) # ordena de mayor a menor, si "ascendig = True" seria alrevez
)
#promedio = (
    #df_limpio.groupby("distrito")["es_fraude"]
    #.mean()
    #)
# print(f"a : {round((promedio * 100),2)} %")
#print(resultado)

### PUEDE AMPLIARSE 

if __name__ == "__main__":
    print("Ingrese su consulta. Escriba 'salir' para finalizar las operaciones")
    while True: 
        pregunta = input("Pregunta: ")
        if entrada(pregunta) == "salir":
            break
        print(respuesta(pregunta), "\n")


