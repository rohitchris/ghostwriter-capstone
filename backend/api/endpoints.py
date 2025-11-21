"""API endpoints for the GhostWriter backend."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import sys
import os
import requests
from datetime import datetime

# Add project root to path for agent imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from helpers.wordpress_checker import is_wordpress

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
    content: str
    platform: str
    style: Optional[str] = None


class ContentRefinementRequest(BaseModel):
    platform: str
    current_content: str
    refinement_instruction: str
    topic: Optional[str] = None


class AgentRunRequest(BaseModel):
    topic: str
    prompt: Optional[str] = None


class WordPressVerifyRequest(BaseModel):
    site_url: str
    username: str
    password: str


class FacebookVerifyRequest(BaseModel):
    access_token: str
    app_id: str
    app_secret: str


class InstagramVerifyRequest(BaseModel):
    access_token: str
    user_id: str


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
    """Generate an image using gemini-2.5-flash-image model directly based on platform content."""
    try:
        # Get Google API key from NANOBANANA_API_KEY env var (for consistency)
        # This will actually be your Google API key
        api_key = os.getenv("NANOBANANA_API_KEY") or os.getenv("GOOGLE_API_KEY")
        
        if not api_key:
            raise HTTPException(status_code=500, detail="API key not configured in environment variables")
        
        # Use the image generator agent (Google image model) to create a prompt based on content and platform
        from ghostwriter_agent.sub_agents.image_generator import build_image_generator_agent
        from google.adk.runners import InMemoryRunner
        
        image_agent = build_image_generator_agent()
        runner_instance = InMemoryRunner(agent=image_agent)
        
        # Create a prompt that includes the content and platform context
        agent_prompt = (
            f"Create an image generation prompt for {request.platform} platform content.\n"
            f"Content: {request.content[:500]}\n"
            f"Style preference: {request.style or 'default'}\n"
            f"Generate an optimized image prompt that captures the essence of this content for {request.platform}."
        )
        
        agent_result = await runner_instance.run_debug(agent_prompt)
        agent_text = str(agent_result)
        
        # Extract the refined prompt from agent result (may be JSON or plain text)
        import json
        try:
            # Try to parse as JSON first
            agent_data = json.loads(agent_text)
            image_prompt = agent_data.get('refined_prompt', agent_text)
        except:
            # If not JSON, use the text directly
            image_prompt = agent_text
        
        
        # Generate the actual image using gemini-2.5-flash-image directly
        # Try using the newer google.genai API first, fallback to google-generativeai
        image_data = None
        image_url = None
        
        try:
            # Try newer API: from google import genai
            try:
                from google import genai as google_genai
                
                client = google_genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model="gemini-2.5-flash-image",
                    contents=[image_prompt],
                )
                
                # Extract image from response
                if response.candidates and len(response.candidates) > 0:
                    candidate = response.candidates[0]
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if hasattr(part, 'inline_data') and part.inline_data:
                                image_data = part.inline_data.data
                            elif hasattr(part, 'image_url') and part.image_url:
                                image_url = part.image_url
                
            except ImportError:
                # Fallback to google-generativeai package
                import google.generativeai as genai
                
                genai.configure(api_key=api_key)
                
                # Use the gemini-2.5-flash-image model to generate the image
                model = genai.GenerativeModel('gemini-2.5-flash-image')
                
                # Generate image with the refined prompt
                response = model.generate_content(
                    image_prompt,
                    generation_config={
                        "temperature": 0.7,
                    }
                )
                
                # Extract image from response (google-generativeai format)
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'content') and candidate.content:
                        if hasattr(candidate.content, 'parts'):
                            for part in candidate.content.parts:
                                if hasattr(part, 'inline_data') and part.inline_data:
                                    image_data = part.inline_data.data
                                elif hasattr(part, 'image_url') and part.image_url:
                                    image_url = part.image_url
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating image with gemini-2.5-flash-image: {str(e)}")
        
        # Process and return the result
        if image_data or image_url:
            # Convert image_data to base64 if it's bytes
            import base64
            image_data_b64 = None
            if image_data:
                if isinstance(image_data, bytes):
                    image_data_b64 = base64.b64encode(image_data).decode('utf-8')
                else:
                    image_data_b64 = image_data
            
            result = {
                "success": True,
                "image_url": image_url,
                "url": image_url,  # Also include as 'url' for compatibility
                "image_data": image_data_b64,  # Base64 encoded image data
                "metadata": {
                    "model": "gemini-2.5-flash-image",
                    "platform": request.platform,
                    "style": request.style
                }
            }
            return result
        else:
            raise HTTPException(status_code=500, detail="Failed to generate image: No image data returned from model")
            
    except HTTPException:
        raise
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request failed: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating image: {str(e)}")


# Agent Endpoints
@router.post("/agents/run-full-cycle")
async def run_full_agent_cycle(request: AgentRunRequest):
    """Run the full GhostWriter agent cycle and return structured platform-specific outputs."""
    try:
        from ghostwriter_agent.prompts import SAMPLE_RUN_PROMPT
        import json
        import re
        
        # Try to import tiktoken, but make it optional
        try:
            import tiktoken
            HAS_TIKTOKEN = True
        except ImportError:
            HAS_TIKTOKEN = False
        
        # Count tokens in the prompt
        user_prompt = SAMPLE_RUN_PROMPT.format(topic=request.topic)
        
        # Use tiktoken if available, otherwise estimate
        if HAS_TIKTOKEN:
            try:
                encoding = tiktoken.get_encoding("cl100k_base")
                prompt_tokens = len(encoding.encode(user_prompt))
            except Exception as e:
                # Fallback: rough estimate (1 token ≈ 4 characters)
                prompt_tokens = len(user_prompt) // 4
        else:
            # Fallback: rough estimate (1 token ≈ 4 characters)
            prompt_tokens = len(user_prompt) // 4
        
        
        result = await runner.run_debug(user_prompt)
        
        # Extract actual text content from Event objects
        def extract_text_from_events(events_result):
            """Extract text content from ADK Event objects, ignoring function calls and metadata."""
            text_parts = []
            
            # Handle if result is a list of Events
            if isinstance(events_result, list):
                # Reverse iterate to get the final responses first (most recent = final output)
                for event in reversed(events_result):
                    # Only process model role events (skip user/function responses)
                    if hasattr(event, 'role') and event.role == 'model':
                        if hasattr(event, 'content') and event.content:
                            if hasattr(event.content, 'parts'):
                                for part in event.content.parts:
                                    # Extract text content, ignore function calls
                                    if hasattr(part, 'text') and part.text:
                                        text_parts.insert(0, part.text)  # Insert at beginning to maintain order
                                    # Check for dict-like structure
                                    elif isinstance(part, dict) and 'text' in part:
                                        text_parts.insert(0, part['text'])
            # Handle if result is a single Event
            elif hasattr(events_result, 'content') and events_result.content:
                if hasattr(events_result.content, 'parts'):
                    for part in events_result.content.parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)
                        elif isinstance(part, dict) and 'text' in part:
                            text_parts.append(part['text'])
            
            # Join all text parts
            extracted_text = "\n\n".join(text_parts) if text_parts else ""
            
            # If we didn't get text from Event parts, extract from string representation
            if not extracted_text or extracted_text.strip() == "" or "Event(" in extracted_text or "Content(" in extracted_text:
                result_str = str(events_result)
                
                # Try to find JSON structure with "assets" (from content_creator)
                # Look for the JSON structure that contains "assets" key
                json_match = None
                
                # Method 1: Find "assets" and extract balanced JSON around it
                start_idx = result_str.find('"assets"')
                if start_idx != -1:
                    # Find the opening brace before "assets"
                    brace_start = result_str.rfind('{', 0, start_idx)
                    if brace_start != -1:
                        # Count braces to find matching closing brace
                        brace_count = 0
                        for i in range(brace_start, len(result_str)):
                            if result_str[i] == '{':
                                brace_count += 1
                            elif result_str[i] == '}':
                                brace_count -= 1
                                if brace_count == 0:
                                    json_match = result_str[brace_start:i+1]
                                    break
                
                # Method 2: Try regex for nested JSON
                if not json_match:
                    # More flexible regex that handles nested structures
                    json_match_obj = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*"assets"[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', result_str, re.DOTALL)
                    if json_match_obj:
                        json_match = json_match_obj.group(0)
                
                # Method 3: Try to find any complete JSON structure
                if not json_match:
                    # Look for any JSON-like structure
                    json_match_obj = re.search(r'\{[^{}]*"assets"[^{}]*\}', result_str, re.DOTALL)
                    if json_match_obj:
                        json_match = json_match_obj.group(0)
                
                if json_match:
                    # Try to parse and validate JSON
                    try:
                        json.loads(json_match)  # Validate it's valid JSON
                        extracted_text = json_match
                    except json.JSONDecodeError:
                        extracted_text = json_match  # Use it anyway
                else:
                    # Last resort: return empty and let fallback handle it
                    extracted_text = ""  # Return empty, fallback will handle it
            
            return extracted_text
        
        # Extract text content from Events
        agent_text = extract_text_from_events(result)
        
        # Helper function to build posting content (caption + hashtags only, no video_script or image_prompt)
        def build_posting_content(platform_data: dict, platform_name: str, fallback_text: str) -> str:
            """Extract only what should be posted: caption and hashtags."""
            # Handle empty dict case
            if not platform_data or not isinstance(platform_data, dict):
                return fallback_text
            
            caption = platform_data.get("caption", "") or platform_data.get("content", "")
            hashtags = platform_data.get("hashtags", "")
            
            # Format hashtags if they're a list
            if isinstance(hashtags, list):
                hashtags = " ".join([f"#{tag.replace('#', '').strip()}" for tag in hashtags if tag])
            elif hashtags and not hashtags.startswith("#"):
                # If it's a string but not formatted, add # prefix
                hashtags = " ".join([f"#{tag.strip()}" for tag in hashtags.split() if tag])
            
            # Combine caption and hashtags
            if caption and hashtags:
                result = f"{caption}\n\n{hashtags}"
            elif caption:
                result = caption
            elif hashtags:
                result = hashtags
            else:
                result = fallback_text
            
            # Ensure we never return empty string
            return result if result.strip() else fallback_text
        
        # Check if agent_text contains Event objects (not useful content)
        is_event_object = "Event(" in agent_text or "Content(" in agent_text or "Part(" in agent_text or "FunctionCall(" in agent_text
        
        # Try to extract structured content from agent result
        # First, try to parse as JSON if the agent returned structured data
        try:
            # Try to find JSON in the result
            json_match = re.search(r'\{.*"assets".*\}', agent_text, re.DOTALL)
            if json_match:
                try:
                    agent_json = json.loads(json_match.group(0))
                    assets = agent_json.get("assets", {})
                    
                    # Extract platform-specific content from JSON structure
                    facebook_data = assets.get("Facebook", {}) or assets.get("facebook", {})
                    wordpress_data = assets.get("WordPress", {}) or assets.get("wordpress", {})
                    instagram_data = assets.get("Instagram", {}) or assets.get("instagram", {})
                    
                    # Extract only posting content (caption + hashtags), exclude video_script and image_prompt
                    # Use topic-based fallback if we have Event objects
                    fallback_fb = f"Engaging content about {request.topic} #ContentStrategy" if is_event_object else (agent_text[:200] if agent_text else f"Content about {request.topic}")
                    fallback_ig = f"Exciting content about {request.topic} #AIContent" if is_event_object else (agent_text[:150] if agent_text else f"Content about {request.topic}")
                    
                    facebook = build_posting_content(facebook_data, "Facebook", fallback_fb)
                    instagram = build_posting_content(instagram_data, "Instagram", fallback_ig)
                    
                    # WordPress uses content (long-form), not caption
                    wordpress_content = wordpress_data.get("content", "") or wordpress_data.get("caption", "")
                    if not wordpress_content or not wordpress_content.strip() or is_event_object:
                        wordpress_content = f"Comprehensive article about {request.topic} covering key insights and trends."
                    wordpress = f"<h1>{request.topic}</h1>\n\n<p>{wordpress_content}</p>"
                    
                    # Master content is a summary
                    master_content = f"## {request.topic}\n\nGenerated content for multiple platforms.\n\n**Generated with tone: Informative and Professional**"
                except json.JSONDecodeError as e:
                    raise ValueError("Invalid JSON structure")
            else:
                raise ValueError("No JSON structure found")
        except (json.JSONDecodeError, ValueError, KeyError):
            # Fallback: Parse text-based agent result OR use topic-based content if Event objects
            if is_event_object:
                # Generate useful fallback content based on topic
                facebook = f"📘 Exciting insights about {request.topic}! Stay ahead of the curve. #ContentStrategy #AI"
                wordpress = f"<h1>{request.topic}</h1>\n\n<p>In this comprehensive article, we explore {request.topic} and its implications for modern content creation and strategy.</p>"
                instagram = f"🔥 Discover the latest on {request.topic}! What are your thoughts? #AIContent #Trending"
                master_content = f"## {request.topic}\n\nContent generated for multiple platforms.\n\n**Generated with tone: Informative and Professional**"
            else:
                
                # Try to extract platform-specific sections from text
                facebook_match = re.search(r'(?i)(facebook|fb)[:\s]+(.*?)(?=\n\n|\nInstagram|\nWordPress|\nTikTok|$)', agent_text, re.DOTALL)
                facebook_content = facebook_match.group(2).strip() if facebook_match else None
                
                wp_match = re.search(r'(?i)(wordpress|wp|blog)[:\s]+(.*?)(?=\n\n|\nFacebook|\nInstagram|\nTikTok|$)', agent_text, re.DOTALL)
                wp_content = wp_match.group(2).strip() if wp_match else None
                
                ig_match = re.search(r'(?i)(instagram|ig)[:\s]+(.*?)(?=\n\n|\nFacebook|\nWordPress|\nTikTok|$)', agent_text, re.DOTALL)
                ig_content = ig_match.group(2).strip() if ig_match else None
                
                # Create structured outputs (only posting content, no extra formatting)
                master_content = f"## {request.topic}\n\n{agent_text[:500] if agent_text else 'Content generated.'}\n\n**Generated with tone: Informative and Professional**"
                facebook = facebook_content if facebook_content and facebook_content.strip() else f"📘 Engaging content about {request.topic} #ContentStrategy"
                wordpress = f"<h1>{request.topic}</h1>\n\n<p>{wp_content if wp_content and wp_content.strip() else f'Comprehensive article about {request.topic}.'}</p>"
                instagram = ig_content if ig_content and ig_content.strip() else f"🔥 Exciting content about {request.topic} #AIContent"
        
        
        return {
            "success": True,
            "outputs": {
                "master": master_content,
                "facebook": facebook,
                "wordpress": wordpress,
                "instagram": instagram
            },
            "topic": request.topic,
            "token_usage": {
                "prompt_tokens": prompt_tokens,
                "estimated_total": prompt_tokens + (len(str(result)) // 4)  # Rough estimate for response tokens
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running agent cycle: {str(e)}")


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
        agent = build_content_creator_agent()
        from google.adk.runners import InMemoryRunner
        runner_instance = InMemoryRunner(agent=agent)
        
        prompt = f"Create engaging content about {request.topic} with a {request.tone} tone. Generate content suitable for Facebook, WordPress blog, and Instagram."
        result = await runner_instance.run_debug(prompt)
        
        
        # Parse agent result into structured content
        agent_text = str(result)
        
        # Create platform-specific content
        master = f"## {request.topic}\n\n{agent_text}\n\n**Tone: {request.tone}**"
        facebook = f"📘 {request.topic}\n\n{agent_text[:200]}...\n\n#{request.topic.replace(' ', '')} #ContentStrategy #AI"
        wordpress = f"<h1>{request.topic}</h1>\n\n<p>{agent_text}</p>"
        instagram = f"🔥 {request.topic}!\n\n{agent_text[:150]}...\n\n#{request.topic.split()[0] if request.topic.split() else 'Content'}"
        
        
        response = {
            "success": True,
            "outputs": {
                "master": master,
                "facebook": facebook,
                "wordpress": wordpress,
                "instagram": instagram
            }
        }
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating content: {str(e)}")


# Content Refinement Endpoint
@router.post("/refine-content")
async def refine_content_endpoint(request: ContentRefinementRequest):
    """Refine/regenerate content for a specific platform based on refinement instruction."""
    try:
        from ghostwriter_agent.sub_agents.content_creator import build_content_creator_agent
        from google.adk.runners import InMemoryRunner
        import json
        import re
        
        agent = build_content_creator_agent()
        runner_instance = InMemoryRunner(agent=agent)
        
        # Build prompt for platform-specific refinement
        platform_requirements = {
            "facebook": "40-250 characters, 1-3 hashtags maximum",
            "wordpress": "500-2000+ words, proper HTML formatting with headings and paragraphs",
            "instagram": "up to 2,200 characters (optimal 125), 5-10 hashtags, include emojis"
        }
        
        req = platform_requirements.get(request.platform.lower(), "platform-appropriate format")
        
        prompt = (
            f"Refine the following {request.platform} content based on this instruction: {request.refinement_instruction}\n\n"
            f"Current content:\n{request.current_content}\n\n"
            f"Requirements for {request.platform}: {req}\n\n"
            f"Generate ONLY the refined {request.platform} content (caption + hashtags for social media, or full content for WordPress). "
            f"Output JSON: {{\"caption\": \"...\", \"hashtags\": [...]}} for social media, or {{\"content\": \"...\"}} for WordPress."
        )
        
        if request.topic:
            prompt = f"Topic: {request.topic}\n\n{prompt}"
        
        result = await runner_instance.run_debug(prompt)
        
        # Extract text from Event objects (same as run-full-cycle)
        def extract_text_from_events(events_result):
            text_parts = []
            if isinstance(events_result, list):
                for event in reversed(events_result):
                    if hasattr(event, 'role') and event.role == 'model':
                        if hasattr(event, 'content') and event.content:
                            if hasattr(event.content, 'parts'):
                                for part in event.content.parts:
                                    if hasattr(part, 'text') and part.text:
                                        text_parts.insert(0, part.text)
            elif hasattr(events_result, 'content') and events_result.content:
                if hasattr(events_result.content, 'parts'):
                    for part in events_result.content.parts:
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)
            
            extracted_text = "\n\n".join(text_parts) if text_parts else ""
            
            if not extracted_text or "Event(" in extracted_text:
                result_str = str(events_result)
                json_match = re.search(r'\{.*?"caption".*?\}|\{.*?"content".*?\}', result_str, re.DOTALL)
                if json_match:
                    extracted_text = json_match.group(0)
                else:
                    extracted_text = result_str
            
            return extracted_text
        
        agent_text = extract_text_from_events(result)
        
        # Parse the refined content
        refined_content = ""
        try:
            # Try to parse as JSON
            json_match = re.search(r'\{.*?\}', agent_text, re.DOTALL)
            if json_match:
                agent_json = json.loads(json_match.group(0))
                
                if request.platform.lower() == "wordpress":
                    refined_content = agent_json.get("content", "") or agent_json.get("caption", "")
                else:
                    # Social media: combine caption and hashtags
                    caption = agent_json.get("caption", "")
                    hashtags = agent_json.get("hashtags", "")
                    
                    if isinstance(hashtags, list):
                        hashtags = " ".join([f"#{tag.replace('#', '').strip()}" for tag in hashtags if tag])
                    elif hashtags and not hashtags.startswith("#"):
                        hashtags = " ".join([f"#{tag.strip()}" for tag in hashtags.split() if tag])
                    
                    if caption and hashtags:
                        refined_content = f"{caption}\n\n{hashtags}"
                    elif caption:
                        refined_content = caption
                    elif hashtags:
                        refined_content = hashtags
        except (json.JSONDecodeError, KeyError):
            # If not JSON, use the text directly
            refined_content = agent_text.strip()
        
        # Ensure we have content
        if not refined_content or not refined_content.strip():
            refined_content = request.current_content  # Fallback to original
        
        
        return {
            "success": True,
            "refined_content": refined_content,
            "platform": request.platform
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refining content: {str(e)}")



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
        initial_count = len(posts)
        posts = [p for p in posts if p.get("id") != post_id]
        _save_user_posts(user_id, posts)
        
        return {
            "success": True,
            "message": "Post deleted successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting scheduled post: {str(e)}")


# Platform Authentication Endpoints
@router.post("/platforms/wordpress/verify")
async def verify_wordpress_credentials(request: WordPressVerifyRequest):
    """Verify WordPress credentials (mocked for demo)."""
    try:
        # Mock verification - simulate API call delay
        await asyncio.sleep(1)
        
        # In a real implementation, this would:
        # 1. Check if the site is WordPress using is_wordpress()
        # 2. Attempt to authenticate using WordPress REST API
        # 3. Return success/failure
        
        # For demo purposes, accept any credentials that look valid
        if not request.site_url or not request.username or not request.password:
            raise HTTPException(status_code=400, detail="All fields are required")
        
        # Basic validation
        if not request.site_url.startswith(('http://', 'https://')):
            raise HTTPException(status_code=400, detail="Invalid site URL format")
        
        if len(request.password) < 8:
            raise HTTPException(status_code=400, detail="Password appears invalid (too short)")
        
        return {
            "success": True,
            "message": "WordPress credentials verified successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying credentials: {str(e)}")


@router.post("/platforms/facebook/verify")
async def verify_facebook_credentials(request: FacebookVerifyRequest):
    """Verify Facebook credentials (mocked for demo)."""
    try:
        # Mock verification - simulate API call delay
        await asyncio.sleep(1)
        
        # In a real implementation, this would:
        # 1. Verify the access token with Facebook Graph API
        # 2. Check app_id and app_secret match
        # 3. Return success/failure
        
        # For demo purposes, accept any credentials that look valid
        if not request.access_token or not request.app_id or not request.app_secret:
            raise HTTPException(status_code=400, detail="All fields are required")
        
        if len(request.access_token) < 10:
            raise HTTPException(status_code=400, detail="Invalid access token format")
        
        if len(request.app_id) < 10:
            raise HTTPException(status_code=400, detail="Invalid app ID format")
        
        return {
            "success": True,
            "message": "Facebook credentials verified successfully",
            "app_id": request.app_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying credentials: {str(e)}")


@router.post("/platforms/instagram/verify")
async def verify_instagram_credentials(request: InstagramVerifyRequest):
    """Verify Instagram credentials (mocked for demo)."""
    try:
        # Mock verification - simulate API call delay
        await asyncio.sleep(1)
        
        # In a real implementation, this would:
        # 1. Verify the access token with Instagram Graph API
        # 2. Check user_id matches the token
        # 3. Return success/failure
        
        # For demo purposes, accept any credentials that look valid
        if not request.access_token or not request.user_id:
            raise HTTPException(status_code=400, detail="All fields are required")
        
        if len(request.access_token) < 10:
            raise HTTPException(status_code=400, detail="Invalid access token format")
        
        return {
            "success": True,
            "message": "Instagram credentials verified successfully",
            "user_id": request.user_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error verifying credentials: {str(e)}")


