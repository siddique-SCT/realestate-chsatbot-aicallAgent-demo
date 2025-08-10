const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const axios = require('axios');
const fs = require('fs');
const path = require('path');

// For OpenAI integration
require('dotenv').config();
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

// For Azure AI services integration
const AZURE_LANGUAGE_KEY = process.env.AZURE_LANGUAGE_KEY;
const AZURE_LANGUAGE_ENDPOINT = process.env.AZURE_LANGUAGE_ENDPOINT;

// For BrightCall.ai integration
const BRIGHTCALL_API_KEY = process.env.BRIGHTCALL_API_KEY;
const BRIGHTCALL_API_ENDPOINT = process.env.BRIGHTCALL_API_ENDPOINT || 'https://api.brightcall.ai/v1';

const app = express();
app.use(cors());
app.use(bodyParser.json());

// Demo listings
const listings = [
  {id:1, title:'3-bed house Clifton', description:'Beautiful 3 bed, 2 bath house in Clifton with sea view', price:250000, location:'Clifton', bedrooms:3, features:['sea view', 'garden', 'parking'], images:['house1_1.jpg', 'house1_2.jpg']},
  {id:2, title:'2-bed flat DHA', description:'2 bed flat near park in DHA', price:120000, location:'DHA', bedrooms:2, features:['balcony', 'security'], images:['flat1_1.jpg', 'flat1_2.jpg']},
  {id:3, title:'3-bed apartment PECHS', description:'Spacious 3 bed apartment in PECHS', price:180000, location:'PECHS', bedrooms:3, features:['gym', 'swimming pool'], images:['apt1_1.jpg', 'apt1_2.jpg']},
  {id:4, title:'4-bed villa Gulshan', description:'Luxury 4 bed villa in Gulshan with private pool', price:350000, location:'Gulshan', bedrooms:4, features:['pool', 'garden', 'security'], images:['villa1_1.jpg', 'villa1_2.jpg']},
  {id:5, title:'1-bed studio Saddar', description:'Cozy 1 bed studio apartment in Saddar', price:80000, location:'Saddar', bedrooms:1, features:['furnished', 'city view'], images:['studio1_1.jpg', 'studio1_2.jpg']}
];

// Try to load listings from JSON file if available
try {
  const listingsPath = path.join(__dirname, '..', 'embeddings', 'listings.json');
  if (fs.existsSync(listingsPath)) {
    const loadedListings = JSON.parse(fs.readFileSync(listingsPath, 'utf8'));
    if (Array.isArray(loadedListings) && loadedListings.length > 0) {
      console.log(`Loaded ${loadedListings.length} listings from file`);
      listings.push(...loadedListings.filter(l => !listings.some(existing => existing.id === l.id)));
    }
  }
} catch (error) {
  console.error('Error loading listings from file:', error.message);
}

// Advanced retrieval with semantic search and LLM enhancement
app.post('/api/chat', async (req, res) => {
  const { message, sessionId } = req.body;
  if(!message) return res.json({reply: "Please send a message."});
  
  // First try semantic search if available
  let matches = [];
  try {
    // Try to use Python embeddings service if available
    const embeddingResponse = await axios.post('http://localhost:5000/api/search', {
      query: message,
      top_k: 5
    }).catch(() => null);
    
    if (embeddingResponse && embeddingResponse.data && embeddingResponse.data.results) {
      matches = embeddingResponse.data.results;
      console.log('Using vector search results');
    }
  } catch (error) {
    console.log('Vector search unavailable, falling back to keyword search');
  }
  
  // Fallback to keyword search if no results or vector search failed
  if (!matches.length) {
    const q = message.toLowerCase();
    matches = listings.filter(l => 
      q.includes(l.location.toLowerCase()) || 
      q.includes(String(l.bedrooms)) ||
      (l.features && l.features.some(f => q.includes(f.toLowerCase())))
    );
  }
  
  let reply;
  
  // Try to use OpenAI for more natural responses if API key is available
  if (OPENAI_API_KEY) {
    try {
      const openaiResponse = await axios.post('https://api.openai.com/v1/chat/completions', {
        model: "gpt-4o-mini",
        messages: [
          {role: "system", content: "You are a helpful real estate assistant. Be concise and professional."},
          {role: "user", content: `User query: ${message}\n\nAvailable listings: ${JSON.stringify(matches.slice(0, 3))}\n\nRespond to the user's query based on these listings. If there are matches, mention one example property. Keep your response under 100 words.`}
        ],
        temperature: 0.7,
        max_tokens: 250
      }, {
        headers: {
          'Authorization': `Bearer ${OPENAI_API_KEY}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (openaiResponse.data && openaiResponse.data.choices && openaiResponse.data.choices[0]) {
        reply = openaiResponse.data.choices[0].message.content;
        console.log('Using OpenAI response');
        return res.json({reply, matches: matches.slice(0, 3)});
      }
    } catch (error) {
      console.error('OpenAI error:', error.message);
    }
  }
  
  // Fallback to template response
  if(matches.length) {
    const match = matches[0];
    reply = `I found ${matches.length} listing(s). Example: ${match.title} — ${match.description} (Price: ${match.price})`;
    
    // Add feature highlights if available
    if (match.features && match.features.length) {
      reply += `. Features: ${match.features.join(', ')}`;
    }
    
    // Add call-to-action for virtual tour or callback
    reply += `. Would you like to see more details, schedule a virtual tour, or speak with an agent?`;
  } else {
    reply = "Sorry, I couldn't find matching listings. Try: '3 bed Clifton' or mention features like 'garden' or 'pool'.";
  }
  
  res.json({reply, matches: matches.slice(0, 3)});
});

// Save lead and trigger BrightCall.ai for immediate callback
app.post('/api/lead', async (req, res) => {
  const { name, phone, email, consent, preferredTime, propertyInterest } = req.body;
  const leadData = { 
    name, 
    phone, 
    email, 
    consent, 
    preferredTime: preferredTime || 'immediate',
    propertyInterest: propertyInterest || '',
    time: new Date().toISOString(),
    source: 'website_chat'
  };
  
  console.log('New lead:', leadData);
  
  // TODO: persist to DB, encrypt phone if storing long-term
  let callbackResult = null;
  
  // Trigger BrightCall.ai for immediate callback if consent given and API key available
  if (consent && phone && BRIGHTCALL_API_KEY) {
    try {
      const brightcallResponse = await axios.post(`${BRIGHTCALL_API_ENDPOINT}/callbacks`, {
        phone: phone,
        name: name,
        email: email,
        message: `New lead interested in ${propertyInterest || 'properties'}`,
        callImmediately: preferredTime === 'immediate',
        scheduleTime: preferredTime !== 'immediate' ? preferredTime : null
      }, {
        headers: {
          'Authorization': `Bearer ${BRIGHTCALL_API_KEY}`,
          'Content-Type': 'application/json'
        }
      }).catch(err => {
        console.error('BrightCall API error:', err.message);
        return null;
      });
      
      if (brightcallResponse && brightcallResponse.data) {
        callbackResult = brightcallResponse.data;
        console.log('BrightCall.ai callback initiated:', callbackResult);
      }
    } catch (error) {
      console.error('Error triggering BrightCall.ai:', error.message);
    }
  }
  
  res.json({ 
    status: 'lead saved', 
    callback: callbackResult ? 'initiated' : 'not initiated',
    callbackDetails: callbackResult
  });
});

// Enhanced callback trigger endpoint with BrightCall.ai integration
app.post('/api/callback', async (req, res) => {
  const { provider='brightcall', phone, name, email, propertyId, scheduleTime } = req.body;
  
  // Log the callback request
  console.log('Callback requested', { provider, phone, name, propertyId, scheduleTime });
  
  // Get property details if propertyId is provided
  let propertyDetails = '';
  if (propertyId) {
    const property = listings.find(l => l.id == propertyId);
    if (property) {
      propertyDetails = `${property.title} (${property.location}, ${property.bedrooms} bed, ${property.price})`;  
    }
  }
  
  if (provider.toLowerCase() === 'brightcall' && BRIGHTCALL_API_KEY) {
    try {
      const brightcallResponse = await axios.post(`${BRIGHTCALL_API_ENDPOINT}/callbacks`, {
        phone: phone,
        name: name || 'Website Visitor',
        email: email || '',
        message: propertyDetails ? `Interested in: ${propertyDetails}` : 'Property inquiry',
        callImmediately: !scheduleTime,
        scheduleTime: scheduleTime || null
      }, {
        headers: {
          'Authorization': `Bearer ${BRIGHTCALL_API_KEY}`,
          'Content-Type': 'application/json'
        }
      }).catch(err => {
        console.error('BrightCall API error:', err.message);
        return { status: 'error', message: err.message };
      });
      
      return res.json({ 
        status: 'callback queued', 
        provider, 
        phone,
        callbackId: brightcallResponse.data?.callbackId || null,
        scheduledTime: scheduleTime || 'immediate'
      });
    } catch (error) {
      console.error('Error triggering BrightCall.ai:', error.message);
      return res.json({ status: 'error', message: error.message });
    }
  } else if (provider.toLowerCase() === 'twilio') {
    // Implement Twilio integration here (stub)
    return res.json({ status: 'callback queued (twilio demo)', provider, phone });
  }
  
  res.json({ status: 'callback queued (demo)', provider, phone });
});

// Virtual tour endpoint
app.get('/api/property/:id/tour', (req, res) => {
  const { id } = req.params;
  const property = listings.find(l => l.id == id);
  
  if (!property) {
    return res.status(404).json({ error: 'Property not found' });
  }
  
  // In a real implementation, this would return virtual tour data
  // For demo, we'll just return the property images
  res.json({
    property,
    tourAvailable: property.images && property.images.length > 0,
    tourImages: property.images || [],
    tour360Url: `/virtual-tours/${id}/index.html` // This would be a real URL in production
  });
});

// Agent directory endpoint
app.get('/api/agents', (req, res) => {
  // Demo agents
  const agents = [
    { id: 1, name: 'Sarah Johnson', specialization: 'Luxury Properties', areas: ['Clifton', 'DHA'], available: true, rating: 4.9 },
    { id: 2, name: 'Ahmed Khan', specialization: 'Apartments', areas: ['PECHS', 'Gulshan'], available: true, rating: 4.7 },
    { id: 3, name: 'Fatima Ali', specialization: 'Commercial', areas: ['Saddar', 'I.I. Chundrigar'], available: false, rating: 4.8 }
  ];
  
  res.json({ agents });
});

// Analytics endpoint
app.post('/api/analytics/conversation', (req, res) => {
  const { sessionId, messages, leadConverted, duration } = req.body;
  
  // In a real implementation, this would store conversation analytics
  console.log('Conversation analytics:', { sessionId, messageCount: messages?.length, leadConverted, duration });
  
  res.json({ status: 'analytics recorded' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Enhanced backend server running on port ${PORT}`));
