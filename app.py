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
        return render_template("success.html", mensaje="Fronteras insertadas correctamente.")
    return render_template("error.html", mensaje="Las fronteras ya han sido insertadas.")

@app.route("/insertar_temperaturas", methods=["POST"])
def insertar_temperaturas():
    lista_paises = weather_data.extraer_paises()
    db_manager.insertar_temperaturas(lista_paises)
    return render_template("success.html", mensaje="Temperaturas insertadas correctamente.")

if __name__ == "__main__":
    app.run(debug=True)
