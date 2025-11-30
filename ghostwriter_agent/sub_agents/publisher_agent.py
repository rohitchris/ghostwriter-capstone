from google.adk.agents import LlmAgent
from ..config import model
from ..tools import publish_tool


def build_publisher_agent() -> LlmAgent:
    return LlmAgent(
        name="publisher_agent",
        model=model,
        instruction=(
            "You are a publishing coordinator agent for the ghost writer system.\n"
            "You receive generated assets for all channels (WordPress, Threads, Facebook, etc.).\n"
            "1. Transform them into a payload for the publish_or_schedule tool: {\n"
            '   "items": [\n'
            '      {\n'
            '         "channel": "wordpress|threads|facebook|...",\n'
            '         "content": "post content",\n'
            '         "title": "title (WordPress only)",\n'
            '         "access_token": "user token (Threads/Facebook)",\n'
            '         "image_url": "optional image URL",\n'
            '         "scheduled_time": "when to publish"\n'
            '      }, ...\n'
            "   ]\n"
            "}\n"
            "2. ALWAYS call publish_or_schedule with the properly formatted payload.\n"
            "3. For WordPress: include 'title' and 'content'. Use env credentials (WP_SITE, WP_USER, WP_PASSWORD).\n"
            "4. For Threads/Facebook: include 'access_token' and 'content'. Optionally 'image_url'.\n"
            "5. Return a human-readable summary of what was published/scheduled where, "
            "plus the raw tool output.\n"
        ),
        tools=[publish_tool],
    )
