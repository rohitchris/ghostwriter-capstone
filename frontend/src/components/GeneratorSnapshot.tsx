import React from 'react';
import { BG_MEDIUM } from '../constants/theme';

const flowShots = [
  {
    title: 'Welcome / Sign In',
    image: 'landing-flow-3.png',
    description: 'Enter demo credentials to start the session. Authentication is mocked so the experience is instant.',
    caption: 'Seamless entry via the “Welcome Back” card.',
  },
  {
    title: 'Pick Platforms',
    image: 'landing-flow-2.png',
    description: 'Select Facebook, WordPress, or Instagram—each card highlights the promised outcome before you continue.',
    caption: 'Every platform is ready in one tap.',
  },
  {
    title: 'Generate Master Content',
    image: 'landing-flow-1.png',
    description: 'Type a topic, choose a tone, and tap the big green button. The backend agent fires on `/api/run-agent` immediately.',
    caption: 'Master prompt → multi-platform drafts.',
  },
  {
    title: 'Refine & Schedule',
    image: 'landing-flow-4.png',
    description: 'Fine-tune drafts, attach visuals, and schedule posts. They persist in `scheduled_posts/` while the UI shows a live dashboard.',
    caption: 'Refine with LLM, then hit “Schedule”.',
  },
];

const GeneratorSnapshot: React.FC = () => {
  return (
    <div className="max-w-6xl mx-auto">
      <div className={`${BG_MEDIUM} rounded-2xl p-6 shadow-2xl border border-slate-800 overflow-hidden space-y-6`}>
        <div>
          <p className="text-sm uppercase tracking-[0.3em] text-slate-400">New</p>
          <h2 className="text-3xl font-bold text-white mt-2">Ghostwriter Workflow Preview</h2>
          <p className="text-slate-300 mt-2 max-w-3xl">
            No mockups—just the actual journey that sells the simplicity: sign up, choose platforms, generate, refine, and schedule. Each step hits the backend so you can focus on ideas.
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {flowShots.map((shot) => (
            <div key={shot.title} className="rounded-3xl border border-blue-800 bg-slate-950/60 shadow-2xl overflow-hidden flex flex-col">
              <div className="h-60 w-full overflow-hidden bg-slate-900">
                <img
                  src={`/media/${shot.image}`}
                  alt={shot.title}
                  className="h-full w-full object-cover object-center"
                />
              </div>
              <div className="p-5 space-y-2">
                <div className="text-xs uppercase tracking-[0.2em] text-emerald-400">Step</div>
                <h3 className="text-xl font-semibold text-white">{shot.title}</h3>
                <p className="text-sm text-slate-300">{shot.description}</p>
                <p className="text-xs text-slate-500">{shot.caption}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default GeneratorSnapshot;

