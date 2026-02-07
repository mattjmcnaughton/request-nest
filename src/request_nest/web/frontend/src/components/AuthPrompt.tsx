import { useState } from "react";
import { setToken } from "../utils";

interface AuthPromptProps {
  onAuthenticated: () => void;
}

export function AuthPrompt({ onAuthenticated }: AuthPromptProps) {
  const [tokenInput, setTokenInput] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmedToken = tokenInput.trim();

    if (!trimmedToken) {
      setError("Please enter your admin token");
      return;
    }

    setToken(trimmedToken);
    setError(null);
    onAuthenticated();
  };

  return (
    <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4">
      <div className="bg-gray-900 border border-gray-700 rounded max-w-md w-full p-6">
        <div className="flex items-center gap-2 mb-4">
          <span className="inline-block h-2 w-2 rounded-full bg-amber-400"></span>
          <h2 className="font-mono text-sm font-semibold text-gray-100">
            auth required
          </h2>
        </div>
        <p className="font-mono text-xs text-gray-400 mb-4">
          Enter admin token to access request-nest.
        </p>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label
              htmlFor="token"
              className="block font-mono text-xs text-gray-500 mb-1"
            >
              token
            </label>
            <input
              type="password"
              id="token"
              value={tokenInput}
              onChange={(e) => setTokenInput(e.target.value)}
              className="w-full px-3 py-2 bg-gray-950 border border-gray-700 rounded font-mono text-sm text-gray-100 placeholder-gray-600 focus:outline-none focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500"
              placeholder="enter token..."
              autoFocus
            />
            {error && <p className="mt-1 font-mono text-xs text-red-400">{error}</p>}
          </div>

          <button
            type="submit"
            className="w-full bg-emerald-600 text-gray-950 py-2 px-4 rounded font-mono text-sm font-semibold hover:bg-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 focus:ring-offset-gray-900 transition-colors"
          >
            authenticate
          </button>
        </form>
      </div>
    </div>
  );
}
