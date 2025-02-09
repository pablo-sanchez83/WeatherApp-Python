# **Aplicacion Del Clima ⛈️🌧️🌦️🌥️⛅🌤️☀️**
## Aplicación del Clima 🌞

Esta es una aplicación sencilla que monitorea el clima utilizando Python, MySQL y Flask. Permite acceder a información metereológica de manera fácil y concisa.

---

## **Descripción**  
La aplicación está diseñada para mostrar información sobre el clima, como temperaturas, sensacion, entre otros. Utiliza MySQL como base de datos y Flask para la lógica de consulta.

---

## **Técnologías Empleado**

- **Motores:**
  - **Científicos:** Python
  - **Lanzamiento:** Docker
  - **Base de Datos:** MySQL
  - **Ruta de Muestreo:** Flask

---

## **Instalación**  
1. **Prerrequisitos:**  
   - Instalar Docker Compose en tu sistema (puedes hacerlo ejecutando `docker-compose install` en la terminal).
   
2. **Configuración de Ambientación:**  
   Asegúrate de que los siguientes archivos estén en la misma carpeta:  
   - `docker-compose.yml`  
   - `init.sql`

3. **Instalar Ambiente de Desarrollo:**  
   Abre una terminal y ejecuta:  
   ```bash
   cd direccion_proyecto
   docker compose up -d
   python -m venv venv
   ./venv/Scripts/activate 
   ```

4. **Instalar Requisitos:**  
   Escribe en la terminal:  
   ```bash
   pip install -r requirements.txt
   ```

5. **Ejecutar la Aplicación:**  
   Finaliza de ejecutar el script `app.py` con:  
   ```bash
   python app.py
   ```

---

## **Técnicas Empleado**

- **Motor de Cálculo:** Flask para crear una interfaz web simple y una API de consulta.
- **Base de Datos:** MySQL para almacenar y manejar datos气象ológicos.
- **Lanzamiento:** Docker Compose para ejecutar la aplicación en un entorno distribuido y manejado.

---
## **Ayuda**  
Si tienes dudas,consulta la documentación de:  
- Python: https://docs.python.org es en español.  
- Docker Compose: https://docs.docker.com/compose/  
- MySQL: https://www.mariadb.com/en/docs/mysql/  
- Flask: https://flask.palletsolutions.com/  

---

## **Ejemplo de Uso en la Terminal**  
```bash
$ docker-compose up -d
$ py app.py
```

La aplicación se ejecutará automáticamente por un servidor local.
