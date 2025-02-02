from flask import Flask, render_template, request
from models.database_manager import DBManager
from models.weather_data import WeatherAppDataRequest

app = Flask(__name__)
db_manager = DBManager()
weather_data = WeatherAppDataRequest()

@app.route("/")
def index():
    """Renderiza el plantillón principal del sitio web."""
    return render_template("index.html")

@app.route("/insertar_paises_fronteras", methods=["POST"])
def insertar_paises_fronteras():
    """
    Inserta paises y fronteras en la base de datos.
    
    Realiza dos operaciones de insertión:
        1. Insertación de paises
        2. Insertación de fronteras
        
    Si ambos operaciones son exitosas, muestra un mensaje de éxito.
    En caso contrario, muestra un mensaje de error.
    """
    lista_paises = weather_data.extraer_paises()
    if db_manager.insertar_paises(lista_paises) and db_manager.insertar_fronteras(lista_paises):
        return render_template("success.html", mensaje="Países y fronteras insertados correctamente.")
    return render_template("error.html", mensaje="Los países o las fronteras ya han sido insertados.")

@app.route("/insertar_temperaturas", methods=["POST"])
def insertar_temperaturas():
    """
    Inserta temperaturas en la base de datos.
    
    Recupera una lista de paises y als temperatura associated,
    luego las inserta en la base de datos.
    
    Si la operación es exitosa, muestra un mensaje de éxito.
    En caso contrario, muestra un mensaje de error.
    """
    lista_paises = weather_data.extraer_paises()
    db_manager.insertar_temperaturas(lista_paises)
    return render_template("success.html", mensaje="Temperaturas insertadas correctamente.")

@app.route("/buscar_pais", methods=["POST"])
def buscar_pais():
    """
    Busca temperaturas de un país específico.
    
    Parameters:
        nombre_pais (str): Nombre del país a buscar.
        
    Si se encuentran temperaturas, muestra los resultados y cierra la conexión
    con la base de datos.
    En caso contrario, muestra un mensaje de error.
    """
    nombre_pais = request.form.get("nombre_pais")
    
    temperaturas = db_manager.buscar_temperaturas_pais(nombre_pais)

    if temperaturas:
        db_manager.cerrar_conexion_bd()
        return render_template("resultado.html", nombre_pais=nombre_pais, temperaturas=temperaturas)
    else:
        db_manager.cerrar_conexion_bd()
        return render_template("error.html", mensaje="No se encontraron datos de temperatura para este país.")

@app.route("/buscar_fronteras", methods=["POST"])
def buscar_fronteras():
    """
    Busca temperaturas de paises fronterizos.
    
    Parameters:
        nombre_pais (str): Nombre del país a buscar.
        
    Si se encuentran temperaturas, muestra los resultados y cierra la conexión
    con la base de datos.
    En caso contrario, muestra un mensaje de error.
    """
    nombre_pais = request.form.get("nombre_pais")
    
    temperaturas_fronteras = db_manager.buscar_temperaturas_fronteras(nombre_pais)

    if temperaturas_fronteras:
        db_manager.cerrar_conexion_bd()
        return render_template("resultado_fronteras.html", nombre_pais=nombre_pais, temperaturas_fronteras=temperaturas_fronteras)
    else:
        db_manager.cerrar_conexion_bd()
        return render_template("error.html", mensaje="No se encontraron temperaturas para los países fronterizos de " + nombre_pais)

@app.route("/borrar_datos", methods=["POST"])
def borrar_datos():
    """
    Borra todos los datos de la base de datos.
    
    Realiza las siguientes operaciones:
        1. Borra todas las tablas relacionadas
        2. Reinicia los autoincrementos (si es necesario)
        
    Muestra un mensaje de éxito si la operación es exitosa,
    en caso contrario, muestra un mensaje de error.
    """
    try:
        # Borrar todas las tablas
        db_manager.borrar_tabla_temperaturas()
        db_manager.borrar_tabla_fronteras()
        db_manager.borrar_tabla_paises()
        
        # Reiniciar los autoincrementos si es necesario (depende de tu DB)
        db_manager.reiniciar_autoincrementos()
        
        return render_template("success.html", mensaje="Base de datos borrada correctamente.")
    except Exception as e:
        print(f"Error al borrar la base de datos: {str(e)}")
        return render_template("error.html", mensaje="Ocurrió un error al intentar borrar la base de datos.")

if __name__ == "__main__":
    app.run(debug=True)