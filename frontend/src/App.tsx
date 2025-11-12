import { useEffect, useMemo, useRef, useState } from 'react';
import { Sparkle, SendHorizonal, HeartPulse } from 'lucide-react';
import ChatMessage, { type Message } from './components/ChatMessage';
import LoadingSkeleton from './components/LoadingSkeleton';
import ErrorCallout from './components/ErrorCallout';
import ProfileCard from './components/ProfileCard';
import { sendMockMessage } from './utils/mockChat';

const initialAssistantMessage: Message = {
  id: 'assistant-welcome',
  role: 'assistant',
  content: `### How can I help today?

I'm your AI health companion. Ask me about symptoms, self-care tips, or when to seek in-person care. I can share:

- Guidance based on reputable clinical sources
- Clear red-flag warnings
- Personalized suggestions informed by your profile

> Always contact a medical professional for emergencies.`,
  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
};

const initialMessages: Message[] = [initialAssistantMessage];

const defaultProfile = {
  name: 'Alex Morgan',
  avatarColor: 'teal',
  stats: [
    { label: 'Primary language', value: 'English' },
    { label: 'Preferred style', value: 'Detailed guidance' },
    { label: 'Allergies', value: 'None logged' },
    { label: 'Last check-in', value: '2 days ago' },
  ],
};

function App() {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [inputValue, setInputValue] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [profileLoading, setProfileLoading] = useState(true);

  const chatEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    const timeout = window.setTimeout(() => setProfileLoading(false), 1200);
    return () => window.clearTimeout(timeout);
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSending]);

  const canSend = useMemo(
    () => inputValue.trim().length > 0 && !isSending,
    [inputValue, isSending]
  );

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    const text = inputValue.trim();

    if (!text || isSending) return;

    const timestamp = new Date().toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    });

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: text,
      timestamp,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsSending(true);
    setError(null);

    try {
      const assistantResponse = await sendMockMessage(text);

      setMessages((prev) => [
        ...prev,
        {
          id: crypto.randomUUID(),
          ...assistantResponse,
        },
      ]);
    } catch (err) {
      const fallbackMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content:
          'I had trouble connecting to my knowledge sources. Please try again in a moment.',
        timestamp: new Date().toLocaleTimeString([], {
          hour: '2-digit',
          minute: '2-digit',
        }),
      };
      setMessages((prev) => [...prev, fallbackMessage]);
      setError(err instanceof Error ? err.message : 'Unexpected error occurred.');
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col">
      <header className="relative overflow-hidden px-6 pb-8 pt-10 sm:px-10 lg:px-16">
        <div className="absolute inset-x-1/3 top-0 h-40 rounded-full bg-ocean-300/40 blur-3xl" />
        <div className="absolute inset-x-0 bottom-0 h-px bg-gradient-to-r from-transparent via-ocean-200 to-transparent" />
        <div className="relative mx-auto flex w-full max-w-6xl flex-col gap-6 lg:flex-row lg:items-end">
          <div className="flex-1 space-y-3">
            <span className="inline-flex items-center gap-2 rounded-full bg-white/70 px-4 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-ocean-700 shadow-sm backdrop-blur">
              <Sparkle className="h-3.5 w-3.5" />
              Health Companion
            </span>
            <h1 className="text-3xl font-bold text-slate-900 sm:text-4xl lg:text-5xl">
              Compassionate guidance for everyday health questions
            </h1>
            <p className="max-w-2xl text-base text-slate-600 sm:text-lg">
              Get clear, conversational answers grounded in reliable medical resources.
              Designed with safety guardrails, calming UI, and responsive feedback.
            </p>
          </div>
          <div className="max-w-sm lg:w-80">
            <ProfileCard
              loading={profileLoading}
              profile={defaultProfile}
              onEdit={() => setError('Profile editing is coming soon in the next milestone.')}
            />
          </div>
        </div>
      </header>

      <main className="flex-1 px-4 pb-10 sm:px-6 lg:px-16">
        <div className="mx-auto grid w-full max-w-6xl gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
          <section
            className="flex h-[70vh] flex-col rounded-[30px] border border-white/60 bg-white/80 shadow-2xl shadow-ocean-100/40 backdrop-blur-md transition md:h-[72vh] lg:h-[75vh]"
            aria-label="Chat with health assistant"
          >
            <div className="flex items-center justify-between border-b border-white/70 bg-white/70 px-5 py-4 backdrop-blur-sm sm:px-7">
              <div>
                <h2 className="text-lg font-semibold text-slate-800 sm:text-xl">
                  Live Care Session
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
              <div className="flex flex-col gap-5" role="list" aria-live="polite">
                {messages.map((message, index) => (
                  <ChatMessage key={message.id} message={message} index={index} />
                ))}

                {isSending && <LoadingSkeleton count={1} />}
              </div>
              <div ref={chatEndRef} />
            </div>

            <form
              onSubmit={handleSubmit}
              className="border-t border-white/70 bg-white/60 px-4 py-4 sm:px-6"
              aria-label="Send a message"
            >
              <div className="flex flex-col gap-4 sm:flex-row sm:items-end">
                <div className="relative flex-1">
                  <textarea
                    value={inputValue}
                    onChange={(event) => setInputValue(event.target.value)}
                    placeholder="Describe your symptoms or ask for guidance..."
                    className="min-h-[110px] w-full resize-y rounded-3xl border border-ocean-100 bg-white/80 px-5 py-4 text-base leading-relaxed text-slate-700 shadow-sm transition focus:border-ocean-300 focus:outline-none focus:ring-4 focus:ring-ocean-200/60 sm:min-h-[90px]"
                    aria-label="Message input"
                  />
                  <span className="pointer-events-none absolute bottom-3 right-5 text-xs text-slate-400">
                    Shift + Enter for new line
                  </span>
                </div>
                <button
                  type="submit"
                  className="flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-ocean-500 via-ocean-400 to-mint-400 px-6 py-3 text-base font-semibold text-white shadow-lg shadow-ocean-400/30 transition hover:scale-[1.01] hover:shadow-ocean-500/30 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ocean-200 disabled:cursor-not-allowed disabled:opacity-50"
                  disabled={!canSend}
                  aria-disabled={!canSend}
                >
                  <SendHorizonal className="h-5 w-5" />
                  Send
                </button>
              </div>
            </form>
          </section>

          <aside className="flex flex-col gap-5" aria-label="Session updates">
            {error && <ErrorCallout message={error} onDismiss={() => setError(null)} />}
            <div className="rounded-2xl border border-white/60 bg-white/70 p-6 shadow-lg backdrop-blur">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-mint-100 text-mint-700">
                  <HeartPulse className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-600">
                    Quick safety reminder
                  </p>
                  <p className="text-xs uppercase tracking-[0.3em] text-slate-400">
                    Emergency
                  </p>
                </div>
              </div>
              <p className="mt-4 text-sm leading-relaxed text-slate-600">
                If you experience chest pain, difficulty breathing, severe bleeding, or
                new confusion, call your local emergency number immediately. This chat is
                for general guidance only.
              </p>
            </div>
          </aside>
        </div>
      </main>
    </div>
  );
}

export default App;
