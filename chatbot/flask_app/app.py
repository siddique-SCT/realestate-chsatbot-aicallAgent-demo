import os
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

import requests
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS


def create_app() -> Flask:
    # Load env from .env if present
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv()
    except Exception:
        pass

    app = Flask(__name__, template_folder="templates", static_folder="static")
    CORS(app)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    app.logger.setLevel(logging.INFO)

    # Load listings from JSON file
    data_path = os.path.join(os.path.dirname(__file__), "data", "listings.json")
    with open(data_path, "r", encoding="utf-8") as f:
        listings: List[Dict[str, Any]] = json.load(f)

    # In-memory Agent Directory (demo)
    # agent = {id, name, channels: {voice, whatsapp, jitsi}, contacts: {phone, whatsapp, jitsi_room},
    #          status: available|busy|offline, current_load: int, skills: [str]}
    agents: Dict[str, Dict[str, Any]] = {}
    active_connections: Dict[str, Dict[str, Any]] = {}
    inbox: List[Dict[str, Any]] = []

    def seed_demo_agents() -> None:
        if agents:
            return
        # Human agent with phone/whatsapp
        a1 = {
            "id": str(uuid4()),
            "name": "Ayesha (Human)",
            "channels": ["voice", "whatsapp"],
            "contacts": {
                "phone": os.getenv("AGENT1_PHONE", "+923229948042"),
                "whatsapp": os.getenv("AGENT1_WHATSAPP", "+923229948042"),
            },
            "status": "available",
            "available_since": datetime.utcnow().isoformat(),
            "current_load": 0,
            "skills": ["english", "urdu", "karachi"],
        }
        # Human agent on Jitsi only
        a2 = {
            "id": str(uuid4()),
            "name": "Bilal (Human)",
            "channels": ["jitsi"],
            "contacts": {
                "jitsi_room": f"realestate-{uuid4().hex[:8]}",
            },
            "status": "available",
            "available_since": datetime.utcnow().isoformat(),
            "current_load": 0,
            "skills": ["lahore"],
        }
        # AI agent (simulated)
        a3 = {
            "id": str(uuid4()),
            "name": "AI Agent",
            "channels": ["jitsi", "whatsapp"],
            "contacts": {
                "jitsi_room": f"realestate-ai-{uuid4().hex[:8]}",
                "whatsapp": os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886"),
            },
            "status": "available",
            "available_since": datetime.utcnow().isoformat(),
            "current_load": 0,
            "skills": ["general"],
        }
        for a in (a1, a2, a3):
            agents[a["id"]] = a
    seed_demo_agents()

    def choose_agent(preferred_channels: List[str]) -> Optional[Dict[str, Any]]:
        # Filter available agents supporting any preferred channel
        pool = [
            a for a in agents.values()
            if a.get("status") == "available" and any(c in a.get("channels", []) for c in preferred_channels)
        ]
        if not pool:
            return None
        # FIFO: earliest available_since first, then current_load, then name
        def avail_key(a: Dict[str, Any]):
            ts = a.get("available_since")
            return (
                ts or "",
                a.get("current_load", 0),
                a.get("name", ""),
            )
        pool.sort(key=avail_key)
        # Prefer agents that match top preferred channel
        for ch in preferred_channels:
            ch_pool = [a for a in pool if ch in a.get("channels", [])]
            if ch_pool:
                return ch_pool[0]
        return pool[0]

    def keyword_retrieve(query: str) -> List[Dict[str, Any]]:
        q = (query or "").lower()
        if not q:
            return []
        matches = [
            l
            for l in listings
            if (l["location"].lower() in q)
            or (str(l["bedrooms"]) in q)
            or (str(l["price"]) in q)
        ]
        return matches

    # Simple TF-IDF based retrieval over listing text fields
    tfidf_ready = False
    tfidf_index: Optional[Tuple[Any, List[Dict[str, Any]]]] = None
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        corpus_texts = [
            f"{l.get('title','')} {l.get('description','')} {l.get('location','')} {l.get('bedrooms','')} {l.get('price','')}"
            for l in listings
        ]
        vectorizer = TfidfVectorizer(stop_words="english")
        matrix = vectorizer.fit_transform(corpus_texts)
        tfidf_index = (vectorizer, matrix, listings)
        tfidf_ready = True

        def tfidf_retrieve(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
            if not query:
                return []
            q_vec = vectorizer.transform([query])
            sims = cosine_similarity(q_vec, matrix).ravel()
            top_indices = sims.argsort()[::-1][:top_k]
            return [listings[i] for i in top_indices if sims[i] > 0]
    except Exception:
        def tfidf_retrieve(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
            return []

    def openai_chat_completion(user_message: str, matches: List[Dict[str, Any]]) -> Optional[str]:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None

        system_prompt = (
            "You are a friendly real-estate assistant. Be concise and helpful."
        )
        context = "\n".join(
            [
                f"- {m['title']}: {m['description']} (Price: {m['price']}, Bedrooms: {m['bedrooms']}, Location: {m['location']})"
                for m in matches[:3]
            ]
        )
        if context:
            user_augmented = (
                f"User query: {user_message}\n\nRelevant listings:\n{context}\n\n"
                "Answer the user's question and mention one example that fits."
            )
        else:
            user_augmented = user_message

        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            # Choose a broadly available, economical model name; adjust if needed.
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_augmented},
                ],
                "temperature": 0.3,
            }
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=20,
            )
            if resp.status_code != 200:
                app.logger.warning("OpenAI API non-200: %s %s", resp.status_code, resp.text[:200])
                return None
            data = resp.json()
            content = (
                data.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
            return content or None
        except Exception as e:  # noqa: BLE001 - log and fallback gracefully
            app.logger.exception("OpenAI call failed: %s", e)
            return None

    def try_twilio_call(phone: str, say_text: str = "You requested a callback. We will contact you shortly.") -> Dict[str, Any]:
        sid = os.getenv("TWILIO_ACCOUNT_SID")
        token = os.getenv("TWILIO_AUTH_TOKEN")
        from_number = os.getenv("TWILIO_FROM_NUMBER")
        if not (sid and token and from_number):
            return {"queued": False, "reason": "twilio_env_missing"}

        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Calls.json"
            auth = (sid, token)
            # Twilio allows inline TwiML via 'Twiml' param
            twiml = f"""
                <Response>
                    <Say voice=\"alice\">{say_text}</Say>
                </Response>
            """.strip()
            data = {"To": phone, "From": from_number, "Twiml": twiml}
            resp = requests.post(url, auth=auth, data=data, timeout=20)
            if resp.status_code in (200, 201):
                return {"queued": True, "sid": resp.json().get("sid")}
            return {"queued": False, "status": resp.status_code, "body": resp.text[:200]}
        except Exception as e:  # noqa: BLE001
            app.logger.exception("Twilio call failed: %s", e)
            return {"queued": False, "error": str(e)}

    def try_twilio_whatsapp(phone: str, text: str = "Thanks for your request. We will contact you shortly.") -> Dict[str, Any]:
        sid = os.getenv("TWILIO_ACCOUNT_SID")
        token = os.getenv("TWILIO_AUTH_TOKEN")
        whatsapp_from = os.getenv("TWILIO_WHATSAPP_FROM")  # e.g., whatsapp:+14155238886 (sandbox) or your sender
        if not (sid and token and whatsapp_from):
            return {"queued": False, "reason": "twilio_whatsapp_env_missing"}

        try:
            url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
            auth = (sid, token)
            data = {
                "From": whatsapp_from,
                "To": f"whatsapp:{phone}" if not phone.startswith("whatsapp:") else phone,
                "Body": text,
            }
            resp = requests.post(url, auth=auth, data=data, timeout=20)
            if resp.status_code in (200, 201):
                return {"queued": True, "sid": resp.json().get("sid")}
            return {"queued": False, "status": resp.status_code, "body": resp.text[:200]}
        except Exception as e:  # noqa: BLE001
            app.logger.exception("Twilio WhatsApp failed: %s", e)
            return {"queued": False, "error": str(e)}

    @app.route("/")
    def home():
        whatsapp_agent_phone = os.getenv("WHATSAPP_AGENT_NUMBER", "+923229948042")
        jitsi_room = os.getenv("JITSI_ROOM", "realestate-demo-room")
        return render_template("index.html", whatsapp_agent_phone=whatsapp_agent_phone, jitsi_room=jitsi_room)

    @app.route("/agents")
    def agents_page():
        return render_template("agents.html", agents=list(agents.values()))

    @app.route("/listings")
    def list_page():
        q = (request.args.get("q") or "").strip().lower()
        if q:
            results = [
                l for l in listings
                if q in l["location"].lower()
                or q in l["title"].lower()
                or q in l["description"].lower()
                or q in str(l.get("bedrooms", ""))
                or q in str(l.get("price", ""))
            ]
        else:
            results = listings
        return render_template("listings.html", listings=results)

    @app.post("/api/chat")
    def chat():
        data = request.get_json(silent=True) or {}
        message: str = (data.get("message") or "").strip()
        if not message:
            return jsonify({"reply": "Please send a message."})

        # Retrieval: combine TF-IDF and keyword; de-duplicate
        tfidf_matches = tfidf_retrieve(message, top_k=5)
        kw_matches = keyword_retrieve(message)
        seen = set()
        matches: List[Dict[str, Any]] = []
        for m in tfidf_matches + kw_matches:
            mid = m.get("id")
            if mid in seen:
                continue
            seen.add(mid)
            matches.append(m)
        # Try LLM first if available, otherwise fallback
        llm_reply = openai_chat_completion(message, matches)
        if llm_reply:
            inbox.append({
                "id": str(uuid4()),
                "type": "chat",
                "message": message,
                "reply": llm_reply,
                "time": datetime.utcnow().isoformat(),
            })
            return jsonify({"reply": llm_reply})

        # Ollama local fallback
        try:
            ollama_base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            ollama_model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
            context = "\n".join(
                [
                    f"- {m['title']}: {m['description']} (Price: {m['price']}, Bedrooms: {m['bedrooms']}, Location: {m['location']})"
                    for m in matches[:3]
                ]
            )
            prompt = (
                f"You are a helpful real-estate assistant.\n\nUser: {message}\n\nRelevant listings:\n{context}\n\nAnswer concisely and suggest one example."
            )
            resp = requests.post(
                f"{ollama_base}/api/generate",
                json={"model": ollama_model, "prompt": prompt, "stream": False},
                timeout=8,
            )
            if resp.status_code == 200:
                data = resp.json()
                out = (data.get("response") or "").strip()
                if out:
                    return jsonify({"reply": out})
        except Exception:
            pass

        if matches:
            m = matches[0]
            reply = (
                f"I found {len(matches)} listing(s). Example: {m['title']} — "
                f"{m['description']} (Price: {m['price']})"
            )
        else:
            reply = (
                "Sorry, I couldn't find matching listings. Try: '3 bed Clifton' or mention an area."
            )
        inbox.append({
            "id": str(uuid4()),
            "type": "chat",
            "message": message,
            "reply": reply,
            "time": datetime.utcnow().isoformat(),
        })
        return jsonify({"reply": reply})

    @app.post("/api/lead")
    def save_lead():
        data = request.get_json(silent=True) or {}
        name = data.get("name", "")
        phone = data.get("phone", "")
        email = data.get("email", "")
        consent = bool(data.get("consent", False))

        app.logger.info(
            "New lead: %s",
            {
                "name": name,
                "phone": phone,
                "email": email,
                "consent": consent,
                "time": datetime.utcnow().isoformat(),
            },
        )

        # Optional: auto-dial when consent is given and env permits
        auto_call = os.getenv("CALL_AUTODIAL", "false").lower() in {"1", "true", "yes"}
        autodial_channel = os.getenv("CALL_AUTODIAL_CHANNEL", "voice").lower()  # voice|whatsapp|ai_agent
        call_result: Optional[Dict[str, Any]] = None
        
        if consent and auto_call and phone:
            # Use AI Call Agent if configured
            if autodial_channel == "ai_agent":
                try:
                    # Call the AI agent API to schedule an immediate call
                    ai_call_data = {
                        "phone_number": phone,
                        "script_type": "lead_qualification",  # Use lead qualification script
                        "context": {
                            "customer_name": name,
                            "customer_email": email,
                            "source": "website_chat"
                        }
                    }
                    
                    # Make internal request to our own API
                    response = requests.post(
                        f"http://localhost:{port}/api/call-agents/calls",
                        json=ai_call_data,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        call_result = response.json()
                    else:
                        app.logger.error(f"Failed to schedule AI call: {response.text}")
                        call_result = {"status": "error", "message": "Failed to schedule AI call"}
                except Exception as e:
                    app.logger.error(f"Error scheduling AI call: {str(e)}")
                    call_result = {"status": "error", "message": str(e)}
            elif autodial_channel == "whatsapp":
                call_result = try_twilio_whatsapp(phone)
            else:
                call_result = try_twilio_call(phone)

        inbox.append({
            "id": str(uuid4()),
            "type": "lead",
            "name": name,
            "phone": phone,
            "email": email,
            "consent": consent,
            "auto_call": call_result,
            "time": datetime.utcnow().isoformat(),
        })
        return jsonify({"status": "lead saved", "auto_call": call_result})

    @app.post("/api/callback")
    def callback():
        data = request.get_json(silent=True) or {}
        provider = (data.get("provider") or "twilio").lower()
        phone = (data.get("phone") or "").strip()
        channel = (data.get("channel") or data.get("mode") or "voice").lower()  # voice|whatsapp
        if not phone:
            return jsonify({"status": "error", "error": "missing phone"}), 400
        if provider == "twilio":
            if channel == "whatsapp":
                result = try_twilio_whatsapp(phone)
            else:
                result = try_twilio_call(phone)
            return jsonify({"status": "callback_queued", "channel": channel, "result": result})
        return jsonify({"status": "unsupported_provider", "provider": provider}), 400

    # Agent Directory API (demo)
    @app.get("/api/agents")
    def api_agents():
        return jsonify({"agents": list(agents.values())})

    @app.post("/api/agents/register")
    def api_agents_register():
        data = request.get_json(silent=True) or {}
        agent_id = str(uuid4())
        agent = {
            "id": agent_id,
            "name": data.get("name", f"Agent-{agent_id[:6]}"),
            "channels": data.get("channels", ["voice", "whatsapp", "jitsi"]),
            "contacts": data.get("contacts", {}),
            "status": data.get("status", "available"),
            "current_load": int(data.get("current_load", 0)),
            "skills": data.get("skills", []),
        }
        agents[agent_id] = agent
        return jsonify(agent)

    @app.post("/api/agents/status")
    def api_agents_status():
        data = request.get_json(silent=True) or {}
        agent_id = data.get("id")
        if not agent_id or agent_id not in agents:
            return jsonify({"status": "error", "error": "unknown agent"}), 400
        for key in ("status", "current_load", "contacts"):
            if key in data:
                agents[agent_id][key] = data[key]
        return jsonify({"status": "ok", "agent": agents[agent_id]})

    def route_customer(customer: Dict[str, Any], preferred: List[str]) -> Dict[str, Any]:
        agent = choose_agent(preferred)
        if not agent:
            return {"status": "queued", "reason": "no_agent_available"}

        # Reserve agent
        agents[agent["id"]]["status"] = "busy"
        agents[agent["id"]]["current_load"] = agents[agent["id"]].get("current_load", 0) + 1
        conn_id = str(uuid4())
        action: Dict[str, Any] = {"kind": None}

        for ch in preferred:
            if ch in agent.get("channels", []):
                if ch == "voice":
                    result = try_twilio_call(customer.get("phone", ""))
                    action = {"kind": "voice", "twilio": result, "agent_phone": agent["contacts"].get("phone")}
                elif ch == "whatsapp":
                    wa_to = agent["contacts"].get("whatsapp") or os.getenv("WHATSAPP_AGENT_NUMBER", "+923229948042")
                    deeplink = f"https://wa.me/{wa_to.replace('+','')}?text=Hi%20I%20want%20to%20talk%20about%20properties"
                    twilio = try_twilio_whatsapp(customer.get("phone", "")) if customer.get("phone") else {"queued": False, "reason": "no_customer_phone"}
                    action = {"kind": "whatsapp", "deeplink": deeplink, "twilio": twilio}
                else:
                    room = agent["contacts"].get("jitsi_room") or f"realestate-{uuid4().hex[:8]}"
                    action = {"kind": "jitsi", "room": room, "url": f"https://meet.jit.si/{room}"}
                break

        conn = {
            "id": conn_id,
            "agent_id": agent["id"],
            "customer": customer,
            "action": action,
            "created_at": datetime.utcnow().isoformat(),
        }
        active_connections[conn_id] = conn
        inbox.append({
            "id": conn_id,
            "type": "connect",
            "customer": customer,
            "agent": {"id": agent["id"], "name": agent["name"]},
            "action": action,
            "time": datetime.utcnow().isoformat(),
        })
        return {"status": "routed", "connection": conn, "agent": agent}

    @app.post("/api/connect")
    def api_connect():
        data = request.get_json(silent=True) or {}
        customer = data.get("customer", {})
        preferred = data.get("preferred_channels", ["voice", "whatsapp", "jitsi"])  # order matters
        result = route_customer(customer, preferred)
        return jsonify(result)

    @app.post("/api/complete")
    def api_complete():
        data = request.get_json(silent=True) or {}
        conn_id = data.get("id")
        conn = active_connections.pop(conn_id, None)
        if not conn:
            return jsonify({"status": "error", "error": "unknown_connection"}), 400
        agent_id = conn.get("agent_id")
        if agent_id in agents:
            agents[agent_id]["current_load"] = max(0, agents[agent_id].get("current_load", 0) - 1)
            agents[agent_id]["status"] = "available"
            agents[agent_id]["available_since"] = datetime.utcnow().isoformat()
        return jsonify({"status": "completed"})

    @app.post("/api/telegram")
    def telegram_send():
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        chat_id = os.getenv("TELEGRAM_CHAT_ID")
        if not (token and chat_id):
            return jsonify({"status": "skipped", "reason": "telegram_env_missing"}), 200

        data = request.get_json(silent=True) or {}
        text = (data.get("text") or data.get("message") or "New callback request").strip()
        try:
            resp = requests.post(
                f"https://api.telegram.org/bot{token}/sendMessage",
                json={"chat_id": chat_id, "text": text},
                timeout=15,
            )
            if resp.status_code == 200:
                return jsonify({"status": "sent"})
            return jsonify({"status": "error", "code": resp.status_code, "body": resp.text[:200]}), 200
        except Exception as e:  # noqa: BLE001
            app.logger.exception("Telegram send failed: %s", e)
            return jsonify({"status": "error", "error": str(e)}), 200

    @app.get("/dashboard")
    def dashboard_page():
        items = sorted(inbox, key=lambda x: x.get("time", ""), reverse=True)
        return render_template("dashboard.html", items=items, agents=list(agents.values()), active=active_connections)
        
    @app.get("/call-agents")
    def call_agents_page():
        return render_template("call_agents.html")

    @app.post("/api/dashboard/action")
    def dashboard_action():
        data = request.get_json(silent=True) or {}
        action = data.get("action")
        item_id = data.get("id")
        if action == "archive":
            for i in range(len(inbox)):
                if inbox[i].get("id") == item_id:
                    inbox.pop(i)
                    return jsonify({"status": "archived"})
            return jsonify({"status": "not_found"}), 404
        if action == "connect":
            customer = data.get("customer", {})
            preferred = data.get("preferred_channels", ["voice", "whatsapp", "jitsi"])  # order matters
            result = route_customer(customer, preferred)
            return jsonify(result)
        return jsonify({"status": "noop"})

    # Import and register blueprints
    from routes.property import property_bp
    from routes.agents import agents_bp
    from routes.analytics import analytics_bp
    from routes.call_agents import call_agents_bp
    
    app.register_blueprint(property_bp, url_prefix='/api/property')
    app.register_blueprint(agents_bp, url_prefix='/api/agents')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(call_agents_bp, url_prefix='/api/call-agents')
    
    return app


# Run the app
if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    app = create_app()
    app.logger.info("Starting Flask app on port %s", port)
    app.run(host="0.0.0.0", port=port, debug=True)


