import mcp
import os
import requests
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

mcp = FastMCP("Trip Planner Server")

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
YELP_API_KEY = os.getenv("YELP_API_KEY")


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


# @mcp.tool(name="get_restaurants", description="Find top restaurants in a city using Yelp.")
# def get_restaurants(city: str, cuisine: str = None) -> str:
#     YELP_SEARCH_URL = "https://api.yelp.com/v3/businesses/search"

#     headers = {
#         "Authorization": f"Bearer {YELP_API_KEY}"
#     }

#     params = {
#         "location": city,
#         "limit": 5,
#         "sort_by": "rating"
#     }

#     if cuisine:
#         params["term"] = cuisine

#     try:
#         response = requests.get(YELP_SEARCH_URL, headers=headers, params=params)
#         response.raise_for_status()
#         data = response.json()

#         businesses = data.get("businesses", [])
#         if not businesses:
#             return f"No restaurants found in {city} for cuisine: {cuisine or 'any'}."

#         result = []
#         for b in businesses:
#             name = b["name"]
#             rating = b["rating"]
#             address = ", ".join(b["location"]["display_address"])
#             result.append(f"{name} (Rating: {rating}) - {address}")

#         return "\n".join(result)

#     except Exception as e:
#         return f"Could not fetch restaurants for {city}. Error: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
