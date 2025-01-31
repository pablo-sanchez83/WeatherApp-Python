import mysql.connector

class DBManager:
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
        except mysql.connector.Error as error:
            print("Error al conectar a la base de datos: ", error)

    def cerrar_conexion_bd(self):
        if self.cursor:
            self.cursor.close()
        if self.base_datos:
            self.base_datos.close()