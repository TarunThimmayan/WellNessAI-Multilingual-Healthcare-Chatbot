"use client";

interface ErrorCalloutProps {
  message: string;
  onDismiss: () => void;
}

export default function ErrorCallout({ message, onDismiss }: ErrorCalloutProps) {
  return (
    <div
      className="relative rounded-2xl border border-red-200/80 bg-red-50 px-5 py-4 text-red-700 shadow-md backdrop-blur-sm transition"
      role="alert"
      aria-live="assertive"
    >
      <p className="font-semibold">Something went wrong</p>
      <p className="mt-1 text-sm text-red-600/90">{message}</p>
      <button
        onClick={onDismiss}
        className="absolute right-4 top-4 rounded-full border border-red-200 px-3 py-1 text-xs font-semibold uppercase tracking-wide text-red-700 transition hover:bg-red-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-red-300"
        aria-label="Dismiss error"
      >
        Dismiss
      </button>
    </div>
  );
}

