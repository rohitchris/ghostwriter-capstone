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

