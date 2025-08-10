from flask import Blueprint, request, jsonify
import os
import json
from datetime import datetime, timedelta

# Import the BrightCall.ai integration
try:
    from brightcall_integration import BrightCallAI
    brightcall = BrightCallAI(api_key=os.getenv('BRIGHTCALL_API_KEY'))
    brightcall_available = True
except ImportError:
    brightcall_available = False
    brightcall = None

# Create blueprint
call_agents_bp = Blueprint('call_agents', __name__, url_prefix='/api/call-agents')

# In-memory storage for demo purposes
if not brightcall_available:
    demo_agents = [
        {
            "id": "agent_ai_1",
            "name": "Alex",
            "voice_profile": "natural_female_1",
            "specialization": ["Lead qualification", "Property inquiries"],
            "language": ["English"],
            "status": "active",
            "calls_handled": 245,
            "avg_call_duration": 3.5,  # minutes
            "success_rate": 0.78,
            "created_at": "2023-06-15T10:00:00Z"
        },
        {
            "id": "agent_ai_2",
            "name": "Michael",
            "voice_profile": "natural_male_1",
            "specialization": ["Appointment scheduling", "Follow-ups"],
            "language": ["English"],
            "status": "active",
            "calls_handled": 189,
            "avg_call_duration": 2.8,  # minutes
            "success_rate": 0.82,
            "created_at": "2023-07-22T14:30:00Z"
        }
    ]
    
    demo_calls = []

@call_agents_bp.route('/', methods=['GET'])
def get_ai_agents():
    """Get all available AI call agents"""
    if brightcall_available:
        agents = brightcall.get_ai_agents()
        return jsonify({
            "success": True,
            "agents": agents
        })
    else:
        return jsonify({
            "success": True,
            "agents": demo_agents,
            "demo_mode": True
        })

@call_agents_bp.route('/<agent_id>', methods=['GET'])
def get_ai_agent(agent_id):
    """Get a specific AI call agent"""
    if brightcall_available:
        agents = brightcall.get_ai_agents()
        agent = next((a for a in agents if a["id"] == agent_id), None)
    else:
        agent = next((a for a in demo_agents if a["id"] == agent_id), None)
    
    if not agent:
        return jsonify({
            "success": False,
            "error": "Agent not found"
        }), 404
    
    return jsonify({
        "success": True,
        "agent": agent
    })

@call_agents_bp.route('/', methods=['POST'])
def create_ai_agent():
    """Create a new AI call agent"""
    data = request.json
    
    # Validate required fields
    required_fields = ["name", "voice_profile", "specialization", "language"]
    for field in required_fields:
        if field not in data:
            return jsonify({
                "success": False,
                "error": f"Missing required field: {field}"
            }), 400
    
    if brightcall_available:
        result = brightcall.create_ai_agent(
            name=data["name"],
            voice_profile=data["voice_profile"],
            specialization=data["specialization"],
            language=data["language"]
        )
        return jsonify(result)
    else:
        # Demo implementation
        agent_id = f"agent_ai_{len(demo_agents) + 1}"
        
        new_agent = {
            "id": agent_id,
            "name": data["name"],
            "voice_profile": data["voice_profile"],
            "specialization": data["specialization"],
            "language": data["language"],
            "status": "training",
            "calls_handled": 0,
            "avg_call_duration": 0,
            "success_rate": 0,
            "created_at": datetime.now().isoformat()
        }
        
        demo_agents.append(new_agent)
        
        return jsonify({
            "success": True,
            "agent_id": agent_id,
            "status": "training",
            "estimated_completion": (datetime.now() + timedelta(hours=2)).isoformat(),
            "demo_mode": True
        })

@call_agents_bp.route('/<agent_id>', methods=['PUT'])
def update_ai_agent(agent_id):
    """Update an existing AI call agent"""
    data = request.json
    
    if brightcall_available:
        result = brightcall.update_ai_agent(agent_id, data)
        return jsonify(result)
    else:
        # Demo implementation
        agent = next((a for a in demo_agents if a["id"] == agent_id), None)
        
        if not agent:
            return jsonify({
                "success": False,
                "error": "Agent not found",
                "agent_id": agent_id
            }), 404
        
        # Update allowed fields
        allowed_updates = ["name", "specialization", "status"]
        for field in allowed_updates:
            if field in data:
                agent[field] = data[field]
        
        return jsonify({
            "success": True,
            "agent_id": agent_id,
            "agent": agent,
            "demo_mode": True
        })

@call_agents_bp.route('/scripts', methods=['GET'])
def get_call_scripts():
    """Get all available call scripts"""
    if brightcall_available:
        scripts = brightcall.get_call_scripts()
        return jsonify({
            "success": True,
            "scripts": scripts
        })
    else:
        # Demo implementation
        demo_scripts = {
            "lead_qualification": {
                "name": "Property Interest Qualification",
                "greeting": "Hello, this is {agent_name} from Bristol Real Estate. I noticed you recently expressed interest in one of our properties. Do you have a moment to chat?",
                "questions": [
                    "Could you tell me what type of property you're looking for?",
                    "What areas in Bristol are you interested in?",
                    "What's your budget range?",
                    "Are you looking to buy or rent?",
                    "What's your timeline for moving?"
                ],
                "responses": {
                    "budget_too_low": "While we might not have properties in that exact price range right now, I can keep you updated if something becomes available. Would that be helpful?",
                    "area_not_available": "We don't currently have listings in that specific area, but we do have some great options in nearby neighborhoods. Would you be open to exploring those?"
                },
                "closing": "Based on what you've shared, I think we might have some properties that would be a good fit. Would you like me to arrange for one of our agents to give you a call to discuss these options in more detail?"
            },
            "appointment_scheduling": {
                "name": "Property Viewing Appointment",
                "greeting": "Hello, this is {agent_name} from Bristol Real Estate. I'm calling about scheduling a viewing for the property you inquired about at {property_address}. Is this a good time to talk?",
                "questions": [
                    "When would be a convenient day for you to view the property?",
                    "Would you prefer a morning or afternoon appointment?",
                    "Will anyone else be joining you for the viewing?",
                    "Have you already viewed other properties in the area?"
                ],
                "responses": {
                    "date_not_available": "I'm sorry, but that date is fully booked. Could we look at either the day before or after?",
                    "agent_preference": "Certainly, I can arrange for that specific agent to show you the property. They have excellent knowledge of the area."
                },
                "closing": "Great! I've scheduled your viewing for {date} at {time} with {agent_name}. You'll receive a confirmation email shortly with all the details. Is there anything else you'd like to know about the property before your visit?"
            }
        }
        
        return jsonify({
            "success": True,
            "scripts": demo_scripts,
            "demo_mode": True
        })

@call_agents_bp.route('/calls', methods=['POST'])
def schedule_call():
    """Schedule a call with an AI agent"""
    data = request.json
    
    # Validate required fields
    required_fields = ["phone_number", "script_type"]
    for field in required_fields:
        if field not in data:
            return jsonify({
                "success": False,
                "error": f"Missing required field: {field}"
            }), 400
    
    if brightcall_available:
        result = brightcall.schedule_call(
            phone_number=data["phone_number"],
            script_type=data["script_type"],
            scheduled_time=data.get("scheduled_time"),
            agent_id=data.get("agent_id"),
            context=data.get("context")
        )
        return jsonify(result)
    else:
        # Demo implementation
        call_id = f"call_{int(datetime.now().timestamp())}_{len(demo_calls) + 1}"
        
        # Select agent
        agent_id = data.get("agent_id")
        if agent_id:
            agent = next((a for a in demo_agents if a["id"] == agent_id), None)
        else:
            # Use first agent if none specified
            agent = demo_agents[0] if demo_agents else None
        
        if not agent:
            return jsonify({
                "success": False,
                "error": "No available agents"
            }), 400
        
        # Set scheduled time
        if data.get("scheduled_time") == "now":
            call_time = datetime.now().isoformat()
            status = "in_progress"
        else:
            # If no specific time provided, schedule for 30 minutes from now
            scheduled_time = data.get("scheduled_time")
            if not scheduled_time:
                scheduled_time = (datetime.now() + timedelta(minutes=30)).isoformat()
            call_time = scheduled_time
            status = "scheduled"
        
        # Create call record
        call_record = {
            "call_id": call_id,
            "phone_number": data["phone_number"],
            "agent_id": agent["id"],
            "agent_name": agent["name"],
            "script_type": data["script_type"],
            "scheduled_time": call_time,
            "status": status,
            "context": data.get("context", {}),
            "created_at": datetime.now().isoformat()
        }
        
        demo_calls.append(call_record)
        
        return jsonify({
            "success": True,
            "call_id": call_id,
            "agent": {
                "id": agent["id"],
                "name": agent["name"]
            },
            "scheduled_time": call_time,
            "status": status,
            "demo_mode": True
        })

@call_agents_bp.route('/calls/<call_id>', methods=['GET'])
def get_call_status(call_id):
    """Get status of a scheduled or active call"""
    if brightcall_available:
        result = brightcall.get_call_status(call_id)
        return jsonify(result)
    else:
        # Demo implementation
        call = next((c for c in demo_calls if c["call_id"] == call_id), None)
        
        if not call:
            return jsonify({
                "success": False,
                "error": "Call not found",
                "call_id": call_id
            }), 404
        
        return jsonify({
            "success": True,
            "call_id": call_id,
            "status": call["status"],
            "details": call,
            "demo_mode": True
        })

@call_agents_bp.route('/calls/<call_id>', methods=['DELETE'])
def cancel_call(call_id):
    """Cancel a scheduled call"""
    if brightcall_available:
        result = brightcall.cancel_call(call_id)
        return jsonify(result)
    else:
        # Demo implementation
        call = next((c for c in demo_calls if c["call_id"] == call_id), None)
        
        if not call:
            return jsonify({
                "success": False,
                "error": "Call not found",
                "call_id": call_id
            }), 404
        
        if call["status"] == "completed":
            return jsonify({
                "success": False,
                "error": "Cannot cancel a completed call",
                "call_id": call_id
            }), 400
        
        call["status"] = "cancelled"
        call["end_time"] = datetime.now().isoformat()
        
        return jsonify({
            "success": True,
            "call_id": call_id,
            "status": "cancelled",
            "demo_mode": True
        })

@call_agents_bp.route('/calls/history', methods=['GET'])
def get_call_history():
    """Get history of completed calls"""
    # Get filter parameters
    agent_id = request.args.get('agent_id')
    status = request.args.get('status')
    phone_number = request.args.get('phone_number')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    filters = {}
    if agent_id:
        filters["agent_id"] = agent_id
    if status:
        filters["status"] = status
    if phone_number:
        filters["phone_number"] = phone_number
    if date_from:
        filters["date_from"] = date_from
    if date_to:
        filters["date_to"] = date_to
    
    if brightcall_available:
        result = brightcall.get_call_history(filters)
        return jsonify(result)
    else:
        # Demo implementation
        history = demo_calls.copy()
        
        if agent_id:
            history = [c for c in history if c["agent_id"] == agent_id]
        if status:
            history = [c for c in history if c["status"] == status]
        if phone_number:
            history = [c for c in history if c["phone_number"] == phone_number]
        
        return jsonify({
            "success": True,
            "total": len(history),
            "calls": history,
            "demo_mode": True
        })