import { useState, useEffect, useCallback } from "react";
import { useApi } from "../contexts";
import { hasToken, clearToken } from "../utils";
import { ApiError } from "../types";
import type { Bin } from "../types";
import { AuthPrompt, BinsTable, CreateBinModal } from "../components";

export function BinsIndex() {
  const api = useApi();
  const [bins, setBins] = useState<Bin[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [needsAuth, setNeedsAuth] = useState(!hasToken());
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);

  const fetchBins = useCallback(async () => {
    if (!hasToken()) {
      setNeedsAuth(true);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const fetchedBins = await api.listBins();
      setBins(fetchedBins);
      setNeedsAuth(false);
    } catch (err) {
      if (ApiError.isUnauthorized(err)) {
        clearToken();
        setNeedsAuth(true);
      } else if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Failed to load bins. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  }, [api]);

  useEffect(() => {
    fetchBins();
  }, [fetchBins]);

  const handleAuthenticated = () => {
    setNeedsAuth(false);
    fetchBins();
  };

  const handleBinCreated = () => {
    fetchBins();
  };

  if (needsAuth) {
    return <AuthPrompt onAuthenticated={handleAuthenticated} />;
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
        <div>
          <h1 className="font-mono text-xl font-bold text-gray-100">
            <span className="text-emerald-400">$</span> bins
          </h1>
          <p className="mt-1 font-mono text-xs text-gray-500">
            webhook inbox for capturing HTTP requests
          </p>
        </div>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="mt-4 sm:mt-0 inline-flex items-center px-4 py-2 bg-emerald-600 text-gray-950 rounded font-mono text-xs font-semibold hover:bg-emerald-500 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2 focus:ring-offset-gray-950 transition-colors"
        >
          <svg
            className="w-4 h-4 mr-2"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          new bin
        </button>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-emerald-400"></div>
        </div>
      ) : error ? (
        <div className="bg-red-950/50 border border-red-800 rounded p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <span className="font-mono text-xs text-red-400">ERR</span>
            </div>
            <div className="ml-3">
              <p className="font-mono text-xs text-red-300">{error}</p>
              <button
                onClick={fetchBins}
                className="mt-2 font-mono text-xs text-red-400 hover:text-red-300 underline"
              >
                retry
              </button>
            </div>
          </div>
        </div>
      ) : (
        <BinsTable bins={bins} />
      )}

      {/* Create Modal */}
      <CreateBinModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onCreated={handleBinCreated}
      />
    </div>
  );
}
