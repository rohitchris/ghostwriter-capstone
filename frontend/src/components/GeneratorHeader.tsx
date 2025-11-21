import React from 'react';
import { useNavigate } from 'react-router-dom';

interface GeneratorHeaderProps {
  userId: string | null;
  currentView: 'generator' | 'dashboard';
  scheduledPostsCount: number;
  onViewChange: (view: 'generator' | 'dashboard') => void;
  onSignOut?: () => void;
}

const GeneratorHeader: React.FC<GeneratorHeaderProps> = ({
  userId,
  currentView,
  scheduledPostsCount,
  onViewChange,
  onSignOut,
}) => {
  const navigate = useNavigate();

  const handleSignOut = async () => {
    if (onSignOut) {
      await onSignOut();
      navigate('/');
    }
  };

  return (
    <header className="p-4 md:p-6 bg-slate-900 border-b border-blue-900/50">
      <div className="max-w-7xl mx-auto flex justify-between items-center">
        <div className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">
          Ghostwriter
        </div>
        <div className="flex items-center space-x-4">
          <p className="text-sm font-mono text-slate-500 hidden sm:block">
            User ID: <span className="text-blue-400 font-semibold">{userId || 'N/A'}</span>
          </p>
          <button
            onClick={() => navigate('/platforms')}
            className="px-4 py-2 text-sm font-semibold rounded-lg bg-slate-700 text-slate-300 hover:bg-slate-600 transition flex items-center gap-2"
            title="Manage Platforms"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            Platforms
          </button>
          <button
            onClick={() => onViewChange('generator')}
            className={`px-4 py-2 text-sm font-semibold rounded-lg transition ${
              currentView === 'generator' 
                ? 'bg-blue-600 text-white' 
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            Generator
          </button>
          <button
            onClick={() => onViewChange('dashboard')}
            className={`px-4 py-2 text-sm font-semibold rounded-lg transition ${
              currentView === 'dashboard' 
                ? 'bg-emerald-600 text-white' 
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
            }`}
          >
            Scheduled Posts ({scheduledPostsCount})
          </button>
          {onSignOut && (
            <button
              onClick={handleSignOut}
              className="px-4 py-2 text-sm font-semibold rounded-lg bg-red-600 text-white hover:bg-red-700 transition"
            >
              Sign Out
            </button>
          )}
        </div>
      </div>
    </header>
  );
};

export default GeneratorHeader;

