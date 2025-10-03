from dotenv import load_dotenv
from fastapi import APIRouter
from views.userQuery import requetsedQuery
from AgenticPattern.reflection_agent import ReflectionAgent


load_dotenv()

router = APIRouter(prefix="/userQuery",tags=["userQuery"])

@router.get("/")
def send_breating_msg():
        return {"message":"I am Jinda Here !!"}

@router.post("/agentResponse")
async def process_Agent_Response(userQuery:requetsedQuery):
        reflection_Agent=ReflectionAgent()
        
        generation_system_prompt = "You are a travel booking agent which creates a best plan according to the user requirements"

        reflection_system_prompt = """You are a Reflection Agent.
        Review the Trip Agent’s itinerary and provide structured feedback.
        Check for completeness (transport, lodging, activities, weather).
        Check for accuracy (dates, times, feasibility).
        Check for user experience (local attractions, budget, upgrades).
        Point out issues clearly and suggest actionable improvements.
        Do not regenerate the plan—only critique and refine.
        """

        user_msg =userQuery.actualQueryString

        final_response = await reflection_Agent.run(
            user_msg=user_msg,
            generation_system_prompt=generation_system_prompt,
            reflection_system_prompt=reflection_system_prompt,
            n_steps=10
        )

        return final_response
