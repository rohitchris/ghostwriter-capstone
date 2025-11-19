import { useState } from 'react';
import { IMAGE_STYLES, ASPECT_RATIOS } from '../constants/generator';

export interface ImageSettings {
  prompt: string;
  linkedin: PlatformImageSettings;
  wordpress: PlatformImageSettings;
  instagram: PlatformImageSettings;
}

export interface PlatformImageSettings {
  mode: 'GENERATE' | 'UPLOAD' | 'NONE';
  style: string;
  imageDataUrl: string | null;
  generatedUrl: string | null;
  aspectRatio: string;
}

const initialImageSettings: ImageSettings = {
  prompt: '',
  linkedin: { mode: 'NONE', style: IMAGE_STYLES[0].value, imageDataUrl: null, generatedUrl: null, aspectRatio: '2:1' },
  wordpress: { mode: 'NONE', style: IMAGE_STYLES[1].value, imageDataUrl: null, generatedUrl: null, aspectRatio: '16:9' },
  instagram: { mode: 'NONE', style: IMAGE_STYLES[2].value, imageDataUrl: null, generatedUrl: null, aspectRatio: '1:1' },
};

export const useImageSettings = () => {
  const [imageSettings, setImageSettings] = useState<ImageSettings>(initialImageSettings);

  const handleImageSettingChange = (platform: keyof ImageSettings, field: string, value: any) => {
    if (platform === 'prompt') {
      setImageSettings(prev => ({ ...prev, prompt: value }));
    } else {
      setImageSettings(prev => ({
        ...prev,
        [platform]: {
          ...prev[platform],
          [field]: value
        }
      }));
    }
  };

  const isImageGenerationActive = ['linkedin', 'wordpress', 'instagram'].some(
    p => imageSettings[p as keyof ImageSettings]?.mode === 'GENERATE'
  );

  return {
    imageSettings,
    handleImageSettingChange,
    isImageGenerationActive,
  };
};

