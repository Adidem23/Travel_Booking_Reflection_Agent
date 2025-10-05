import mcp
import os
import requests
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

mcp = FastMCP("Trip Planner Server",host="0.0.0.0",port="1820")

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

@mcp.tool(name="get_weather", description="Get current weather for a city using OpenWeatherMap.")
def get_weather(destination: str) -> str:
    WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": destination,
        "appid": WEATHER_API_KEY,
        "units": "metric"
    }

    try:
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        weather_description = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return f"The weather in {destination} is {weather_description} with a temperature of {temp}°C."
    except Exception as e:
        return f"Could not fetch weather for {destination}. Error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="sse")
