# agent.py
# step 1 imports
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
# load_dotenv(dotenv_path="/Users/siweitang/Documents/experienment/DataCamp_GoogleADK/.env")

# step 2: defines a top-level ADK agent responsible for 
# coordinating the full trip plan. While we don’t invoke sub-agents 
# from the LLM in this implementation, the system prompt sets up 
# the role for a future extension where the LLM could potentially 
# handle tool use and meta-reasoning.
host_agent = Agent(
    name="host_agent",
    model=LiteLlm("openai/gpt-4o"),
    description="Coordinates travel planning by calling flight, stay, and activity agents.",
    instruction="You are the host agent responsible for orchestrating trip planning tasks. "
                "You call external agents to gather flights, stays, and activities, then return a final result."
)
session_service = InMemorySessionService()
runner = Runner(
    agent=host_agent,
    app_name="host_app",
    session_service=session_service
)
USER_ID = "user_host"
SESSION_ID = "session_host"


"""
This execute() function serves as the main entry point to the host agent’s LLM. It:

Initializes a session (for memory support if needed)
Dynamically constructs a user prompt
Sends it to the model using ADK’s runner.run_async() method
Finally, awaits and extracts the final response
"""
async def execute(request):
    # Ensure session exists
    session_service.create_session(
        app_name="host_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    prompt = (
        f"Plan a trip to {request['destination']} from {request['start_date']} to {request['end_date']} "
        f"within a total budget of {request['budget']}. Call the flights, stays, and activities agents for results."
    )
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            return {"summary": event.content.parts[0].text}
        

    # # Return a mock response for testing
    # return {
    #     "activities": [
    #         {
    #             "name": "Test Activity 1",
    #             "description": "A fun test activity.",
    #             "price_estimate": "$50",
    #             "duration": "2h"
    #         },
    #         {
    #             "name": "Test Activity 2",
    #             "description": "Another test activity.",
    #             "price_estimate": "$30",
    #             "duration": "1.5h"
    #         }
    #     ]
    # }