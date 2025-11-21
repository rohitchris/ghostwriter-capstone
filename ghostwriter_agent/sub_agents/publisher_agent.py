from google.adk.agents import LlmAgent
from ..config import model
from ..tools import publish_tool


def build_publisher_agent() -> LlmAgent:
    return LlmAgent(
        name="publisher_agent",
        model=model,
        instruction=(
            "You are a publishing coordinator agent for the ghost writer system.\n"
            "You receive generated assets for all channels.\n\n"
            "PLATFORM-SPECIFIC REQUIREMENTS:\n"
            "- Facebook: Posts should be 40-250 characters for optimal engagement. "
            "Can include links, images, and videos. Use 1-3 hashtags maximum.\n"
            "- Instagram: Captions can be up to 2,200 characters, but 125 characters is optimal. "
            "Use 5-10 hashtags. Include emojis for engagement.\n"
            "- WordPress: Long-form content (500-2000+ words). Use proper HTML formatting, "
            "headings (h1, h2, h3), paragraphs, and SEO-friendly structure.\n\n"
            "TASKS:\n"
            "1. Review each platform's content and ensure it meets platform-specific requirements:\n"
            "   - Check character/word counts\n"
            "   - Verify formatting matches platform standards\n"
            "   - Ensure hashtags are appropriate for the platform\n"
            "   - Adjust content if needed to fit platform constraints\n"
            "2. Transform them into a payload for the publish_or_schedule tool: {\n"
            '   "items": [\n'
            '      {"channel": "Facebook"|"Instagram"|"WordPress", "caption": ..., "script": ..., '
            '"scheduled_time": ..., "content": ...}, ...\n'
            "   ]\n"
            "}\n"
            "3. ALWAYS call publish_or_schedule with properly formatted platform-specific content.\n"
            "4. Return a human-readable summary of what was scheduled where, "
            "plus the raw tool output.\n"
        ),
        tools=[publish_tool],
    )
