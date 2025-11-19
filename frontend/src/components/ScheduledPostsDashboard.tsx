import React from 'react';
import { ScheduledPost } from '../hooks/useScheduledPosts';

interface ScheduledPostsDashboardProps {
  posts: ScheduledPost[];
}

const ScheduledPostsDashboard: React.FC<ScheduledPostsDashboardProps> = ({ posts }) => {
  return (
    <section className="py-10 px-4 md:px-8">
      <div className="max-w-7xl mx-auto">
        <h2 className="text-3xl font-bold mb-8 text-white">Scheduled Posts Dashboard</h2>
        
        {posts.length === 0 ? (
          <div className="text-center p-12 rounded-xl bg-slate-800 text-slate-400 border-dashed border-2 border-slate-700">
            <p className="text-xl font-medium">No posts currently scheduled.</p>
            <p className="text-sm mt-2">Generate a draft and click 'Schedule Post' to see it here.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {posts.map(post => (
              <div key={post.id} className="p-5 rounded-xl bg-slate-800 shadow-lg border-l-4 border-emerald-500 flex justify-between items-center flex-wrap">
                <div className="flex-1 min-w-[300px]">
                  <p className="text-lg font-bold text-white">{post.platform} Post</p>
                  <p className="text-sm text-slate-400 truncate max-w-full">{post.content.substring(0, 100)}...</p>
                  {post.imageUrl && (
                    <div className="mt-2 flex items-center text-xs text-blue-400">
                      <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4.586-4.586a2 2 0 012.828 0L14 13.172l-1.586 1.586a2 2 0 01-2.828 0L8 12.828l-2.586 2.586zm4-10a1 1 0 00-1-1H4a1 1 0 00-1 1v1h14V5z" clipRule="evenodd"></path>
                      </svg>
                      Image included
                    </div>
                  )}
                </div>
                <div className="text-right mt-3 md:mt-0">
                  <p className="text-emerald-400 font-mono text-xl">
                    {new Date(post.dateTime).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: 'numeric' })}
                  </p>
                  <p className="text-xs text-slate-500 mt-1">Status: {post.status}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
};

export default ScheduledPostsDashboard;

