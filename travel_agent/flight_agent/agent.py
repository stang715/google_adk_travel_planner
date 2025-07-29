from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json
from dotenv import load_dotenv

load_dotenv()

flight_agent = Agent(
    name="flight_agent",
    model=LiteLlm("openai/gpt-4o"),
    description="Recommends flight options within budget.",
    instruction=(
        "Given an origin, destination, dates, and budget, suggest 2-3 flight options. "
        "For each flight, provide a name, description, price estimate, and duration. "
        "Respond in JSON format using the key 'flights' with a list of flight objects."
    )
)

session_service = InMemorySessionService()
runner = Runner(
    agent=flight_agent,
    app_name="flight_app",
    session_service=session_service
)
USER_ID = "user_flight"
SESSION_ID = "session_flight"

async def execute(request):
    # await session_service.create_session(

    session_service.create_session(
        app_name="flight_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    prompt = (
        f"User wants flights from {request['origin']} to {request['destination']} from {request['start_date']} to {request['end_date']}, "
        f"with a budget of {request['budget']}. Suggest 2-3 flight options, each with name, description, price estimate, and duration. "
        f"Respond in JSON format using the key 'flights' with a list of flight objects."
    )
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    try:
        async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
            if event.is_final_response():
                response_text = event.content.parts[0].text
                print(f"Flight agent raw response: {response_text}")
                
                print(f"Flight agent raw response (first 200 chars): {repr(response_text[:200])}")
                
                # Try multiple parsing strategies
                flights = None
                
                # Strategy 1: Direct JSON parsing (if response is pure JSON)
                try:
                    parsed = json.loads(response_text.strip())
                    flights = parsed.get("flights")
                    if flights:
                        print("Strategy 1 (direct JSON) successful")
                except:
                    pass
                
                # Strategy 2: Extract from ```json blocks
                if not flights:
                    try:
                        import re
                        # Find JSON block with regex
                        json_match = re.search(r'```json\s*\n(.*?)\n```', response_text, re.DOTALL)
                        if json_match:
                            json_content = json_match.group(1).strip()
                            parsed = json.loads(json_content)
                            flights = parsed.get("flights")
                            if flights:
                                print("Strategy 2 (regex extraction) successful")
                    except Exception as e:
                        print(f"Strategy 2 failed: {e}")
                
                # Strategy 3: Simple string replacement
                if not flights:
                    try:
                        cleaned = response_text.replace('```json', '').replace('```', '').strip()
                        parsed = json.loads(cleaned)
                        flights = parsed.get("flights")
                        if flights:
                            print("Strategy 3 (string replacement) successful")
                    except Exception as e:
                        print(f"Strategy 3 failed: {e}")
                
                # Strategy 4: Line-by-line parsing
                if not flights:
                    try:
                        lines = response_text.strip().split('\n')
                        # Remove first and last lines if they contain ```
                        if lines and '```' in lines[0]:
                            lines = lines[1:]
                        if lines and '```' in lines[-1]:
                            lines = lines[:-1]
                        cleaned = '\n'.join(lines).strip()
                        parsed = json.loads(cleaned)
                        flights = parsed.get("flights")
                        if flights:
                            print("Strategy 4 (line-by-line) successful")
                    except Exception as e:
                        print(f"Strategy 4 failed: {e}")
                
                if flights and isinstance(flights, list) and len(flights) > 0:
                    print(f"Successfully parsed {len(flights)} flights")
                    return {"flights": flights}
                else:
                    print("All parsing strategies failed")
                    print(f"Full response content: {repr(response_text)}")
                    return {"flights": []}
        
        # If the loop completes without returning, return empty flights
        return {"flights": []}
    except Exception as e:
        print("Runner failed:", e)
        return {"flights": []}