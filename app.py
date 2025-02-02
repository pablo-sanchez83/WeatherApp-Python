from flask import Flask, render_template, request
from models.database_manager import DBManager
from models.weather_data import WeatherAppDataRequest

app = Flask(__name__)
db_manager = DBManager()
weather_data = WeatherAppDataRequest()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/insertar_paises", methods=["POST"])
def insertar_paises():
    lista_paises = weather_data.extraer_paises()
    if db_manager.insertar_paises(lista_paises):
        return render_template("success.html", mensaje="Países insertados correctamente.")
    return render_template("error.html", mensaje="Los países ya han sido insertados.")

@app.route("/insertar_fronteras", methods=["POST"])
def insertar_fronteras():
    lista_paises = weather_data.extraer_paises()
    if db_manager.insertar_fronteras(lista_paises):
        return render_template("success.html", mensaje="Fronteras insertados correctamente.")
    return render_template("error.html", mensaje="Las fronteras ya han sido insertadas.")

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


if __name__ == "__main__":
    app.run(debug=True)
