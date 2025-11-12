import { memo } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import clsx from 'clsx';

export type MessageRole = 'user' | 'assistant' | 'system';

export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
}

interface ChatMessageProps {
  message: Message;
  index: number;
}

const roleStyles: Record<MessageRole, string> = {
  user: 'bg-ocean-600 text-white shadow-glass border border-ocean-500',
  assistant:
    'bg-white/90 backdrop-blur-sm text-slate-800 border border-slate-200 shadow-lg',
  system: 'bg-mint-100 text-slate-700 border border-mint-200',
};

const alignment: Record<MessageRole, string> = {
  user: 'items-end',
  assistant: 'items-start',
  system: 'items-center',
};

function ChatMessage({ message, index }: ChatMessageProps) {
  return (
    <div
      className={clsx(
        'flex w-full',
        alignment[message.role],
        message.role === 'system' && 'justify-center'
      )}
      aria-live="polite"
      role="listitem"
      data-testid={`chat-message-${index}`}
    >
      <div
        className={clsx(
          'max-w-[90%] rounded-3xl px-5 py-4 md:px-6 md:py-5 transition-all',
          'ring-1 ring-transparent hover:ring-ocean-200 focus-within:ring-ocean-300',
          'shadow-sm',
          roleStyles[message.role]
        )}
        tabIndex={0}
      >
        <div
          className={clsx(
            'prose prose-sm md:prose-base',
            message.role === 'user'
              ? 'prose-invert text-white'
              : 'prose-slate [&_a]:text-ocean-600 [&_a:hover]:underline'
          )}
        >
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              li: ({ children, ...props }) => (
                <li className="marker:text-ocean-500" {...props}>
                  {children}
                </li>
              ),
            }}
          >
            {message.content}
          </ReactMarkdown>
        </div>
        <p className="mt-3 text-xs uppercase tracking-wide opacity-70">
          {message.timestamp}
        </p>
      </div>
    </div>
  );
}

export default memo(ChatMessage);

