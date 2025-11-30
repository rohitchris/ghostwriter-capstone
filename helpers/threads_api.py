"""
Threads API Integration Module
Handles posting content to Threads (Instagram Threads) using the Meta Graph API.
"""
import requests
import os
from typing import Dict, Optional, Any
from datetime import datetime


class ThreadsAPI:
    """Client for interacting with the Threads API."""
    
    def __init__(self, app_id: str = None, app_secret: str = None, access_token: str = None):
        """
        Initialize Threads API client.
        
        Args:
            app_id: Threads App ID (defaults to env var THREADS_APP_ID)
            app_secret: Threads App Secret (defaults to env var THREADS_APP_SECRET)
            access_token: User access token (required for posting)
        """
        self.app_id = app_id or os.getenv("THREADS_APP_ID")
        self.app_secret = app_secret or os.getenv("THREADS_APP_SECRET")
        self.access_token = access_token
        self.base_url = "https://graph.threads.net/v1.0"
        
    def check_connection(self) -> Dict[str, Any]:
        """
        Check if Threads API credentials are valid.
        
        Returns:
            Dict with success status and message
        """
        if not self.app_id or not self.app_secret:
            return {
                "success": False,
                "message": "Threads API credentials not configured"
            }
        
        if not self.access_token:
            return {
                "success": False,
                "message": "User access token required. Please authenticate with Threads."
            }
        
        try:
            # Verify token by getting user info
            response = requests.get(
                f"{self.base_url}/me",
                params={"access_token": self.access_token},
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return {
                    "success": True,
                    "message": f"Connected to Threads as {user_data.get('username', 'Unknown')}",
                    "user_id": user_data.get("id"),
                    "username": user_data.get("username")
                }
            else:
                return {
                    "success": False,
                    "message": f"Threads API error: {response.json().get('error', {}).get('message', 'Unknown error')}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Connection error: {str(e)}"
            }
    
    def create_post(
        self,
        text: str,
        media_url: Optional[str] = None,
        media_type: str = "TEXT"
    ) -> Dict[str, Any]:
        """
        Create a post on Threads.
        
        Args:
            text: The text content of the post
            media_url: Optional URL to image/video
            media_type: Type of media (TEXT, IMAGE, VIDEO)
            
        Returns:
            Dict with success status, post ID, and message
        """
        if not self.access_token:
            return {
                "success": False,
                "message": "User access token required. Please authenticate with Threads."
            }
        
        try:
            # Step 1: Create media container
            user_id = self._get_user_id()
            if not user_id:
                return {
                    "success": False,
                    "message": "Failed to get user ID"
                }
            
            container_data = {
                "media_type": media_type,
                "text": text,
                "access_token": self.access_token
            }
            
            if media_url and media_type != "TEXT":
                if media_type == "IMAGE":
                    container_data["image_url"] = media_url
                elif media_type == "VIDEO":
                    container_data["video_url"] = media_url
            
            # Create container
            container_response = requests.post(
                f"{self.base_url}/{user_id}/threads",
                data=container_data,
                timeout=30
            )
            
            if container_response.status_code != 200:
                error_msg = container_response.json().get("error", {}).get("message", "Unknown error")
                return {
                    "success": False,
                    "message": f"Failed to create thread container: {error_msg}"
                }
            
            container_id = container_response.json().get("id")
            
            # Step 2: Publish the thread
            publish_response = requests.post(
                f"{self.base_url}/{user_id}/threads_publish",
                data={
                    "creation_id": container_id,
                    "access_token": self.access_token
                },
                timeout=30
            )
            
            if publish_response.status_code == 200:
                thread_id = publish_response.json().get("id")
                return {
                    "success": True,
                    "message": "Successfully posted to Threads",
                    "thread_id": thread_id,
                    "url": f"https://www.threads.net/t/{thread_id}"
                }
            else:
                error_msg = publish_response.json().get("error", {}).get("message", "Unknown error")
                return {
                    "success": False,
                    "message": f"Failed to publish thread: {error_msg}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Unexpected error: {str(e)}"
            }
    
    def _get_user_id(self) -> Optional[str]:
        """Get the user ID from the access token."""
        try:
            response = requests.get(
                f"{self.base_url}/me",
                params={"access_token": self.access_token},
                timeout=10
            )
            if response.status_code == 200:
                return response.json().get("id")
        except:
            pass
        return None


def publish_to_threads(
    text: str,
    access_token: str,
    media_url: Optional[str] = None,
    media_type: str = "TEXT"
) -> Dict[str, Any]:
    """
    Convenience function to publish content to Threads.
    
    Args:
        text: The text content
        access_token: User's Threads access token
        media_url: Optional media URL
        media_type: TEXT, IMAGE, or VIDEO
        
    Returns:
        Dict with success status and details
    """
    client = ThreadsAPI(access_token=access_token)
    return client.create_post(text=text, media_url=media_url, media_type=media_type)


def check_threads_connection(access_token: str) -> Dict[str, Any]:
    """
    Check Threads API connection.
    
    Args:
        access_token: User's Threads access token
        
    Returns:
        Dict with connection status
    """
    client = ThreadsAPI(access_token=access_token)
    return client.check_connection()
