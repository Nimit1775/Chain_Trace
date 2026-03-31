# ChainTrace AI 🔍
> Crypto Crime Intelligence Platform — TigerGraph Hackathon Track

## Stack
- **Frontend**: React + Vite + Tailwind + Cytoscape.js
- **Backend**: Python + FastAPI
- **Database**: TigerGraph Savanna (free cloud)
- **AI**: OpenAI GPT-4o or Google Gemini

---

## Quick Start (do this in order)

### Step 1 — TigerGraph Savanna Setup
1. Go to https://savanna.tigergraph.com
2. Sign up free → Create Workspace → pick any region
3. Once running, go to "Connect" tab → copy your **hostname**
4. Set password, note your **username** (default: `tigergraph`)
5. Paste into `backend/.env`

### Step 2 — Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # fill in your keys
python scripts/setup_schema.py    # creates schema in TigerGraph
python scripts/seed_data.py       # loads demo wallet data
uvicorn main:app --reload --port 8000
```

### Step 3 — Frontend
```bash
cd frontend
npm install
cp .env.example .env              # set VITE_API_URL=http://localhost:8000
npm run dev
```

Open http://localhost:5173 — you're live.

---

## Project Structure
```
chaintrace/
├── backend/
│   ├── main.py                  # FastAPI app entry
│   ├── requirements.txt
│   ├── .env.example
│   ├── routes/
│   │   ├── graph.py             # wallet graph endpoints
│   │   ├── analysis.py          # risk score, algorithms
│   │   └── ai.py                # AI agent endpoint
│   ├── services/
│   │   ├── tigergraph.py        # TigerGraph connection + queries
│   │   └── ai_agent.py          # LLM investigation report
│   ├── algorithms/
│   │   └── risk.py              # risk score calculation
│   └── scripts/
│       ├── setup_schema.py      # creates TigerGraph schema
│       └── seed_data.py         # loads demo data
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── pages/
│   │   │   └── Investigate.jsx  # main investigation page
│   │   ├── components/
│   │   │   ├── GraphCanvas.jsx  # Cytoscape.js graph
│   │   │   ├── Sidebar.jsx      # wallet details + AI report
│   │   │   ├── SearchBar.jsx    # wallet input
│   │   │   └── RiskBadge.jsx    # risk score display
│   │   ├── hooks/
│   │   │   └── useGraph.js      # graph data fetching
│   │   └── services/
│   │       └── api.js           # backend API calls
│   └── .env.example
└── data/
    └── sample_wallets.json      # demo transaction dataset
```
