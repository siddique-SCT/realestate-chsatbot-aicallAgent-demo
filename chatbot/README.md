# Real-Estate AI Chat Demo

This repo contains a runnable proof-of-concept demo for an AI-powered chat widget for real-estate sites.
It includes:
- Frontend: minimal Next.js app with a floating ChatWidget component.
- Backend: Node/Express server with `/api/chat`, `/api/lead`, `/api/callback`.
- Embeddings: Python script to index listing descriptions with Sentence-Transformers + FAISS (demo).
- Botpress flow skeleton (JSON).
- BrightCall.ai integration for real-time agent connection.
- Azure AI services integration for enhanced NLP capabilities.

**How to run (local demo)**

1. Backend
```bash
# from repo root
cd backend
npm install
node server.js
# server will run on http://localhost:3000
```

2. Frontend
```bash
cd frontend
npm install
npm run dev
# open http://localhost:3001 (or default Next.js port 3000 conflict - adjust env)
```

3. Embeddings (optional)
```bash
cd embeddings
pip install -r requirements.txt  # sentence-transformers, faiss-cpu
python embed_index.py
```

Notes:
- This is a demo scaffold. Replace placeholder API calls with real vector search / LLM calls for production.
- For callbacks, integrate Brightcall or Twilio in `/api/callback`.
- You'll find the Botpress flow JSON in `botpress/botpress_flow.json` — import into Botpress to get a starting flow.

### Windows quickstart tips
- If PowerShell blocks `npm.ps1`, use `npm.cmd` (e.g., `npm.cmd install`, `npm.cmd run dev`) or run commands in `cmd.exe`.
- Frontend dev server runs on port 3001 and proxies `/api/*` to the backend at `http://localhost:3000` via `frontend/next.config.js`.

### One-click scripts (Windows)
- Node demo (backend + Next frontend):
  - Double-click `scripts/run_node_demo.cmd`
- Flask demo (Python):
  - Double-click `scripts/run_flask_demo.cmd`

