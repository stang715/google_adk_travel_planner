# ADK-Powered Travel Planner

A multi-agent travel planning system built with Google's Agent Development Kit (ADK). This application demonstrates distributed agent architecture where specialized agents collaborate to create comprehensive travel itineraries.

## 🏗️ Architecture Overview

The system uses a **host-agent orchestration pattern** with four specialized agents:

- **Host Agent** (`localhost:8000`): Orchestrates the entire travel planning workflow
- **Flight Agent** (`localhost:8001`): Finds and recommends flight options
- **Stay Agent** (`localhost:8002`): Suggests hotels and accommodations
- **Activities Agent** (`localhost:8003`): Recommends activities and attractions

## 📁 Project Structure

```
google_adk_travel_planner/
├── travel_agent/
│   ├── host_agent/
│   │   ├── agent.py              # Host agent LLM logic
│   │   ├── task_manager.py       # Orchestration and agent coordination
│   │   ├── __main__.py           # FastAPI server entry point
│   │   └── .well-known/
│   │       └── agent.json        # Agent metadata and capabilities
│   │
│   ├── flight_agent/
│   │   ├── agent.py              # Flight recommendation logic
│   │   ├── task_manager.py       # Flight-specific processing
│   │   ├── __main__.py           # FastAPI server entry point
│   │   └── .well-known/
│   │       └── agent.json        # Agent metadata
│   │
│   ├── stay_agent/
│   │   ├── agent.py              # Hotel recommendation logic
│   │   ├── task_manager.py       # Stay-specific processing
│   │   ├── __main__.py           # FastAPI server entry point
│   │   └── .well-known/
│   │       └── agent.json        # Agent metadata
│   │
│   ├── activities_agent/
│   │   ├── agent.py              # Activity recommendation logic
│   │   ├── task_manager.py       # Activity-specific processing
│   │   ├── __main__.py           # FastAPI server entry point
│   │   └── .well-known/
│   │       └── agent.json        # Agent metadata
│   │
│   ├── common/
│   │   ├── a2a_client.py         # Utility for agent-to-agent communication
│   │   └── a2a_server.py         # Shared FastAPI A2A-compatible server template
│   │
│   ├── shared/
│   │   └── schemas.py            # Shared Pydantic schemas for request/response
│   │
│   └── travel_ui_1.py            # Frontend UI for user interaction
│
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- Google ADK installed

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd google_adk_travel_planner

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
echo "OPENAI_API_KEY=your_openai_api_key" > .env
```

### 2. Start the Agents

You can start all agents with uvicorn commands. Run these from the project root directory:

**Start all agents in background:**
```bash
uvicorn travel_agent.host_agent.__main__:app --port 8000 &
uvicorn travel_agent.flight_agent.__main__:app --port 8001 &
uvicorn travel_agent.stay_agent.__main__:app --port 8002 &      
uvicorn travel_agent.activities_agent.__main__:app --port 8003 &
```

**Or start each agent in separate terminals:**

**Terminal 1 - Host Agent (Port 8000):**
```bash
uvicorn travel_agent.host_agent.__main__:app --port 8000
```

**Terminal 2 - Flight Agent (Port 8001):**
```bash
uvicorn travel_agent.flight_agent.__main__:app --port 8001
```

**Terminal 3 - Stay Agent (Port 8002):**
```bash
uvicorn travel_agent.stay_agent.__main__:app --port 8002
```

**Terminal 4 - Activities Agent (Port 8003):**
```bash
uvicorn travel_agent.activities_agent.__main__:app --port 8003
```

### 3. Start the Frontend

**Streamlit UI:**
```bash
streamlit run travel_agent/travel_ui_1.py
```

## 🖥️ Usage

1. Start all agents using the uvicorn commands above
2. Open your browser to `http://localhost:8501` (Streamlit default port)
3. Fill in the travel planning form:
   - **Origin**: Departure city
   - **Destination**: Travel destination
   - **Start Date**: Trip start date
   - **End Date**: Trip end date
   - **Budget**: Total budget in USD
4. Click "Plan My Trip ✨"
5. View the comprehensive travel plan with flights, accommodations, and activities

## 🛠️ How It Works

### Request Flow

1. **User Input**: Streamlit frontend (`travel_ui_1.py`) collects travel preferences
2. **Host Agent**: Receives request via uvicorn server and coordinates with specialized agents
3. **Parallel Processing**: Flight, Stay, and Activities agents process requests simultaneously
4. **Response Aggregation**: Host agent combines all responses
5. **Frontend Display**: Streamlit renders the formatted travel plan

### Agent Communication

- **Protocol**: HTTP-based A2A (Agent-to-Agent) communication
- **Format**: JSON request/response with shared schemas
- **Endpoints**: Each agent exposes `/run` endpoint for processing requests
- **Discovery**: Agents use `.well-known/agent.json` for capability advertisement

### Data Flow

```
User Input → Streamlit → Host Agent → [Flight, Stay, Activities] Agents
                ↑                              ↓
            Formatted Results ← Host Agent ← Agent Responses
```

## 🔧 Configuration

### Agent Ports
- Host Agent: `8000`
- Flight Agent: `8001`
- Stay Agent: `8002`
- Activities Agent: `8003`
- Streamlit UI: `8501`

### Environment Variables
- `OPENAI_API_KEY`: Required for LLM functionality
- Custom configurations can be added to `.env` file

## 🧪 Testing

Test individual agents using curl:

```bash
# Test flight agent
curl -X POST http://localhost:8001/run \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "New York",
    "destination": "Paris",
    "start_date": "2024-06-01",
    "end_date": "2024-06-10",
    "budget": 3000
  }'
```

## 🐛 Troubleshooting

### Common Issues

1. **Agents not starting**: Check if ports are available and API keys are set
2. **Connection errors**: Ensure all agents are running before starting Streamlit
3. **JSON parsing errors**: Check agent logs for response format issues
4. **Empty results**: Verify agent-specific logic and LLM responses

### Debug Mode

Add debug prints in `task_manager.py` files to trace request/response flow:

```python
print("Incoming payload:", payload)
print("Agent response:", response)
```

## 📝 API Reference

### Request Schema
```json
{
  "origin": "string",
  "destination": "string", 
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "budget": number
}
```

### Response Schema
```json
{
  "flights": "string (JSON formatted)",
  "stay": "string (JSON formatted)", 
  "activities": "string (JSON formatted)"
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with all agents running
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with Google's Agent Development Kit (ADK)
- Uses OpenAI's GPT models for intelligent recommendations
- Streamlit for the user interface
- FastAPI for agent communication