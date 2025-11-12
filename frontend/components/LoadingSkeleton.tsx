"use client";

import clsx from "clsx";

interface LoadingSkeletonProps {
  variant?: "message" | "profile";
  count?: number;
}

const shimmer =
  "relative overflow-hidden before:absolute before:inset-0 before:-translate-x-full before:animate-[shimmer_1.8s_infinite] before:bg-gradient-to-r before:from-transparent before:via-white/60 before:to-transparent";

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
          "w-[92%] max-w-3xl rounded-3xl bg-white/80 p-5 shadow",
          shimmer
        )}
      >
        <div className="h-4 w-3/4 rounded-full bg-slate-200" />
        <div className="mt-3 h-4 w-5/6 rounded-full bg-slate-200" />
        <div className="mt-3 h-4 w-2/5 rounded-full bg-slate-200" />
      </div>
    </div>
  );
}

function ProfileSkeleton() {
  return (
    <div
      className={clsx(
        "rounded-2xl border border-white/50 bg-white/70 p-6 shadow backdrop-blur",
        shimmer
      )}
      aria-hidden
    >
      <style>{keyframes}</style>
      <div className="h-5 w-1/3 rounded-full bg-slate-200" />
      <div className="mt-4 flex flex-col gap-2">
        <div className="h-4 w-full rounded-full bg-slate-200" />
        <div className="h-4 w-5/6 rounded-full bg-slate-200" />
        <div className="h-4 w-2/3 rounded-full bg-slate-200" />
      </div>
    </div>
  );
}

export default function LoadingSkeleton({
  variant = "message",
  count = 1,
}: LoadingSkeletonProps) {
  const renderItem = variant === "profile" ? <ProfileSkeleton /> : <MessageSkeleton />;

  return (
    <div className="flex flex-col gap-4" role="presentation">
      {Array.from({ length: count }).map((_, idx) => (
        <div key={idx}>{renderItem}</div>
      ))}
    </div>
  );
}

