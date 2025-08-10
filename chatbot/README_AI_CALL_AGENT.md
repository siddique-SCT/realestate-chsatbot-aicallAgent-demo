# AI Call Agent Integration

## Overview

The AI Call Agent feature enhances the real estate chatbot with voice-based AI agents that can make cold calls, call leads, or answer support calls while sounding like real humans. These AI agents work 24/7, never get sick, never quit, remember every instruction perfectly, and are cost-effective compared to human agents.

## Features

- **Human-like Voice Agents**: Multiple voice profiles available (male/female)
- **Specialized Agents**: Create agents with specific skills (lead qualification, appointment scheduling, etc.)
- **Scalable**: Deploy thousands of agents with a single click
- **24/7 Availability**: Agents are always available to make or receive calls
- **Perfect Recall**: Agents remember every instruction and conversation detail
- **Cost-effective**: Lower cost than human agents

## Integration

The system integrates with BrightCall.ai for production use, with a fallback to a demo implementation when the BrightCall.ai API is not available.

### Components

1. **Backend Integration**:
   - `brightcall_integration.py`: Handles the BrightCall.ai API integration
   - `routes/call_agents.py`: API endpoints for managing AI call agents

2. **Frontend**:
   - `templates/call_agents.html`: User interface for managing AI agents and scheduling calls

## API Endpoints

### Agent Management

- `GET /api/call-agents/`: List all available AI agents
- `GET /api/call-agents/<agent_id>`: Get details for a specific agent
- `POST /api/call-agents/`: Create a new AI agent
- `PUT /api/call-agents/<agent_id>`: Update an existing agent

### Call Scripts

- `GET /api/call-agents/scripts`: Get available call scripts

### Call Management

- `POST /api/call-agents/calls`: Schedule a new call
- `GET /api/call-agents/calls/<call_id>`: Get status of a specific call
- `DELETE /api/call-agents/calls/<call_id>`: Cancel a scheduled call
- `GET /api/call-agents/calls/history`: Get call history with optional filters

## Usage

### Creating an AI Agent

```python
data = {
    "name": "Alex",
    "voice_profile": "natural_female_1",
    "specialization": ["Lead qualification", "Property inquiries"],
    "language": ["English"]
}

response = requests.post("/api/call-agents/", json=data)
```

### Scheduling a Call

```python
data = {
    "phone_number": "+1234567890",
    "script_type": "lead_qualification",
    "scheduled_time": "now",  # or ISO timestamp for scheduled calls
    "agent_id": "agent_ai_1",  # optional, will auto-select if not provided
    "context": {  # optional additional context
        "property_id": "prop123",
        "customer_name": "John Doe",
        "notes": "Interested in 3-bedroom properties in downtown"
    }
}

response = requests.post("/api/call-agents/calls", json=data)
```

## Configuration

The AI Call Agent feature can be configured using environment variables:

- `BRIGHTCALL_API_KEY`: API key for BrightCall.ai integration
- `BRIGHTCALL_BASE_URL`: Base URL for BrightCall.ai API (optional)

## Demo Mode

When the BrightCall.ai integration is not available (API key not set or module import fails), the system operates in demo mode with simulated agents and calls. This allows for testing and demonstration without requiring the actual BrightCall.ai service.

## Web Interface

A web interface is available at `/call-agents` that provides:

- List of available AI agents with their status and statistics
- Form to create new AI agents
- Interface to schedule calls
- Call history with filtering options
- Detailed view of call information