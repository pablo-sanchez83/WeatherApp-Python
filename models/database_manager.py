import mysql.connector
from config import DB_CONFIG

class DBManager:
    def __init__(self):
        self.conexion = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conexion.cursor()

    def cerrar_conexion_bd(self):
        self.cursor.close()
        self.conexion.close()

    def paises_existen(self):
        """ Verifica si hay países en la base de datos. """
        self.cursor.execute("SELECT COUNT(*) FROM paises")
        count = self.cursor.fetchone()[0]
        return count > 0

    def fronteras_existen(self):
        """ Verifica si hay fronteras en la base de datos. """
        self.cursor.execute("SELECT COUNT(*) FROM fronteras")
        count = self.cursor.fetchone()[0]
        return count > 0

    def insertar_paises(self, datos_paises):
        """ Inserta países en la base de datos si aún no han sido insertados. """
        if self.paises_existen():
            return False  # Evita la inserción duplicada

        try:
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
            for pais in lista_paises:
                id_pais = pais.get("cca3")
                for frontera in pais.get("borders", []):
                    sql = "INSERT INTO fronteras (idpais, cca3_frontera) VALUES (%s, %s)"
                    self.cursor.execute(sql, (id_pais, frontera))

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
            for pais in lista_paises:
                sql = "INSERT INTO temperaturas (idpais, timestamp, temperatura) VALUES (%s, NOW(), %s)"
                val = (pais["Código cca3"], 25.0)  # Simulación de temperatura
                self.cursor.execute(sql, val)

            self.conexion.commit()
            return True
        except mysql.connector.Error as error:
            print("Error al insertar temperaturas:", error)
            return False
        finally:
            self.cerrar_conexion_bd()
