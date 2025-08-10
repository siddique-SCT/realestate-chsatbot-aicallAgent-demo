from flask import Blueprint, jsonify, request
import os
import json
from datetime import datetime
import time

analytics_bp = Blueprint('analytics', __name__)

# In-memory storage for demo purposes
# In a real implementation, this would be stored in a database
conversation_analytics = []
lead_analytics = []

@analytics_bp.route('/conversation', methods=['POST'])
def log_conversation():
    """Log conversation analytics"""
    data = request.json
    
    # Validate required fields
    required_fields = ['sessionId', 'messages']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Add timestamp
    analytics_entry = {
        'timestamp': datetime.now().isoformat(),
        'sessionId': data['sessionId'],
        'messages': data['messages'],
        'messageCount': len(data['messages']),
        'userMessageCount': len([m for m in data['messages'] if m.get('from') == 'user']),
        'botMessageCount': len([m for m in data['messages'] if m.get('from') == 'bot']),
        'leadConverted': data.get('leadConverted', False),
        'duration': data.get('duration', 0)  # in seconds
    }
    
    # Extract common user intents/topics
    user_messages = [m.get('text', '') for m in data['messages'] if m.get('from') == 'user']
    topics = extract_topics(user_messages)
    analytics_entry['topics'] = topics
    
    # Store analytics
    conversation_analytics.append(analytics_entry)
    
    # In a real implementation, this would be saved to a database
    
    return jsonify({
        'status': 'success',
        'message': 'Conversation analytics logged'
    })

@analytics_bp.route('/lead', methods=['POST'])
def log_lead():
    """Log lead analytics"""
    data = request.json
    
    # Validate required fields
    required_fields = ['name', 'phone']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Add timestamp
    analytics_entry = {
        'timestamp': datetime.now().isoformat(),
        'name': data['name'],
        'phone': data['phone'],
        'email': data.get('email', ''),
        'propertyInterest': data.get('propertyInterest', ''),
        'preferredTime': data.get('preferredTime', 'immediate'),
        'source': data.get('source', 'chat'),
        'callbackRequested': data.get('callbackRequested', True),
        'callbackInitiated': data.get('callbackInitiated', False)
    }
    
    # Store analytics
    lead_analytics.append(analytics_entry)
    
    # In a real implementation, this would be saved to a database
    
    return jsonify({
        'status': 'success',
        'message': 'Lead analytics logged'
    })

@analytics_bp.route('/dashboard', methods=['GET'])
def get_analytics_dashboard():
    """Get analytics dashboard data"""
    # Calculate conversation metrics
    total_conversations = len(conversation_analytics)
    total_leads = len(lead_analytics)
    
    conversion_rate = 0
    if total_conversations > 0:
        conversion_rate = (total_leads / total_conversations) * 100
    
    # Calculate average conversation duration
    avg_duration = 0
    if total_conversations > 0:
        durations = [c.get('duration', 0) for c in conversation_analytics]
        avg_duration = sum(durations) / len(durations)
    
    # Get common topics
    all_topics = []
    for conv in conversation_analytics:
        all_topics.extend(conv.get('topics', []))
    
    topic_counts = {}
    for topic in all_topics:
        if topic in topic_counts:
            topic_counts[topic] += 1
        else:
            topic_counts[topic] = 1
    
    # Sort topics by count
    sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
    top_topics = sorted_topics[:5] if sorted_topics else []
    
    # Get recent conversations
    recent_conversations = sorted(conversation_analytics, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
    
    # Get recent leads
    recent_leads = sorted(lead_analytics, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
    
    return jsonify({
        'metrics': {
            'totalConversations': total_conversations,
            'totalLeads': total_leads,
            'conversionRate': round(conversion_rate, 2),
            'avgDuration': round(avg_duration, 2)
        },
        'topTopics': [{'topic': t[0], 'count': t[1]} for t in top_topics],
        'recentConversations': recent_conversations,
        'recentLeads': recent_leads
    })

def extract_topics(messages):
    """Extract common topics from user messages"""
    # Simple keyword-based topic extraction
    # In a real implementation, this would use NLP techniques
    
    topics = []
    
    # Define topic keywords
    topic_keywords = {
        'price': ['price', 'cost', 'budget', 'afford', 'expensive', 'cheap'],
        'location': ['location', 'area', 'neighborhood', 'city', 'town', 'street'],
        'bedrooms': ['bedroom', 'bed', 'br', 'sleep'],
        'bathrooms': ['bathroom', 'bath', 'shower', 'toilet'],
        'amenities': ['garden', 'garage', 'parking', 'pool', 'gym', 'balcony'],
        'schools': ['school', 'education', 'university', 'college'],
        'transport': ['transport', 'bus', 'train', 'subway', 'commute'],
        'viewing': ['viewing', 'tour', 'visit', 'see the property'],
        'agent': ['agent', 'broker', 'realtor', 'speak with someone']
    }
    
    # Check each message for topics
    for message in messages:
        message_lower = message.lower()
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                topics.append(topic)
    
    # Remove duplicates
    return list(set(topics))