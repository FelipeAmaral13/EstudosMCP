from mcp.server.fastmcp import FastMCP
import requests
import os
from dotenv import load_dotenv

load_dotenv()
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

mcp = FastMCP("CityServices")

def search_lat_lon_city(cidade: str) -> tuple[float, float] | None:
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": cidade, "format": "json", "limit": 1}
    headers = {"User-Agent": "mcp-city-services/1.0"}
    try:
        response = requests.get(url=url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        if not data:
            return None
        return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as error:
        print(f"[ERRO] Geolocalização: {error}")
        return None

@mcp.tool(name="LatLon")
def latitude_longitude(cidade: str) -> str:
    coords = search_lat_lon_city(cidade=cidade)
    if not coords:
        return f"Não encontrei a cidade '{cidade}'."
    lat, lon = coords
    return f"A cidade {cidade} está localizada em Latitude {lat:.4f}, Longitude {lon:.4f}."

@mcp.tool(name="WeatherNow")
def clima_atual(cidade: str) -> str:
    coords = search_lat_lon_city(cidade=cidade)
    if not coords:
        return f"Não encontrei a cidade '{cidade}'."
    
    lat, lon = coords
    weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=pt_br"
    
    try:
        response = requests.get(weather_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        temp = data['main']['temp']
        description = data['weather'][0]['description']
        return f"Clima agora em {cidade}: {description.capitalize()}, {temp:.1f}°C."
    except Exception as error:
        return f"[ERRO] Falha ao consultar clima: {error}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
