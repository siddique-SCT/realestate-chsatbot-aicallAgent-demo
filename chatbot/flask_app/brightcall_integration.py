import os
import json
import time
import random
from datetime import datetime, timedelta

# This file simulates integration with BrightCall.ai for AI call agent functionality

class BrightCallAI:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('BRIGHTCALL_API_KEY', 'demo_key')
        self.call_agents = []
        self.active_calls = {}
        self.call_history = []
        self.call_scripts = {}
        self.load_demo_agents()
        self.load_demo_scripts()
    
    def load_demo_agents(self):
        """Load demo AI call agents"""
        self.call_agents = [
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
            },
            {
                "id": "agent_ai_3",
                "name": "Sophia",
                "voice_profile": "natural_female_2",
                "specialization": ["Customer support", "Technical inquiries"],
                "language": ["English", "Spanish"],
                "status": "active",
                "calls_handled": 312,
                "avg_call_duration": 4.2,  # minutes
                "success_rate": 0.75,
                "created_at": "2023-05-10T09:15:00Z"
            }
        ]
    
    def load_demo_scripts(self):
        """Load demo call scripts for different scenarios"""
        self.call_scripts = {
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
            },
            "follow_up": {
                "name": "Post-Viewing Follow-Up",
                "greeting": "Hello, this is {agent_name} from Bristol Real Estate. I'm calling to follow up on your recent viewing of the property at {property_address}. Do you have a moment to chat about your impressions?",
                "questions": [
                    "What did you think of the property?",
                    "Was there anything particular that you liked or disliked?",
                    "How does it compare to other properties you've viewed?",
                    "Are you interested in making an offer or would you like to see more properties?"
                ],
                "responses": {
                    "interested": "That's great to hear! Would you like me to connect you with our sales team to discuss next steps for making an offer?",
                    "not_interested": "I appreciate your feedback. Based on what you've shared, I might have some other properties that better match your preferences. Would you be interested in hearing about those?"
                },
                "closing": "Thank you for sharing your thoughts. I'll {next_step} and get back to you by {follow_up_date}. Is there anything else you'd like to discuss about your property search?"
            }
        }
    
    def get_ai_agents(self):
        """Get list of available AI call agents"""
        return self.call_agents
    
    def get_call_scripts(self):
        """Get available call scripts"""
        return self.call_scripts
    
    def schedule_call(self, phone_number, script_type, scheduled_time=None, agent_id=None, context=None):
        """Schedule a call with an AI agent"""
        # Validate phone number (simple validation)
        if not phone_number or not isinstance(phone_number, str) or len(phone_number) < 10:
            return {
                "success": False,
                "error": "Invalid phone number",
                "call_id": None
            }
        
        # Validate script type
        if script_type not in self.call_scripts:
            return {
                "success": False,
                "error": f"Unknown script type: {script_type}",
                "call_id": None
            }
        
        # Select agent
        selected_agent = None
        if agent_id:
            selected_agent = next((a for a in self.call_agents if a["id"] == agent_id), None)
        
        if not selected_agent:
            # Randomly select an agent if none specified or specified agent not found
            selected_agent = random.choice(self.call_agents)
        
        # Generate call ID
        call_id = f"call_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Set scheduled time
        if scheduled_time == "now":
            call_time = datetime.now().isoformat()
            status = "in_progress"
        else:
            # If no specific time provided, schedule for 30 minutes from now
            if not scheduled_time:
                scheduled_time = (datetime.now() + timedelta(minutes=30)).isoformat()
            call_time = scheduled_time
            status = "scheduled"
        
        # Create call record
        call_record = {
            "call_id": call_id,
            "phone_number": phone_number,
            "agent_id": selected_agent["id"],
            "agent_name": selected_agent["name"],
            "script_type": script_type,
            "scheduled_time": call_time,
            "status": status,
            "context": context or {},
            "created_at": datetime.now().isoformat()
        }
        
        # Store call record
        self.active_calls[call_id] = call_record
        
        return {
            "success": True,
            "call_id": call_id,
            "agent": {
                "id": selected_agent["id"],
                "name": selected_agent["name"]
            },
            "scheduled_time": call_time,
            "status": status
        }
    
    def get_call_status(self, call_id):
        """Get status of a scheduled or active call"""
        if call_id not in self.active_calls:
            # Check call history
            historical_call = next((c for c in self.call_history if c["call_id"] == call_id), None)
            if historical_call:
                return {
                    "success": True,
                    "call_id": call_id,
                    "status": historical_call["status"],
                    "details": historical_call
                }
            return {
                "success": False,
                "error": "Call not found",
                "call_id": call_id
            }
        
        call = self.active_calls[call_id]
        
        # Simulate call progress for demo purposes
        if call["status"] == "in_progress" and random.random() < 0.3:
            # 30% chance the call has completed since last check
            call["status"] = "completed"
            call["end_time"] = datetime.now().isoformat()
            call["duration"] = random.randint(2, 8) * 60  # 2-8 minutes in seconds
            call["outcome"] = random.choice(["successful", "voicemail", "no_answer", "follow_up_needed"])
            
            # Move to history
            self.call_history.append(call)
            del self.active_calls[call_id]
        
        # Simulate starting scheduled calls
        if call["status"] == "scheduled":
            scheduled_time = datetime.fromisoformat(call["scheduled_time"].replace('Z', '+00:00'))
            if datetime.now() > scheduled_time:
                call["status"] = "in_progress"
                call["start_time"] = datetime.now().isoformat()
        
        return {
            "success": True,
            "call_id": call_id,
            "status": call["status"],
            "details": call
        }
    
    def cancel_call(self, call_id):
        """Cancel a scheduled call"""
        if call_id not in self.active_calls:
            return {
                "success": False,
                "error": "Call not found",
                "call_id": call_id
            }
        
        call = self.active_calls[call_id]
        
        if call["status"] == "completed":
            return {
                "success": False,
                "error": "Cannot cancel a completed call",
                "call_id": call_id
            }
        
        if call["status"] == "in_progress":
            # End the call if it's in progress
            call["status"] = "cancelled"
            call["end_time"] = datetime.now().isoformat()
            self.call_history.append(call)
            del self.active_calls[call_id]
        else:
            # Just mark as cancelled if it's scheduled
            call["status"] = "cancelled"
            self.call_history.append(call)
            del self.active_calls[call_id]
        
        return {
            "success": True,
            "call_id": call_id,
            "status": "cancelled"
        }
    
    def get_call_history(self, filters=None):
        """Get history of completed calls with optional filtering"""
        history = self.call_history.copy()
        
        if filters:
            if "agent_id" in filters:
                history = [c for c in history if c["agent_id"] == filters["agent_id"]]
            if "status" in filters:
                history = [c for c in history if c["status"] == filters["status"]]
            if "phone_number" in filters:
                history = [c for c in history if c["phone_number"] == filters["phone_number"]]
            if "date_from" in filters:
                date_from = datetime.fromisoformat(filters["date_from"].replace('Z', '+00:00'))
                history = [c for c in history if datetime.fromisoformat(c["created_at"].replace('Z', '+00:00')) >= date_from]
            if "date_to" in filters:
                date_to = datetime.fromisoformat(filters["date_to"].replace('Z', '+00:00'))
                history = [c for c in history if datetime.fromisoformat(c["created_at"].replace('Z', '+00:00')) <= date_to]
        
        return {
            "success": True,
            "total": len(history),
            "calls": history
        }
    
    def create_ai_agent(self, name, voice_profile, specialization, language):
        """Create a new AI call agent (demo implementation)"""
        # In a real implementation, this would train a new AI agent with the specified parameters
        agent_id = f"agent_ai_{len(self.call_agents) + 1}"
        
        new_agent = {
            "id": agent_id,
            "name": name,
            "voice_profile": voice_profile,
            "specialization": specialization,
            "language": language,
            "status": "training",  # New agents start in training mode
            "calls_handled": 0,
            "avg_call_duration": 0,
            "success_rate": 0,
            "created_at": datetime.now().isoformat()
        }
        
        self.call_agents.append(new_agent)
        
        # Simulate training process (in real implementation, this would be an async process)
        # After a delay, the agent would move to "active" status
        
        return {
            "success": True,
            "agent_id": agent_id,
            "status": "training",
            "estimated_completion": (datetime.now() + timedelta(hours=2)).isoformat()
        }
    
    def update_ai_agent(self, agent_id, updates):
        """Update an existing AI call agent"""
        agent = next((a for a in self.call_agents if a["id"] == agent_id), None)
        
        if not agent:
            return {
                "success": False,
                "error": "Agent not found",
                "agent_id": agent_id
            }
        
        # Update allowed fields
        allowed_updates = ["name", "specialization", "status"]
        for field in allowed_updates:
            if field in updates:
                agent[field] = updates[field]
        
        return {
            "success": True,
            "agent_id": agent_id,
            "agent": agent
        }
    
    def create_call_script(self, script_name, script_type, script_content):
        """Create a new call script"""
        if script_type in self.call_scripts:
            return {
                "success": False,
                "error": f"Script type '{script_type}' already exists",
                "script_type": script_type
            }
        
        # Validate script content (simplified)
        required_fields = ["greeting", "questions", "responses", "closing"]
        for field in required_fields:
            if field not in script_content:
                return {
                    "success": False,
                    "error": f"Missing required field in script content: {field}",
                    "script_type": script_type
                }
        
        # Add the new script
        script_content["name"] = script_name
        self.call_scripts[script_type] = script_content
        
        return {
            "success": True,
            "script_type": script_type,
            "script_name": script_name
        }
    
    def update_call_script(self, script_type, updates):
        """Update an existing call script"""
        if script_type not in self.call_scripts:
            return {
                "success": False,
                "error": f"Script type '{script_type}' not found",
                "script_type": script_type
            }
        
        # Update script fields
        for field, value in updates.items():
            if field in self.call_scripts[script_type]:
                self.call_scripts[script_type][field] = value
        
        return {
            "success": True,
            "script_type": script_type,
            "script": self.call_scripts[script_type]
        }

# Example usage
def test_brightcall():
    brightcall = BrightCallAI()
    
    # Get available agents
    agents = brightcall.get_ai_agents()
    print(f"Available AI agents: {len(agents)}")
    
    # Schedule a call
    call_result = brightcall.schedule_call(
        phone_number="+44 7700 900123",
        script_type="lead_qualification",
        context={
            "lead_name": "John Smith",
            "property_interest": "3-bed apartment in Clifton",
            "source": "Website chat"
        }
    )
    
    print(f"Scheduled call: {call_result}")
    
    # Check call status
    if call_result["success"]:
        call_id = call_result["call_id"]
        status = brightcall.get_call_status(call_id)
        print(f"Call status: {status}")

if __name__ == "__main__":
    test_brightcall()