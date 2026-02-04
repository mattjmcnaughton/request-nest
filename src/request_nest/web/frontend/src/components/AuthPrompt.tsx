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
    <div className="fixed inset-0 bg-gray-600/50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Authentication Required
        </h2>
        <p className="text-gray-600 mb-4">
          Enter your admin token to access request-nest.
        </p>

        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label
              htmlFor="token"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Admin Token
            </label>
            <input
              type="password"
              id="token"
              value={tokenInput}
              onChange={(e) => setTokenInput(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Enter your token"
              autoFocus
            />
            {error && <p className="mt-1 text-sm text-red-600">{error}</p>}
          </div>

          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
          >
            Authenticate
          </button>
        </form>
      </div>
    </div>
  );
}
