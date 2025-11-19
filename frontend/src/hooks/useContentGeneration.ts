import { useState } from 'react';

export interface ContentOutputs {
  master: string;
  linkedin: string;
  wordpress: string;
  instagram: string;
}

export const useContentGeneration = () => {
  const [topic, setTopic] = useState<string>('');
  const [tone, setTone] = useState<string>('Informative and Professional');
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [contentOutputs, setContentOutputs] = useState<ContentOutputs>({
    master: '',
    linkedin: '',
    wordpress: '',
    instagram: '',
  });

  const generateContent = async (): Promise<string> => {
    if (!topic.trim()) {
      throw new Error('Please enter a topic to begin content generation.');
    }

    setIsGenerating(true);

    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Simulate Text Generation
    const masterDraft = `## The Future of ${topic} in a Digital World\n\nIn today's rapidly evolving landscape, the role of ${topic} has never been more critical. The shift towards digital consumption, amplified by AI and high-speed networks, demands a nuanced and adaptable approach.\n\n### Key Insight: Tone is King\nThe requested tone, '${tone}', is essential for resonating with the target audience. This long-form draft provides foundational paragraphs suitable for deep diving into the subject matter. It's ready for platform-specific tailoring and deployment.\n\n---\n\n**Actionable Takeaway:** We must leverage data-driven insights to maintain editorial consistency. The Ghostwriter platform guarantees style adherence across all channels.\n\n*Keywords: ${topic}, Content Strategy, Digital Transformation, ${tone}*`;

    const linkedInDraft = `💡 Key Takeaway: The digital revolution makes ${topic} more vital than ever. Leveraging a '${tone}' approach, we ensure our content maintains credibility and authority online. Are you ready for AI-driven content consistency?\n\n#${topic.replace(/\s/g, '')} #ContentStrategy #AI #DigitalMarketing`;
    
    const wordPressDraft = `<h1>The Definitive Guide to ${topic} Mastery</h1>\n\n<p>This comprehensive guide delves into the specifics of navigating the ${topic} landscape. Given the '${tone}' requirement, we focus on factual, actionable advice.</p>\n\n<p>Use this detailed draft as the body for your next pillar content piece.</p>`;

    const instagramDraft = `🔥 Trending Topic: ${topic}! The digital landscape demands a '${tone}' voice to stand out. We've got the draft that keeps your brand authoritative and consistent. Check out the link in bio for the full story!\n\n#${topic.split(' ')[0]} #AIAssisted #ContentGoals`;

    const outputs: ContentOutputs = {
      master: masterDraft,
      linkedin: linkedInDraft,
      wordpress: wordPressDraft,
      instagram: instagramDraft,
    };

    setContentOutputs(outputs);
    setIsGenerating(false);

    return `Master Drafts processed successfully for topic: "${topic}"! Now generate your visuals.`;
  };

  const clearContent = () => {
    setContentOutputs({
      master: '',
      linkedin: '',
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

