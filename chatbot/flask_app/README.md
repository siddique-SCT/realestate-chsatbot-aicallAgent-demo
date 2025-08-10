Flask Real-Estate AI Chat

Run locally (Windows):

1) Create venv and install deps
```
cd flask_app
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2) Optional: set env for OpenAI and Twilio (voice/WhatsApp)
```
set OPENAI_API_KEY=sk-...
set OPENAI_MODEL=gpt-4o-mini
set CALL_AUTODIAL=true
set CALL_AUTODIAL_CHANNEL=voice  # voice | whatsapp
set TWILIO_ACCOUNT_SID=AC...
set TWILIO_AUTH_TOKEN=...
set TWILIO_FROM_NUMBER=+15551234567
set TWILIO_WHATSAPP_FROM=whatsapp:+923229948042  
# TIP: this must be a Twilio WhatsApp-enabled sender. Configure your Twilio sandbox/sender first.
```

3) Start server
```
python app.py
# open http://localhost:5000
```

API
- POST /api/chat { message }
- POST /api/lead { name, phone, email, consent }
- POST /api/callback { provider="twilio", phone, channel="voice"|"whatsapp" }

Notes
- If OPENAI_API_KEY is unset, the app falls back to a simple keyword-based reply.
- Twilio integration uses REST; you can swap to the official SDK if preferred.
- You can also create a `.env` file in `flask_app/` with the same variables (the app auto-loads it).

