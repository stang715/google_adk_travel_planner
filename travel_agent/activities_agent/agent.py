from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json
from dotenv import load_dotenv

load_dotenv()

activities_agent = Agent(
    name="activities_agent",
    model=LiteLlm("openai/gpt-4o"),
    description="Suggests engaging activities within budget.",
    instruction=(
        "Given a destination, dates, and budget, suggest 2-3 engaging activities. "
        "For each activity, provide a name, description, price estimate, and duration. "
        "Respond in JSON format using the key 'activities' with a list of activity objects."
    )
)

session_service = InMemorySessionService()
runner = Runner(
    agent=activities_agent,
    app_name="activities_app",
    session_service=session_service
)
USER_ID = "user_activities"
SESSION_ID = "session_activities"

async def execute(request):
    # await session_service.create_session(
    session_service.create_session(
        app_name="activities_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    prompt = (
        f"User is visiting {request['destination']} from {request['start_date']} to {request['end_date']}, "
        f"with a budget of {request['budget']}. Suggest 2-3 engaging activities, each with name, description, price estimate, and duration. "
        f"Respond in JSON format using the key 'activities' with a list of activity objects."
    )
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    try:
        async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
            if event.is_final_response():
                response_text = event.content.parts[0].text
                print(f"Activities agent raw response: {response_text}")
                
                print(f"Activities agent raw response (first 200 chars): {repr(response_text[:200])}")
                
                # Try multiple parsing strategies
                activities = None
                
                # Strategy 1: Direct JSON parsing (if response is pure JSON)
                try:
                    parsed = json.loads(response_text.strip())
                    activities = parsed.get("activities")
                    if activities:
                        print("Strategy 1 (direct JSON) successful")
                except:
                    pass
                
                # Strategy 2: Extract from ```json blocks
                if not activities:
                    try:
                        import re
                        # Find JSON block with regex
                        json_match = re.search(r'```json\s*\n(.*?)\n```', response_text, re.DOTALL)
                        if json_match:
                            json_content = json_match.group(1).strip()
                            parsed = json.loads(json_content)
                            activities = parsed.get("activities")
                            if activities:
                                print("Strategy 2 (regex extraction) successful")
                    except Exception as e:
                        print(f"Strategy 2 failed: {e}")
                
                # Strategy 3: Simple string replacement
                if not activities:
                    try:
                        cleaned = response_text.replace('```json', '').replace('```', '').strip()
                        parsed = json.loads(cleaned)
                        activities = parsed.get("activities")
                        if activities:
                            print("Strategy 3 (string replacement) successful")
                    except Exception as e:
                        print(f"Strategy 3 failed: {e}")
                
                # Strategy 4: Line-by-line parsing
                if not activities:
                    try:
                        lines = response_text.strip().split('\n')
                        # Remove first and last lines if they contain ```
                        if lines and '```' in lines[0]:
                            lines = lines[1:]
                        if lines and '```' in lines[-1]:
                            lines = lines[:-1]
                        cleaned = '\n'.join(lines).strip()
                        parsed = json.loads(cleaned)
                        activities = parsed.get("activities")
                        if activities:
                            print("Strategy 4 (line-by-line) successful")
                    except Exception as e:
                        print(f"Strategy 4 failed: {e}")
                
                if activities and isinstance(activities, list) and len(activities) > 0:
                    print(f"Successfully parsed {len(activities)} activities")
                    return {"activities": activities}
                else:
                    print("All parsing strategies failed")
                    print(f"Full response content: {repr(response_text)}")
                    return {"activities": []}
        
        # If the loop completes without returning, return empty activities
        return {"activities": []}
    except Exception as e:
        print("Runner failed:", e)
        return {"activities": []}