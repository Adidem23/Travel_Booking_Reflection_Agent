import os
import requests
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
from fastapi import Request, HTTPException
from jose import jwt, JWTError

load_dotenv()

# === JWT Config ===
JWT_SECRET = os.getenv("JWT_SECRET", "nashikislove")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ISSUER = os.getenv("JWT_ISSUER", "fastapi-auth-server")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "mcp-server")

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Create MCP server
mcp = FastMCP("Trip Planner Server", host="0.0.0.0", port=1820)

# === Tool with built-in JWT auth ===
@mcp.tool(name="get_weather", description="Get current weather for a city using OpenWeatherMap.")
def get_weather(destination: str, request: Request = None) -> str:
    # --- Auth check ---
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Authorization Header")

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER
        )
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired JWT: {str(e)}")

    # --- Scope check ---
    scopes = payload.get("scope", "")
    if "weather:read" not in scopes.split():
        raise HTTPException(status_code=403, detail="Missing required scope: weather:read")

    # --- Weather fetch logic ---
    WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": destination, "appid": WEATHER_API_KEY, "units": "metric"}

    try:
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        weather_description = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return f"[User: {payload['sub']}] Weather in {destination}: {weather_description}, {temp}°C."
    except Exception as e:
        return f"Could not fetch weather for {destination}. Error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport="sse")