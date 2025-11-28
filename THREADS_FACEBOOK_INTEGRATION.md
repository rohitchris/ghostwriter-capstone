# Threads & Facebook API Integration

This document explains how to use the Threads and Facebook publishing features in the GhostWriter platform.

## Overview

The platform now supports publishing content to:
- **WordPress** (existing feature)
- **Threads** (Instagram Threads - NEW)
- **Facebook** (Pages and personal profiles - NEW)

## API Credentials

### Threads API
- **App ID**: `1393569372162716`
- **App Secret**: Configured in `.env` as `THREADS_APP_SECRET`
- **Access Token**: Required per-user (obtained through OAuth flow)

### Facebook API
- **App ID**: `1166650488940455`
- **App Secret**: Configured in `.env` as `FACEBOOK_APP_SECRET`
- **Access Token**: Required per-user (obtained through OAuth flow)

## Setup Instructions

### 1. Environment Configuration

Add the following to your `.env` file:

```env
# Threads API (Meta)
THREADS_APP_ID=1393569372162716
THREADS_APP_SECRET=your_threads_app_secret_here

# Facebook API (Meta)
FACEBOOK_APP_ID=1166650488940455
FACEBOOK_APP_SECRET=your_facebook_app_secret_here
```

### 2. Obtain User Access Tokens

#### For Threads:
1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Navigate to your app (App ID: 1393569372162716)
3. Use the Graph API Explorer to generate a Threads user access token
4. Required permissions: `threads_basic`, `threads_content_publish`

#### For Facebook:
1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Navigate to your app (App ID: 1166650488940455)
3. Use the Graph API Explorer to generate a user access token
4. Required permissions: `pages_manage_posts`, `pages_read_engagement`, `publish_to_groups`
5. For Page posting, you'll also need the Page ID and Page Access Token

## Usage

### Frontend - Scheduled Posts Dashboard

The `ScheduledPostsDashboard` component now includes publish buttons for all three platforms:

1. **WordPress**: Uses environment credentials (no token modal)
2. **Threads**: Prompts for user access token
3. **Facebook**: Prompts for user access token (and optionally page info)

When you click "Publish to Threads" or "Publish to Facebook":
- A modal appears asking for your access token
- Paste your token and click "Publish"
- The post is sent to the respective platform

### Backend API Endpoints

#### Publish to Threads
```
POST /api/scheduled-posts/publish-threads
Body: {
  "user_id": "string",
  "post_id": "string",
  "access_token": "string"
}
```

#### Publish to Facebook
```
POST /api/scheduled-posts/publish-facebook
Body: {
  "user_id": "string",
  "post_id": "string",
  "access_token": "string",
  "page_id": "optional_string",
  "page_access_token": "optional_string"
}
```

#### Check Connections
```
GET /api/check-threads?access_token=YOUR_TOKEN
GET /api/check-facebook?access_token=YOUR_TOKEN
GET /api/facebook-pages?access_token=YOUR_TOKEN
```

### AI Agent Publishing

The `publisher_agent` now supports all three platforms through the `publish_or_schedule` tool:

```python
{
  "items": [
    {
      "channel": "threads",
      "content": "Your post content",
      "access_token": "user_threads_token",
      "image_url": "optional_image_url"
    },
    {
      "channel": "facebook",
      "content": "Your post content",
      "access_token": "user_facebook_token",
      "page_id": "optional_page_id",
      "page_access_token": "optional_page_token",
      "image_url": "optional_image_url"
    }
  ]
}
```

## Helper Modules

### `helpers/threads_api.py`
- `ThreadsAPI` class for Threads integration
- `publish_to_threads()` - Publish text/image posts
- `check_threads_connection()` - Verify credentials

### `helpers/facebook_api.py`
- `FacebookAPI` class for Facebook integration
- `publish_to_facebook()` - Publish text/image/link posts
- `check_facebook_connection()` - Verify credentials
- `get_facebook_pages()` - List managed pages

## Features

### Threads Publishing
- ✅ Text posts
- ✅ Image posts (with URL)
- ✅ Connection verification
- ✅ Post status tracking
- ✅ Published post URLs

### Facebook Publishing
- ✅ Text posts
- ✅ Image posts (with URL)
- ✅ Link sharing
- ✅ Page posting (with Page ID/token)
- ✅ User feed posting
- ✅ Connection verification
- ✅ List managed pages
- ✅ Post status tracking
- ✅ Published post URLs

## Security Notes

1. **Never commit access tokens** to version control
2. **Use environment variables** for app secrets
3. **Access tokens expire** - implement refresh logic for production
4. **Use HTTPS** in production for token transmission
5. **Validate tokens** before publishing

## Testing

### Quick Test - Threads
```bash
curl -X POST http://localhost:8000/api/scheduled-posts/publish-threads \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "post_id": "post-123",
    "access_token": "YOUR_THREADS_TOKEN"
  }'
```

### Quick Test - Facebook
```bash
curl -X POST http://localhost:8000/api/scheduled-posts/publish-facebook \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "post_id": "post-123",
    "access_token": "YOUR_FACEBOOK_TOKEN"
  }'
```

## Troubleshooting

### "Access token required"
- Make sure you're providing a valid access token in the request
- Check that the token has not expired

### "Failed to create thread container"
- Verify your Threads token has `threads_content_publish` permission
- Check that the image URL is publicly accessible (if using images)

### "Facebook API error: Invalid OAuth access token"
- Verify your Facebook token is valid and not expired
- Check that the token has required permissions
- For Page posting, ensure you have a Page access token

### "Rate limit exceeded"
- Meta APIs have rate limits
- Implement exponential backoff for retries
- Consider queueing posts for gradual publishing

## Next Steps

1. **Implement OAuth Flow**: Add proper OAuth2 flow for token generation in the frontend
2. **Token Storage**: Store encrypted tokens in database for seamless re-use
3. **Refresh Tokens**: Implement automatic token refresh
4. **Scheduling**: Add time-based scheduling for Threads/Facebook posts
5. **Analytics**: Fetch post metrics after publishing
6. **Multi-Account**: Support multiple Threads/Facebook accounts per user

## References

- [Threads API Documentation](https://developers.facebook.com/docs/threads)
- [Facebook Graph API Documentation](https://developers.facebook.com/docs/graph-api)
- [Meta for Developers](https://developers.facebook.com/)

---

**Last Updated**: November 26, 2025
