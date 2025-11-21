import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BG_DARK, BG_MEDIUM } from '../constants/theme';
import PlatformConnection, { PlatformCredentials } from './PlatformConnection';

interface Platform {
  key: string;
  name: string;
  icon: JSX.Element;
  description: string;
  color: string;
}

const platforms: Platform[] = [
  {
    key: 'facebook',
    name: 'Facebook',
    icon: (
      <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
        <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
      </svg>
    ),
    description: 'Share posts and engage with your audience',
    color: 'blue',
  },
  {
    key: 'wordpress',
    name: 'WordPress',
    icon: (
      <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2zm0 18c-4.411 0-8-3.589-8-8s3.589-8 8-8 8 3.589 8 8-3.589 8-8 8zM9.5 7.5C9.5 6.67 8.83 6 8 6S6.5 6.67 6.5 7.5 7.17 9 8 9s1.5-.67 1.5-1.5zM16 17c-2.45 0-4.52-1.75-4.9-4.05L11.5 12c.38-2.3 2.45-4.05 4.9-4.05 2.53 0 4.58 2.05 4.58 4.58S18.53 17 16 17z"/>
      </svg>
    ),
    description: 'Publish long-form articles and blog posts',
    color: 'emerald',
  },
  {
    key: 'instagram',
    name: 'Instagram',
    icon: (
      <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-13a5 5 0 100 10 5 5 0 000-10zm0 8a3 3 0 110-6 3 3 0 010 6zm6.5-7.5a1.5 1.5 0 100-3 1.5 1.5 0 000 3z"/>
      </svg>
    ),
    description: 'Create visual content and stories',
    color: 'purple',
  },
];

interface PlatformSelectionProps {
  onComplete: (platforms: string[]) => Promise<void>;
  onConnectPlatform: (credentials: PlatformCredentials | null) => Promise<void>;
  initialPlatforms?: string[];
  initialCredentials?: PlatformCredentials;
  isSetup?: boolean; // If true, this is initial setup after signup
}

const PlatformSelection: React.FC<PlatformSelectionProps> = ({ 
  onComplete, 
  onConnectPlatform,
  initialPlatforms = [],
  initialCredentials = {},
  isSetup = false 
}) => {
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>(initialPlatforms);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [connectingPlatform, setConnectingPlatform] = useState<string | null>(null);
  const [credentials, setCredentials] = useState<PlatformCredentials>(initialCredentials);
  const navigate = useNavigate();

  const togglePlatform = (platformKey: string) => {
    setSelectedPlatforms(prev => {
      if (prev.includes(platformKey)) {
        return prev.filter(p => p !== platformKey);
      } else {
        return [...prev, platformKey];
      }
    });
    setError(null);
  };

  const handleConnectPlatform = async (platformKey: string, newCredentials: PlatformCredentials | null) => {
    try {
      // Merge credentials
      const updatedCredentials: PlatformCredentials = {
        ...credentials,
        ...newCredentials,
      };
      
      // If disconnecting (null), remove that platform's credentials
      if (!newCredentials) {
        if (platformKey === 'facebook') {
          delete updatedCredentials.facebook;
        } else if (platformKey === 'wordpress') {
          delete updatedCredentials.wordpress;
        } else if (platformKey === 'instagram') {
          delete updatedCredentials.instagram;
        }
      }

      await onConnectPlatform(updatedCredentials);
      setCredentials(updatedCredentials);
      setConnectingPlatform(null);
    } catch (err: any) {
      setError(err.message || 'Failed to save connection');
      throw err;
    }
  };

  const isPlatformConnected = (platformKey: string): boolean => {
    if (platformKey === 'facebook') return !!credentials.facebook;
    if (platformKey === 'wordpress') return !!credentials.wordpress;
    if (platformKey === 'instagram') return !!credentials.instagram;
    return false;
  };

  const handleContinue = async () => {
    if (selectedPlatforms.length === 0) {
      setError('Please select at least one platform to continue');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      await onComplete(selectedPlatforms);
      if (isSetup) {
        navigate('/generator');
      } else {
        navigate('/generator');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to save platform selection');
    } finally {
      setIsLoading(false);
    }
  };

  const getColorClasses = (color: string, isSelected: boolean) => {
    const baseClasses = 'border-2 transition-all duration-200 cursor-pointer';
    if (isSelected) {
      switch (color) {
        case 'blue':
          return `${baseClasses} border-blue-500 bg-blue-500/20 shadow-lg shadow-blue-500/30`;
        case 'emerald':
          return `${baseClasses} border-emerald-500 bg-emerald-500/20 shadow-lg shadow-emerald-500/30`;
        case 'purple':
          return `${baseClasses} border-purple-500 bg-purple-500/20 shadow-lg shadow-purple-500/30`;
        default:
          return `${baseClasses} border-blue-500 bg-blue-500/20`;
      }
    }
    return `${baseClasses} border-slate-600 hover:border-slate-500`;
  };

  return (
    <div className={`min-h-screen ${BG_DARK} flex items-center justify-center px-4 py-12`}>
      <div className={`w-full max-w-4xl p-8 rounded-2xl ${BG_MEDIUM} border border-emerald-600/50 shadow-2xl`}>
        <div className="text-center mb-8">
          <h2 className="text-3xl md:text-4xl font-bold mb-4 text-white">
            {isSetup ? 'Select Your Platforms' : 'Manage Your Platforms'}
          </h2>
          <p className="text-slate-400 text-lg">
            {isSetup 
              ? 'Choose which platforms you want to use for content creation and scheduling'
              : 'Select or deselect platforms to customize your content workflow'
            }
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-900/30 border border-red-600/50 rounded-lg text-red-300 text-sm">
            {error}
          </div>
        )}

        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {platforms.map((platform) => {
            const isSelected = selectedPlatforms.includes(platform.key);
            const isConnected = isPlatformConnected(platform.key);
            const isConnecting = connectingPlatform === platform.key;
            
            return (
              <div key={platform.key}>
                <div
                  onClick={() => {
                    if (!isConnecting) {
                      togglePlatform(platform.key);
                    }
                  }}
                  className={`${getColorClasses(platform.color, isSelected)} ${BG_DARK} rounded-xl p-6 flex flex-col items-center text-center cursor-pointer`}
                >
                  <div className={`mb-4 ${isSelected ? 'text-white' : 'text-slate-400'}`}>
                    {platform.icon}
                  </div>
                  <h3 className={`text-xl font-bold mb-2 ${isSelected ? 'text-white' : 'text-slate-300'}`}>
                    {platform.name}
                  </h3>
                  <p className={`text-sm ${isSelected ? 'text-slate-300' : 'text-slate-500'}`}>
                    {platform.description}
                  </p>
                  <div className="mt-4 flex flex-col gap-2 w-full">
                    {isSelected && (
                      <div className="px-3 py-1 bg-emerald-500 text-white text-xs font-semibold rounded-full">
                        Selected
                      </div>
                    )}
                    {isSelected && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setConnectingPlatform(platform.key);
                        }}
                        className={`px-4 py-2 text-xs font-semibold rounded-lg transition ${
                          isConnected
                            ? 'bg-blue-600 text-white hover:bg-blue-700'
                            : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                        }`}
                      >
                        {isConnected ? 'Manage Connection' : 'Connect Account'}
                      </button>
                    )}
                    {isConnected && (
                      <div className="flex items-center justify-center text-emerald-400 text-xs">
                        <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                        Connected
                      </div>
                    )}
                  </div>
                </div>
                
                {isConnecting && (
                  <div className="mt-4">
                    <PlatformConnection
                      platform={platform.key as 'facebook' | 'wordpress' | 'instagram'}
                      onConnect={(creds) => handleConnectPlatform(platform.key, creds)}
                      onCancel={() => setConnectingPlatform(null)}
                      existingCredentials={credentials}
                    />
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          {!isSetup && (
            <button
              onClick={() => navigate('/generator')}
              disabled={isLoading}
              className={`px-6 py-3 rounded-lg font-semibold transition ${
                isLoading
                  ? 'bg-slate-600 text-slate-400 cursor-not-allowed'
                  : 'bg-slate-700 text-white hover:bg-slate-600'
              }`}
            >
              Cancel
            </button>
          )}
          <button
            onClick={handleContinue}
            disabled={isLoading || selectedPlatforms.length === 0}
            className={`px-8 py-3 rounded-lg font-semibold transition ${
              isLoading || selectedPlatforms.length === 0
                ? 'bg-slate-600 text-slate-400 cursor-not-allowed'
                : 'bg-emerald-600 text-white hover:bg-emerald-700 shadow-lg shadow-emerald-500/30'
            }`}
          >
            {isLoading ? 'Saving...' : isSetup ? 'Continue to Generator' : 'Save Changes'}
          </button>
        </div>

        {selectedPlatforms.length === 0 && (
          <p className="text-center text-slate-500 text-sm mt-4">
            Select at least one platform to continue
          </p>
        )}
      </div>
    </div>
  );
};

export default PlatformSelection;

