"use client";

import clsx from "clsx";

interface LoadingSkeletonProps {
  variant?: "message" | "profile" | "chatHistory";
  count?: number;
}

const shimmer =
  "relative overflow-hidden before:absolute before:inset-0 before:-translate-x-full before:animate-[shimmer_1.8s_infinite] before:bg-gradient-to-r before:from-transparent before:via-emerald-400/60 before:to-transparent";

const keyframes = `
@keyframes shimmer {
  100% {
    transform: translateX(100%);
  }
}
`;

function MessageSkeleton() {
  return (
    <div className="flex w-full justify-start" aria-hidden>
      <style>{keyframes}</style>
      <div
        className={clsx(
          "w-[92%] max-w-3xl rounded-3xl bg-slate-900/60 border border-white/10 p-5 shadow-[0_18px_45px_rgba(15,23,42,0.55)]",
          shimmer
        )}
      >
        <div className="h-4 w-3/4 rounded-full bg-emerald-500/30" />
        <div className="mt-3 h-4 w-5/6 rounded-full bg-emerald-500/30" />
        <div className="mt-3 h-4 w-2/5 rounded-full bg-emerald-500/30" />
      </div>
    </div>
  );
}

function ProfileSkeleton() {
  return (
    <div
      className={clsx(
        "rounded-2xl border border-white/10 bg-slate-950/60 p-6 shadow-[0_18px_45px_rgba(15,23,42,0.55)] backdrop-blur",
        shimmer
      )}
      aria-hidden
    >
      <style>{keyframes}</style>
      <div className="h-5 w-1/3 rounded-full bg-emerald-500/30" />
      <div className="mt-4 flex flex-col gap-2">
        <div className="h-4 w-full rounded-full bg-emerald-500/30" />
        <div className="h-4 w-5/6 rounded-full bg-emerald-500/30" />
        <div className="h-4 w-2/3 rounded-full bg-emerald-500/30" />
      </div>
    </div>
  );
}

function ChatHistorySkeleton() {
  return (
    <div
      className={clsx(
        "group relative flex items-center gap-2 rounded-lg border border-transparent bg-slate-800/30 px-3 py-2",
        shimmer
      )}
      aria-hidden
    >
      <style>{keyframes}</style>
      <div className="flex-1 min-w-0">
        <div className="h-3 w-16 rounded-full bg-emerald-500/30 mb-2" />
        <div className="h-4 w-full rounded-full bg-emerald-500/30 mb-1" />
        <div className="h-3 w-12 rounded-full bg-emerald-500/30" />
      </div>
      <div className="flex-shrink-0 h-4 w-4 rounded bg-emerald-500/30" />
    </div>
  );
}

export default function LoadingSkeleton({
  variant = "message",
  count = 1,
}: LoadingSkeletonProps) {
  const renderItem = 
    variant === "profile" ? <ProfileSkeleton /> :
    variant === "chatHistory" ? <ChatHistorySkeleton /> :
    <MessageSkeleton />;

  return (
    <div className={clsx(
      "flex flex-col",
      variant === "chatHistory" ? "gap-1" : "gap-4"
    )} role="presentation">
      {Array.from({ length: count }).map((_, idx) => (
        <div key={idx}>{renderItem}</div>
      ))}
    </div>
  );
}

