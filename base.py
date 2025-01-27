#Completo
import json
import requests
import mysql.connector
import datetime
import xml.etree.ElementTree as ET

class WeatherAppBase():
    def __init__(self):
        self.base_datos = None
        self.cursor = None

    def iniciar_conexion_bd(self):
        try:
            self.base_datos = mysql.connector.connect(
                        host="127.0.0.1",
                        port="3306",
                        user="root",
                        password="12345",
                        database="temperaturas"
                    )
            self.cursor = self.base_datos.cursor()
            return True
        except mysql.connector.Error as error:
            print("Error al conectar a la base de datos: ", error)
            return False

    def cerrar_conexion_bd(self):
        if self.cursor:
            self.cursor.close()
        if self.base_datos:
            self.base_datos.close()

    def extraer_datos_paises(self, lista_paises):
        datos_extraidos = []

        for pais in lista_paises:
            nombre = pais.get("name", {}).get("common", "Desconocido")
            capital = ", ".join(pais.get("capital", ["No especificada"]))
            region = pais.get("region", "Desconocida")
            subregion = pais.get("subregion", "Desconocida")
            codigo_cca2 = pais.get("cca2", "N/A")
            codigo_cca3 = pais.get("cca3", "N/A")
            pertenece_ue = 1 if pais.get("region") == "Europe" and "Europe" in pais.get("subregion") and "EUR" in pais.get("currencies") else 0
            longitud = pais.get("latlng", [0, 0])[1]
            latitud = pais.get("latlng", [0, 0])[0]
            lat_cap = pais.get("capitalInfo", {}).get("latlng", [0, 0])[0]
            lon_cap = pais.get("capitalInfo", {}).get("latlng", [0, 0])[1]

            datos_extraidos.append({
                "Nombre": nombre,
                "Capital": capital,
                "Región": region,
                "Subregión": subregion,
                "Código cca2": codigo_cca2,
                "Código cca3": codigo_cca3,
                "Pertenece a la UE": pertenece_ue,
                "Longitud": longitud,
                "Latitud": latitud,
                "lat_cap": lat_cap,
                "lon_cap": lon_cap
            })

        return datos_extraidos

    def enviar_paises_bd(self, lista_paises):
        datos = self.extraer_datos_paises(lista_paises)
        if not datos:
            print("No hay datos para insertar.")
            return {}

        pais_id_map = {}
        try:
            if not self.iniciar_conexion_bd():
                return {}

            for dato in datos:
                sql = (
                    "INSERT INTO paises (nombre, capital, region, subregion, cca2, cca3, miembroUE, latitud, longitud) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                )
                val = (
                    dato["Nombre"],
                    dato["Capital"],
                    dato["Región"],
                    dato["Subregión"],
                    dato["Código cca2"],
                    dato["Código cca3"],
                    dato["Pertenece a la UE"],
                    dato["Latitud"],
                    dato["Longitud"]
                )
                self.cursor.execute(sql, val)
                pais_id_map[dato["Código cca3"]] = self.cursor.lastrowid

            self.base_datos.commit()
            print("Países insertados correctamente.")
        except mysql.connector.Error as error:
            print(f"Error al insertar países en la base de datos: {error}")
        finally:
            self.cerrar_conexion_bd()

        return pais_id_map

    def enviar_fronteras_bd(self, pais_id_map, lista_paises):
        try:
            if not self.iniciar_conexion_bd():
                return

            for pais in lista_paises:
                codigo_cca3 = pais.get("cca3", "N/A")
                id_pais = pais_id_map.get(codigo_cca3)  # Obtiene el ID del país de origen
                if not id_pais:
                    continue

                for frontera in pais.get("borders", []):
                    # `frontera` ya es el código cca3 del país frontera
                    sql = "INSERT INTO fronteras (idpais, cca3_frontera) VALUES (%s, %s)"
                    val = (id_pais, frontera)  # Inserta el ID del país origen y el código cca3 del país frontera
                    self.cursor.execute(sql, val)

            self.base_datos.commit()
            print("Fronteras insertadas correctamente.")
        except mysql.connector.Error as error:
            print(f"Error al insertar fronteras en la base de datos: {error}")
        finally:
            self.cerrar_conexion_bd()

    def enviar_temperaturas_bd(self, lista_paises):
        try:
            self.iniciar_conexion_bd()

            datos = self.extraer_datos_paises(lista_paises)
            mitad_paises = len(datos) // 2

            json_temperaturas = datos[:mitad_paises]
            xml_temperaturas = datos[mitad_paises:]
            
            # Manejo de JSON
            for pais in json_temperaturas:
                temperatura = requests.get(f"http://api.openweathermap.org/data/2.5/weather?appid=a60fef3fc371c50c0c57c17361925fad&lat={pais['lat_cap']}&lon={pais['lon_cap']}&units=metric")
                temperatura.raise_for_status()
                temperatura = temperatura.json()

                id_pais_query = "SELECT idpais FROM paises WHERE cca3 = %s"
                self.cursor.execute(id_pais_query, (pais["Código cca3"],))
                id_pais = self.cursor.fetchall()

                if id_pais and temperatura:
                    sql = """
                    INSERT INTO temperaturas 
                    (idpais, timestamp, temperatura, sensacion, minima, maxima, humedad, amanecer, atardecer) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    val = (
                        id_pais[0][0], datetime.datetime.now(),
                        temperatura["main"]["temp"], temperatura["main"]["feels_like"],
                        temperatura["main"]["temp_min"], temperatura["main"]["temp_max"],
                        temperatura["main"]["humidity"],
                        datetime.datetime.fromtimestamp(temperatura["sys"]["sunrise"]),
                        datetime.datetime.fromtimestamp(temperatura["sys"]["sunset"])
                    )
                    self.cursor.execute(sql, val)

            self.base_datos.commit()
            print("Temperaturas insertadas correctamente en el formato JSON.")
            
            # Manejo de XML
            for pais in xml_temperaturas:
                temperatura = requests.get(f"http://api.openweathermap.org/data/2.5/weather?appid=a60fef3fc371c50c0c57c17361925fad&lat={pais['lat_cap']}&lon={pais['lon_cap']}&units=metric&mode=xml")
                temperatura.raise_for_status()
                xml_data = temperatura.text

                root = ET.fromstring(xml_data)
                
                temp = root.find("temperature")
                sun = root.find("city/sun")
                humidity = root.find("humidity")

                temperatura_value = float(temp.get("value"))
                sensacion_value = float(root.find("feels_like").get("value"))
                minima = float(temp.get("min"))
                maxima = float(temp.get("max"))
                humedad = int(humidity.get("value"))
                amanecer = datetime.datetime.fromisoformat(sun.get("rise"))
                atardecer = datetime.datetime.fromisoformat(sun.get("set"))

                id_pais_query = "SELECT idpais FROM paises WHERE cca3 = %s"
                self.cursor.execute(id_pais_query, (pais["Código cca3"],))
                id_pais = self.cursor.fetchall()

                if id_pais:
                    sql = """
                    INSERT INTO temperaturas 
                    (idpais, timestamp, temperatura, sensacion, minima, maxima, humedad, amanecer, atardecer) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    val = (
                        id_pais[0][0], datetime.datetime.now(),
                        temperatura_value, sensacion_value,
                        minima, maxima, humedad,
                        amanecer, atardecer
                    )
                    self.cursor.execute(sql, val)
            self.base_datos.commit()
            print("Temperaturas insertadas correctamente en el formato XML.")
        except mysql.connector.Error as error:
            print("Error al conectar a la base de datos o al insertar datos: ", error)
        except requests.exceptions.RequestException as error:
            print("Error al obtener los datos de temperatura: ", error)
        except ET.ParseError as error:
            print("Error al analizar el XML: ", error)
        finally:
            self.cerrar_conexion_bd()
    def run(self):
        try:
            respuesta = requests.get("https://restcountries.com/v3.1/region/europe")
            respuesta.raise_for_status()
            lista_paises = respuesta.json()

            pais_id_map = self.enviar_paises_bd(lista_paises)
            if pais_id_map:
                self.enviar_fronteras_bd(pais_id_map, lista_paises)
                self.enviar_temperaturas_bd(lista_paises)
        except requests.exceptions.RequestException as error:
            print("Error al obtener los datos de paises: ", error)

if __name__ == "__main__":
    proceso = ProcesoCompleto()
    proceso.run()
