
# GhostWriter Agent – Multi-Agent Brand Visibility System

This README describes how to run the GhostWriter multi-agent system with a **React frontend** and **FastAPI backend**, including installation, configuration, API endpoints, and usage examples.

---

## Overview

GhostWriter is a full-stack AI content generation platform that demonstrates the following workflow:

- **Trend discovery** for brand/topic insights
- **AI-powered content generation** for LinkedIn, WordPress, Instagram, and master drafts
- **Image generation** with customizable styles per platform
- **Scheduled post management** with backend storage
- **WordPress integration** for direct publishing
- **Brand-aware chatbot** for content strategy assistance

## Architecture

- **Frontend:** React + TypeScript + Vite (port 5173)
- **Backend:** FastAPI + Google ADK Agents (port 8000)
- **AI Agents:** Content creator, strategist, publisher, evaluator, trend watcher, image generator
- **Storage:** File-based JSON storage for sessions and scheduled posts

---

## Quick Start

### Prerequisites
- **Python 3.8+**
- **Node.js** (for frontend)
- Git

### Installation

1. **Clone the repository:**
```powershell
git clone https://github.com/rohitchris/ghostwriter-capstone.git
cd ghostwriter-capstone
git checkout feature/azita
```

2. **Install Python dependencies:**
```powershell
pip install -r requirements.txt
```

3. **Install frontend dependencies:**
```powershell
cd frontend
npm install
cd ..
```

4. **Create `.env` file in the project root:**
```env
GOOGLE_API_KEY=your_google_api_key_here
GROQ_API_KEY=your_groq_key_if_used
WP_SITE=https://yourwpsite.com
WP_USER=your_wp_username
WP_PASSWORD=your_wp_app_password
NANOBANANA_API_KEY=your_nanobanana_key
NANOBANANA_API_URL=https://api.nanobanana.com/v1/generate
PORT=8000
```

---

## Running the Application

### Start Backend Server
```powershell
python run_backend.py
# Or: uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
- Backend API: http://127.0.0.1:8000
- API Docs: http://127.0.0.1:8000/docs

### Start Frontend Development Server
```powershell
cd frontend
npm run dev
```
- Frontend: http://localhost:5173

### Access the Application
1. Open http://localhost:5173 in your browser
2. Sign up or log in (accepts any email/password for demo)
3. Navigate to `/generator` to create content
4. View scheduled posts in the Dashboard

---

## API Endpoints

### Content Generation
- **POST** `/api/generate-content` - Generate AI content for all platforms
  - Body: `{ "topic": string, "tone": string }`
  - Returns: Structured content for LinkedIn, WordPress, Instagram, master draft

### Image Generation
- **POST** `/api/generate-image` - Generate images with style options
  - Body: `{ "prompt": string, "style": string }`
  - Returns: `{ "url": string, "image_url": string }`

### Scheduled Posts
- **POST** `/api/scheduled-posts/save` - Save a scheduled post
  - Body: `{ "user_id": string, "platform": string, "content": string, "date_time": string, "image_url": string }`
  
- **POST** `/api/scheduled-posts/list` - Get all scheduled posts for a user
  - Body: `{ "user_id": string }`
  
- **DELETE** `/api/scheduled-posts/{user_id}/{post_id}` - Delete a scheduled post

### WordPress
- **POST** `/api/check-wordpress` - Verify if a URL is a WordPress site
  - Body: `{ "url": string }`

### Chat
- **POST** `/api/chat` - Brand-aware chatbot for content strategy
  - Body: `{ "brand_info": string, "message": string, "session_id": string }`

### Agent Endpoints
- **POST** `/api/agents/run-full-cycle` - Run complete GhostWriter agent workflow
- **POST** `/api/agents/content-creator` - Run content creator agent
- **POST** `/api/agents/trend-watcher` - Run trend analysis
- **POST** `/api/agents/publisher` - Run publisher agent

---

## Features

### ✅ Connected to Backend
- Content generation (AI-powered)
- Image generation (nanobanana)
- Scheduled posts (persistent storage)
- WordPress site verification

### 🔄 Mock/Demo
- User authentication (accepts any credentials)
- Social media auto-posting (coming soon)

---

## Storage

### Backend Storage Directories
- `sessions/` - Chat conversation history (JSON files per session)
- `scheduled_posts/` - User scheduled posts (JSON files per user)

### Data Format
All data stored as JSON for easy debugging and portability.

---

## Testing

### Run Python Tests
```powershell
pytest -q
```

### Test WordPress Credentials
```powershell
python ghostwriter_agent/test_publish.py
```

---

## Project Structure

```
ghostwriter_agent/
├── backend/
│   ├── api/
│   │   └── endpoints.py      # FastAPI routes and logic
│   ├── services/
│   │   └── image_generator.py
│   └── main.py               # FastAPI app initialization
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── hooks/            # Custom hooks (now connected to backend)
│   │   ├── types/            # TypeScript types
│   │   └── utils/            # Utility functions
│   ├── package.json
│   └── vite.config.ts        # Vite config with API proxy
├── ghostwriter_agent/
│   ├── agent.py              # Main orchestrator
│   ├── config.py             # Configuration
│   ├── prompts.py            # Prompt templates
│   ├── tools.py              # Helper functions
│   └── sub_agents/           # Individual agent implementations
├── GhostWriter/
│   └── main.ipynb            # Original prompt examples
├── helpers/
│   └── wordpress_checker.py
├── sessions/                 # Chat session storage (created at runtime)
├── scheduled_posts/          # Scheduled posts storage (created at runtime)
├── .env                      # Environment variables (not committed)
├── requirements.txt
└── README.md
```

---

## Recent Updates (November 2025)

### Backend Integration
- ✅ Connected content generation to backend AI agents
- ✅ Connected image generation to nanobanana API
- ✅ Migrated scheduled posts from localStorage to backend storage
- ✅ Added persistent session management for chat
- ✅ Created RESTful API endpoints for all features

### Frontend Improvements
- ✅ Updated all hooks to use backend APIs instead of mock data
- ✅ Real-time polling for scheduled posts updates
- ✅ Error handling and loading states
- ✅ Maintained mock authentication for demo purposes

---

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `GOOGLE_API_KEY` | Yes | For AI content generation |
| `GROQ_API_KEY` | Optional | Alternative LLM provider |
| `WP_SITE` | Optional | WordPress site URL for publishing |
| `WP_USER` | Optional | WordPress username |
| `WP_PASSWORD` | Optional | WordPress app password |
| `NANOBANANA_API_KEY` | Optional | Image generation service |
| `NANOBANANA_API_URL` | Optional | Image generation endpoint |
| `PORT` | Optional | Backend server port (default: 8000) |

---

## Security & Best Practices

- ✅ `.env` file ignored by git
- ✅ Use WordPress application passwords (not main password)
- ✅ Environment variables for all secrets
- ⚠️ Demo authentication accepts any credentials (replace with real auth for production)
- ⚠️ File-based storage suitable for demo (use database for production)

---

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (need 3.8+)
- Install dependencies: `pip install -r requirements.txt`
- Verify `.env` file exists with `GOOGLE_API_KEY`

### Frontend won't start
- Check Node.js: `node --version`
- Install dependencies: `cd frontend && npm install`
- Clear cache: `rm -rf node_modules && npm install`

### Content generation fails
- Verify `GOOGLE_API_KEY` in `.env`
- Check backend is running on port 8000
- Review backend logs for errors

### Scheduled posts not saving
- Verify backend is running
- Check `scheduled_posts/` directory exists and is writable
- Review browser console for API errors

---

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests: `pytest`
4. Push and create a pull request

---

## License

This project is part of a capstone demonstration for AI-powered content generation.

---

## Support

For issues or questions, please create an issue in the GitHub repository.




