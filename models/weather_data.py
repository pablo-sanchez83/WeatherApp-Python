class WeatherAppDataRequest:
    def extraer_paises(self):
        """
        Obtiene datos de paises de la API REST Europe.

        Esta función hace una solicitud GET a la API REST Europe para obtener información sobre los países de Europa.
        Luego, procesa el JSON de la respuesta y lo convierte en una lista de diccionarios con información detallada 
        sobre cada país, incluyendo su nombre, capital, región, códigos, pertenencia a las UE, coordenadas generales
        y capitales, entre otros.

        Returns:
            List[Dict]: Lista de diccionarios con datos extraidos de la respuesta de la API.
            
        Raises:
            requests.exceptions.HTTPError: Si ocurre un error de conexión o respuesta no OK.
        """
        respuesta = requests.get("https://restcountries.com/v3.1/region/europe")
        respuesta.raise_for_status()

        try:
            # Procesamos la respuesta JSON
            datos_extraidos = []
            for pais in respuesta.json():
                info_pais = {
                    "Nombre": pais.get("name", {}).get("common", "Desconocido"),
                    "Capital": ", ".join(pais.get("capital", ["No especificada"])),
                    "Region": pais.get("region", "Desconocida"),
                    "Subregión": pais.get("subregion", "Desconocida"),
                    "Código cca2": pais.get("cca2", "N/A"),
                    "Código cca3": pais.get("cca3", "N/A"),
                    "Pertenece a las NU": pais.get("unMember", False),
                    "Latitud": pais.get("latlng", [0, 0])[0],
                    "Longitud": pais.get("latlng", [0, 0])[1],
                    "lat_cap": pais.get("capitalInfo.latlng", [0, 0])[0],
                    "lon_cap": pais.get("capitalInfo.latlng", [0, 0])[1],
                    "borders": pais.get("borders", []),
                }
                datos_extraidos.append(info_pais)
            
            return datos_extraidos
        except requests.exceptions.HTTPError as e:
            print(f"Error en la solicitud HTTP: {e}")
            raise
