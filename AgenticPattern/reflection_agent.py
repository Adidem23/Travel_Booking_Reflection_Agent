import os
from agents import Agent, Runner
from agents.mcp import MCPServerSse
from utils.completions import build_prompt_structure, FixedFirstChatHistory, update_chat_history
from dotenv import load_dotenv

load_dotenv()

GOOGLE_GEMINI_API_KEY = os.getenv("GOOGLE_GEMINI_API_KEY", "")

BASE_GENERATION_SYSTEM_PROMPT = """
Your task is to Generate the best content possible for the user's request.
If the user provides critique, respond with a revised version of your previous attempt.
You must always output the revised content.
"""

BASE_REFLECTION_SYSTEM_PROMPT = """
You are tasked with generating critique and recommendations to the user's generated content.
If the user content has something wrong or something to be improved, output a list of recommendations
and critiques. If the user content is ok and there's nothing to change, output this: <OK>
"""

class ReflectionAgent:
    def __init__(self, user_claims: dict, name: str = "Travel Booking Agent",
                 instructions: str = "You are a travel booking agent which creates a best plan according to the user requirements"):
        """
        :param user_claims: JWT claims dict (decoded token) from FastAPI route
        """
        self.name = name
        self.instructions = instructions
        self.user_claims = user_claims
        self.jwt_token = user_claims.get("token") if "token" in user_claims else None

    async def _request_completion(self, history: list) -> str:
        """
        Makes a call to MCP Server with Authorization header
        """
        headers = {}
        if self.jwt_token:
            headers["Authorization"] = f"Bearer {self.jwt_token}"

        async with MCPServerSse(
            name="Trip Planner Server",
            params={
                "url": "http://localhost:1820/sse",
                "headers": headers
            },
            cache_tools_list=True,
        ) as server:
            agent = Agent(
                name=self.name,
                instructions=self.instructions,
                model="gpt-4.1",
                mcp_servers=[server]
            )
            result = await Runner.run(agent, history)
            return result.final_output

    async def generate(self, generation_history: list) -> str:
        return await self._request_completion(generation_history)

    async def reflect(self, reflection_history: list) -> str:
        return await self._request_completion(reflection_history)

    async def run(
        self,
        user_msg: str,
        generation_system_prompt: str = "",
        reflection_system_prompt: str = "",
        n_steps: int = 10,
    ) -> str:
        generation_system_prompt += BASE_GENERATION_SYSTEM_PROMPT
        reflection_system_prompt += BASE_REFLECTION_SYSTEM_PROMPT

        generation_history = FixedFirstChatHistory(
            [
                build_prompt_structure(prompt=generation_system_prompt, role="system"),
                build_prompt_structure(prompt=user_msg, role="user"),
            ],
            total_length=3,
        )

        reflection_history = FixedFirstChatHistory(
            [build_prompt_structure(prompt=reflection_system_prompt, role="system")],
            total_length=3,
        )

        for step in range(n_steps):
            generation = await self.generate(generation_history)
            update_chat_history(generation_history, generation, "assistant")
            update_chat_history(reflection_history, generation, "user")

            critique = await self.reflect(reflection_history)

            if "<OK>" in critique:
                print("\n\nStop Sequence found. Stopping the reflection loop ... \n\n")
                break

            update_chat_history(generation_history, critique, "user")
            update_chat_history(reflection_history, critique, "assistant")

        return generation
