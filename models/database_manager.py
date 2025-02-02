import mysql.connector
from config import DB_CONFIG
import xml.etree.ElementTree as ET
import datetime
import requests

class DBManager:
    def __init__(self):
        """ Inicializa la conexión a la base de datos y crea un cursor. """
        self.conexion = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conexion.cursor()

    def cerrar_conexion_bd(self):
        """ Cierra el cursor y la conexión a la base de datos. """
        self.cursor.close()
        self.conexion.close()

    def paises_existen(self):
        """ Verifica si hay países en la base de datos. """
        if not self.conexion.is_connected():
                self.conexion = mysql.connector.connect(**DB_CONFIG)
                self.cursor = self.conexion.cursor()
        self.cursor.execute("SELECT COUNT(*) FROM paises")
        count = self.cursor.fetchone()[0]
        return count > 0
    
    def borrar_tabla_temperaturas(self):
        """ Borra todos los registros de la tabla temperaturas. """
        if not self.conexion.is_connected():
                self.conexion = mysql.connector.connect(**DB_CONFIG)
                self.cursor = self.conexion.cursor()
        self.cursor.execute("DELETE FROM temperaturas")
        self.conexion.commit()

    def borrar_tabla_fronteras(self):
        """ Borra todos los registros de la tabla fronteras. """
        if not self.conexion.is_connected():
                self.conexion = mysql.connector.connect(**DB_CONFIG)
                self.cursor = self.conexion.cursor()
        self.cursor.execute("DELETE FROM fronteras")
        self.conexion.commit()

    def borrar_tabla_paises(self):
        """ Borra todos los registros de la tabla paises. """
        if not self.conexion.is_connected():
                self.conexion = mysql.connector.connect(**DB_CONFIG)
                self.cursor = self.conexion.cursor()
        self.cursor.execute("DELETE FROM paises")
        self.conexion.commit()

    def reiniciar_autoincrementos(self):
        """ Reinicia los valores de autoincremento de las tablas. """
        if not self.conexion.is_connected():
                self.conexion = mysql.connector.connect(**DB_CONFIG)
                self.cursor = self.conexion.cursor()
        self.cursor.execute("ALTER TABLE temperaturas AUTO_INCREMENT = 1")
        self.cursor.execute("ALTER TABLE fronteras AUTO_INCREMENT = 1")
        self.cursor.execute("ALTER TABLE paises AUTO_INCREMENT = 1")
        self.conexion.commit()

    def fronteras_existen(self):
        """ Verifica si hay fronteras en la base de datos. """
        if not self.conexion.is_connected():
                self.conexion = mysql.connector.connect(**DB_CONFIG)
                self.cursor = self.conexion.cursor()
        self.cursor.execute("SELECT COUNT(*) FROM fronteras")
        count = self.cursor.fetchone()[0]
        return count > 0

    def insertar_paises(self, datos_paises):
        """ Inserta países en la base de datos si aún no han sido insertados. """
        if self.paises_existen():
            return False  # Evita la inserción duplicada
        try:
            if not self.conexion.is_connected():
                self.conexion = mysql.connector.connect(**DB_CONFIG)
                self.cursor = self.conexion.cursor()
            for dato in datos_paises:
                sql = "INSERT INTO paises (nombre, capital, region, subregion, cca2, cca3, miembroNU, latitud, longitud) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (dato["Nombre"], dato["Capital"], dato["Región"], dato["Subregión"], dato["Código cca2"], dato["Código cca3"], dato["Pertenece a las NU"], dato["Latitud"], dato["Longitud"])
                self.cursor.execute(sql, val)

            self.conexion.commit()
            return True
        except mysql.connector.Error as error:
            print("Error al insertar países:", error)
            return False
        finally:
            self.cerrar_conexion_bd()

    def insertar_fronteras(self, lista_paises):
        """ Inserta fronteras en la base de datos si aún no han sido insertadas. """
        if self.fronteras_existen():
            return False  # Evita la inserción duplicada

        try:
            if not self.conexion.is_connected():
                self.conexion = mysql.connector.connect(**DB_CONFIG)
                self.cursor = self.conexion.cursor()

            for pais in lista_paises:
                # Obtener el ID del país desde su código CCA3
                self.cursor.execute("SELECT idpais FROM paises WHERE cca3 = %s", (pais["Código cca3"],))
                id_pais = self.cursor.fetchone()

                if not id_pais:  # Si el país no existe en la base de datos, saltarlo
                    print(f"Advertencia: No se encontró el país {pais['Código cca3']} en la base de datos.")
                    continue

                id_pais = id_pais[0]  # Extraer el valor del tuple

                for frontera in pais.get("borders", []):
                    self.cursor.execute("INSERT INTO fronteras (idpais, cca3_frontera) VALUES (%s, %s)", (id_pais, frontera))

            self.conexion.commit()
            return True

        except mysql.connector.Error as error:
            print("Error al insertar fronteras:", error)
            return False
        finally:
            self.cerrar_conexion_bd()

    def insertar_temperaturas(self, lista_paises):
        """ Inserta temperaturas en la base de datos (pueden insertarse múltiples veces). """
        try:
            if not self.conexion.is_connected():
                self.conexion = mysql.connector.connect(**DB_CONFIG)
                self.cursor = self.conexion.cursor()
            mitad_paises = len(lista_paises) // 2
            json_temperaturas = lista_paises[:mitad_paises]
            xml_temperaturas = lista_paises[mitad_paises:]
            
            # Manejo de JSON
            for pais in json_temperaturas:
                response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?appid=a60fef3fc371c50c0c57c17361925fad&lat={pais['lat_cap']}&lon={pais['lon_cap']}&units=metric")
                response.raise_for_status()
                temperatura = response.json()
                
                id_pais_query = "SELECT idpais FROM paises WHERE cca3 = %s"
                self.cursor.execute(id_pais_query, (pais["Código cca3"],))
                id_pais = self.cursor.fetchone()
                
                if id_pais and temperatura:
                    sql = """
                    INSERT INTO temperaturas (idpais, timestamp, temperatura, sensacion, minima, maxima, humedad, amanecer, atardecer) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    val = (
                        id_pais[0], datetime.datetime.now(),
                        temperatura["main"]["temp"], temperatura["main"]["feels_like"],
                        temperatura["main"]["temp_min"], temperatura["main"]["temp_max"],
                        temperatura["main"]["humidity"],
                        datetime.datetime.fromtimestamp(temperatura["sys"]["sunrise"]),
                        datetime.datetime.fromtimestamp(temperatura["sys"]["sunset"])
                    )
                    self.cursor.execute(sql, val)
            self.conexion.commit()
            print("Temperaturas insertadas correctamente en el formato JSON.")
            
            # Manejo de XML
            for pais in xml_temperaturas:
                response = requests.get(f"http://api.openweathermap.org/data/2.5/weather?appid=a60fef3fc371c50c0c57c17361925fad&lat={pais['lat_cap']}&lon={pais['lon_cap']}&units=metric&mode=xml")
                response.raise_for_status()
                root = ET.fromstring(response.text)
                
                temp = root.find("temperature")
                sun = root.find("city/sun")
                humidity = root.find("humidity")
                sensacion = root.find("feels_like")
                
                temperatura_value = float(temp.get("value"))
                sensacion_value = float(sensacion.get("value"))
                minima = float(temp.get("min"))
                maxima = float(temp.get("max"))
                humedad = int(humidity.get("value"))
                amanecer = datetime.datetime.fromisoformat(sun.get("rise"))
                atardecer = datetime.datetime.fromisoformat(sun.get("set"))
                
                id_pais_query = "SELECT idpais FROM paises WHERE cca3 = %s"
                self.cursor.execute(id_pais_query, (pais["Código cca3"],))
                id_pais = self.cursor.fetchone()
                
                if id_pais:
                    sql = """
                    INSERT INTO temperaturas (idpais, timestamp, temperatura, sensacion, minima, maxima, humedad, amanecer, atardecer) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    val = (
                        id_pais[0], datetime.datetime.now(),
                        temperatura_value, sensacion_value,
                        minima, maxima, humedad,
                        amanecer, atardecer
                    )
                    self.cursor.execute(sql, val)
            self.conexion.commit()
            print("Temperaturas insertadas correctamente en el formato XML.")
        except mysql.connector.Error as error:
            print("Error al conectar a la base de datos o al insertar datos: ", error)
        except requests.exceptions.RequestException as error:
            print("Error al obtener los datos de temperatura: ", error)
        except ET.ParseError as error:
            print("Error al analizar el XML: ", error)
        finally:
            self.cerrar_conexion_bd()

    def buscar_temperaturas_pais(self, nombre_pais):
        """ Devuelve todas las temperaturas registradas para un país. """
        try:
            # Asegurar que la conexión y el cursor están abiertos
            if not self.conexion.is_connected():
                self.conexion = mysql.connector.connect(**DB_CONFIG)
                self.cursor = self.conexion.cursor()

            self.cursor.execute("""
                SELECT t.timestamp, t.temperatura, t.sensacion, t.minima, t.maxima, 
                    t.humedad, t.amanecer, t.atardecer
                FROM temperaturas t
                JOIN paises p ON t.idpais = p.idpais
                WHERE p.nombre = %s
                ORDER BY t.timestamp DESC
            """, (nombre_pais,))

            resultados = self.cursor.fetchall()
            
            # Si hay resultados, devuelve la lista de temperaturas
            if resultados:
                temperaturas = [{
                    "timestamp": r[0],
                    "temperatura": r[1],
                    "sensacion": r[2],
                    "minima": r[3],
                    "maxima": r[4],
                    "humedad": r[5],
                    "amanecer": r[6],
                    "atardecer": r[7]
                } for r in resultados]
                return temperaturas

            return None  # Si no hay resultados

        except mysql.connector.Error as error:
            print("Error al buscar las temperaturas:", error)
            return None

    def buscar_temperaturas_fronteras(self, nombre_pais):
        """ Devuelve las temperaturas de todos los países que hacen frontera con el país dado. """
        try:
            if not self.conexion.is_connected():
                self.conexion = mysql.connector.connect(**DB_CONFIG)
                self.cursor = self.conexion.cursor()

            # Obtener el código `cca3` del país consultado
            self.cursor.execute("""
                SELECT cca3 FROM paises WHERE nombre = %s
            """, (nombre_pais,))
            resultado = self.cursor.fetchone()

            if not resultado:
                return None  # Si el país no existe en la base de datos

            cca3_pais = resultado[0]

            # Obtener los códigos `cca3` de los países que hacen frontera con el país consultado
            self.cursor.execute("""
                SELECT f.cca3_frontera 
                FROM fronteras f 
                JOIN paises p ON f.idpais = p.idpais
                WHERE p.cca3 = %s
            """, (cca3_pais,))

            fronteras = [row[0] for row in self.cursor.fetchall()]
            
            if not fronteras:
                return None  # Si el país no tiene fronteras registradas

            # Obtener las temperaturas más recientes de los países fronterizos
            self.cursor.execute("""
                SELECT p.nombre, t.timestamp, t.temperatura, t.sensacion, t.minima, t.maxima, 
                    t.humedad, t.amanecer, t.atardecer
                FROM temperaturas t
                JOIN paises p ON t.idpais = p.idpais
                WHERE p.cca3 IN ({})
                ORDER BY t.timestamp DESC
            """.format(",".join(["%s"] * len(fronteras))), fronteras)

            resultados = self.cursor.fetchall()
            
            if resultados:
                temperaturas_fronteras = [{
                    "nombre_pais": r[0],
                    "timestamp": r[1],
                    "temperatura": r[2],
                    "sensacion": r[3],
                    "minima": r[4],
                    "maxima": r[5],
                    "humedad": r[6],
                    "amanecer": r[7],
                    "atardecer": r[8]
                } for r in resultados]
                return temperaturas_fronteras

            return None  # Si no hay datos de temperatura de los países fronterizos

        except mysql.connector.Error as error:
            print("Error al buscar las temperaturas de los países fronterizos:", error)
            return None