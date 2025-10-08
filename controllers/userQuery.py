import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from views.userQuery import requetsedQuery
from AgenticPattern.reflection_agent import ReflectionAgent

load_dotenv()

router = APIRouter(prefix="/userQuery", tags=["userQuery"])

JWT_SECRET = os.getenv("JWT_SECRET", "nashikislove")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_ISSUER = os.getenv("JWT_ISSUER", "fastapi-auth-server")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "mcp-server")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/userQuery/generate_token")


def create_jwt(username: str, scope: str = "trip:plan weather:read"):
    payload = {
        "sub": username,                         
        "iss": JWT_ISSUER,                       
        "aud": JWT_AUDIENCE,                     
        "scope": scope,                           
        "exp": datetime.utcnow() + timedelta(hours=1)  
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_jwt(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM],
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER
        )
        return payload 
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {str(e)}")


@router.get("/")
def send_breating_msg():
    return {"message": "I am Jinda Here !!"}


@router.get("/generate_token")
def generate_token(
    username: str = Query(..., description="Username for the token"),
    scope: str = Query("trip:plan weather:read", description="OAuth scopes")
):
    token = create_jwt(username=username, scope=scope)
    return {"access_token": token, "token_type": "bearer"}


@router.post("/agentResponse")
async def process_Agent_Response(
    userQuery: requetsedQuery,
    user: dict = Depends(verify_jwt)  
):
    reflection_Agent = ReflectionAgent(user_claims=user)

    generation_system_prompt = "You are a travel booking agent which creates the best plan according to the user requirements"

    reflection_system_prompt = """You are a Reflection Agent.
    Review the Trip Agent’s itinerary and provide structured feedback.
    Check for completeness (transport, lodging, activities, weather).
    Check for accuracy (dates, times, feasibility).
    Check for user experience (local attractions, budget, upgrades).
    Point out issues clearly and suggest actionable improvements.
    Do not regenerate the plan—only critique and refine.
    """

    user_msg = userQuery.actualQueryString

    final_response = await reflection_Agent.run(
        user_msg=user_msg,
        generation_system_prompt=generation_system_prompt,
        reflection_system_prompt=reflection_system_prompt,
        n_steps=10
    )

    return {"user": user, "response": final_response}