from flask import Flask, render_template, request
from models.database_manager import DBManager
from models.weather_data import WeatherAppDataRequest

app = Flask(__name__)
db_manager = DBManager()
weather_data = WeatherAppDataRequest()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/insertar_paises_fronteras", methods=["POST"])
def insertar_paises():
    lista_paises = weather_data.extraer_paises()
    if db_manager.insertar_paises(lista_paises) and db_manager.insertar_fronteras(lista_paises):
        return render_template("success.html", mensaje="Países y fronteras insertados correctamente.")
    return render_template("error.html", mensaje="Los países o las fronteras ya han sido insertados.")

@app.route("/insertar_temperaturas", methods=["POST"])
def insertar_temperaturas():
    lista_paises = weather_data.extraer_paises()
    db_manager.insertar_temperaturas(lista_paises)
    return render_template("success.html", mensaje="Temperaturas insertadas correctamente.")

@app.route("/buscar_pais", methods=["POST"])
def buscar_pais():
    nombre_pais = request.form.get("nombre_pais")
    
    temperaturas = db_manager.buscar_temperaturas_pais(nombre_pais)

    if temperaturas:
        db_manager.cerrar_conexion_bd()  # 🔥 Cerramos aquí después de obtener los datos
        return render_template("resultado.html", nombre_pais=nombre_pais, temperaturas=temperaturas)

    db_manager.cerrar_conexion_bd()  # 🔥 Cerramos aquí si no se encontraron datos
    return render_template("error.html", mensaje="No se encontraron datos de temperatura para este país.")

@app.route("/buscar_fronteras", methods=["POST"])
def buscar_fronteras():
    nombre_pais = request.form.get("nombre_pais")
    temperaturas_fronteras = db_manager.buscar_temperaturas_fronteras(nombre_pais)

    if temperaturas_fronteras:
        db_manager.cerrar_conexion_bd()
        return render_template("resultado_fronteras.html", nombre_pais=nombre_pais, temperaturas_fronteras=temperaturas_fronteras)

    db_manager.cerrar_conexion_bd()
    return render_template("error.html", mensaje="No se encontraron temperaturas para los países fronterizos de " + nombre_pais)

@app.route("/borrar_datos", methods=["POST"])
def borrar_datos():
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
