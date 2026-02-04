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
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">request-nest</h1>
            <p className="mt-1 text-gray-600">
              Webhook inbox for capturing HTTP requests
            </p>
          </div>
          <button
            onClick={() => setIsCreateModalOpen(true)}
            className="mt-4 sm:mt-0 inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
          >
            <svg
              className="w-5 h-5 mr-2"
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
            Create Bin
          </button>
        </div>

        {/* Content */}
        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-red-400"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm text-red-700">{error}</p>
                <button
                  onClick={fetchBins}
                  className="mt-2 text-sm text-red-600 hover:text-red-500 underline"
                >
                  Try again
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
    </div>
  );
}
