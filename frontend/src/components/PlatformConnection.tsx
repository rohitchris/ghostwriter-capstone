import React, { useState } from 'react';
import { BG_DARK, BG_MEDIUM } from '../constants/theme';

export interface PlatformCredentials {
  facebook?: {
    accessToken: string;
    appId: string;
    appSecret: string;
  };
  wordpress?: {
    siteUrl: string;
    username: string;
    password: string;
  };
  instagram?: {
    accessToken: string;
    userId: string;
  };
}

interface PlatformConnectionProps {
  platform: 'facebook' | 'wordpress' | 'instagram';
  onConnect: (credentials: any) => Promise<void>;
  onCancel: () => void;
  existingCredentials?: any;
}

const PlatformConnection: React.FC<PlatformConnectionProps> = ({
  platform,
  onConnect,
  onCancel,
  existingCredentials,
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(!!existingCredentials);

  // WordPress form state
  const [wpSiteUrl, setWpSiteUrl] = useState(existingCredentials?.wordpress?.siteUrl || '');
  const [wpUsername, setWpUsername] = useState(existingCredentials?.wordpress?.username || '');
  const [wpPassword, setWpPassword] = useState(existingCredentials?.wordpress?.password || '');

  // Facebook form state
  const [fbAccessToken, setFbAccessToken] = useState(existingCredentials?.facebook?.accessToken || '');
  const [fbAppId, setFbAppId] = useState(existingCredentials?.facebook?.appId || '');
  const [fbAppSecret, setFbAppSecret] = useState(existingCredentials?.facebook?.appSecret || '');

  // Instagram form state
  const [igAccessToken, setIgAccessToken] = useState(existingCredentials?.instagram?.accessToken || '');
  const [igUserId, setIgUserId] = useState(existingCredentials?.instagram?.userId || '');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      let credentials: any = {};

      if (platform === 'wordpress') {
        if (!wpSiteUrl || !wpUsername || !wpPassword) {
          setError('Please fill in all WordPress fields');
          setIsLoading(false);
          return;
        }
        credentials = {
          wordpress: {
            siteUrl: wpSiteUrl.trim(),
            username: wpUsername.trim(),
            password: wpPassword,
          },
        };
      } else if (platform === 'facebook') {
        if (!fbAccessToken || !fbAppId || !fbAppSecret) {
          setError('Please fill in all Facebook fields');
          setIsLoading(false);
          return;
        }
        credentials = {
          facebook: {
            accessToken: fbAccessToken.trim(),
            appId: fbAppId.trim(),
            appSecret: fbAppSecret.trim(),
          },
        };
      } else if (platform === 'instagram') {
        if (!igAccessToken || !igUserId) {
          setError('Please fill in all Instagram fields');
          setIsLoading(false);
          return;
        }
        credentials = {
          instagram: {
            accessToken: igAccessToken.trim(),
            userId: igUserId.trim(),
          },
        };
      }

      // Mock API call to verify credentials
      await verifyPlatformCredentials(platform, credentials);
      
      // Save credentials
      await onConnect(credentials);
      setIsConnected(true);
    } catch (err: any) {
      setError(err.message || 'Failed to connect. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  const verifyPlatformCredentials = async (platform: string, credentials: any): Promise<void> => {
    // Mock API call - simulate network delay
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Mock verification - in real app, this would call the backend
    if (platform === 'wordpress') {
      // Mock WordPress verification
      const response = await fetch('/api/platforms/wordpress/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          site_url: credentials.wordpress.siteUrl,
          username: credentials.wordpress.username,
          password: credentials.wordpress.password,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'WordPress authentication failed');
      }
    } else if (platform === 'facebook') {
      // Mock Facebook verification
      const response = await fetch('/api/platforms/facebook/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          access_token: credentials.facebook.accessToken,
          app_id: credentials.facebook.appId,
          app_secret: credentials.facebook.appSecret,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Facebook authentication failed');
      }
    } else if (platform === 'instagram') {
      // Mock Instagram verification
      const response = await fetch('/api/platforms/instagram/verify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          access_token: credentials.instagram.accessToken,
          user_id: credentials.instagram.userId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Instagram authentication failed');
      }
    }
  };

  const handleDisconnect = async () => {
    setIsLoading(true);
    try {
      await onConnect(null); // Pass null to disconnect
      setIsConnected(false);
      // Reset form fields
      setWpSiteUrl('');
      setWpUsername('');
      setWpPassword('');
      setFbAccessToken('');
      setFbAppId('');
      setFbAppSecret('');
      setIgAccessToken('');
      setIgUserId('');
    } catch (err: any) {
      setError(err.message || 'Failed to disconnect');
    } finally {
      setIsLoading(false);
    }
  };

  const platformInfo = {
    wordpress: {
      name: 'WordPress',
      icon: (
        <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2zm0 18c-4.411 0-8-3.589-8-8s3.589-8 8-8 8 3.589 8 8-3.589 8-8 8zM9.5 7.5C9.5 6.67 8.83 6 8 6S6.5 6.67 6.5 7.5 7.17 9 8 9s1.5-.67 1.5-1.5zM16 17c-2.45 0-4.52-1.75-4.9-4.05L11.5 12c.38-2.3 2.45-4.05 4.9-4.05 2.53 0 4.58 2.05 4.58 4.58S18.53 17 16 17z"/>
        </svg>
      ),
      description: 'Connect your WordPress site to publish blog posts',
    },
    facebook: {
      name: 'Facebook',
      icon: (
        <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
          <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
        </svg>
      ),
      description: 'Connect your Facebook account to publish posts',
    },
    instagram: {
      name: 'Instagram',
      icon: (
        <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm0-13a5 5 0 100 10 5 5 0 000-10zm0 8a3 3 0 110-6 3 3 0 010 6zm6.5-7.5a1.5 1.5 0 100-3 1.5 1.5 0 000 3z"/>
        </svg>
      ),
      description: 'Connect your Instagram account to publish posts',
    },
  };

  const info = platformInfo[platform];

  return (
    <div className={`${BG_DARK} rounded-xl p-6 border border-blue-600/50`}>
      <div className="flex items-center mb-6">
        <div className="text-blue-400 mr-4">{info.icon}</div>
        <div>
          <h3 className="text-2xl font-bold text-white">{info.name}</h3>
          <p className="text-slate-400 text-sm">{info.description}</p>
        </div>
      </div>

      {isConnected && existingCredentials && (
        <div className="mb-6 p-4 bg-emerald-900/30 border border-emerald-600/50 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-emerald-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span className="text-emerald-400 font-semibold">Connected</span>
            </div>
            <button
              onClick={handleDisconnect}
              disabled={isLoading}
              className="px-4 py-2 text-sm font-semibold rounded-lg bg-red-600 text-white hover:bg-red-700 transition disabled:opacity-50"
            >
              Disconnect
            </button>
          </div>
        </div>
      )}

      {error && (
        <div className="mb-6 p-4 bg-red-900/30 border border-red-600/50 rounded-lg text-red-300 text-sm">
          {error}
        </div>
      )}

      {!isConnected && (
        <form onSubmit={handleSubmit} className="space-y-4">
          {platform === 'wordpress' && (
            <>
              <div>
                <label htmlFor="wp-site-url" className="block text-sm font-medium text-slate-300 mb-2">
                  WordPress Site URL *
                </label>
                <input
                  id="wp-site-url"
                  type="url"
                  value={wpSiteUrl}
                  onChange={(e) => setWpSiteUrl(e.target.value)}
                  placeholder="https://yoursite.com"
                  className={`w-full px-4 py-3 ${BG_MEDIUM} border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
                  required
                  disabled={isLoading}
                />
                <p className="mt-1 text-xs text-slate-500">Your WordPress site URL (e.g., https://yoursite.com)</p>
              </div>

              <div>
                <label htmlFor="wp-username" className="block text-sm font-medium text-slate-300 mb-2">
                  WordPress Username *
                </label>
                <input
                  id="wp-username"
                  type="text"
                  value={wpUsername}
                  onChange={(e) => setWpUsername(e.target.value)}
                  placeholder="your-username"
                  className={`w-full px-4 py-3 ${BG_MEDIUM} border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
                  required
                  disabled={isLoading}
                />
                <p className="mt-1 text-xs text-slate-500">Your WordPress username</p>
              </div>

              <div>
                <label htmlFor="wp-password" className="block text-sm font-medium text-slate-300 mb-2">
                  Application Password *
                </label>
                <input
                  id="wp-password"
                  type="password"
                  value={wpPassword}
                  onChange={(e) => setWpPassword(e.target.value)}
                  placeholder="••••••••"
                  className={`w-full px-4 py-3 ${BG_MEDIUM} border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
                  required
                  disabled={isLoading}
                />
                <p className="mt-1 text-xs text-slate-500">
                  WordPress Application Password (not your regular password). 
                  <a href="https://wordpress.org/support/article/application-passwords/" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline ml-1">
                    Learn more
                  </a>
                </p>
              </div>
            </>
          )}

          {platform === 'facebook' && (
            <>
              <div>
                <label htmlFor="fb-access-token" className="block text-sm font-medium text-slate-300 mb-2">
                  Access Token *
                </label>
                <input
                  id="fb-access-token"
                  type="text"
                  value={fbAccessToken}
                  onChange={(e) => setFbAccessToken(e.target.value)}
                  placeholder="EAABwzLix..."
                  className={`w-full px-4 py-3 ${BG_MEDIUM} border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
                  required
                  disabled={isLoading}
                />
                <p className="mt-1 text-xs text-slate-500">Facebook Graph API Access Token</p>
              </div>

              <div>
                <label htmlFor="fb-app-id" className="block text-sm font-medium text-slate-300 mb-2">
                  App ID *
                </label>
                <input
                  id="fb-app-id"
                  type="text"
                  value={fbAppId}
                  onChange={(e) => setFbAppId(e.target.value)}
                  placeholder="1234567890123456"
                  className={`w-full px-4 py-3 ${BG_MEDIUM} border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
                  required
                  disabled={isLoading}
                />
                <p className="mt-1 text-xs text-slate-500">Your Facebook App ID</p>
              </div>

              <div>
                <label htmlFor="fb-app-secret" className="block text-sm font-medium text-slate-300 mb-2">
                  App Secret *
                </label>
                <input
                  id="fb-app-secret"
                  type="password"
                  value={fbAppSecret}
                  onChange={(e) => setFbAppSecret(e.target.value)}
                  placeholder="••••••••"
                  className={`w-full px-4 py-3 ${BG_MEDIUM} border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
                  required
                  disabled={isLoading}
                />
                <p className="mt-1 text-xs text-slate-500">Your Facebook App Secret</p>
              </div>
            </>
          )}

          {platform === 'instagram' && (
            <>
              <div>
                <label htmlFor="ig-access-token" className="block text-sm font-medium text-slate-300 mb-2">
                  Access Token *
                </label>
                <input
                  id="ig-access-token"
                  type="text"
                  value={igAccessToken}
                  onChange={(e) => setIgAccessToken(e.target.value)}
                  placeholder="IGQWRN..."
                  className={`w-full px-4 py-3 ${BG_MEDIUM} border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
                  required
                  disabled={isLoading}
                />
                <p className="mt-1 text-xs text-slate-500">Instagram Graph API Access Token</p>
              </div>

              <div>
                <label htmlFor="ig-user-id" className="block text-sm font-medium text-slate-300 mb-2">
                  User ID *
                </label>
                <input
                  id="ig-user-id"
                  type="text"
                  value={igUserId}
                  onChange={(e) => setIgUserId(e.target.value)}
                  placeholder="17841405309211844"
                  className={`w-full px-4 py-3 ${BG_MEDIUM} border border-slate-600 rounded-lg text-white placeholder-slate-500 focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
                  required
                  disabled={isLoading}
                />
                <p className="mt-1 text-xs text-slate-500">Your Instagram Business Account User ID</p>
              </div>
            </>
          )}

          <div className="flex gap-4 pt-4">
            <button
              type="button"
              onClick={onCancel}
              disabled={isLoading}
              className={`flex-1 px-6 py-3 rounded-lg font-semibold transition ${
                isLoading
                  ? 'bg-slate-600 text-slate-400 cursor-not-allowed'
                  : 'bg-slate-700 text-white hover:bg-slate-600'
              }`}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className={`flex-1 px-6 py-3 rounded-lg font-semibold transition ${
                isLoading
                  ? 'bg-slate-600 text-slate-400 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700 shadow-lg shadow-blue-500/30'
              }`}
            >
              {isLoading ? 'Connecting...' : 'Connect'}
            </button>
          </div>
        </form>
      )}
    </div>
  );
};

export default PlatformConnection;

