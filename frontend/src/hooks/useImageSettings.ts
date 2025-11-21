import { useState } from 'react';
import { IMAGE_STYLES } from '../constants/generator';

export interface ImageSettings {
  facebook: PlatformImageSettings;
  wordpress: PlatformImageSettings;
  instagram: PlatformImageSettings;
}

export interface PlatformImageSettings {
  mode: 'GENERATE' | 'UPLOAD' | 'NONE';
  style: string;
  imageDataUrl: string | null;
  generatedUrl: string | null;
}

const initialImageSettings: ImageSettings = {
  facebook: { mode: 'NONE', style: IMAGE_STYLES[0].value, imageDataUrl: null, generatedUrl: null },
  wordpress: { mode: 'NONE', style: IMAGE_STYLES[1].value, imageDataUrl: null, generatedUrl: null },
  instagram: { mode: 'NONE', style: IMAGE_STYLES[2].value, imageDataUrl: null, generatedUrl: null },
};

export const useImageSettings = () => {
  const [imageSettings, setImageSettings] = useState<ImageSettings>(initialImageSettings);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);

  const handleImageSettingChange = (platform: keyof ImageSettings, field: string, value: any) => {
    setImageSettings(prev => ({
      ...prev,
      [platform]: {
        ...prev[platform],
        [field]: value
      }
    }));
  };

  const generateImage = async (
    platform: 'facebook' | 'wordpress' | 'instagram',
    content: string
  ) => {
    const settings = imageSettings[platform];
    if (settings.mode !== 'GENERATE') {
      return;
    }

    if (!content.trim()) {
      throw new Error('Content is required to generate an image');
    }

    setIsGenerating(true);
    try {
      const response = await fetch('/api/generate-image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: content,
          platform: platform,
          style: settings.style,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate image');
      }

      const data = await response.json();
      
      // Handle image response - can be URL or base64 data
      let imageUrl = null;
      
      if (data.url || data.image_url) {
        imageUrl = data.url || data.image_url;
      } else if (data.image_data) {
        const imageFormat = data.metadata?.format || 'png';
        imageUrl = `data:image/${imageFormat};base64,${data.image_data}`;
      }
      
      setImageSettings(prev => ({
        ...prev,
        [platform]: {
          ...prev[platform],
          generatedUrl: imageUrl,
        }
      }));

      setIsGenerating(false);
      return data;
    } catch (error) {
      setIsGenerating(false);
      throw error;
    }
  };

  const isImageGenerationActive = ['facebook', 'wordpress', 'instagram'].some(
    p => imageSettings[p as keyof ImageSettings]?.mode === 'GENERATE'
  );

  return {
    imageSettings,
    handleImageSettingChange,
    generateImage,
    isGenerating,
    isImageGenerationActive,
  };
};

