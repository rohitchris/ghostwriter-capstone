import React, { useState, useEffect } from 'react';
import { BG_DARK } from '../constants/theme';
import { PRIMARY_BLUE_CLASS, ACCENT_EMERALD_CLASS } from '../constants/theme';
import { useAuth as useFirebase } from '../hooks/useAuth';
import { useMockScheduledPosts } from '../hooks/useMockScheduledPosts';
import { useMockSaveScheduledPost } from '../hooks/useMockSaveScheduledPost';
import { useContentGeneration } from '../hooks/useContentGeneration';
import { useImageSettings } from '../hooks/useImageSettings';
import CustomAlert from './CustomAlert';
import GeneratorHeader from './GeneratorHeader';
import MasterContentGenerator from './MasterContentGenerator';
import ContentOutput from './ContentOutput';
import ScheduledPostsDashboard from './ScheduledPostsDashboard';
import Footer from './Footer';

interface GeneratorProps {
  onSignOut?: () => void;
}

const Generator: React.FC<GeneratorProps> = ({ onSignOut }) => {
  const [currentView, setCurrentView] = useState<'generator' | 'dashboard'>('generator');
  const [alertMessage, setAlertMessage] = useState('');

  // Track which platforms have scheduled the CURRENT content
  const [scheduledPlatformsForCurrentContent, setScheduledPlatformsForCurrentContent] = useState<Set<string>>(new Set());

  // Hooks - Using mock Firebase
  const { db, userId, isAuthReady, error } = useFirebase();
  const scheduledPosts = useMockScheduledPosts(db, userId);
  const { saveScheduledPost } = useMockSaveScheduledPost(db, userId);
  const {
    topic,
    setTopic,
    tone,
    setTone,
    isGenerating,
    contentOutputs,
    generateContent: generateContentHook,
    clearContent,
  } = useContentGeneration();
  const {
    imageSettings,
    handleImageSettingChange,
    generateImage,
    isImageGenerationActive,
  } = useImageSettings();

  // Content state setters
  const [contentFacebook, setContentFacebook] = useState('');
  const [contentWordPress, setContentWordPress] = useState('');
  const [contentInstagram, setContentInstagram] = useState('');

  const setGlobalAlert = (message: string) => setAlertMessage(message);
  const handleCloseAlert = () => setAlertMessage('');

  const handleGenerateContent = async () => {
    try {
      // Clear previous content when regenerating
      clearContent();
      setContentFacebook('');
      setContentWordPress('');
      setContentInstagram('');
      
      // Reset scheduled status for all platforms when generating new content
      setScheduledPlatformsForCurrentContent(new Set());
      
      const message = await generateContentHook();
      // Update content outputs after generation
      setContentFacebook(contentOutputs.facebook || '');
      setContentWordPress(contentOutputs.wordpress || '');
      setContentInstagram(contentOutputs.instagram || '');
      setAlertMessage(message);
    } catch (error: any) {
      setAlertMessage(error.message);
    }
  };

  // Sync content outputs when they change
  useEffect(() => {
    if (contentOutputs.facebook) setContentFacebook(contentOutputs.facebook);
    if (contentOutputs.wordpress) setContentWordPress(contentOutputs.wordpress);
    if (contentOutputs.instagram) setContentInstagram(contentOutputs.instagram);
  }, [contentOutputs]);

  const handleSaveScheduledPost = async (
    platform: string,
    content: string,
    date: string,
    timeKey: string,
    imageUrl: string | null
  ) => {
    try {
      const result = await saveScheduledPost(platform, content, date, timeKey, imageUrl);
      
      // Mark this platform as scheduled for the current content
      setScheduledPlatformsForCurrentContent(prev => {
        const newSet = new Set(prev);
        newSet.add(platform.toLowerCase());
        return newSet;
      });
      
      setAlertMessage(result.message);
      setCurrentView('dashboard');
    } catch (error: any) {
      setAlertMessage(error.message);
    }
  };

  // Check if platforms are scheduled for CURRENT content
  const isFacebookScheduled = scheduledPlatformsForCurrentContent.has('facebook');
  const isWordPressScheduled = scheduledPlatformsForCurrentContent.has('wordpress');
  const isInstagramScheduled = scheduledPlatformsForCurrentContent.has('instagram');

  if (!isAuthReady) {
    return (
      <div className={`min-h-screen ${BG_DARK} flex items-center justify-center`}>
        <p className="text-xl text-blue-300">Initializing Content Engine...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`min-h-screen ${BG_DARK} flex items-center justify-center`}>
        <p className="text-xl text-red-400">{error}</p>
      </div>
    );
  }

  return (
    <div className={`min-h-screen ${BG_DARK}`}>
      <CustomAlert message={alertMessage} onClose={handleCloseAlert} />

      <GeneratorHeader
        userId={userId}
        currentView={currentView}
        scheduledPostsCount={scheduledPosts.length}
        onViewChange={setCurrentView}
        onSignOut={onSignOut}
      />

      {currentView === 'generator' && (
        <>
          <MasterContentGenerator
            topic={topic}
            tone={tone}
            isGenerating={isGenerating}
            onTopicChange={setTopic}
            onToneChange={setTone}
            onGenerate={handleGenerateContent}
          />

          <section className="py-20 px-4 md:px-8">
            <div className="max-w-7xl mx-auto">
              <h2 className="text-3xl font-bold text-center mb-12 text-white">
                2. Platform-Specific Refinement & Scheduling
              </h2>

              <div className="grid lg:grid-cols-3 gap-8">
                <ContentOutput 
                  title="Facebook"
                  content={contentFacebook}
                  setContent={setContentFacebook}
                  colorClass={PRIMARY_BLUE_CLASS}
                  platformKey="facebook"
                  setGlobalAlert={setGlobalAlert}
                  imageSettings={imageSettings.facebook}
                  handleImageSettingChange={handleImageSettingChange}
                  generateImage={generateImage}
                  saveScheduledPost={handleSaveScheduledPost}
                  isScheduled={isFacebookScheduled}
                />
                
                <ContentOutput 
                  title="WordPress"
                  content={contentWordPress}
                  setContent={setContentWordPress}
                  colorClass={ACCENT_EMERALD_CLASS}
                  platformKey="wordpress"
                  setGlobalAlert={setGlobalAlert}
                  imageSettings={imageSettings.wordpress}
                  handleImageSettingChange={handleImageSettingChange}
                  generateImage={generateImage}
                  saveScheduledPost={handleSaveScheduledPost}
                  isScheduled={isWordPressScheduled}
                />
                
                <ContentOutput 
                  title="Instagram"
                  content={contentInstagram}
                  setContent={setContentInstagram}
                  colorClass={PRIMARY_BLUE_CLASS}
                  platformKey="instagram"
                  setGlobalAlert={setGlobalAlert}
                  imageSettings={imageSettings.instagram}
                  handleImageSettingChange={handleImageSettingChange}
                  generateImage={generateImage}
                  saveScheduledPost={handleSaveScheduledPost}
                  isScheduled={isInstagramScheduled}
                />
              </div>
            </div>
          </section>
        </>
      )}

      {currentView === 'dashboard' && (
        <ScheduledPostsDashboard 
          posts={scheduledPosts} 
          userId={userId}
          onPostUpdated={() => {
            // Force refresh by re-fetching posts
            // The hook will automatically update due to polling
          }}
        />
      )}

      <Footer userId={userId} />
    </div>
  );
};

export default Generator;

