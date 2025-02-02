import requests

class WeatherAppDataRequest:
    def extraer_paises(self):
        respuesta = requests.get("https://restcountries.com/v3.1/region/europe")
        respuesta.raise_for_status()
        lista_paises = respuesta.json()
        
        datos_extraidos = []
        for pais in lista_paises:
            datos_extraidos.append({
                "Nombre": pais.get("name", {}).get("common", "Desconocido"),
                "Capital": ", ".join(pais.get("capital", ["No especificada"])),
                "Región": pais.get("region", "Desconocida"),
                "Subregión": pais.get("subregion", "Desconocida"),
                "Código cca2": pais.get("cca2", "N/A"),
                "Código cca3": pais.get("cca3", "N/A"),
                "Pertenece a las NU": pais.get("unMember", False),
                "Latitud": pais.get("latlng", [0, 0])[0],
                "Longitud": pais.get("latlng", [0, 0])[1],
                "lat_cap": pais.get("capitalInfo.latlng", [0, 0])[0],
                "lon_cap": pais.get("capitalInfo.latlng", [0, 0])[1],
                "borders": pais.get("borders", []),
            })
        return datos_extraidos
