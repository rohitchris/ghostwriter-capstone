
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
- **Threads publishing** with Meta Threads API
- **Facebook publishing** to pages and profiles
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

# Threads API (Meta)
THREADS_APP_ID=1393569372162716
THREADS_APP_SECRET=your_threads_app_secret_here

# Facebook API (Meta)
FACEBOOK_APP_ID=1166650488940455
FACEBOOK_APP_SECRET=your_facebook_app_secret_here
```

5. **Configure Firebase Authentication:**

Create `frontend/.env` file with your Firebase credentials:
```env
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

**See [FIREBASE_SETUP.md](FIREBASE_SETUP.md) for detailed Firebase configuration instructions.**

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
2. **Sign up** with a real email and password (Firebase authentication)
3. Check your Firebase Console to see the registered user
4. Navigate to `/generator` to create content
5. View scheduled posts in the Dashboard

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

- **POST** `/api/scheduled-posts/publish-wordpress/{user_id}/{post_id}` - Publish a WordPress post directly
  - Requires: `WP_SITE`, `WP_USER`, `WP_PASSWORD` in `.env`
  - Updates post status to "Published"
  - Returns WordPress post URL

- **POST** `/api/scheduled-posts/publish-threads` - Publish to Threads
  - Body: `{ "user_id": string, "post_id": string, "access_token": string }`
  - Returns Threads post URL
  
- **POST** `/api/scheduled-posts/publish-facebook` - Publish to Facebook
  - Body: `{ "user_id": string, "post_id": string, "access_token": string, "page_id": string?, "page_access_token": string? }`
  - Returns Facebook post URL

### Social Media Connections
- **GET** `/api/check-threads?access_token=TOKEN` - Verify Threads connection
- **GET** `/api/check-facebook?access_token=TOKEN` - Verify Facebook connection
- **GET** `/api/facebook-pages?access_token=TOKEN` - List managed Facebook pages

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
- **Real Firebase Authentication** - Email/password sign-up and login
- **Content generation** - AI-powered content for all platforms
- **Image generation** - nanobanana integration
- **Scheduled posts** - Persistent storage with dashboard
- **WordPress auto-publish** - One-click publishing from dashboard
- **Threads publishing** - Publish to Instagram Threads with access token
- **Facebook publishing** - Publish to Facebook pages and profiles
- **WordPress site verification** - Check if a URL is WordPress

### 🔄 Coming Soon
- OAuth flow for Threads/Facebook tokens
- Scheduled auto-posting at specific times
- Social media analytics integration
- Email verification for new users
- Password reset functionality

---

## Documentation

- **[FIREBASE_SETUP.md](FIREBASE_SETUP.md)** - Complete Firebase authentication setup
- **[THREADS_FACEBOOK_INTEGRATION.md](THREADS_FACEBOOK_INTEGRATION.md)** - Threads and Facebook API integration guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture and AI agent workflow

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

### Firebase Authentication Integration
- ✅ Replaced mock authentication with real Firebase
- ✅ Email/password sign-up and login
- ✅ User session management
- ✅ Secure authentication state handling
- ✅ User-friendly error messages

### WordPress Publishing
- ✅ One-click WordPress publishing from scheduled posts dashboard
- ✅ Automatic post status updates
- ✅ WordPress post URL tracking
- ✅ Delete scheduled posts
- ✅ Error handling for WordPress API

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
- ✅ Real Firebase authentication with proper error handling

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

### Firebase Variables (in `frontend/.env`)

| Variable | Required | Purpose |
|----------|----------|---------|
| `VITE_FIREBASE_API_KEY` | Yes | Firebase API key |
| `VITE_FIREBASE_AUTH_DOMAIN` | Yes | Firebase auth domain |
| `VITE_FIREBASE_PROJECT_ID` | Yes | Firebase project ID |
| `VITE_FIREBASE_STORAGE_BUCKET` | Yes | Firebase storage bucket |
| `VITE_FIREBASE_MESSAGING_SENDER_ID` | Yes | Firebase messaging sender ID |
| `VITE_FIREBASE_APP_ID` | Yes | Firebase app ID |

---

## Security & Best Practices

- ✅ `.env` files ignored by git (both root and `frontend/.env`)
- ✅ Firebase authentication with secure password requirements
- ✅ Use WordPress application passwords (not main password)
- ✅ Environment variables for all secrets
- ⚠️ File-based storage suitable for demo (use database for production)
- ⚠️ Enable Firebase Security Rules for production deployments

**For Firebase setup:** See [FIREBASE_SETUP.md](FIREBASE_SETUP.md) for complete instructions.

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




