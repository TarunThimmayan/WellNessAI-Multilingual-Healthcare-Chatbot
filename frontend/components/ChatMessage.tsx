"use client";

import { memo, useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import clsx from "clsx";

export type ChatRole = "user" | "assistant";

export interface Citation {
  source?: string;
  topic?: string;
  url?: string;
}

export interface ChatMessageModel {
  id: string;
  role: ChatRole;
  content: string;
  timestamp: string;
  citations?: Citation[];
}

const roleStyles: Record<ChatRole, string> = {
  user: "bg-ocean-600 text-white shadow-glass border border-ocean-500",
  assistant:
    "bg-white/90 backdrop-blur-sm text-slate-800 border border-slate-200 shadow-lg",
};

const alignment: Record<ChatRole, string> = {
  user: "items-end justify-end",
  assistant: "items-start justify-start",
};

interface ChatMessageProps {
  message: ChatMessageModel;
  index: number;
}

function ChatMessage({ message, index }: ChatMessageProps) {
  const [formattedTime, setFormattedTime] = useState<string>("");

  useEffect(() => {
    try {
      const value = new Intl.DateTimeFormat("en-US", {
        hour: "2-digit",
        minute: "2-digit",
        hour12: true,
      }).format(new Date(message.timestamp));
      setFormattedTime(value);
    } catch (error) {
      setFormattedTime(message.timestamp);
    }
  }, [message.timestamp]);

  return (
    <article
      className={clsx(
        "flex w-full",
        alignment[message.role],
        message.role === "assistant" ? "animate-fadeUp" : ""
      )}
      aria-live="polite"
      role="listitem"
      data-message-role={message.role}
      data-testid={`chat-message-${index}`}
    >
      <div
        className={clsx(
          "max-w-[90%] rounded-3xl px-5 py-4 md:px-6 md:py-5 transition-all outline-none focus-visible:ring-4 focus-visible:ring-ocean-200/70",
          roleStyles[message.role]
        )}
        tabIndex={0}
      >
        <div
          className={clsx(
            "prose prose-sm md:prose-base max-w-none break-words",
            message.role === "user"
              ? "prose-invert text-white [&_a]:text-mint-200"
              : "prose-slate [&_code]:rounded [&_code]:bg-slate-100 [&_code]:px-1.5 [&_code]:py-0.5 [&_a]:text-ocean-600 [&_a:hover]:underline"
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

        <footer className="mt-4 flex flex-wrap items-center gap-3 text-xs uppercase tracking-wide text-white/70 md:text-[0.7rem]">
          <span
            className={clsx(
              "rounded-full border px-3 py-1",
              message.role === "assistant"
                ? "border-ocean-200 text-ocean-500/80"
                : "border-white/30 text-white/70"
            )}
          >
            {message.role === "assistant" ? "Assistant" : "You"}
          </span>
          <time
            className={clsx(
              "font-medium",
              message.role === "assistant" ? "text-ocean-600/80" : "text-white/60"
            )}
            dateTime={message.timestamp}
            suppressHydrationWarning
          >
            {formattedTime || ""}
          </time>
        </footer>

        {message.citations && message.citations.length > 0 && (
          <div className="mt-4 rounded-2xl border border-ocean-100 bg-white/80 p-4 text-sm text-slate-600 shadow-md">
            <p className="mb-2 text-xs font-semibold uppercase tracking-[0.3em] text-ocean-400">
              Sources
            </p>
            <ul className="flex flex-wrap gap-2">
              {message.citations.map((citation, idx) => {
                const label = citation.topic
                  ? `${citation.topic}${citation.source ? ` (${citation.source})` : ""}`
                  : citation.source ?? `Source ${idx + 1}`;
                return (
                  <li key={`${citation.url ?? label}-${idx}`}>
                    {citation.url ? (
                      <a
                        href={citation.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 rounded-full border border-ocean-100 bg-ocean-50 px-3 py-1 text-xs font-semibold text-ocean-600 transition hover:border-ocean-200 hover:bg-ocean-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ocean-300"
                      >
                        {label}
                      </a>
                    ) : (
                      <span className="inline-flex items-center rounded-full border border-slate-200 bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
                        {label}
                      </span>
                    )}
                  </li>
                );
              })}
            </ul>
          </div>
        )}
      </div>
    </article>
  );
}

export default memo(ChatMessage);

