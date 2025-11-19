import { useCallback } from 'react';
import { ScheduledPost } from './useScheduledPosts';

/**
 * Mock hook for saving scheduled posts - stores in localStorage instead of Firestore
 */
export const useMockSaveScheduledPost = (db: any, userId: string | null) => {
  const saveScheduledPost = useCallback(async (
    platform: string, 
    content: string, 
    date: string, 
    timeKey: string, 
    imageUrl: string | null
  ) => {
    if (!userId) {
      throw new Error("Error: User not authenticated. Cannot save post.");
    }
    
    const [h, m] = timeKey.split(':');
    const timeFormatted = `${h.padStart(2, '0')}:${m}`;
    const dateTime = `${date}T${timeFormatted}:00`;
    
    // Generate a mock ID
    const postId = `mock-post-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    
    const newPost: ScheduledPost = {
      id: postId,
      platform,
      content,
      dateTime,
      status: 'Scheduled',
      imageUrl: imageUrl || null,
      createdAt: new Date().toISOString(),
    };

    try {
      // Load existing posts
      const stored = localStorage.getItem(`mock_scheduled_posts_${userId}`);
      const existingPosts: ScheduledPost[] = stored ? JSON.parse(stored) : [];
      
      // Add new post
      existingPosts.push(newPost);
      
      // Save back to localStorage
      localStorage.setItem(`mock_scheduled_posts_${userId}`, JSON.stringify(existingPosts));
      
      return { 
        success: true, 
        message: `Post for ${platform} successfully scheduled! View on Dashboard.` 
      };
    } catch (error: any) {
      console.error("Error saving mock post:", error);
      throw new Error(`Failed to schedule post: ${error.message}`);
    }
  }, [userId]);

  return { saveScheduledPost };
};

