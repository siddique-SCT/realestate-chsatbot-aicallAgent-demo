from flask import Blueprint, jsonify
import os
import json
from pathlib import Path

property_bp = Blueprint('property', __name__)

# Mock property tour data for demo purposes
MOCK_TOURS = {
    '1': {
        'tourAvailable': True,
        'tourImages': ['property1_1.jpg', 'property1_2.jpg', 'property1_3.jpg'],
        'tourDescription': 'Spacious living room with natural light, modern kitchen with island, and master bedroom with en-suite bathroom.'
    },
    '2': {
        'tourAvailable': True,
        'tourImages': ['property2_1.jpg', 'property2_2.jpg'],
        'tourDescription': 'Open concept living area, renovated kitchen with stainless steel appliances, and private balcony with city views.'
    },
    '3': {
        'tourAvailable': True,
        'tourImages': ['property3_1.jpg', 'property3_2.jpg', 'property3_3.jpg', 'property3_4.jpg'],
        'tourDescription': 'Elegant entrance hall, formal dining room, chef\'s kitchen, and landscaped garden with patio area.'
    }
}

@property_bp.route('/<property_id>/tour', methods=['GET'])
def get_property_tour(property_id):
    """Get virtual tour data for a specific property"""
    # In a real implementation, this would fetch tour data from a database
    # For demo purposes, we'll return mock data
    
    # Check if we have actual listings data
    listings_path = Path(__file__).parent.parent.parent / 'embeddings' / 'listings.json'
    if listings_path.exists():
        try:
            with open(listings_path, 'r') as f:
                listings = json.load(f)
                
            # Find the property in listings
            property_data = next((listing for listing in listings if str(listing.get('id')) == str(property_id)), None)
            
            if property_data:
                # Check if property has images field
                if 'images' in property_data and property_data['images']:
                    return jsonify({
                        'tourAvailable': True,
                        'tourImages': property_data['images'],
                        'tourDescription': property_data.get('description', 'No description available'),
                        'propertyDetails': property_data
                    })
        except Exception as e:
            print(f"Error loading listings: {e}")
    
    # Fallback to mock data
    if property_id in MOCK_TOURS:
        return jsonify(MOCK_TOURS[property_id])
    
    # Default response if no tour is available
    return jsonify({
        'tourAvailable': False,
        'message': 'Virtual tour not available for this property'
    })