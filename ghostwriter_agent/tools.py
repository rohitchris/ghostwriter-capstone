from datetime import datetime
import os
from google.adk.tools import FunctionTool

# local import for small templates
from .prompts import DAILY_TITLE_TEMPLATE

# ------------- TOOL FUNCTIONS -------------


def fetch_trends(brand_topic: str) -> dict:
    """Mock: return a few trending topics for the brand niche."""
    return {
        "status": "success",
        "brand_topic": brand_topic,
        "trends": [
            {
                "topic": "AI won’t replace you, but someone using AI will",
                "platform": "TikTok",
                "velocity_score": 0.92,
            },
            {
                "topic": "Women in tech switching careers into AI",
                "platform": "Instagram",
                "velocity_score": 0.87,
            },
            {
                "topic": "How to stay relevant in the age of agents",
                "platform": "LinkedIn",
                "velocity_score": 0.81,
            },
        ],
        "as_of": datetime.utcnow().isoformat(),
    }


def publish_or_schedule(payload: dict) -> dict:
    """
    Publish or schedule posts to various platforms including WordPress, Threads, and Facebook.
    
    Expected payload structure:
    {
        "items": [
            {
                "channel": "wordpress|threads|facebook|...",
                "title": "...",  # For WordPress
                "content": "...",  # Post content
                "caption": "...",  # Alternative to content
                "status": "publish|draft",  # WordPress only
                "post_to_wp": true,  # Force WordPress posting
                "access_token": "...",  # For Threads/Facebook
                "page_id": "...",  # For Facebook pages
                "page_access_token": "...",  # For Facebook pages
                "image_url": "...",  # Optional image URL
                "scheduled_time": "..."  # When to publish
            }
        ]
    }
    """
    scheduled_items = []

    for item in payload.get("items", []):
        channel = item.get("channel", "unknown").lower()

        # WordPress Publishing
        if "wordpress" in channel or item.get("post_to_wp"):
            wp_site = os.getenv("WP_SITE")
            wp_user = os.getenv("WP_USER")
            wp_password = os.getenv("WP_PASSWORD")

            if wp_site and wp_user and wp_password:
                try:
                    import requests
                    from requests.auth import HTTPBasicAuth

                    wp_url = f"{wp_site.rstrip('/')}/wp-json/wp/v2/posts"
                    today = datetime.today().strftime("%B %d, %Y")
                    title = item.get("title") or DAILY_TITLE_TEMPLATE.format(date=today)
                    content = item.get("content") or item.get("caption") or ""

                    payload_wp = {
                        "title": title,
                        "content": content,
                        "status": item.get("status", "draft"),
                    }

                    resp = requests.post(
                        wp_url, json=payload_wp, auth=HTTPBasicAuth(wp_user, wp_password)
                    )

                    scheduled_items.append(
                        {
                            "channel": "wordpress",
                            "status": "posted" if resp.status_code in (200, 201) else "error",
                            "response_code": resp.status_code,
                            "response": resp.json() if resp.headers.get("content-type", "").startswith("application/json") else resp.text,
                        }
                    )
                    continue
                except Exception as e:
                    scheduled_items.append(
                        {
                            "channel": "wordpress",
                            "status": "error",
                            "note": f"WP post failed: {e}",
                        }
                    )
                    continue

        # Threads Publishing
        elif "threads" in channel:
            access_token = item.get("access_token")
            if access_token:
                try:
                    from helpers.threads_api import publish_to_threads
                    
                    content = item.get("content") or item.get("caption") or ""
                    image_url = item.get("image_url")
                    media_type = "IMAGE" if image_url else "TEXT"
                    
                    result = publish_to_threads(
                        text=content,
                        access_token=access_token,
                        media_url=image_url,
                        media_type=media_type
                    )
                    
                    scheduled_items.append(
                        {
                            "channel": "threads",
                            "status": "posted" if result.get("success") else "error",
                            "thread_id": result.get("thread_id"),
                            "url": result.get("url"),
                            "message": result.get("message"),
                        }
                    )
                    continue
                except Exception as e:
                    scheduled_items.append(
                        {
                            "channel": "threads",
                            "status": "error",
                            "note": f"Threads post failed: {e}",
                        }
                    )
                    continue
            else:
                scheduled_items.append(
                    {
                        "channel": "threads",
                        "status": "error",
                        "note": "Access token required for Threads posting",
                    }
                )
                continue

        # Facebook Publishing
        elif "facebook" in channel:
            access_token = item.get("access_token")
            if access_token:
                try:
                    from helpers.facebook_api import publish_to_facebook
                    
                    content = item.get("content") or item.get("caption") or ""
                    image_url = item.get("image_url")
                    page_id = item.get("page_id")
                    page_access_token = item.get("page_access_token")
                    
                    result = publish_to_facebook(
                        message=content,
                        access_token=access_token,
                        page_id=page_id,
                        page_access_token=page_access_token,
                        image_url=image_url
                    )
                    
                    scheduled_items.append(
                        {
                            "channel": "facebook",
                            "status": "posted" if result.get("success") else "error",
                            "post_id": result.get("post_id"),
                            "url": result.get("url"),
                            "message": result.get("message"),
                        }
                    )
                    continue
                except Exception as e:
                    scheduled_items.append(
                        {
                            "channel": "facebook",
                            "status": "error",
                            "note": f"Facebook post failed: {e}",
                        }
                    )
                    continue
            else:
                scheduled_items.append(
                    {
                        "channel": "facebook",
                        "status": "error",
                        "note": "Access token required for Facebook posting",
                    }
                )
                continue

        # Default mock scheduling behavior for other channels or missing creds
        scheduled_items.append(
            {
                "channel": channel,
                "status": "scheduled",
                "scheduled_time": item.get("scheduled_time", "now"),
                "mock_url": f"https://social.example.com/{channel}/post/12345",
            }
        )

    return {
        "status": "success",
        "items": scheduled_items,
        "note": "Publishing attempted. WordPress/Threads/Facebook posts sent when credentials provided, otherwise mock scheduling used.",
    }


def get_mock_analytics() -> dict:
    """Return fake engagement metrics so the Evaluator agent can learn."""
    return {
        "status": "success",
        "metrics": [
            {"channel": "TikTok", "views": 18450, "likes": 3200, "comments": 240},
            {"channel": "Instagram", "views": 8200, "likes": 970, "comments": 54},
            {"channel": "YouTubeShort", "views": 4200, "likes": 380, "comments": 21},
            {"channel": "LinkedIn", "views": 3100, "likes": 265, "comments": 19},
        ],
        "as_of": datetime.utcnow().isoformat(),
    }


# ------------- ADK FUNCTION TOOLS -------------
# In this ADK version, FunctionTool takes ONLY the function as argument.


fetch_trends_tool = FunctionTool(fetch_trends)
publish_tool = FunctionTool(publish_or_schedule)
analytics_tool = FunctionTool(get_mock_analytics)
