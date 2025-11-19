
# GhostWriter Agent – Multi-Agent Brand Visibility System

This README describes how to run the GhostWriter multi-agent system, where to store your
Google API key, architecture details, instructions, and usage examples.

---

# GhostWriter Agent

GhostWriter is a small multi-agent content engine that demonstrates the following workflow:

- Trend discovery (mocked) for a brand/topic.
- Cross-channel content planning and generation (scripts, captions, hashtags, image prompts).
- A publishing tool that either mocks scheduling for social channels or optionally posts to WordPress when credentials are provided.
- A simple evaluation step that returns mock analytics for generated content.

Quick links
- Code: `ghostwriter_agent/`
- Notebook with prompt examples: `GhostWriter/main.ipynb`

Prerequisites
- Python 3.8+
- Install dependencies:
```powershell
pip install -r requirements.txt
```

Environment & secrets
- Use a `.env` file or system environment variables to store secrets. The project ignores `.env` by default.
- Example `.env`:
```
GROQ_API_KEY=your_groq_or_llm_key
GOOGLE_API_KEY=your_google_key_if_used
WP_SITE=https://yourwpsite.com
WP_USER=your_wp_username_or_app_password
WP_PASSWORD=your_wp_password_or_app_password
NANOBANANA_API_KEY=your_nanobanana_key
NANOBANANA_API_URL=https://api.nanobanana.com/v1/generate
PORT=8000
```
- If `WP_SITE`, `WP_USER`, and `WP_PASSWORD` are set, the publishing tool will attempt to POST to WordPress. Otherwise, mock scheduling is used.

Run the demo (local)
```powershell
python -m ghostwriter_agent.agent
```

Backend API Server
- Install backend dependencies:
```bash
pip install -r requirements.txt
```
- Run the FastAPI backend:
```bash
python run_backend.py
# Or: uvicorn backend.main:app --reload --port 8000
```
- API documentation available at: http://localhost:8000/docs
- The frontend is configured to proxy `/api/*` requests to the backend

Testing
- Run tests with:
```powershell
pytest -q
```

Repository structure
- `ghostwriter_agent/agent.py` — orchestrator and demo runner
- `ghostwriter_agent/config.py` — model configuration and env loading
- `ghostwriter_agent/prompts.py` — prompt templates used by the agents
- `ghostwriter_agent/tools.py` — helper functions (trends, publishing, analytics)
- `ghostwriter_agent/sub_agents/` — agent role implementations
- `GhostWriter/main.ipynb` — notebook with original prompt examples

Security & best practices
- Use WordPress application passwords where possible.
- Do not commit secrets to git; prefer environment variables or a secret manager for production.




