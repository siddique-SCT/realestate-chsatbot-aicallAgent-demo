from flask import Blueprint, jsonify, request
import os
import json
from datetime import datetime

agents_bp = Blueprint('agents', __name__)

# Demo agent data
DEMO_AGENTS = [
    {
        'id': '1',
        'name': 'Sarah Johnson',
        'specialization': 'Residential Properties',
        'rating': 4.9,
        'available': True,
        'areas': ['Clifton', 'Redland', 'Cotham'],
        'channels': ['voice', 'whatsapp', 'jitsi'],
        'image': 'agent1.jpg'
    },
    {
        'id': '2',
        'name': 'Michael Chen',
        'specialization': 'Luxury Properties',
        'rating': 4.8,
        'available': True,
        'areas': ['Harbourside', 'Hotwells', 'Clifton'],
        'channels': ['voice', 'whatsapp'],
        'image': 'agent2.jpg'
    },
    {
        'id': '3',
        'name': 'Emma Williams',
        'specialization': 'First-time Buyers',
        'rating': 4.7,
        'available': True,
        'areas': ['Southville', 'Bedminster', 'Totterdown'],
        'channels': ['voice', 'jitsi'],
        'image': 'agent3.jpg'
    },
    {
        'id': '4',
        'name': 'David Thompson',
        'specialization': 'Investment Properties',
        'rating': 4.6,
        'available': False,
        'areas': ['City Centre', 'Old Market', 'St Pauls'],
        'channels': ['whatsapp', 'jitsi'],
        'image': 'agent4.jpg'
    }
]

@agents_bp.route('/', methods=['GET'])
def get_agents():
    """Get list of available agents"""
    # In a real implementation, this would fetch agents from a database
    # For demo purposes, we'll return mock data
    return jsonify({
        'agents': DEMO_AGENTS
    })

@agents_bp.route('/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    """Get details for a specific agent"""
    agent = next((a for a in DEMO_AGENTS if a['id'] == agent_id), None)
    
    if agent:
        return jsonify(agent)
    else:
        return jsonify({'error': 'Agent not found'}), 404

@agents_bp.route('/<agent_id>/availability', methods=['PUT'])
def update_agent_availability(agent_id):
    """Update agent availability status"""
    data = request.json
    
    if 'available' not in data:
        return jsonify({'error': 'Missing available status'}), 400
    
    agent = next((a for a in DEMO_AGENTS if a['id'] == agent_id), None)
    
    if not agent:
        return jsonify({'error': 'Agent not found'}), 404
    
    # Update availability
    agent['available'] = data['available']
    
    return jsonify({
        'status': 'success',
        'agent': agent
    })

@agents_bp.route('/match', methods=['POST'])
def match_agent():
    """Match customer with an appropriate agent based on criteria"""
    data = request.json
    
    # Extract matching criteria
    area = data.get('area')
    property_type = data.get('property_type')
    channels = data.get('channels', [])
    
    # Filter available agents
    available_agents = [a for a in DEMO_AGENTS if a['available']]
    
    # Apply filters if provided
    if area:
        available_agents = [a for a in available_agents if any(a_area.lower() == area.lower() for a_area in a['areas'])]
    
    if property_type == 'luxury':
        available_agents = [a for a in available_agents if 'Luxury' in a['specialization']]
    elif property_type == 'investment':
        available_agents = [a for a in available_agents if 'Investment' in a['specialization']]
    elif property_type == 'first-time':
        available_agents = [a for a in available_agents if 'First-time' in a['specialization']]
    
    if channels:
        available_agents = [a for a in available_agents if any(channel in a['channels'] for channel in channels)]
    
    # Sort by rating (highest first)
    available_agents.sort(key=lambda x: x['rating'], reverse=True)
    
    if available_agents:
        return jsonify({
            'status': 'success',
            'agent': available_agents[0]
        })
    else:
        return jsonify({
            'status': 'no_match',
            'message': 'No matching agents available at this time'
        })