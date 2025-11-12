'use client';

import clsx from 'clsx';
import { useEffect, useMemo, useRef, useState } from 'react';
import axios from 'axios';
import {
  AlertTriangle,
  HeartPulse,
  Mic,
  Phone,
  SendHorizonal,
  Settings,
  Sparkle,
  Menu,
  X,
} from 'lucide-react';
import ChatMessage, { type ChatMessageModel } from '../components/ChatMessage';
import LoadingSkeleton from '../components/LoadingSkeleton';
import ErrorCallout from '../components/ErrorCallout';
import ProfileCard from '../components/ProfileCard';
import { CalendarDays, Heart, MapPin, Stethoscope } from 'lucide-react';

type LangCode = 'en' | 'hi' | 'ta' | 'te' | 'kn' | 'ml';
type SexOption = 'male' | 'female' | 'other';

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE?.replace(/\/$/, '') ?? 'http://localhost:8000';

const LANGUAGE_OPTIONS: Array<{
  value: LangCode;
  label: string;
  speechLang: string;
  placeholder: string;
  introTitle: string;
  introSubtitle: string;
}> = [
  {
    value: 'en',
    label: 'English',
    speechLang: 'en-US',
    placeholder: 'Describe your symptoms or ask about first steps…',
    introTitle: 'How can I care for you today?',
    introSubtitle:
      'Ask about symptoms, self-care, or when it’s safest to see a clinician.',
  },
  {
    value: 'hi',
    label: 'हिन्दी',
    speechLang: 'hi-IN',
    placeholder: 'अपने लक्षण साझा करें या देखभाल के बारे में पूछें…',
    introTitle: 'आज मैं आपकी कैसे मदद कर सकता हूँ?',
    introSubtitle:
      'लक्षणों, घरेलू देखभाल या डॉक्टर से मिलने के सही समय के बारे में पूछें।',
  },
  {
    value: 'ta',
    label: 'தமிழ்',
    speechLang: 'ta-IN',
    placeholder: 'உங்கள் அறிகுறிகளை அல்லது வழிகாட்டலை பற்றி கேளுங்கள்…',
    introTitle: 'இன்று நான் எப்படி உதவலாம்?',
    introSubtitle:
      'அறிகுறிகள், சுய பராமரிப்பு அல்லது மருத்துவரை அணுக வேண்டிய நேரத்தை கேளுங்கள்.',
  },
  {
    value: 'te',
    label: 'తెలుగు',
    speechLang: 'te-IN',
    placeholder: 'మీ లక్షణాలు లేదా జాగ్రత్తల గురించి అడగండి…',
    introTitle: 'ఈ రోజు నేను ఎలా సహాయం చేయగలను?',
    introSubtitle:
      'లక్షణాలు, స్వీయ సంరక్షణ లేదా డాక్టర్‌ను ఎప్పుడు సంప్రదించాలో అడగండి.',
  },
  {
    value: 'kn',
    label: 'ಕನ್ನಡ',
    speechLang: 'kn-IN',
    placeholder: 'ನಿಮ್ಮ ಲಕ್ಷಣಗಳನ್ನು ಅಥವಾ ಆರೈಕೆಯನ್ನು ಕುರಿತು ಕೇಳಿ…',
    introTitle: 'ಇಂದು ನಾನು ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?',
    introSubtitle:
      'ಲಕ್ಷಣಗಳು, ಸ್ವ-ಆರೈಕೆ ಅಥವಾ ವೈದ್ಯರನ್ನು ಭೇಟಿಯಾಗುವ ಸಮಯವನ್ನು ಕುರಿತು ಕೇಳಿ.',
  },
  {
    value: 'ml',
    label: 'മലയാളം',
    speechLang: 'ml-IN',
    placeholder: 'ലക്ഷണങ്ങൾ പങ്കിടുക അല്ലെങ്കിൽ പരിപാലനത്തെക്കുറിച്ച് ചോദിക്കുക…',
    introTitle: 'ഇന്ന് നിങ്ങളെ എങ്ങനെ സഹായിക്കാം?',
    introSubtitle:
      'ലക്ഷണങ്ങൾ, സ്വയംപരിചരണം, ഡോക്ടറെ കാണേണ്ട ശരിയായ സമയം എന്നിവയെക്കുറിച്ച് ചോദിക്കുക.',
  },
];

const LANGUAGE_SPEECH_MAP: Record<LangCode, string> = LANGUAGE_OPTIONS.reduce(
  (acc, option) => {
    acc[option.value] = option.speechLang;
    return acc;
  },
  {} as Record<LangCode, string>
);

interface Profile {
  diabetes: boolean;
  hypertension: boolean;
  pregnancy: boolean;
  age?: number;
  sex?: SexOption;
  city?: string;
}

interface ChatEntry extends ChatMessageModel {
  facts?: any[];
  safety?: any;
}

const defaultProfile: Profile = {
  diabetes: false,
  hypertension: false,
  pregnancy: false,
  age: undefined,
  sex: undefined,
  city: '',
};

const initialAssistantMessage: ChatEntry = {
  id: 'assistant-welcome',
  role: 'assistant',
  content: `### Welcome to your Health Companion

I can help you understand mild to moderate symptoms, highlight red-flag warnings, and point you toward reliable self-care steps.

**Important:** I am not a substitute for a licensed clinician or emergency care.

Let me know what you’re experiencing, and we’ll take it one step at a time.`,
  timestamp: new Date().toISOString(),
};

const createId = () =>
  typeof crypto !== 'undefined' && 'randomUUID' in crypto
    ? crypto.randomUUID()
    : Math.random().toString(36).slice(2);

const formatTimestamp = () => new Date().toISOString();

export default function Home() {
  const [messages, setMessages] = useState<ChatEntry[]>([initialAssistantMessage]);
  const [inputValue, setInputValue] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lang, setLang] = useState<LangCode>('en');
  const [showProfile, setShowProfile] = useState(false);
  const [showPreferences, setShowPreferences] = useState(false);
  const [showSafety, setShowSafety] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [profile, setProfile] = useState<Profile>(defaultProfile);
  const [profileLoading, setProfileLoading] = useState(true);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  const currentLanguage =
    LANGUAGE_OPTIONS.find((option) => option.value === lang) ?? LANGUAGE_OPTIONS[0];

  useEffect(() => {
    const saved = localStorage.getItem('healthProfile');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setProfile({ ...defaultProfile, ...parsed });
      } catch (err) {
        console.warn('Unable to parse saved profile', err);
        setProfile(defaultProfile);
      }
    }
    setProfileLoading(false);
  }, []);

  useEffect(() => {
    localStorage.setItem('healthProfile', JSON.stringify(profile));
  }, [profile]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const profileStats = useMemo(() => {
    const chronicConditions = [
      profile.diabetes && 'Diabetes',
      profile.hypertension && 'Hypertension',
      profile.pregnancy && 'Pregnancy',
    ]
      .filter(Boolean)
      .join(', ');

    return [
      {
        label: 'Age',
        value: profile.age ? `${profile.age} years` : 'Not provided',
        icon: <CalendarDays className="h-4 w-4" aria-hidden />,
      },
      {
        label: 'Sex',
        value: profile.sex ? profile.sex : 'Not provided',
        icon: <Stethoscope className="h-4 w-4" aria-hidden />,
      },
      {
        label: 'Chronic',
        value: chronicConditions || 'No chronic conditions logged',
        highlights: chronicConditions ? chronicConditions.split(', ') : undefined,
        icon: <Heart className="h-4 w-4" aria-hidden />,
      },
      {
        label: 'City',
        value: profile.city && profile.city.trim().length > 0 ? profile.city : 'Not provided',
        icon: <MapPin className="h-4 w-4" aria-hidden />,
      },
    ];
  }, [profile]);

  const profileName = useMemo(() => {
    if (profile.city) {
      return `${profile.city} Resident`;
    }
    return 'Guest Member';
  }, [profile.city]);

  const avatarColor: 'teal' | 'mint' | 'blue' =
    profile.diabetes || profile.hypertension ? 'blue' : 'teal';

  const handleSend = async (overrides?: string) => {
    const messageText = (overrides ?? inputValue).trim();
    if (!messageText || isLoading) return;

    const userMessage: ChatEntry = {
      id: createId(),
      role: 'user',
      content: messageText,
      timestamp: formatTimestamp(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE}/chat`, {
        text: messageText,
        lang,
        profile,
      });

      const assistantMessage: ChatEntry = {
        id: createId(),
        role: 'assistant',
        content: response.data.answer,
        timestamp: formatTimestamp(),
        citations: response.data.citations,
        facts: response.data.facts,
        safety: response.data.safety,
      };

      setMessages((prev) => [...prev, assistantMessage]);

      if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(response.data.answer);
        utterance.lang = LANGUAGE_SPEECH_MAP[lang] ?? 'en-US';
        utterance.rate = 0.92;
        window.speechSynthesis.speak(utterance);
      }
    } catch (err) {
      console.error('Chat error', err);
      setError(
        'I had trouble connecting to my clinical sources. Please check your network and try again.'
      );
      setMessages((prev) => [
        ...prev,
        {
          id: createId(),
          role: 'assistant',
          content:
            'I’m sorry—something went wrong while retrieving information. Let’s try again in a few moments.',
          timestamp: formatTimestamp(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const startRecording = async () => {
    if (typeof navigator === 'undefined' || !navigator.mediaDevices) {
      setError('Microphone access is not available in this environment.');
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        stream.getTracks().forEach((track) => track.stop());
        await transcribeAudio(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error('Microphone error', err);
      setError('Could not access the microphone. Please check browser permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const transcribeAudio = async (audioBlob: Blob) => {
    try {
      const formData = new FormData();
      formData.append('file', audioBlob, 'voice-note.webm');

      const response = await axios.post(`${API_BASE}/stt`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      const text: string = response.data.text;
      if (text) {
        setInputValue(text);
        await handleSend(text);
      }
    } catch (err) {
      console.error('Transcription error', err);
      setError(
        'Speech recognition did not succeed. You can continue by typing your question.'
      );
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      void handleSend();
    }
  };

  const selectedPlaceholder = currentLanguage.placeholder;

  const handleOpenProfileModal = () => {
    setShowPreferences(false);
    setShowProfile(true);
  };

  const sidebarClasses = useMemo(
    () =>
      clsx(
        'fixed inset-y-0 left-0 z-40 flex w-72 flex-col gap-4 overflow-y-auto bg-white/95 p-6 shadow-2xl transition-transform duration-300 lg:relative lg:inset-auto lg:z-auto lg:w-64 lg:overflow-visible lg:bg-transparent lg:p-0 lg:shadow-none',
        isSidebarOpen
          ? 'translate-x-0 lg:flex lg:translate-x-0'
          : '-translate-x-full lg:hidden'
      ),
    [isSidebarOpen]
  );

  const layoutClasses = useMemo(
    () =>
      clsx(
        'mx-auto flex w-full max-w-6xl flex-col gap-10 lg:grid lg:items-start lg:gap-14',
        isSidebarOpen
          ? 'lg:grid-cols-[260px_minmax(0,1fr)]'
          : 'lg:grid-cols-[minmax(0,1fr)]'
      ),
    [isSidebarOpen]
  );

  useEffect(() => {
    const media = window.matchMedia('(min-width: 1024px)');
    const handleChange = () => setIsSidebarOpen(media.matches);
    handleChange();
    media.addEventListener('change', handleChange);
    return () => media.removeEventListener('change', handleChange);
  }, []);

  return (
    <div className="flex min-h-screen flex-col">
      <header className="relative overflow-hidden px-6 pb-8 pt-10 sm:px-10 lg:px-16">
        <div className="absolute inset-x-1/3 top-0 h-40 rounded-full bg-ocean-300/40 blur-3xl" />
        <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-ocean-200 to-transparent" />
        <div className="relative mx-auto flex w-full max-w-6xl items-center justify-between pb-4">
          <button
            type="button"
            onClick={() => setIsSidebarOpen((prev) => !prev)}
            className="inline-flex items-center gap-2 rounded-full border border-white/60 bg-white/80 px-3 py-2 text-sm font-semibold text-slate-600 shadow-sm transition hover:border-ocean-200 hover:bg-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ocean-200"
          >
            {isSidebarOpen ? (
              <X className="h-4 w-4" aria-hidden />
            ) : (
              <Menu className="h-4 w-4" aria-hidden />
            )}
            <span className="hidden sm:inline">
              {isSidebarOpen ? 'Hide panel' : 'Show panel'}
            </span>
            <span className="sr-only">Toggle sidebar</span>
          </button>
        </div>
        <div className="relative mx-auto flex w-full max-w-6xl flex-col gap-6 lg:items-start">
          <div className="flex-1 max-w-3xl space-y-3 text-left">
            <span className="inline-flex items-center gap-2 rounded-full bg-white/70 px-4 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-ocean-700 shadow-sm backdrop-blur animate-fadeUp">
              <Sparkle className="h-3.5 w-3.5" />
              Health Companion
            </span>
            <h1 className="text-3xl font-bold text-slate-900 sm:text-4xl lg:text-5xl">
              Compassionate guidance for everyday health questions
            </h1>
            <p className="max-w-2xl text-base text-slate-600 sm:text-lg">
              Receive calming, evidence-aligned direction on symptoms and self-care. Every
              answer includes safety guardrails, gentle language, and accessible
              formatting.
            </p>
          </div>
        </div>
      </header>

      {isSidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-slate-900/40 backdrop-blur-sm lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      <main className="flex-1 px-4 pb-12 sm:px-6 lg:px-16">
        <div className={layoutClasses}>
          <aside className={sidebarClasses} aria-label="Quick actions">
            <div className="mb-4 flex items-center justify-between lg:hidden">
              <h2 className="text-sm font-semibold text-slate-600">Quick actions</h2>
              <button
                type="button"
                onClick={() => setIsSidebarOpen(false)}
                className="inline-flex items-center justify-center rounded-full border border-slate-200 bg-white/80 p-1.5 text-slate-500 shadow-sm focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ocean-200"
                aria-label="Close quick actions"
              >
                <X className="h-4 w-4" />
              </button>
            </div>

            {error && (
              <ErrorCallout message={error} onDismiss={() => setError(null)} />
            )}

            <nav className="flex flex-col gap-3" aria-label="Secondary panels">
              <button
                type="button"
                onClick={() => setShowPreferences(true)}
                className="flex items-center justify-between rounded-2xl border border-white/60 bg-white/75 px-5 py-4 text-left shadow-lg transition hover:border-ocean-200 hover:shadow-xl focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ocean-200"
              >
                <span className="flex items-center gap-3 text-slate-700">
                  <Settings className="h-5 w-5 text-ocean-500" />
                  <span className="text-sm font-semibold leading-tight">
                    Session preferences
                  </span>
                </span>
                <span className="text-xs uppercase tracking-[0.3em] text-ocean-400">
                  Open
                </span>
              </button>

              <button
                type="button"
                onClick={() => setShowSafety(true)}
                className="flex items-center justify-between rounded-2xl border border-white/60 bg-white/75 px-5 py-4 text-left shadow-lg transition hover:border-mint-200 hover:shadow-xl focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-mint-200"
              >
                <span className="flex items-center gap-3 text-slate-700">
                  <HeartPulse className="h-5 w-5 text-mint-600" />
                  <span className="text-sm font-semibold leading-tight">
                    Safety guidance
                  </span>
                </span>
                <span className="text-xs uppercase tracking-[0.3em] text-mint-500">
                  Open
                </span>
              </button>
            </nav>
          </aside>

          <section
            className="flex h-[72vh] flex-col rounded-[30px] border border-white/60 bg-white/80 shadow-2xl shadow-ocean-100/40 backdrop-blur-md transition md:h-[74vh] lg:h-[76vh]"
            aria-label="Chat with health assistant"
          >
            <div className="flex items-center justify-between border-b border-white/70 bg-white/70 px-5 py-4 backdrop-blur-sm sm:px-7">
              <div>
                <h2 className="text-lg font-semibold text-slate-800 sm:text-xl">
                  Live care session
                </h2>
                <p className="text-xs font-medium uppercase tracking-[0.3em] text-ocean-500">
                  Not a substitute for emergency care
                </p>
              </div>
              <div className="flex items-center gap-2 rounded-full border border-ocean-100 bg-ocean-50 px-4 py-1 text-sm font-medium text-ocean-700 shadow-sm">
                <span className="flex h-2.5 w-2.5 animate-pulse rounded-full bg-mint-500" />
                Online
              </div>
            </div>

            <div className="flex-1 space-y-5 overflow-y-auto px-4 py-5 sm:px-6">
              <div className="mx-auto flex w-full flex-col gap-5 px-2 lg:max-w-3xl lg:px-4" role="list" aria-live="polite">
                {messages.length === 0 && (
                  <div className="flex justify-center pt-20">
                    <div className="max-w-lg rounded-3xl border border-white/70 bg-white/80 p-6 text-center shadow-lg">
                      <h3 className="text-xl font-semibold text-slate-800">
                        {currentLanguage.introTitle}
                      </h3>
                      <p className="mt-2 text-sm text-slate-600">
                        {currentLanguage.introSubtitle}
                      </p>
                    </div>
                  </div>
                )}

                {messages.map((message, index) => (
                  <div key={message.id} className="space-y-4">
                    <ChatMessage message={message} index={index} />

                    {message.safety?.red_flag && (
                      <div className="rounded-3xl border border-red-200/80 bg-red-50/70 p-5 text-red-800 shadow-lg shadow-red-100/50">
                        <div className="flex items-start gap-3">
                          <AlertTriangle className="h-6 w-6 flex-shrink-0 text-red-500" />
                          <div className="space-y-3">
                            <div>
                              <h3 className="flex items-center gap-2 text-base font-bold">
                                <span role="img" aria-hidden>
                                  ⚠️
                                </span>
                                Seek immediate medical care
                              </h3>
                              <p className="mt-1 text-sm text-red-700/90">
                                Your symptoms may signal an urgent concern. If you feel unsafe
                                right now, contact emergency services.
                              </p>
                            </div>
                            {message.facts
                              ?.find((fact: any) => fact.type === 'red_flags')
                              ?.data?.map((flag: any, idx: number) => (
                                <div
                                  key={`${flag.symptom}-${idx}`}
                                  className="rounded-2xl border border-red-200 bg-white/80 p-3 text-sm text-red-700"
                                >
                                  <strong>{flag.symptom}</strong>: {flag.conditions.join(', ')}
                                </div>
                              ))}
                            <button
                              onClick={() => window.open('tel:108')}
                              className="flex w-full items-center justify-center gap-2 rounded-2xl bg-red-600 px-4 py-2 font-semibold text-white shadow transition hover:bg-red-700 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-300"
                            >
                              <Phone className="h-4 w-4" />
                              Call Emergency (108)
                            </button>
                          </div>
                        </div>
                      </div>
                    )}

                    {message.facts && message.facts.length > 0 && !message.safety?.red_flag && (
                      <div className="rounded-3xl border border-ocean-100 bg-ocean-50/70 p-5 text-sm text-slate-700 shadow">
                        <h4 className="text-sm font-semibold uppercase tracking-[0.3em] text-ocean-600">
                          Additional insights
                        </h4>
                        <div className="mt-3 space-y-3">
                          {message.facts.map((fact: any, factIndex: number) => {
                            if (!fact?.data || fact.data.length === 0) return null;

                            if (fact.type === 'contraindications') {
                              return (
                                <div
                                  key={`fact-${fact.type}-${factIndex}`}
                                  className="rounded-2xl border border-red-100 bg-white/80 p-3"
                                >
                                  <p className="font-semibold text-red-700">
                                    Things to avoid for safety
                                  </p>
                                  <ul className="mt-2 space-y-1 text-sm">
                                    {fact.data.map((group: any, idx: number) => (
                                      <li key={`${group.condition}-${idx}`}>
                                        <strong>{group.condition}:</strong>{' '}
                                        {group.avoid.join(', ')}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              );
                            }

                            if (fact.type === 'safe_actions') {
                              return (
                                <div
                                  key={`fact-${fact.type}-${factIndex}`}
                                  className="rounded-2xl border border-mint-100 bg-white/80 p-3"
                                >
                                  <p className="font-semibold text-mint-700">
                                    Generally safe self-care ideas
                                  </p>
                                  <ul className="mt-2 space-y-1 text-sm">
                                    {fact.data.map((group: any, idx: number) => (
                                      <li key={`${group.condition}-${idx}`}>
                                        <strong>{group.condition}:</strong>{' '}
                                        {group.actions.join(', ')}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              );
                            }

                            if (fact.type === 'providers') {
                              return (
                                <div
                                  key={`fact-${fact.type}-${factIndex}`}
                                  className="rounded-2xl border border-ocean-100 bg-white/80 p-3"
                                >
                                  <p className="font-semibold text-ocean-700">
                                    Providers you might consider
                                  </p>
                                  <ul className="mt-2 space-y-1 text-sm">
                                    {fact.data.map((provider: any, idx: number) => (
                                      <li key={`${provider.provider}-${idx}`}>
                                        <strong>{provider.provider}</strong>
                                        {provider.mode ? ` • ${provider.mode}` : ''}
                                        {provider.phone ? ` – ${provider.phone}` : ''}
                                      </li>
                                    ))}
                                  </ul>
                                </div>
                              );
                            }

                            if (fact.type === 'mental_health_crisis') {
                              return (
                                <div
                                  key={`fact-${fact.type}-${factIndex}`}
                                  className="rounded-2xl border border-purple-200 bg-white/80 p-3"
                                >
                                  <p className="font-semibold text-purple-700">
                                    Mental health support steps
                                  </p>
                                  {fact.data.matched?.length > 0 && (
                                    <p className="mt-1 text-xs text-purple-600/80">
                                      Detected phrases: {fact.data.matched.join(', ')}
                                    </p>
                                  )}
                                  <ul className="mt-2 list-disc space-y-1 pl-5 text-sm">
                                    {fact.data.actions?.map((action: string, idx: number) => (
                                      <li key={`${action}-${idx}`}>{action}</li>
                                    ))}
                                  </ul>
                                </div>
                              );
                            }

                            if (fact.type === 'pregnancy_alert') {
                              return (
                                <div
                                  key={`fact-${fact.type}-${factIndex}`}
                                  className="rounded-2xl border border-pink-200 bg-white/80 p-3"
                                >
                                  <p className="font-semibold text-pink-700">
                                    Pregnancy-specific guidance
                                  </p>
                                  {fact.data.matched?.length > 0 && (
                                    <p className="mt-1 text-xs text-pink-600/80">
                                      Detected: {fact.data.matched.join(', ')}
                                    </p>
                                  )}
                                  <ul className="mt-2 list-disc space-y-1 pl-5 text-sm">
                                    {fact.data.guidance?.map((tip: string, idx: number) => (
                                      <li key={`${tip}-${idx}`}>{tip}</li>
                                    ))}
                                  </ul>
                                </div>
                              );
                            }

                            if (fact.type === 'personalization') {
                              return (
                                <div
                                  key={`fact-${fact.type}-${factIndex}`}
                                  className="rounded-2xl border border-yellow-200 bg-white/80 p-3"
                                >
                                  <p className="font-semibold text-yellow-700">
                                    Tailored notes
                                  </p>
                                  <ul className="mt-2 list-disc space-y-1 pl-5 text-sm">
                                    {fact.data.map((note: string, idx: number) => (
                                      <li key={`${note}-${idx}`}>{note}</li>
                                    ))}
                                  </ul>
                                </div>
                              );
                            }

                            return null;
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                ))}

                {isLoading && <LoadingSkeleton count={1} />}
              </div>
              <div ref={messagesEndRef} />
            </div>

            <form
              onSubmit={(event) => {
                event.preventDefault();
                void handleSend();
              }}
              className="border-t border-white/70 bg-white/60 px-4 py-4 sm:px-6"
              aria-label="Send a message"
            >
              <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-end lg:w-full lg:max-w-3xl lg:self-center">
                  <button
                    type="button"
                    onClick={isRecording ? stopRecording : startRecording}
                    className={`flex h-12 w-full items-center justify-center rounded-2xl border border-ocean-200 text-white shadow transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ocean-200 sm:w-12 ${
                      isRecording
                        ? 'animate-pulse bg-red-500 hover:bg-red-600'
                        : 'bg-ocean-500 hover:bg-ocean-600'
                    }`}
                    aria-pressed={isRecording}
                    aria-label={isRecording ? 'Stop recording' : 'Start voice recording'}
                  >
                    <Mic className="h-5 w-5" />
                  </button>
                  <div className="relative w-full flex-1">
                    <textarea
                      value={inputValue}
                      onChange={(event) => setInputValue(event.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder={selectedPlaceholder}
                      className="min-h-[110px] w-full resize-y rounded-3xl border border-ocean-100 bg-white/80 px-5 py-4 text-base leading-relaxed text-slate-700 shadow-sm transition focus:border-ocean-300 focus:outline-none focus:ring-4 focus:ring-ocean-200/60 sm:min-h-[90px]"
                      aria-label="Message input"
                      disabled={isLoading}
                    />
                    <span className="pointer-events-none absolute bottom-3 right-4 text-xs text-slate-400">
                      Shift + Enter for new line
                    </span>
                  </div>
                </div>
                <button
                  type="submit"
                  className="flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-ocean-500 via-ocean-400 to-mint-400 px-6 py-3 text-base font-semibold text-white shadow-lg shadow-ocean-400/30 transition hover:scale-[1.01] hover:shadow-ocean-500/30 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ocean-200 disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
                  disabled={inputValue.trim().length === 0 || isLoading}
                  aria-disabled={inputValue.trim().length === 0 || isLoading}
                >
                  <SendHorizonal className="h-5 w-5" />
                  Send
                </button>
              </div>
            </form>
          </section>
        </div>
      </main>

      {showPreferences && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 px-4 py-8 backdrop-blur-sm">
          <section
            className="relative w-full max-w-2xl rounded-3xl border border-white/60 bg-white/95 p-8 shadow-2xl"
            role="dialog"
            aria-modal="true"
            aria-label="Session preferences"
          >
            <button
              onClick={() => setShowPreferences(false)}
              className="absolute right-5 top-5 rounded-full border border-slate-200 px-2 py-1 text-xs font-semibold uppercase tracking-[0.3em] text-slate-500 transition hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ocean-200"
              aria-label="Close session preferences"
            >
              Close
            </button>
            <header>
              <h2 className="text-2xl font-bold text-slate-800">Session preferences</h2>
              <p className="mt-2 text-sm text-slate-600">
                Adjust how the assistant responds and update your health profile for more
                tailored guidance.
              </p>
            </header>

            <div className="mt-6 space-y-6">
              <ProfileCard
                loading={profileLoading}
                name={profileName}
                avatarColor={avatarColor}
                stats={profileStats}
                onEdit={handleOpenProfileModal}
              />

              <div className="space-y-3 rounded-2xl border border-ocean-100 bg-white/80 p-5 shadow-sm">
                <label
                  htmlFor="language-preferences"
                  className="text-xs font-semibold uppercase tracking-[0.3em] text-slate-400"
                >
                  Language
                </label>
                <select
                  id="language-preferences"
                  value={lang}
                  onChange={(event) => setLang(event.target.value as LangCode)}
                  className="rounded-2xl border border-ocean-100 bg-white px-4 py-2 text-sm text-slate-700 shadow focus:border-ocean-300 focus:outline-none focus:ring-4 focus:ring-ocean-200/40"
                >
                  {LANGUAGE_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-slate-500">
                  Switching the language updates the assistant’s replies and placeholder
                  prompts.
                </p>
                <button
                  onClick={handleOpenProfileModal}
                  className="rounded-2xl border border-ocean-100 px-4 py-2 text-sm font-semibold text-ocean-700 transition hover:bg-ocean-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ocean-200"
                >
                  Edit health profile
                </button>
              </div>
            </div>
          </section>
        </div>
      )}

      {showSafety && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 px-4 py-8 backdrop-blur-sm">
          <section
            className="relative w-full max-w-xl rounded-3xl border border-white/60 bg-white/95 p-8 shadow-2xl"
            role="dialog"
            aria-modal="true"
            aria-label="Safety guidance"
          >
            <button
              onClick={() => setShowSafety(false)}
              className="absolute right-5 top-5 rounded-full border border-slate-200 px-2 py-1 text-xs font-semibold uppercase tracking-[0.3em] text-slate-500 transition hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-mint-200"
              aria-label="Close safety guidance"
            >
              Close
            </button>
            <header className="flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-mint-100 text-mint-700">
                <HeartPulse className="h-5 w-5" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-slate-800">Emergency guidance</h2>
                <p className="text-xs uppercase tracking-[0.3em] text-slate-400">
                  Stay prepared
                </p>
              </div>
            </header>

            <div className="mt-6 space-y-4 text-sm leading-relaxed text-slate-600">
              <p>
                This assistant can highlight red flags, but it cannot diagnose or provide
                emergency care. Contact local services immediately if you notice:
              </p>
              <ul className="list-disc space-y-2 pl-5">
                <li>Chest pain, shortness of breath, or sudden weakness.</li>
                <li>Severe bleeding, confusion, or loss of consciousness.</li>
                <li>Worsening symptoms after self-care guidance.</li>
              </ul>
              <p className="rounded-2xl border border-mint-200 bg-mint-50/70 p-4 text-mint-800">
                Call your local emergency number (India: 108) or visit the nearest emergency
                department for urgent concerns.
              </p>
              <button
                onClick={() => window.open('tel:108')}
                className="flex w-full items-center justify-center gap-2 rounded-2xl bg-mint-500 px-4 py-2 font-semibold text-white shadow transition hover:bg-mint-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-mint-200"
              >
                <Phone className="h-4 w-4" />
                Call Emergency (108)
              </button>
            </div>
          </section>
        </div>
      )}

      {showProfile && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 px-4 py-8 backdrop-blur-sm">
          <div className="relative w-full max-w-lg rounded-3xl border border-white/60 bg-white/90 p-8 shadow-2xl">
            <button
              onClick={() => setShowProfile(false)}
              className="absolute right-5 top-5 rounded-full border border-slate-200 px-2 py-1 text-xs font-semibold uppercase tracking-[0.3em] text-slate-500 transition hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ocean-200"
              aria-label="Close profile modal"
            >
              Close
            </button>
            <h2 className="text-2xl font-bold text-slate-800">Health profile</h2>
            <p className="mt-2 text-sm text-slate-600">
              Update basic details so I can tailor contextual guidance. Your information
              stays on this device.
            </p>

            <div className="mt-6 space-y-4">
              <label className="flex items-center gap-3 rounded-2xl border border-ocean-100 bg-white/80 px-4 py-3 text-sm text-slate-700 shadow-sm transition hover:border-ocean-200">
                <input
                  type="checkbox"
                  checked={profile.diabetes}
                  onChange={(event) =>
                    setProfile((prev) => ({ ...prev, diabetes: event.target.checked }))
                  }
                  className="h-5 w-5 rounded border-ocean-200 text-ocean-500 focus:ring-ocean-300"
                />
                I have diabetes
              </label>

              <label className="flex items-center gap-3 rounded-2xl border border-ocean-100 bg-white/80 px-4 py-3 text-sm text-slate-700 shadow-sm transition hover:border-ocean-200">
                <input
                  type="checkbox"
                  checked={profile.hypertension}
                  onChange={(event) =>
                    setProfile((prev) => ({ ...prev, hypertension: event.target.checked }))
                  }
                  className="h-5 w-5 rounded border-ocean-200 text-ocean-500 focus:ring-ocean-300"
                />
                I have hypertension
              </label>

              {(profile.sex === 'female' || profile.sex === undefined || profile.sex === 'other') && (
                <label className="flex items-center gap-3 rounded-2xl border border-ocean-100 bg-white/80 px-4 py-3 text-sm text-slate-700 shadow-sm transition hover:border-ocean-200">
                  <input
                    type="checkbox"
                    checked={profile.pregnancy}
                    onChange={(event) =>
                      setProfile((prev) => ({ ...prev, pregnancy: event.target.checked }))
                    }
                    className="h-5 w-5 rounded border-ocean-200 text-ocean-500 focus:ring-ocean-300"
                  />
                  I am currently pregnant
                </label>
              )}

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <label className="space-y-2 text-sm text-slate-600">
                  <span className="block font-semibold text-slate-500">Age (years)</span>
                  <input
                    type="number"
                    min={0}
                    value={profile.age ?? ''}
                    onChange={(event) =>
                      setProfile((prev) => ({
                        ...prev,
                        age: event.target.value ? Number(event.target.value) : undefined,
                      }))
                    }
                    className="w-full rounded-2xl border border-ocean-100 bg-white/80 px-4 py-2 text-slate-700 shadow-sm focus:border-ocean-300 focus:outline-none focus:ring-4 focus:ring-ocean-200/50"
                  />
                </label>

                <label className="space-y-2 text-sm text-slate-600">
                  <span className="block font-semibold text-slate-500">Sex</span>
                  <select
                    value={profile.sex ?? ''}
                    onChange={(event) =>
                      setProfile((prev) => ({
                        ...prev,
                        sex: event.target.value
                          ? (event.target.value as SexOption)
                          : undefined,
                        pregnancy:
                          event.target.value === 'female' ? prev.pregnancy : false,
                      }))
                    }
                    className="w-full rounded-2xl border border-ocean-100 bg-white/80 px-4 py-2 text-slate-700 shadow-sm focus:border-ocean-300 focus:outline-none focus:ring-4 focus:ring-ocean-200/50"
                  >
                    <option value="">Select</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other / Prefer not to say</option>
                  </select>
                </label>
              </div>

              <label className="space-y-2 text-sm text-slate-600">
                <span className="block font-semibold text-slate-500">
                  City (optional)
                </span>
                <input
                  type="text"
                  value={profile.city ?? ''}
                  onChange={(event) =>
                    setProfile((prev) => ({ ...prev, city: event.target.value }))
                  }
                  placeholder="e.g., Mumbai"
                  className="w-full rounded-2xl border border-ocean-100 bg-white/80 px-4 py-2 text-slate-700 shadow-sm focus:border-ocean-300 focus:outline-none focus:ring-4 focus:ring-ocean-200/50"
                />
              </label>
            </div>

            <div className="mt-6 flex justify-end gap-3">
              <button
                onClick={() => setShowProfile(false)}
                className="rounded-2xl border border-slate-200 px-4 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-300"
              >
                Cancel
              </button>
              <button
                onClick={() => setShowProfile(false)}
                className="rounded-2xl bg-ocean-500 px-4 py-2 text-sm font-semibold text-white shadow hover:bg-ocean-600 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ocean-300"
              >
                Save profile
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

