import { useState, useEffect } from 'react';
import { ScheduledPost } from './useScheduledPosts';

/**
 * Mock hook for scheduled posts - stores in localStorage instead of Firestore
 */
export const useMockScheduledPosts = (db: any, userId: string | null) => {
  const [scheduledPosts, setScheduledPosts] = useState<ScheduledPost[]>([]);

  useEffect(() => {
    if (!userId) {
      setScheduledPosts([]);
      return;
    }

    // Load from localStorage
    const loadPosts = () => {
      const stored = localStorage.getItem(`mock_scheduled_posts_${userId}`);
      if (stored) {
        try {
          const posts = JSON.parse(stored);
          setScheduledPosts(posts.sort((a: ScheduledPost, b: ScheduledPost) => 
            new Date(a.dateTime).getTime() - new Date(b.dateTime).getTime()
          ));
        } catch (e) {
          console.error('Error loading mock posts:', e);
          setScheduledPosts([]);
        }
      } else {
        setScheduledPosts([]);
      }
    };

    loadPosts();

    // Simulate real-time updates by checking localStorage periodically
    const interval = setInterval(loadPosts, 1000);

    return () => clearInterval(interval);
  }, [userId]);

  return scheduledPosts;
};

