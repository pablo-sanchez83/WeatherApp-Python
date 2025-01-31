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

@app.route("/insertar_temperaturas", methods=["POST"])
def insertar_temperaturas():
    lista_paises = weather_data.extraer_paises()
    db_manager.insertar_temperaturas(lista_paises)
    return render_template("success.html", mensaje="Temperaturas insertadas correctamente.")

@app.route("/buscar_pais", methods=["POST"])
def buscar_pais():
    nombre_pais = request.form.get("nombre_pais")
    resultado = db_manager.buscar_temperatura_pais(nombre_pais)

    if resultado:
        return render_template("resultado.html", nombre=resultado[0], temperatura=resultado[1], timestamp=resultado[2])
    return render_template("error.html", mensaje="No se encontraron datos de temperatura para este país.")

if __name__ == "__main__":
    app.run(debug=True)
