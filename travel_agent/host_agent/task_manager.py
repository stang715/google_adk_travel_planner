import json
import re
"""
The task manager executes the orchestration logic by calling remote agents 
and handling the full trip-planning workflow. 
For its practical implementation, we define the service URLs for each child agent. 
These endpoints conform to the A2A /run protocol 
and expect a shared TravelRequest` JSON schema.
"""
from travel_agent.common.a2a_client import call_agent

FLIGHT_URL = "http://localhost:8001/run"
STAY_URL = "http://localhost:8002/run"
ACTIVITIES_URL = "http://localhost:8003/run"

def extract_json_from_response(response):
    """
    Helper function to extract JSON from various response formats
    """
    if isinstance(response, dict):
        return response
    
    if isinstance(response, str):
        # Try to parse as direct JSON first
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Try to extract from markdown code blocks
        cleaned = response.strip()
        if cleaned.startswith('```'):
            lines = cleaned.split('\n')
            if lines[0].startswith('```'):
                lines = lines[1:]
            if lines and lines[-1].strip() == '```':
                lines = lines[:-1]
            cleaned = '\n'.join(lines).strip()
        
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return {}
    
    return {}

# define the payload.
async def run(payload):
    # Print what the host agent is sending
    print("Incoming payload:", payload)
    
    flights_response = await call_agent(FLIGHT_URL, payload)
    stay_response = await call_agent(STAY_URL, payload)
    activities_response = await call_agent(ACTIVITIES_URL, payload)
    
    # Log raw responses
    print("Raw flights response:", flights_response)
    print("Raw stay response:", stay_response)
    print("Raw activities response:", activities_response)
    
    # Extract JSON from responses
    flights_data = extract_json_from_response(flights_response)
    stay_data = extract_json_from_response(stay_response)
    activities_data = extract_json_from_response(activities_response)
    
    print("Parsed flights data:", flights_data)
    print("Parsed stay data:", stay_data)
    print("Parsed activities data:", activities_data)
    
    # Extract the actual data arrays with fallback handling
    flights = flights_data.get("flights", [])
    stays = stay_data.get("stays", []) or stay_data.get("hotels", [])
    activities = activities_data.get("activities", [])
    
    # Additional fallback: if stay_data is empty but stay_response is a string, try to parse it
    if not stays and isinstance(stay_response, str) and stay_response != "No stay options returned.":
        print("Attempting fallback parsing of stay_response string...")
        fallback_data = extract_json_from_response(stay_response)
        stays = fallback_data.get("stays", []) or fallback_data.get("hotels", [])
        print(f"Fallback parsing result: {stays}")
    
    print(f"Final extracted data - flights: {len(flights)}, stays: {len(stays)}, activities: {len(activities)}")
    
    # Format for frontend (as JSON strings wrapped in markdown)
    flights_result = f'```json\n{{"flights": {json.dumps(flights)}}}\n```' if flights else "No flights returned."
    stays_result = f'```json\n{{"hotels": {json.dumps(stays)}}}\n```' if stays else "No stay options returned."
    activities_result = f'```json\n{{"activities": {json.dumps(activities)}}}\n```' if activities else "No activities found."
    
    return {
        "flights": flights_result,
        "stay": stays_result,
        "activities": activities_result
    }