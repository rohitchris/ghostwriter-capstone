"""
Facebook API Integration Module
Handles posting content to Facebook Pages using the Meta Graph API.
"""
import requests
import os
from typing import Dict, Optional, Any, List


class FacebookAPI:
    """Client for interacting with the Facebook Graph API."""
    
    def __init__(self, app_id: str = None, app_secret: str = None, access_token: str = None):
        """
        Initialize Facebook API client.
        
        Args:
            app_id: Facebook App ID (defaults to env var FACEBOOK_APP_ID)
            app_secret: Facebook App Secret (defaults to env var FACEBOOK_APP_SECRET)
            access_token: Page or user access token (required for posting)
        """
        self.app_id = app_id or os.getenv("FACEBOOK_APP_ID")
        self.app_secret = app_secret or os.getenv("FACEBOOK_APP_SECRET")
        self.access_token = access_token
        self.base_url = "https://graph.facebook.com/v18.0"
        
    def check_connection(self) -> Dict[str, Any]:
        """
        Check if Facebook API credentials are valid.
        
        Returns:
            Dict with success status and message
        """
        if not self.app_id or not self.app_secret:
            return {
                "success": False,
                "message": "Facebook API credentials not configured"
            }
        
        if not self.access_token:
            return {
                "success": False,
                "message": "Access token required. Please authenticate with Facebook."
            }
        
        try:
            # Verify token and get page/user info
            response = requests.get(
                f"{self.base_url}/me",
                params={
                    "access_token": self.access_token,
                    "fields": "id,name"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "message": f"Connected to Facebook as {data.get('name', 'Unknown')}",
                    "id": data.get("id"),
                    "name": data.get("name")
                }
            else:
                error = response.json().get("error", {})
                return {
                    "success": False,
                    "message": f"Facebook API error: {error.get('message', 'Unknown error')}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Connection error: {str(e)}"
            }
    
    def get_pages(self) -> Dict[str, Any]:
        """
        Get list of pages managed by the user.
        
        Returns:
            Dict with success status and list of pages
        """
        if not self.access_token:
            return {
                "success": False,
                "message": "Access token required"
            }
        
        try:
            response = requests.get(
                f"{self.base_url}/me/accounts",
                params={
                    "access_token": self.access_token,
                    "fields": "id,name,access_token"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                pages = data.get("data", [])
                return {
                    "success": True,
                    "pages": pages,
                    "message": f"Found {len(pages)} page(s)"
                }
            else:
                error = response.json().get("error", {})
                return {
                    "success": False,
                    "message": f"Failed to get pages: {error.get('message', 'Unknown error')}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Network error: {str(e)}"
            }
    
    def create_post(
        self,
        message: str,
        page_id: Optional[str] = None,
        page_access_token: Optional[str] = None,
        link: Optional[str] = None,
        image_url: Optional[str] = None,
        published: bool = True
    ) -> Dict[str, Any]:
        """
        Create a post on Facebook Page.
        
        Args:
            message: The text content of the post
            page_id: Facebook Page ID (if None, posts to user's feed)
            page_access_token: Page-specific access token
            link: Optional link to share
            image_url: Optional image URL
            published: Whether to publish immediately (True) or save as draft (False)
            
        Returns:
            Dict with success status, post ID, and URL
        """
        token = page_access_token or self.access_token
        
        if not token:
            return {
                "success": False,
                "message": "Access token required"
            }
        
        # Determine endpoint (page or user feed)
        endpoint = f"{self.base_url}/{page_id}/feed" if page_id else f"{self.base_url}/me/feed"
        
        try:
            post_data = {
                "message": message,
                "access_token": token,
                "published": str(published).lower()
            }
            
            if link:
                post_data["link"] = link
            
            # Handle image posting
            if image_url:
                # For images, use photos endpoint
                photo_endpoint = f"{self.base_url}/{page_id}/photos" if page_id else f"{self.base_url}/me/photos"
                photo_data = {
                    "url": image_url,
                    "caption": message,
                    "access_token": token,
                    "published": str(published).lower()
                }
                
                response = requests.post(
                    photo_endpoint,
                    data=photo_data,
                    timeout=30
                )
            else:
                # Regular post
                response = requests.post(
                    endpoint,
                    data=post_data,
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                post_id = result.get("id", "")
                
                # Construct URL
                if page_id and "_" in post_id:
                    page_id_part, post_id_part = post_id.split("_")
                    post_url = f"https://www.facebook.com/{page_id_part}/posts/{post_id_part}"
                else:
                    post_url = f"https://www.facebook.com/{post_id.replace('_', '/posts/')}"
                
                return {
                    "success": True,
                    "message": "Successfully posted to Facebook",
                    "post_id": post_id,
                    "url": post_url
                }
            else:
                error = response.json().get("error", {})
                return {
                    "success": False,
                    "message": f"Failed to create post: {error.get('message', 'Unknown error')}",
                    "error_code": error.get("code"),
                    "error_type": error.get("type")
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
    
    def delete_post(self, post_id: str) -> Dict[str, Any]:
        """
        Delete a Facebook post.
        
        Args:
            post_id: The ID of the post to delete
            
        Returns:
            Dict with success status
        """
        if not self.access_token:
            return {
                "success": False,
                "message": "Access token required"
            }
        
        try:
            response = requests.delete(
                f"{self.base_url}/{post_id}",
                params={"access_token": self.access_token},
                timeout=10
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Post deleted successfully"
                }
            else:
                error = response.json().get("error", {})
                return {
                    "success": False,
                    "message": f"Failed to delete post: {error.get('message', 'Unknown error')}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "message": f"Network error: {str(e)}"
            }


def publish_to_facebook(
    message: str,
    access_token: str,
    page_id: Optional[str] = None,
    page_access_token: Optional[str] = None,
    link: Optional[str] = None,
    image_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to publish content to Facebook.
    
    Args:
        message: The post message
        access_token: User access token
        page_id: Optional page ID to post to
        page_access_token: Optional page-specific token
        link: Optional link to share
        image_url: Optional image URL
        
    Returns:
        Dict with success status and details
    """
    client = FacebookAPI(access_token=access_token)
    return client.create_post(
        message=message,
        page_id=page_id,
        page_access_token=page_access_token,
        link=link,
        image_url=image_url
    )


def check_facebook_connection(access_token: str) -> Dict[str, Any]:
    """
    Check Facebook API connection.
    
    Args:
        access_token: User or page access token
        
    Returns:
        Dict with connection status
    """
    client = FacebookAPI(access_token=access_token)
    return client.check_connection()


def get_facebook_pages(access_token: str) -> Dict[str, Any]:
    """
    Get list of Facebook pages managed by the user.
    
    Args:
        access_token: User access token
        
    Returns:
        Dict with list of pages
    """
    client = FacebookAPI(access_token=access_token)
    return client.get_pages()
