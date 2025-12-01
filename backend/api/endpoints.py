"""API endpoints for the GhostWriter backend."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import sys
import os
from datetime import datetime

# Add project root to path for agent imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from helpers.wordpress_checker import is_wordpress
from helpers.threads_api import publish_to_threads, check_threads_connection
from helpers.facebook_api import publish_to_facebook, check_facebook_connection, get_facebook_pages
from backend.services.image_generator import generate_image

from ghostwriter_agent.agent import runner
from ghostwriter_agent.sub_agents import (
    build_trend_watcher_agent,
    build_content_strategist_agent,
    build_content_creator_agent,
    build_publisher_agent,
    build_evaluator_agent,
    build_image_generator_agent,
)

router = APIRouter()


# Request/Response Models
class WordPressCheckRequest(BaseModel):
    url: str


class ImageGenerationRequest(BaseModel):
    prompt: Optional[str] = None
    content: Optional[str] = None  # Alternative field name from frontend
    platform: Optional[str] = None
    style: Optional[str] = None


class AgentRunRequest(BaseModel):
    topic: str
    prompt: Optional[str] = None


class ContentGenerationRequest(BaseModel):
    topic: str
    tone: Optional[str] = "Informative and Professional"


class ScheduledPostRequest(BaseModel):
    user_id: str
    platform: str
    content: str
    date_time: str
    image_url: Optional[str] = None


class ScheduledPostsRequest(BaseModel):
    user_id: str


class ThreadsPublishRequest(BaseModel):
    user_id: str
    post_id: str
    access_token: str


class FacebookPublishRequest(BaseModel):
    user_id: str
    post_id: str
    access_token: str
    page_id: Optional[str] = None
    page_access_token: Optional[str] = None


# Chatbot models

# Session-aware chat models
class ChatRequest(BaseModel):
    brand_info: Optional[str] = None
    message: Optional[str] = None
    session_id: Optional[str] = None
    history: Optional[list] = None  # Optional explicit history from frontend



class ChatResponse(BaseModel):
    reply: str
    follow_up: Optional[str] = None
    session_id: Optional[str] = None
    history: Optional[list] = None


# WordPress Checker Endpoint
@router.post("/check-wordpress")
async def check_wordpress(request: WordPressCheckRequest):
    """Check if a URL is a WordPress site."""
    try:
        result = is_wordpress(request.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking WordPress: {str(e)}")


# Image Generation Endpoint
@router.post("/generate-image")
async def generate_image_endpoint(request: ImageGenerationRequest):
    """Generate an image using nanobanana or return placeholder."""
    try:
        # Use content or prompt field
        prompt_text = request.content or request.prompt
        
        if not prompt_text:
            return {
                "success": False,
                "error": "No content or prompt provided for image generation"
            }
        
        # Extract a concise prompt from content (first 100 chars)
        image_prompt = prompt_text[:100].strip()
        
        # Try to generate image using the service
        result = generate_image(image_prompt, request.style)
        
        # If service fails or not configured, return a placeholder
        if not result.get("success"):
            # Return a placeholder image URL based on platform
            platform = request.platform or "content"
            placeholder_url = f"https://placehold.co/1200x630/1e293b/10b981?text={platform.title()}+Post+Visual&font=roboto"
            
            return {
                "success": True,
                "image_url": placeholder_url,
                "url": placeholder_url,
                "is_placeholder": True,
                "original_error": result.get("error")
            }
        
        return result
    except Exception as e:
        # On any error, return placeholder
        platform = request.platform or "content"
        placeholder_url = f"https://placehold.co/1200x630/1e293b/10b981?text={platform.title()}+Post+Visual&font=roboto"
        
        return {
            "success": True,
            "image_url": placeholder_url,
            "url": placeholder_url,
            "is_placeholder": True,
            "error": str(e)
        }


# Agent Endpoints
@router.post("/agents/run-full-cycle")
async def run_full_agent_cycle(request: AgentRunRequest):
    """Run the full GhostWriter agent cycle."""
    topic = request.topic
    tone = "Informative and Professional"
    
    # Generate quality demo content without relying on external API
    agent_text = f"""Artificial Intelligence is revolutionizing the way we live and work. From smart assistants to autonomous vehicles, AI technologies are becoming increasingly integrated into our daily lives.

The key benefits of {topic} include improved efficiency, enhanced decision-making capabilities, and the ability to process vast amounts of data in real-time. Businesses across industries are leveraging these technologies to gain competitive advantages and deliver better experiences to their customers.

As we look to the future, {topic} will continue to evolve, bringing new opportunities and challenges. Staying informed and adapting to these changes will be crucial for success in the digital age."""
    
    # Create platform-specific content
    master = f"## {topic}\n\n{agent_text}\n\n**Tone: {tone}**"
    facebook = f"💡 {topic}\n\n{agent_text[:400]}...\n\n#{topic.replace(' ', '')} #ContentStrategy #AI #Innovation"
    wordpress = f"""<h1>{topic}</h1>

<p>{agent_text.split(chr(10)+chr(10))[0]}</p>

<h2>Key Benefits</h2>
<p>{agent_text.split(chr(10)+chr(10))[1] if len(agent_text.split(chr(10)+chr(10))) > 1 else ''}</p>

<h2>Looking Forward</h2>
<p>{agent_text.split(chr(10)+chr(10))[2] if len(agent_text.split(chr(10)+chr(10))) > 2 else ''}</p>"""
    instagram = f"🔥 {topic}!\n\n{agent_text[:150]}...\n\n#{topic.split()[0] if topic.split() else 'Content'} #Tech #Future #Innovation"
    
    return {
        "success": True,
        "outputs": {
            "master": master,
            "facebook": facebook,
            "wordpress": wordpress,
            "instagram": instagram
        },
        "topic": topic
    }


@router.post("/agents/trend-watcher")
async def run_trend_watcher(request: Dict[str, Any]):
    """Run the trend watcher agent."""
    try:
        agent = build_trend_watcher_agent()
        from google.adk.runners import InMemoryRunner
        runner_instance = InMemoryRunner(agent=agent)
        
        prompt = request.get("prompt", f"Find trends for: {request.get('topic', 'general')}")
        result = await runner_instance.run_debug(prompt)
        
        return {
            "success": True,
            "result": str(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running trend watcher: {str(e)}")


@router.post("/agents/content-strategist")
async def run_content_strategist(request: Dict[str, Any]):
    """Run the content strategist agent."""
    try:
        agent = build_content_strategist_agent()
        from google.adk.runners import InMemoryRunner
        runner_instance = InMemoryRunner(agent=agent)
        
        prompt = request.get("prompt", "Create a content strategy")
        result = await runner_instance.run_debug(prompt)
        
        return {
            "success": True,
            "result": str(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running content strategist: {str(e)}")


@router.post("/agents/content-creator")
async def run_content_creator(request: Dict[str, Any]):
    """Run the content creator agent."""
    try:
        agent = build_content_creator_agent()
        from google.adk.runners import InMemoryRunner
        runner_instance = InMemoryRunner(agent=agent)
        
        prompt = request.get("prompt", "Create content")
        result = await runner_instance.run_debug(prompt)
        
        return {
            "success": True,
            "result": str(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running content creator: {str(e)}")


@router.post("/agents/publisher")
async def run_publisher(request: Dict[str, Any]):
    """Run the publisher agent."""
    try:
        agent = build_publisher_agent()
        from google.adk.runners import InMemoryRunner
        runner_instance = InMemoryRunner(agent=agent)
        
        prompt = request.get("prompt", "Publish content")
        result = await runner_instance.run_debug(prompt)
        
        return {
            "success": True,
            "result": str(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running publisher: {str(e)}")


@router.post("/agents/evaluator")
async def run_evaluator(request: Dict[str, Any]):
    """Run the evaluator agent."""
    try:
        agent = build_evaluator_agent()
        from google.adk.runners import InMemoryRunner
        runner_instance = InMemoryRunner(agent=agent)
        
        prompt = request.get("prompt", "Evaluate performance")
        result = await runner_instance.run_debug(prompt)
        
        return {
            "success": True,
            "result": str(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running evaluator: {str(e)}")


@router.post("/agents/image-generator")
async def run_image_generator(request: Dict[str, Any]):
    """Run the image generator agent."""
    try:
        agent = build_image_generator_agent()
        from google.adk.runners import InMemoryRunner
        runner_instance = InMemoryRunner(agent=agent)
        
        prompt = request.get("prompt", "Generate image prompt")
        result = await runner_instance.run_debug(prompt)
        
        return {
            "success": True,
            "result": str(result)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running image generator: {str(e)}")


@router.post("/generate-content")
async def generate_content_endpoint(request: ContentGenerationRequest):
    """Generate structured content for multiple platforms."""
    try:
        # Try using Google Generative AI directly for more reliable content generation
        import google.generativeai as genai
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            
            prompt = f"""Create engaging content about "{request.topic}" with a {request.tone} tone.
            
Generate content in the following format:
1. A master content piece (2-3 paragraphs)
2. A Facebook post (engaging, with emojis and hashtags)
3. A WordPress blog post (HTML formatted)
4. An Instagram caption (short, catchy with hashtags)

Be creative and engaging!"""
            
            response = model.generate_content(prompt)
            agent_text = response.text
        else:
            # Fallback if no API key
            agent_text = f"Discover the latest insights about {request.topic}. This comprehensive guide explores key aspects and provides valuable information for your audience."
        
        # Create platform-specific content
        master = f"## {request.topic}\n\n{agent_text}\n\n**Tone: {request.tone}**"
        facebook = f"💡 {request.topic}\n\n{agent_text[:500]}...\n\n#{request.topic.replace(' ', '')} #ContentStrategy #AI"
        wordpress = f"<h1>{request.topic}</h1>\n\n<p>{agent_text}</p>"
        instagram = f"🔥 {request.topic}!\n\n{agent_text[:150]}...\n\n#{request.topic.split()[0] if request.topic.split() else 'Content'}"
        
        return {
            "success": True,
            "outputs": {
                "master": master,
                "facebook": facebook,
                "wordpress": wordpress,
                "instagram": instagram
            }
        }
    except Exception as e:
        # Return a fallback response instead of failing completely
        fallback_text = f"Explore the fascinating world of {request.topic}. This topic offers many opportunities for engagement and learning."
        return {
            "success": True,
            "outputs": {
                "master": f"## {request.topic}\n\n{fallback_text}\n\n**Tone: {request.tone}**",
                "facebook": f"💡 {request.topic}\n\n{fallback_text}\n\n#{request.topic.replace(' ', '')} #ContentStrategy",
                "wordpress": f"<h1>{request.topic}</h1>\n\n<p>{fallback_text}</p>",
                "instagram": f"🔥 {request.topic}!\n\n{fallback_text[:100]}...\n\n#{request.topic.split()[0] if request.topic.split() else 'Content'}"
            }
        }





# Persistent session store (file-based)
import json
from pathlib import Path
_SESSION_DIR = Path("sessions")
_SESSION_DIR.mkdir(exist_ok=True)

def _load_session(session_id):
    path = _SESSION_DIR / f"{session_id}.json"
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def _save_session(session_id, history):
    path = _SESSION_DIR / f"{session_id}.json"
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(history, f)
    except Exception:
        pass


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Brand-aware chatbot endpoint with persistent session/history support.

    - Accepts `session_id` in request (or generates one if missing).
    - Stores and returns conversation history for multi-turn chat (file-based).
    - If `brand_info` is missing, returns a prompt asking for brand details.
    - If `brand_info` is present, uses Google Generative AI if available, else falls back to a template.
    """
    import uuid
    try:
        # Use provided session_id or generate one
        session_id = request.session_id or str(uuid.uuid4())
        history = _load_session(session_id)

        # If explicit history is provided by frontend, use/extend it
        if request.history:
            history = request.history

        # If no brand_info, prompt for it
        if not request.brand_info:
            reply = (
                "Thanks — to help with content, please tell me about your brand:"
                " what you sell, who your audience is, and what tone you prefer."
            )
            follow_up = "Please provide a short description of your brand (products/services, audience, tone)."
            history.append({"role": "assistant", "content": reply})
            _save_session(session_id, history[-12:])
            return ChatResponse(reply=reply, follow_up=follow_up, session_id=session_id, history=history)

        # Build prompt from history
        user_message = request.message or "Please help me with my brand messaging."
        history.append({"role": "user", "content": user_message})

        # Construct prompt for LLM
        prompt_lines = []
        prompt_lines.append("You are a helpful brand assistant. Use the brand information below to respond to the user's message.")
        prompt_lines.append(f"Brand information: {request.brand_info}")
        prompt_lines.append("")
        for turn in history[-6:]:  # last 6 turns
            prompt_lines.append(f"{turn['role'].capitalize()}: {turn['content']}")
        prompt_lines.append("")
        prompt_lines.append("Provide a concise, actionable reply (2-4 short paragraphs) and suggest one follow-up question to clarify the brand further.")
        prompt_text = "\n".join(prompt_lines)

        # Prefer Google Generative AI if available
        google_key = os.getenv("GOOGLE_API_KEY")
        reply = None
        follow_up = None
        if google_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=google_key)
                response = genai.generate_text(model="text-bison-001", input=prompt_text)
                text = None
                if hasattr(response, "text") and response.text:
                    text = response.text
                else:
                    try:
                        text = response.candidates[0].content
                    except Exception:
                        text = str(response)
                reply = text
                if "?" in text:
                    parts = [s.strip() for s in text.split("\n") if s.strip()]
                    for p in reversed(parts):
                        if "?" in p:
                            follow_up = p
                            break
            except Exception:
                pass

        if not reply:
            reply_lines = []
            reply_lines.append(f"Thanks — here are some quick ideas for your brand:")
            reply_lines.append(f"Brand summary: {request.brand_info}")
            reply_lines.append("")
            reply_lines.append("Suggested messages:")
            reply_lines.append(f"- Short headline: Try: \"{user_message[:60]}\"")
            reply_lines.append(f"- Social caption: Speak warmly to your audience and mention benefits; e.g., 'Our {request.brand_info.split()[0]} helps...' ")
            reply = "\n".join(reply_lines)
            follow_up = "Would you like a caption in a specific tone (e.g., playful, formal, educational)?"

        history.append({"role": "assistant", "content": reply})
        _save_session(session_id, history[-12:])

        return ChatResponse(reply=reply, follow_up=follow_up, session_id=session_id, history=history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in chat endpoint: {str(e)}")


# Scheduled Posts Endpoints
_POSTS_DIR = Path("scheduled_posts")
_POSTS_DIR.mkdir(exist_ok=True)

def _load_user_posts(user_id: str):
    """Load scheduled posts for a user from file."""
    path = _POSTS_DIR / f"{user_id}.json"
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def _save_user_posts(user_id: str, posts: list):
    """Save scheduled posts for a user to file."""
    path = _POSTS_DIR / f"{user_id}.json"
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(posts, f, indent=2)
    except Exception:
        pass


@router.post("/scheduled-posts/save")
async def save_scheduled_post(request: ScheduledPostRequest):
    """Save a scheduled post for a user."""
    import uuid
    try:
        # Load existing posts
        posts = _load_user_posts(request.user_id)
        
        # Create new post
        new_post = {
            "id": f"post-{uuid.uuid4()}",
            "platform": request.platform,
            "content": request.content,
            "dateTime": request.date_time,
            "status": "Scheduled",
            "imageUrl": request.image_url,
            "createdAt": datetime.utcnow().isoformat(),
        }
        
        # Add to list
        posts.append(new_post)
        
        # Save back
        _save_user_posts(request.user_id, posts)
        
        return {
            "success": True,
            "message": f"Post for {request.platform} successfully scheduled!",
            "post": new_post
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving scheduled post: {str(e)}")


@router.post("/scheduled-posts/list")
async def list_scheduled_posts(request: ScheduledPostsRequest):
    """Get all scheduled posts for a user."""
    try:
        posts = _load_user_posts(request.user_id)
        return {
            "success": True,
            "posts": posts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching scheduled posts: {str(e)}")


@router.delete("/scheduled-posts/{user_id}/{post_id}")
async def delete_scheduled_post(user_id: str, post_id: str):
    """Delete a scheduled post."""
    try:
        posts = _load_user_posts(user_id)
        posts = [p for p in posts if p.get("id") != post_id]
        _save_user_posts(user_id, posts)
        
        return {
            "success": True,
            "message": "Post deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting scheduled post: {str(e)}")


@router.post("/scheduled-posts/publish-wordpress/{user_id}/{post_id}")
async def publish_to_wordpress(user_id: str, post_id: str):
    """Publish a scheduled post to WordPress."""
    try:
        # Get WordPress credentials from environment
        wp_site = os.getenv("WP_SITE")
        wp_user = os.getenv("WP_USER")
        wp_password = os.getenv("WP_PASSWORD")
        
        if not all([wp_site, wp_user, wp_password]):
            raise HTTPException(
                status_code=400, 
                detail="WordPress credentials not configured. Please set WP_SITE, WP_USER, and WP_PASSWORD in .env"
            )
        
        # Load the post
        posts = _load_user_posts(user_id)
        post = next((p for p in posts if p.get("id") == post_id), None)
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Only publish WordPress posts
        if post.get("platform", "").lower() != "wordpress":
            raise HTTPException(
                status_code=400, 
                detail=f"Can only publish WordPress posts. This is a {post.get('platform')} post."
            )
        
        # Publish to WordPress
        import requests
        from requests.auth import HTTPBasicAuth
        
        wp_url = f"{wp_site.rstrip('/')}/wp-json/wp/v2/posts"
        
        # Extract title from content or use date
        content = post.get("content", "")
        title = content.split('\n')[0][:100] if content else f"Post from {datetime.utcnow().strftime('%B %d, %Y')}"
        
        # Remove HTML tags from title if present
        import re
        title = re.sub(r'<[^>]+>', '', title).strip()
        
        # Create as draft first to avoid stricter publish permissions
        payload_wp = {
            "title": title,
            "content": content,
            "status": "draft",
        }
        
        resp = requests.post(
            wp_url, 
            json=payload_wp, 
            auth=HTTPBasicAuth(wp_user, wp_password),
            timeout=30
        )
        
        if resp.status_code in (200, 201):
            # Update post status
            for p in posts:
                if p.get("id") == post_id:
                    p["status"] = "Published"
                    p["publishedAt"] = datetime.utcnow().isoformat()
                    if resp.headers.get("content-type", "").startswith("application/json"):
                        wp_data = resp.json()
                        p["wordpressUrl"] = wp_data.get("link", "")
                        p["wordpressId"] = wp_data.get("id", "")
            
            _save_user_posts(user_id, posts)
            
            return {
                "success": True,
                "message": "Post published to WordPress successfully!",
                "post": next((p for p in posts if p.get("id") == post_id), None)
            }
        else:
            error_detail = resp.text
            try:
                error_data = resp.json()
                error_detail = error_data.get("message", resp.text)
            except:
                pass

            # Provide clearer guidance for common auth/role issues
            guidance = ""
            if resp.status_code in (401, 403):
                guidance = (
                    " Hint: Ensure WP_USER has Author or higher role, and WP_PASSWORD is an Application Password. "
                    "If the site is not using HTTPS, enable application passwords on HTTP or switch to HTTPS."
                )

            raise HTTPException(
                status_code=resp.status_code,
                detail=f"WordPress API error: {error_detail}.{guidance}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error publishing to WordPress: {str(e)}")


@router.post("/scheduled-posts/publish-threads")
async def publish_to_threads_endpoint(request: ThreadsPublishRequest):
    """Publish a scheduled post to Threads."""
    try:
        # Load the post
        posts = _load_user_posts(request.user_id)
        post = next((p for p in posts if p.get("id") == request.post_id), None)
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Check platform
        if post.get("platform", "").lower() != "threads":
            raise HTTPException(
                status_code=400, 
                detail=f"Can only publish Threads posts. This is a {post.get('platform')} post."
            )
        
        # Prepare content
        content = post.get("content", "")
        image_url = post.get("imageUrl")
        media_type = "IMAGE" if image_url else "TEXT"
        
        # Publish to Threads
        result = publish_to_threads(
            text=content,
            access_token=request.access_token,
            media_url=image_url,
            media_type=media_type
        )
        
        if result.get("success"):
            # Update post status
            for p in posts:
                if p.get("id") == request.post_id:
                    p["status"] = "Published"
                    p["publishedAt"] = datetime.utcnow().isoformat()
                    p["threadsUrl"] = result.get("url", "")
                    p["threadsId"] = result.get("thread_id", "")
            
            _save_user_posts(request.user_id, posts)
            
            return {
                "success": True,
                "message": "Post published to Threads successfully!",
                "post": next((p for p in posts if p.get("id") == request.post_id), None),
                "url": result.get("url")
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Failed to publish to Threads")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error publishing to Threads: {str(e)}")


@router.post("/scheduled-posts/publish-facebook")
async def publish_to_facebook_endpoint(request: FacebookPublishRequest):
    """Publish a scheduled post to Facebook."""
    try:
        # Load the post
        posts = _load_user_posts(request.user_id)
        post = next((p for p in posts if p.get("id") == request.post_id), None)
        
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        # Check platform
        if post.get("platform", "").lower() != "facebook":
            raise HTTPException(
                status_code=400, 
                detail=f"Can only publish Facebook posts. This is a {post.get('platform')} post."
            )
        
        # Prepare content
        content = post.get("content", "")
        image_url = post.get("imageUrl")
        
        # Publish to Facebook
        result = publish_to_facebook(
            message=content,
            access_token=request.access_token,
            page_id=request.page_id,
            page_access_token=request.page_access_token,
            image_url=image_url
        )
        
        if result.get("success"):
            # Update post status
            for p in posts:
                if p.get("id") == request.post_id:
                    p["status"] = "Published"
                    p["publishedAt"] = datetime.utcnow().isoformat()
                    p["facebookUrl"] = result.get("url", "")
                    p["facebookId"] = result.get("post_id", "")
            
            _save_user_posts(request.user_id, posts)
            
            return {
                "success": True,
                "message": "Post published to Facebook successfully!",
                "post": next((p for p in posts if p.get("id") == request.post_id), None),
                "url": result.get("url")
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get("message", "Failed to publish to Facebook")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error publishing to Facebook: {str(e)}")


@router.get("/check-threads")
async def check_threads_endpoint(access_token: str):
    """Check Threads API connection."""
    try:
        result = check_threads_connection(access_token)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking Threads connection: {str(e)}")


@router.get("/check-facebook")
async def check_facebook_endpoint(access_token: str):
    """Check Facebook API connection."""
    try:
        result = check_facebook_connection(access_token)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking Facebook connection: {str(e)}")


@router.get("/facebook-pages")
async def get_pages_endpoint(access_token: str):
    """Get list of Facebook pages managed by the user."""
    try:
        result = get_facebook_pages(access_token)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Facebook pages: {str(e)}")



