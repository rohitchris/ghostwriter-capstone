import { useState } from 'react';

export interface ContentOutputs {
  master: string;
  facebook: string;
  wordpress: string;
  instagram: string;
}

export const useContentGeneration = () => {
  const [topic, setTopic] = useState<string>('');
  const [tone, setTone] = useState<string>('Informative and Professional');
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [contentOutputs, setContentOutputs] = useState<ContentOutputs>({
    master: '',
    facebook: '',
    wordpress: '',
    instagram: '',
  });

  const generateContent = async (): Promise<string> => {
    if (!topic.trim()) {
      console.error('[useContentGeneration] Error: Topic is empty');
      throw new Error('Please enter a topic to begin content generation.');
    }

    console.log('[useContentGeneration] Starting content generation...');
    console.log('[useContentGeneration] Input data:', {
      topic: topic,
      tone: tone
    });

    setIsGenerating(true);

    try {
      const requestBody = {
        topic: topic,
        tone: tone
      };

      console.log('[useContentGeneration] Sending request to /api/agents/run-full-cycle');
      console.log('[useContentGeneration] Request body:', JSON.stringify(requestBody, null, 2));

      // Call backend full orchestration agent endpoint
      const response = await fetch('/api/agents/run-full-cycle', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      console.log('[useContentGeneration] Response received:', {
        status: response.status,
        statusText: response.statusText,
        ok: response.ok,
        headers: Object.fromEntries(response.headers.entries())
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('[useContentGeneration] Response not OK:', {
          status: response.status,
          statusText: response.statusText,
          body: errorText
        });
        throw new Error(`Failed to generate content from backend: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      console.log('[useContentGeneration] Response data received:', {
        success: data.success,
        hasOutputs: !!data.outputs,
        hasResult: !!data.result,
        outputsKeys: data.outputs ? Object.keys(data.outputs) : null,
        outputsPreview: data.outputs ? {
          master: data.outputs.master?.substring(0, 100) + '...',
          facebook: data.outputs.facebook?.substring(0, 100) + '...',
          wordpress: data.outputs.wordpress?.substring(0, 100) + '...',
          instagram: data.outputs.instagram?.substring(0, 100) + '...',
        } : null,
        resultPreview: data.result ? data.result.substring(0, 200) + '...' : null
      });
      
      // Backend now returns structured outputs - use them directly
      if (data.outputs) {
        console.log('[useContentGeneration] Using structured outputs from backend');
        console.log('[useContentGeneration] Output lengths:', {
          master: data.outputs.master?.length || 0,
          facebook: data.outputs.facebook?.length || 0,
          wordpress: data.outputs.wordpress?.length || 0,
          instagram: data.outputs.instagram?.length || 0,
        });
        setContentOutputs(data.outputs);
      } else {
        // Fallback: if backend doesn't return structured outputs, log error
        console.error('[useContentGeneration] Backend did not return structured outputs');
        throw new Error('Backend did not return structured content outputs. Please check backend logs.');
      }

      setIsGenerating(false);
      console.log('[useContentGeneration] Content generation completed successfully');

      return `Content generated successfully for topic: "${topic}"! Now generate your visuals.`;
    } catch (error) {
      setIsGenerating(false);
      console.error('[useContentGeneration] Error during content generation:', error);
      if (error instanceof Error) {
        console.error('[useContentGeneration] Error message:', error.message);
        console.error('[useContentGeneration] Error stack:', error.stack);
      }
      throw error;
    }
  };

  const clearContent = () => {
    setContentOutputs({
      master: '',
      facebook: '',
      wordpress: '',
      instagram: '',
    });
  };

  return {
    topic,
    setTopic,
    tone,
    setTone,
    isGenerating,
    contentOutputs,
    generateContent,
    clearContent,
  };
};

