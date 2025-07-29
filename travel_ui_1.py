import streamlit as st
import requests

st.set_page_config(page_title="ADK-Powered Travel Planner", page_icon="✈️")
st.title("🌍 ADK-Powered Travel Planner")
origin = st.text_input("Where are you flying from?", placeholder="e.g., New York")
destination = st.text_input("Destination", placeholder="e.g., Paris")
start_date = st.date_input("Start Date")
end_date = st.date_input("End Date")
budget = st.number_input("Budget (in USD)", min_value=100, step=50)


import json
import re

def extract_json_list(raw_str, key):
    """
    Extracts and parses a JSON list from a string like '```json\n{ "flights": [...] }\n```'
    Returns the list or None.
    """
    if not raw_str or not isinstance(raw_str, str):
        return None
    
    # More robust cleaning approach
    cleaned = raw_str.strip()
    
    # Remove markdown code block markers
    if cleaned.startswith('```'):
        # Find the first newline after ```json or ```
        lines = cleaned.split('\n')
        if lines[0].startswith('```'):
            lines = lines[1:]  # Remove first line with ```
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]  # Remove last line with ```
        cleaned = '\n'.join(lines)
    
    cleaned = cleaned.strip()
    
    # Debug print to see what we're trying to parse
    print(f"Attempting to parse: {cleaned[:100]}...")
    
    try:
        parsed = json.loads(cleaned)
        return parsed.get(key)
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed: {e}")
        print(f"Full content being parsed: {repr(cleaned)}")
        return None
    except Exception as e:
        print(f"Other error: {e}")
        return None


# Function to format flight options, activities, and stays
# so that they are displayed nicely in Streamlit
# instead of returning raw JSON
def format_flights(flights):
    if not flights:
        return "No flights found."
    result = ""
    for f in flights:
        result += f"**{f['name']}**\n\n"
        result += f"{f['description']}\n\n"
        result += f"Price: ${f['price_estimate']}\n"
        result += f"Duration: {f['duration']} hours\n\n---\n"
    return result

def format_activities(activities):
    if not activities:
        return "No activities found."
    result = ""
    for a in activities:
        duration = a.get('duration', a.get('duration_in_hours', 'N/A'))
        result += f"**{a.get('name', 'Unknown Activity')}**\n\n"
        result += f"{a.get('description', '')}\n\n"
        result += f"Price: ${a.get('price_estimate', 'N/A')}\n"
        result += f"Duration: {duration} hours\n\n---\n"
    return result

def format_stays(stays):
    if not stays:
        return "No stays found."
    result = ""
    for s in stays:
        result += f"**{s.get('name', 'Unknown Hotel')}**\n\n"
        result += f"{s.get('description', '')}\n\n"
        result += f"Price: ${s.get('price_estimate', 'N/A')}\n"
        result += f"Amenities: {s.get('amenities', 'N/A')}\n\n---\n"
    return result

# Ensure all fields are filled before submitting
if st.button("Plan My Trip ✨"):
    if not all([origin, destination, start_date, end_date, budget]):
        st.warning("Please fill in all the details.")
    else:
        payload = {
            "origin": origin,
            "destination": destination,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "budget": budget
        }
        response = requests.post("http://localhost:8000/run", json=payload)
        if response.ok:
            data = response.json()
            st.write("Raw response:", data)
            # Flights
            st.subheader("✈️ Flights")
            try:
                flights_raw = data.get("flights", None)
                flights = extract_json_list(flights_raw, "flights")
                if flights:
                    st.markdown(format_flights(flights), unsafe_allow_html=True)
                else:
                    st.warning("No flight options returned or format incorrect.")
            except Exception as e:
                st.error(f"Error displaying flights: {e}")

            # Stays
            st.subheader("🏨 Stays")
            try:
                stays_raw = data.get("stay", None)
                print(f"Raw stays data received: {stays_raw}")  # Debug print
                
                # Try "hotels" first since that's what your backend returns
                stays = extract_json_list(stays_raw, "hotels") or extract_json_list(stays_raw, "stays")
                
                if stays:
                    st.markdown(format_stays(stays), unsafe_allow_html=True)
                else:
                    st.warning("No stay options returned or format incorrect.")
                    # Show raw data for debugging
                    if stays_raw:
                        st.text("Debug - Raw stays data:")
                        st.text(stays_raw)
            except Exception as e:
                st.error(f"Error displaying stays: {e}")
                print(f"Exception in stays processing: {e}")

            # Activities
            st.subheader("🗺️ Activities")
            try:
                activities_raw = data.get("activities", None)
                activities = extract_json_list(activities_raw, "activities")
                if activities:
                    st.markdown(format_activities(activities), unsafe_allow_html=True)
                else:
                    st.warning("No activities returned or format incorrect.")
            except Exception as e:
                st.error(f"Error displaying activities: {e}")
        else:
            st.error("Failed to fetch travel plan. Please try again.")