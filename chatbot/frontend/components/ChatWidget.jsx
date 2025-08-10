import { useState, useEffect, useRef } from 'react';
import Image from 'next/image';

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([{from:'bot', text:'Hi! I can help you find properties. Try saying: "3 bed in Clifton"'}]);
  const [text, setText] = useState('');
  const [lead, setLead] = useState({
    name: '',
    phone: '',
    email: '',
    consent: false,
    preferredTime: 'immediate',
    propertyInterest: ''
  });
  const [currentMatches, setCurrentMatches] = useState([]);
  const [showVirtualTour, setShowVirtualTour] = useState(false);
  const [tourData, setTourData] = useState(null);
  const [currentTourImage, setCurrentTourImage] = useState(0);
  const [agents, setAgents] = useState([]);
  const [showAgents, setShowAgents] = useState(false);
  const [sessionId] = useState(`session_${Math.random().toString(36).substring(2, 15)}`);
  const [conversationStartTime] = useState(new Date());
  const messagesEndRef = useRef(null);
  
  // Fetch agents on component mount
  useEffect(() => {
    fetchAgents();
    
    // Cleanup function to send analytics when component unmounts
    return () => {
      sendAnalytics();
    };
  }, []);
  
  // Auto-scroll to bottom of messages
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };
  
  const fetchAgents = async () => {
    try {
      const res = await fetch('/api/agents');
      const data = await res.json();
      if (data.agents) {
        setAgents(data.agents);
      }
    } catch (error) {
      console.error('Error fetching agents:', error);
    }
  };
  
  const sendAnalytics = async () => {
    try {
      await fetch('/api/analytics/conversation', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          sessionId,
          messages,
          leadConverted: lead.name && lead.phone ? true : false,
          duration: Math.round((new Date() - conversationStartTime) / 1000)
        })
      });
    } catch (error) {
      console.error('Error sending analytics:', error);
    }
  };

  async function sendMessage() {
    if(!text) return;
    const userMsg = {from:'user', text};
    setMessages(m=>[...m,userMsg]);
    setText('');
    
    // Check for special commands
    const lowerText = text.toLowerCase();
    if (lowerText === 'show agents' || lowerText.includes('speak with agent') || lowerText.includes('talk to agent')) {
      setShowAgents(true);
      setMessages(m=>[...m,{from:'bot', text: 'Here are our available agents:'}]);
      return;
    }
    
    if (lowerText.includes('virtual tour') || lowerText.includes('see property')) {
      if (currentMatches.length > 0) {
        await fetchPropertyTour(currentMatches[0].id);
        return;
      }
    }
    
    const res = await fetch('/api/chat', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({message: text, sessionId})
    });
    
    const data = await res.json();
    setMessages(m=>[...m,{from:'bot', text: data.reply}]);
    
    // Store matches if available
    if (data.matches && data.matches.length > 0) {
      setCurrentMatches(data.matches);
      setLead(prev => ({
        ...prev,
        propertyInterest: data.matches[0].title
      }));
    }
  }

  async function submitLead() {
    if (!lead.name || !lead.phone) {
      alert('Please provide your name and phone number');
      return;
    }
    
    if (!lead.consent) {
      alert('Please consent to be contacted');
      return;
    }
    
    const res = await fetch('/api/lead', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify(lead)
    });
    
    const result = await res.json();
    
    if (result.callback === 'initiated') {
      setMessages(m => [...m, {from: 'bot', text: `Thanks ${lead.name}! Our agent will call you ${lead.preferredTime === 'immediate' ? 'right away' : 'at your preferred time'}.`}]);
    } else {
      setMessages(m => [...m, {from: 'bot', text: `Thanks ${lead.name}! Your contact information has been saved, and an agent will reach out to you soon.`}]);
    }
  }
  
  async function requestCallback(agent = null) {
    if (!lead.phone) {
      alert('Please provide your phone number first');
      return;
    }
    
    const payload = {
      provider: 'brightcall',
      phone: lead.phone,
      name: lead.name,
      email: lead.email,
      propertyId: currentMatches.length > 0 ? currentMatches[0].id : null,
      scheduleTime: lead.preferredTime !== 'immediate' ? lead.preferredTime : null
    };
    
    if (agent) {
      payload.agentId = agent.id;
    }
    
    const res = await fetch('/api/callback', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    
    const result = await res.json();
    
    if (result.status.includes('queued')) {
      setMessages(m => [...m, {from: 'bot', text: `Your callback has been ${lead.preferredTime === 'immediate' ? 'initiated! You should receive a call shortly.' : 'scheduled for your preferred time.'}`}]);
    } else {
      alert(result.status || 'Callback requested');
    }
  }
  
  async function fetchPropertyTour(propertyId) {
    try {
      const res = await fetch(`/api/property/${propertyId}/tour`);
      const data = await res.json();
      
      if (data.tourAvailable) {
        setTourData(data);
        setShowVirtualTour(true);
        setMessages(m => [...m, {from: 'bot', text: `Here's a virtual tour of the property. Use the navigation buttons to view different images.`}]);
      } else {
        setMessages(m => [...m, {from: 'bot', text: `I'm sorry, a virtual tour isn't available for this property. Would you like to speak with an agent instead?`}]);
      }
    } catch (error) {
      console.error('Error fetching property tour:', error);
      setMessages(m => [...m, {from: 'bot', text: `I'm sorry, I couldn't load the virtual tour. Would you like to speak with an agent instead?`}]);
    }
  }

  return (
    <div style={{position:'fixed', right:20, bottom:20, width:380, zIndex:9999}}>
      <button 
        onClick={()=>setOpen(!open)} 
        style={{
          padding:'10px 16px', 
          backgroundColor:'#2563eb', 
          color:'white', 
          border:'none', 
          borderRadius:'8px',
          boxShadow:'0 2px 5px rgba(0,0,0,0.1)',
          fontWeight:'bold'
        }}
      >
        {open ? 'Close Chat' : 'Chat with Us'}
      </button>
      
      {open && (
        <div style={{
          border:'1px solid #e5e7eb', 
          background:'#fff', 
          padding:16, 
          borderRadius:12, 
          boxShadow:'0 4px 12px rgba(0,0,0,0.1)',
          marginTop:12,
          maxHeight:'80vh',
          display:'flex',
          flexDirection:'column'
        }}>
          <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:12}}>
            <h3 style={{margin:0, color:'#1e40af'}}>Real Estate Assistant</h3>
            <span style={{fontSize:12, color:'#6b7280'}}>Session: {sessionId.substring(0,8)}</span>
          </div>
          
          <div style={{height:320, overflow:'auto', marginBottom:12, flex:1}}>
            {messages.map((m,i)=> (
              <div key={i} style={{
                margin:'8px 0', 
                padding:10, 
                borderRadius:8, 
                backgroundColor: m.from === 'bot' ? '#f3f4f6' : '#e0f2fe',
                alignSelf: m.from === 'bot' ? 'flex-start' : 'flex-end',
                maxWidth:'85%',
                wordBreak:'break-word'
              }}>
                <div style={{fontWeight:'bold', marginBottom:4, fontSize:14, color: m.from === 'bot' ? '#4b5563' : '#0369a1'}}>
                  {m.from === 'bot' ? 'Assistant' : 'You'}
                </div>
                <div>{m.text}</div>
              </div>
            ))}
            {showVirtualTour && tourData && (
              <div style={{margin:'12px 0', padding:10, borderRadius:8, backgroundColor:'#f3f4f6', width:'100%'}}>
                <div style={{fontWeight:'bold', marginBottom:8}}>Virtual Tour</div>
                <div style={{position:'relative', width:'100%', height:200, backgroundColor:'#e5e7eb', borderRadius:4, overflow:'hidden'}}>
                  {tourData.tourImages && tourData.tourImages.length > 0 ? (
                    <img 
                      src={`/images/${tourData.tourImages[currentTourImage]}`} 
                      alt="Property tour" 
                      style={{width:'100%', height:'100%', objectFit:'cover'}}
                    />
                  ) : (
                    <div style={{display:'flex', alignItems:'center', justifyContent:'center', height:'100%'}}>
                      No images available
                    </div>
                  )}
                </div>
                {tourData.tourImages && tourData.tourImages.length > 1 && (
                  <div style={{display:'flex', justifyContent:'center', gap:8, marginTop:8}}>
                    <button 
                      onClick={() => setCurrentTourImage(prev => (prev > 0 ? prev - 1 : tourData.tourImages.length - 1))}
                      style={{padding:'4px 8px', backgroundColor:'#e5e7eb', border:'none', borderRadius:4}}
                    >
                      Previous
                    </button>
                    <span>{currentTourImage + 1} / {tourData.tourImages.length}</span>
                    <button 
                      onClick={() => setCurrentTourImage(prev => (prev < tourData.tourImages.length - 1 ? prev + 1 : 0))}
                      style={{padding:'4px 8px', backgroundColor:'#e5e7eb', border:'none', borderRadius:4}}
                    >
                      Next
                    </button>
                  </div>
                )}
                <button 
                  onClick={() => setShowVirtualTour(false)}
                  style={{marginTop:8, padding:'4px 8px', backgroundColor:'#ef4444', color:'white', border:'none', borderRadius:4, width:'100%'}}
                >
                  Close Tour
                </button>
              </div>
            )}
            {showAgents && agents.length > 0 && (
              <div style={{margin:'12px 0', padding:10, borderRadius:8, backgroundColor:'#f3f4f6', width:'100%'}}>
                <div style={{fontWeight:'bold', marginBottom:8}}>Available Agents</div>
                {agents.filter(a => a.available).map(agent => (
                  <div key={agent.id} style={{padding:8, borderRadius:4, backgroundColor:'white', marginBottom:6}}>
                    <div style={{fontWeight:'bold'}}>{agent.name}</div>
                    <div style={{fontSize:12, color:'#6b7280'}}>{agent.specialization} • Rating: {agent.rating}/5</div>
                    <div style={{fontSize:12, color:'#6b7280'}}>Areas: {agent.areas.join(', ')}</div>
                    <button 
                      onClick={() => {
                        requestCallback(agent);
                        setShowAgents(false);
                      }}
                      style={{marginTop:4, padding:'4px 8px', backgroundColor:'#2563eb', color:'white', border:'none', borderRadius:4, width:'100%'}}
                    >
                      Connect with {agent.name.split(' ')[0]}
                    </button>
                  </div>
                ))}
                <button 
                  onClick={() => setShowAgents(false)}
                  style={{marginTop:8, padding:'4px 8px', backgroundColor:'#6b7280', color:'white', border:'none', borderRadius:4, width:'100%'}}
                >
                  Close
                </button>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          
          <div style={{display:'flex', gap:6, marginBottom:12}}>
            <input 
              value={text} 
              onChange={e=>setText(e.target.value)} 
              onKeyPress={e => e.key === 'Enter' && sendMessage()}
              placeholder="Type message..." 
              style={{flex:1, padding:'8px 12px', borderRadius:6, border:'1px solid #d1d5db'}} 
            />
            <button 
              onClick={sendMessage}
              style={{padding:'8px 16px', backgroundColor:'#2563eb', color:'white', border:'none', borderRadius:6}}
            >
              Send
            </button>
          </div>
          
          {currentMatches.length > 0 && (
            <div style={{marginBottom:12, padding:10, backgroundColor:'#f3f4f6', borderRadius:8}}>
              <h4 style={{margin:'0 0 8px 0', fontSize:14}}>Property Matched</h4>
              <div style={{fontSize:13}}>
                <div style={{fontWeight:'bold'}}>{currentMatches[0].title}</div>
                <div>{currentMatches[0].description}</div>
                <div style={{display:'flex', justifyContent:'space-between', marginTop:6}}>
                  <button 
                    onClick={() => fetchPropertyTour(currentMatches[0].id)}
                    style={{padding:'4px 8px', backgroundColor:'#2563eb', color:'white', border:'none', borderRadius:4, fontSize:12}}
                  >
                    Virtual Tour
                  </button>
                  <button 
                    onClick={() => setShowAgents(true)}
                    style={{padding:'4px 8px', backgroundColor:'#10b981', color:'white', border:'none', borderRadius:4, fontSize:12}}
                  >
                    Speak with Agent
                  </button>
                </div>
              </div>
            </div>
          )}

          <hr style={{margin:'8px 0', borderColor:'#e5e7eb'}} />
          
          <div>
            <h4 style={{margin:'8px 0', color:'#1e40af'}}>Request Callback</h4>
            <input 
              placeholder="Name" 
              value={lead.name} 
              onChange={e=>setLead({...lead,name:e.target.value})} 
              style={{width:'100%', padding:'8px 12px', borderRadius:6, border:'1px solid #d1d5db', marginBottom:8}}
            />
            <input 
              placeholder="Phone" 
              value={lead.phone} 
              onChange={e=>setLead({...lead,phone:e.target.value})} 
              style={{width:'100%', padding:'8px 12px', borderRadius:6, border:'1px solid #d1d5db', marginBottom:8}}
            />
            <input 
              placeholder="Email" 
              value={lead.email} 
              onChange={e=>setLead({...lead,email:e.target.value})} 
              style={{width:'100%', padding:'8px 12px', borderRadius:6, border:'1px solid #d1d5db', marginBottom:8}}
            />
            
            <div style={{marginBottom:8}}>
              <label style={{display:'block', marginBottom:4, fontSize:14}}>Preferred Time:</label>
              <select 
                value={lead.preferredTime} 
                onChange={e=>setLead({...lead,preferredTime:e.target.value})}
                style={{width:'100%', padding:'8px 12px', borderRadius:6, border:'1px solid #d1d5db'}}
              >
                <option value="immediate">Call me immediately</option>
                <option value="morning">Morning (9AM-12PM)</option>
                <option value="afternoon">Afternoon (12PM-5PM)</option>
                <option value="evening">Evening (5PM-8PM)</option>
              </select>
            </div>
            
            <label style={{display:'block', marginBottom:12}}>
              <input 
                type="checkbox" 
                checked={lead.consent} 
                onChange={e=>setLead({...lead,consent:e.target.checked})}
                style={{marginRight:8}}
              /> 
              I consent to be contacted about real estate opportunities.
            </label>
            
            <div style={{display:'flex', gap:8}}>
              <button 
                onClick={submitLead} 
                style={{flex:1, padding:'8px 0', backgroundColor:'#2563eb', color:'white', border:'none', borderRadius:6, fontWeight:'bold'}}
              >
                Request Callback
              </button>
              <button 
                onClick={() => requestCallback()} 
                style={{flex:1, padding:'8px 0', backgroundColor:'#10b981', color:'white', border:'none', borderRadius:6, fontWeight:'bold'}}
              >
                Call Now
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
