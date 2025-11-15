"use client";

import { X, AlertTriangle } from 'lucide-react';
import clsx from 'clsx';

interface ConfirmDeleteModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title?: string;
  message?: string;
  confirmText?: string;
  cancelText?: string;
}

export default function ConfirmDeleteModal({
  isOpen,
  onClose,
  onConfirm,
  title = "Delete Chat Session",
  message = "Are you sure you want to delete this chat session? This action cannot be undone.",
  confirmText = "Delete",
  cancelText = "Cancel",
}: ConfirmDeleteModalProps) {
  if (!isOpen) return null;

  const handleConfirm = () => {
    onConfirm();
    onClose();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      onClick={onClose}
      role="dialog"
      aria-modal="true"
      aria-labelledby="confirm-delete-title"
    >
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

      {/* Modal */}
      <div
        className="relative z-10 w-full max-w-md rounded-2xl border border-red-500/30 bg-slate-900/95 p-6 shadow-[0_20px_60px_rgba(239,68,68,0.3)] backdrop-blur-xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          type="button"
          onClick={onClose}
          className="absolute right-4 top-4 rounded-lg p-1.5 text-slate-400 transition hover:bg-slate-800/50 hover:text-slate-200"
          aria-label="Close"
        >
          <X className="h-4 w-4" />
        </button>

        {/* Icon */}
        <div className="mb-4 flex items-center justify-center">
          <div className="rounded-full bg-red-500/20 p-3">
            <AlertTriangle className="h-6 w-6 text-red-400" />
          </div>
        </div>

        {/* Title */}
        <h3
          id="confirm-delete-title"
          className="mb-2 text-center text-lg font-semibold text-white"
        >
          {title}
        </h3>

        {/* Message */}
        <p className="mb-6 text-center text-sm text-slate-300">
          {message}
        </p>

        {/* Buttons */}
        <div className="flex gap-3">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 rounded-lg border border-white/10 bg-slate-800/50 px-4 py-2.5 text-sm font-medium text-slate-200 transition hover:border-slate-600/50 hover:bg-slate-800/70 hover:text-white"
          >
            {cancelText}
          </button>
          <button
            type="button"
            onClick={handleConfirm}
            className="flex-1 rounded-lg border border-red-500/50 bg-red-500/20 px-4 py-2.5 text-sm font-medium text-red-200 transition hover:border-red-500/70 hover:bg-red-500/30 hover:text-red-100"
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}

