"""API endpoints for the GhostWriter backend."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import sys
import os

# Add project root to path for agent imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from helpers.wordpress_checker import is_wordpress
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
    prompt: str
    style: Optional[str] = None


class AgentRunRequest(BaseModel):
    topic: str
    prompt: Optional[str] = None


# Chatbot models
class ChatRequest(BaseModel):
    brand_info: Optional[str] = None
    message: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    follow_up: Optional[str] = None


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
    """Generate an image using nanobanana."""
    try:
        result = generate_image(request.prompt, request.style)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating image: {str(e)}")


# Agent Endpoints
@router.post("/agents/run-full-cycle")
async def run_full_agent_cycle(request: AgentRunRequest):
    """Run the full GhostWriter agent cycle."""
    try:
        from ghostwriter_agent.prompts import SAMPLE_RUN_PROMPT
        
        user_prompt = SAMPLE_RUN_PROMPT.format(topic=request.topic)
        result = await runner.run_debug(user_prompt)
        
        return {
            "success": True,
            "result": str(result),
            "topic": request.topic
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



@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Brand-aware chatbot endpoint.

    Behavior:
    - If `brand_info` is missing, returns a prompt asking the user to describe their brand.
    - If `brand_info` is present, tries to use Google Generative AI when `GOOGLE_API_KEY` is set.
      Falls back to a simple templated reply when the Google API is not configured or an error occurs.
    """
    try:
        if not request.brand_info:
            return ChatResponse(
                reply=(
                    "Thanks — to help with content, please tell me about your brand:"
                    " what you sell, who your audience is, and what tone you prefer."
                ),
                follow_up="Please provide a short description of your brand (products/services, audience, tone).",
            )

        # Build a concise assistant prompt that uses the brand info and user's message
        user_message = request.message or "Please help me with my brand messaging."
        prompt_text = (
            "You are a helpful brand assistant. Use the brand information below to respond to the user's message.\n\n"
            f"Brand information: {request.brand_info}\n\n"
            f"User message: {user_message}\n\n"
            "Provide a concise, actionable reply (2-4 short paragraphs) and suggest one follow-up question to clarify the brand further."
        )

        # Prefer Google Generative AI if available
        google_key = os.getenv("GOOGLE_API_KEY")
        if google_key:
            try:
                import google.generativeai as genai

                genai.configure(api_key=google_key)
                # Use a text model (text-bison) if available
                response = genai.generate_text(model="text-bison-001", input=prompt_text)
                # Response handling: the library may expose .text or .candidates
                text = None
                if hasattr(response, "text") and response.text:
                    text = response.text
                else:
                    # try candidates
                    try:
                        text = response.candidates[0].content
                    except Exception:
                        text = str(response)

                # Heuristic follow-up extraction
                follow_up = None
                if "?" in text:
                    parts = [s.strip() for s in text.split("\n") if s.strip()]
                    for p in reversed(parts):
                        if "?" in p:
                            follow_up = p
                            break

                return ChatResponse(reply=text, follow_up=follow_up)
            except Exception:
                # Fall through to rule-based fallback if Google call fails
                pass

        # Fallback: simple templated reply without external API
        reply_lines = []
        reply_lines.append(f"Thanks — here are some quick ideas for your brand:")
        reply_lines.append(f"Brand summary: {request.brand_info}")
        reply_lines.append("")
        reply_lines.append("Suggested messages:")
        reply_lines.append(f"- Short headline: Try: \"{user_message[:60]}\"")
        reply_lines.append(f"- Social caption: Speak warmly to your audience and mention benefits; e.g., 'Our {request.brand_info.split()[0]} helps...' ")
        reply = "\n".join(reply_lines)

        follow_up = "Would you like a caption in a specific tone (e.g., playful, formal, educational)?"
        return ChatResponse(reply=reply, follow_up=follow_up)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in chat endpoint: {str(e)}")

