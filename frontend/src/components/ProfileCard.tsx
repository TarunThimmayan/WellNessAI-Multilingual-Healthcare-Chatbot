import { useMemo } from 'react';
import clsx from 'clsx';

interface ProfileCardProps {
  loading: boolean;
  onEdit?: () => void;
  profile: {
    name: string;
    avatarColor: string;
    stats: Array<{ label: string; value: string }>;
  };
}

const gradientMap: Record<string, string> = {
  teal: 'from-ocean-500 via-ocean-400 to-mint-400',
  mint: 'from-mint-500 via-mint-400 to-ocean-300',
  blue: 'from-sky-500 via-ocean-500 to-teal-500',
};

export default function ProfileCard({ loading, profile, onEdit }: ProfileCardProps) {
  const gradient = useMemo(
    () => gradientMap[profile.avatarColor] ?? gradientMap.teal,
    [profile.avatarColor]
  );

  if (loading) {
    return (
      <div
        className="flex flex-col gap-3 rounded-2xl border border-white/40 bg-white/60 p-6 shadow backdrop-blur animate-pulse"
        aria-busy="true"
        aria-live="polite"
      >
        <div className="h-4 w-1/2 rounded-full bg-slate-200" />
        <div className="flex gap-3">
          <div className="h-10 w-10 rounded-full bg-slate-200" />
          <div className="flex-1 space-y-2">
            <div className="h-4 w-1/3 rounded-full bg-slate-200" />
            <div className="h-4 w-2/3 rounded-full bg-slate-200" />
          </div>
        </div>
        <div className="mt-2 grid grid-cols-2 gap-2">
          <div className="h-4 rounded-full bg-slate-200" />
          <div className="h-4 rounded-full bg-slate-200" />
          <div className="h-4 rounded-full bg-slate-200" />
          <div className="h-4 rounded-full bg-slate-200" />
        </div>
      </div>
    );
  }

  return (
    <section
      className="relative overflow-hidden rounded-2xl border border-white/50 bg-white/80 p-6 shadow-lg backdrop-blur transition"
      aria-label="Profile summary"
    >
      <div
        className={clsx(
          'absolute inset-y-0 right-0 w-1/3 opacity-80 blur-3xl',
          `bg-gradient-to-br ${gradient}`
        )}
        aria-hidden
      />
      <div className="relative flex items-center gap-4">
        <div
          className={clsx(
            'flex h-12 w-12 items-center justify-center rounded-full text-lg font-semibold text-white shadow-lg',
            `bg-gradient-to-br ${gradient}`
          )}
          aria-hidden
        >
          {profile.name.slice(0, 1).toUpperCase()}
        </div>
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Welcome back
          </p>
          <h2 className="text-xl font-bold text-slate-800">{profile.name}</h2>
        </div>
        {onEdit && (
          <button
            onClick={onEdit}
            className="ml-auto rounded-full border border-ocean-100 px-4 py-2 text-sm font-semibold text-ocean-700 transition hover:bg-ocean-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ocean-200"
          >
            Edit
          </button>
        )}
      </div>
      <dl className="relative mt-5 grid grid-cols-2 gap-3 text-sm text-slate-600">
        {profile.stats.map((stat) => (
          <div
            key={stat.label}
            className="rounded-xl border border-white/60 bg-white/70 px-3 py-2 shadow-sm"
          >
            <dt className="text-xs uppercase tracking-wide text-slate-400">
              {stat.label}
            </dt>
            <dd className="mt-1 font-semibold text-slate-700">{stat.value}</dd>
          </div>
        ))}
      </dl>
    </section>
  );
}

