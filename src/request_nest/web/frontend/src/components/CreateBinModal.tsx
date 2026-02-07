import { useState } from "react";
import { useApi } from "../contexts";
import { ApiError } from "../types";

interface CreateBinModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCreated: () => void;
}

export function CreateBinModal({
  isOpen,
  onClose,
  onCreated,
}: CreateBinModalProps) {
  const api = useApi();
  const [name, setName] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      await api.createBin(name.trim() || null);
      setName("");
      onCreated();
      onClose();
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Failed to create bin. Please try again.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setName("");
    setError(null);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
      <div className="bg-gray-900 border border-gray-700 rounded max-w-md w-full p-6">
        <div className="flex justify-between items-center mb-4">
          <div className="flex items-center gap-2">
            <span className="inline-block h-2 w-2 rounded-full bg-emerald-400"></span>
            <h2 className="font-mono text-sm font-semibold text-gray-100">
              new bin
            </h2>
          </div>
          <button
            onClick={handleClose}
            className="text-gray-500 hover:text-gray-300 transition-colors"
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label
              htmlFor="bin-name"
              className="block font-mono text-xs text-gray-500 mb-1"
            >
              name (optional)
            </label>
            <input
              type="text"
              id="bin-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 bg-gray-950 border border-gray-700 rounded font-mono text-sm text-gray-100 placeholder-gray-600 focus:outline-none focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500"
              placeholder="e.g., stripe-webhooks"
              disabled={isSubmitting}
              autoFocus
            />
            <p className="mt-1 font-mono text-xs text-gray-600">
              Give your bin a name to identify it later.
            </p>
            {error && <p className="mt-2 font-mono text-xs text-red-400">{error}</p>}
          </div>

          <div className="flex gap-3 justify-end">
            <button
              type="button"
              onClick={handleClose}
              className="px-4 py-2 font-mono text-xs text-gray-400 bg-gray-800 border border-gray-700 rounded hover:bg-gray-700 focus:outline-none focus:ring-1 focus:ring-gray-500 transition-colors"
              disabled={isSubmitting}
            >
              cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-emerald-600 text-gray-950 rounded font-mono text-xs font-semibold hover:bg-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 focus:ring-offset-gray-900 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={isSubmitting}
            >
              {isSubmitting ? "creating..." : "create"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
