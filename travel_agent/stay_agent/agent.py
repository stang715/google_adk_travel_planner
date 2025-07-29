from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json
from dotenv import load_dotenv

load_dotenv()

stay_agent = Agent(
    name="stay_agent",
    model=LiteLlm("openai/gpt-4o"),
    description="Finds hotels within budget.",
    instruction=(
        "Given a destination, dates, and budget, suggest 2-3 hotel options. "
        "For each hotel, provide a name, a short description, price estimate, and amenities. "
        "Respond in JSON format using the key 'hotels' or 'stays' with a list of hotel objects."
    )
)

session_service = InMemorySessionService()
runner = Runner(
    agent=stay_agent,
    app_name="stay_app",
    session_service=session_service
)
USER_ID = "user_stay"
SESSION_ID = "session_stay"

async def execute(request):
    # await session_service.create_session(
    session_service.create_session(
        app_name="stay_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    prompt = (
        f"User is looking for hotels in {request['destination']} from {request['start_date']} to {request['end_date']}, "
        f"with a budget of {request['budget']}. Suggest 2-3 hotels, each with name, description, price estimate, and amenities. "
        f"Respond in JSON format using the key 'hotels' with a list of hotel objects."
    )
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    try:
        async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
            if event.is_final_response():
                response_text = event.content.parts[0].text
                print(f"Stay agent raw response: {response_text}")  # Debug print
                
                # More robust cleaning of markdown code blocks
                cleaned = response_text.strip()
                print(f"Original response: {repr(response_text[:100])}...")
                
                # Remove markdown code blocks more reliably
                if '```json' in cleaned:
                    # Find and extract content between ```json and ```
                    start_marker = '```json'
                    end_marker = '```'
                    
                    start_idx = cleaned.find(start_marker)
                    if start_idx != -1:
                        start_idx += len(start_marker)
                        end_idx = cleaned.find(end_marker, start_idx)
                        if end_idx != -1:
                            cleaned = cleaned[start_idx:end_idx].strip()
                elif cleaned.startswith('```'):
                    # Handle generic ``` blocks
                    lines = cleaned.split('\n')
                    # Remove first line if it starts with ```
                    if lines[0].strip().startswith('```'):
                        lines = lines[1:]
                    # Remove last line if it's just ```
                    if lines and lines[-1].strip() == '```':
                        lines = lines[:-1]
                    cleaned = '\n'.join(lines).strip()
                
                print(f"Cleaned response: {repr(cleaned[:100])}...")
                
                try:
                    parsed = json.loads(cleaned)
                    hotels = parsed.get("hotels") or parsed.get("stays")
                    if isinstance(hotels, list) and len(hotels) > 0:
                        print(f"Successfully parsed {len(hotels)} hotels")
                        # Return a proper dictionary, not a markdown string
                        return {"stays": hotels}
                    else:
                        print("No hotels found in parsed response")
                        return {"stays": []}
                except json.JSONDecodeError as e:
                    print("JSON parsing failed:", e)
                    print("Response content:", repr(response_text))
                    print("Cleaned content:", repr(cleaned))
                    # Try one more fallback - maybe there's extra whitespace
                    try:
                        # Remove all possible markdown artifacts
                        fallback_clean = response_text.replace('```json', '').replace('```', '').strip()
                        print(f"Fallback cleaned: {repr(fallback_clean[:100])}...")
                        parsed = json.loads(fallback_clean)
                        hotels = parsed.get("hotels") or parsed.get("stays")
                        if isinstance(hotels, list) and len(hotels) > 0:
                            print(f"Fallback parsing successful: {len(hotels)} hotels")
                            return {"stays": hotels}
                    except Exception as fallback_e:
                        print(f"Fallback parsing also failed: {fallback_e}")
                    
                    return {"stays": []}
                except Exception as e:
                    print("Other parsing error:", e)
                    print("Response content:", repr(response_text))
                    return {"stays": []}
        
        # If the loop completes without returning, return empty stays
        return {"stays": []}
    except Exception as e:
        print("Runner failed:", e)
        return {"stays": []}