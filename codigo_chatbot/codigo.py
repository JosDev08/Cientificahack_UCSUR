import unicodedata

# Con "Path" se puede trabar con rutas de archivos y carpetas
from pathlib import Path 

import pandas as pd # Sirve para trabajar con tablas de datos

# Averigua en que carpeta esta el archivo "codigo.py" y la guarda en la variable "CARPETA".
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
    "negocio" : "tipo_negocio",
    "operacion" : "tipo_operacion",
    "hora" : "hora",
    "fecha" : "fecha",
    "dispositivo" : "dispositivo_nuevo"
}

MEDIDA = {
    "fraude" : ("es_fraude", "sum"),
    "monto" : ("monto_soles", "mean"),
    "antiguedad" : ("antiguedad_cuenta_dias", "mean")
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


# Como se llama cada calculo cuando lo mostramos
NOMBRE_CALCULO = {
    "sum" : "Total",
    "mean" : "Promedio"
}

# Como se llama cada columna medida cuando la mostramos
NOMBRE_MEDIDA = {
    "es_fraude" : "fraudes",
    "monto_soles" : "monto (S/)",
    "antiguedad_cuenta_dias" : "antiguedad (dias)"
}

def respuesta(pregunta):    
    texto = entrada(pregunta)
    columna = busqueda(texto, CLASES)
    medida = busqueda(texto, MEDIDA)
    
    # Si no se detecta bien lo que se solicita entonces sugerir algo.
    
    if medida is None:
        return "No entendi, prueba con: fraudes por distrito"

    col_medida, calculo = medida
    nombre_calculo = NOMBRE_CALCULO[calculo]
    nombre_medida = NOMBRE_MEDIDA[col_medida]

    # NUEVO: si solo pidio la medida (ej. "fraudes"), damos el valor de toda la tabla
    if columna is None:
        valor = round(df_limpio[col_medida].agg(calculo), 2)
        return f"{nombre_calculo} de {nombre_medida}: {valor}"

    # Si la pregunta trae "menos", ordenamos de menor a mayor
    de_menor_a_mayor = "menos" in texto

    resultado = (
        df_limpio.groupby(columna)[col_medida]
        .agg(calculo)
        .sort_values(ascending = de_menor_a_mayor)
        .round(2)
    )

# NUEVO: armamos la lista completa, una linea por cada elemento
    lista = ""
    for nombre, valor in resultado.items():
        lista += f"  {nombre}: {valor}\n"

    nombre_clase = columna.replace("_", " ")
    orden = "de menor a mayor" if de_menor_a_mayor else "de mayor a menor"
    return f"{nombre_calculo} de {nombre_medida} por {nombre_clase} ({orden}):\n{lista}"
        
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
        




