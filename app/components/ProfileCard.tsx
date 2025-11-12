"use client";

import { useMemo } from "react";
import clsx from "clsx";

interface ProfileStat {
  label: string;
  value: string;
  icon?: React.ReactNode;
  highlights?: string[];
}

interface ProfileCardProps {
  loading: boolean;
  name: string;
  avatarColor?: "teal" | "mint" | "blue";
  stats: ProfileStat[];
  onEdit?: () => void;
}

const gradientMap: Record<string, string> = {
  teal: "from-ocean-500 via-ocean-400 to-mint-400",
  mint: "from-mint-500 via-mint-400 to-ocean-300",
  blue: "from-sky-500 via-ocean-500 to-teal-500",
};

export default function ProfileCard({
  loading,
  name,
  avatarColor = "teal",
  stats,
  onEdit,
}: ProfileCardProps) {
  const gradient = useMemo(
    () => gradientMap[avatarColor] ?? gradientMap.teal,
    [avatarColor]
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
      className="relative overflow-hidden rounded-3xl border border-white/50 bg-white/85 p-6 shadow-lg backdrop-blur transition"
      aria-label="Profile summary"
    >
      <div
        className={clsx(
          "absolute inset-y-0 right-0 w-[45%] opacity-70 blur-3xl",
          `bg-gradient-to-br ${gradient}`
        )}
        aria-hidden
      />
      <div className="relative flex items-center gap-4 border-b border-white/60 pb-5">
        <div
          className={clsx(
            "flex h-12 w-12 items-center justify-center rounded-full text-lg font-semibold text-white shadow-lg",
            `bg-gradient-to-br ${gradient}`
          )}
          aria-hidden
        >
          {name.slice(0, 1).toUpperCase()}
        </div>
        <div className="flex flex-1 flex-col">
          <div className="flex items-center justify-between">
            <p className="text-xs font-semibold uppercase tracking-[0.35em] text-slate-400">
              Health profile
            </p>
            {onEdit && (
              <button
                onClick={onEdit}
                className="rounded-full border border-white/70 bg-white/60 px-3.5 py-1 text-[11px] font-semibold uppercase tracking-[0.3em] text-ocean-600 transition hover:border-ocean-200 hover:bg-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-ocean-200"
              >
                Update
              </button>
            )}
          </div>
          <h2 className="mt-1 text-lg font-semibold text-slate-800">{name}</h2>
        </div>
      </div>

      <dl className="relative mt-5 grid gap-3 sm:grid-cols-2">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className="flex h-full flex-col gap-2 rounded-2xl border border-white/60 bg-white/75 px-4 py-3 shadow-sm transition hover:border-ocean-100 hover:shadow-sm"
          >
            <dt className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.35em] text-slate-400">
              {stat.icon && (
                <span className="flex h-7 w-7 items-center justify-center rounded-full bg-ocean-50 text-ocean-500">
                  {stat.icon}
                </span>
              )}
              <span>{stat.label}</span>
            </dt>
            <dd className="text-sm font-semibold text-slate-700">
              {stat.highlights && stat.highlights.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {stat.highlights.map((highlight) => (
                    <span
                      key={highlight}
                      className="rounded-full bg-ocean-50 px-2.5 py-1 text-xs font-medium text-ocean-600"
                    >
                      {highlight}
                    </span>
                  ))}
                </div>
              ) : (
                stat.value
              )}
            </dd>
          </div>
        ))}
      </dl>
    </section>
  );
}

