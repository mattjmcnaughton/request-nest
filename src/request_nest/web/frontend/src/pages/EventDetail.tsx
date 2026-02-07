import { useState, useEffect, useCallback } from "react";
import { useParams, Link } from "react-router";
import { useApi } from "../contexts";
import { hasToken, clearToken, formatDate } from "../utils";
import { ApiError } from "../types";
import type { Event, Bin } from "../types";
import { AuthPrompt, CopyButton } from "../components";

const METHOD_COLORS: Record<string, string> = {
  GET: "bg-green-100 text-green-800",
  POST: "bg-blue-100 text-blue-800",
  PUT: "bg-yellow-100 text-yellow-800",
  PATCH: "bg-orange-100 text-orange-800",
  DELETE: "bg-red-100 text-red-800",
};

function MethodBadge({ method }: { method: string }) {
  const colorClass = METHOD_COLORS[method] ?? "bg-gray-100 text-gray-800";
  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded text-sm font-medium ${colorClass}`}
    >
      {method}
    </span>
  );
}

function formatHeaders(headers: Record<string, string>): string {
  return Object.entries(headers)
    .map(([key, value]) => `${key}: ${value}`)
    .join("\n");
}

function tryFormatJson(body: string): { formatted: string; isJson: boolean } {
  try {
    const parsed = JSON.parse(body);
    return { formatted: JSON.stringify(parsed, null, 2), isJson: true };
  } catch {
    return { formatted: body, isJson: false };
  }
}

interface KeyValueTableProps {
  entries: Record<string, string>;
}

function KeyValueTable({ entries }: KeyValueTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Key
            </th>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Value
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {Object.entries(entries).map(([key, value]) => (
            <tr key={key}>
              <td className="px-4 py-2 text-sm font-mono text-gray-900 whitespace-nowrap">
                {key}
              </td>
              <td className="px-4 py-2 text-sm font-mono text-gray-600 break-all">
                {value}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function EventDetail() {
  const { eventId } = useParams<{ eventId: string }>();
  const api = useApi();

  const [event, setEvent] = useState<Event | null>(null);
  const [bin, setBin] = useState<Bin | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);
  const [needsAuth, setNeedsAuth] = useState(!hasToken());

  const fetchData = useCallback(async () => {
    if (!hasToken()) {
      setNeedsAuth(true);
      setIsLoading(false);
      return;
    }

    if (!eventId) {
      setError("No event ID provided");
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);
    setNotFound(false);

    try {
      const fetchedEvent = await api.getEvent(eventId);
      setEvent(fetchedEvent);
      setNeedsAuth(false);

      try {
        const fetchedBin = await api.getBin(fetchedEvent.bin_id);
        setBin(fetchedBin);
      } catch {
        // Bin fetch failure is non-critical; breadcrumb will use bin_id
      }
    } catch (err) {
      if (ApiError.isUnauthorized(err)) {
        clearToken();
        setNeedsAuth(true);
      } else if (ApiError.isNotFound(err)) {
        setNotFound(true);
      } else if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Failed to load event details. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  }, [api, eventId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleAuthenticated = () => {
    setNeedsAuth(false);
    fetchData();
  };

  if (needsAuth) {
    return <AuthPrompt onAuthenticated={handleAuthenticated} />;
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </div>
    );
  }

  if (notFound) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
          <div className="text-center py-12">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">
              Event Not Found
            </h1>
            <p className="text-gray-600 mb-6">
              The event you are looking for does not exist or has been deleted.
            </p>
            <Link
              to="/"
              className="text-blue-600 hover:text-blue-500 underline"
            >
              Back to bins list
            </Link>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
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
                  onClick={fetchData}
                  className="mt-2 text-sm text-red-600 hover:text-red-500 underline"
                >
                  Try again
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!event) {
    return null;
  }

  const { formatted: bodyContent, isJson } = event.body
    ? tryFormatJson(event.body)
    : { formatted: "", isJson: false };
  const hasQueryParams = Object.keys(event.query_params).length > 0;
  const hasBody = event.body.length > 0;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Breadcrumb */}
        <nav className="mb-6 text-sm text-gray-600">
          <ol className="flex items-center space-x-2">
            <li>
              <Link to="/" className="hover:text-gray-900 underline">
                Bins
              </Link>
            </li>
            <li>
              <span className="mx-1">/</span>
            </li>
            <li>
              <Link
                to={`/bins/${event.bin_id}`}
                className="hover:text-gray-900 underline"
              >
                {bin?.name ?? event.bin_id}
              </Link>
            </li>
            <li>
              <span className="mx-1">/</span>
            </li>
            <li className="text-gray-900 font-medium">{event.id}</li>
          </ol>
        </nav>

        {/* Header */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4">
            <div className="flex items-center gap-3">
              <MethodBadge method={event.method} />
              <code className="text-lg font-mono text-gray-900">
                {event.path}
              </code>
            </div>
            <code className="text-sm text-gray-500 font-mono mt-2 sm:mt-0">
              {event.id}
            </code>
          </div>
          <div className="flex flex-col sm:flex-row sm:items-center gap-4 text-sm text-gray-600">
            <span>{formatDate(event.created_at)}</span>
            {event.remote_ip && (
              <span className="font-mono">{event.remote_ip}</span>
            )}
          </div>
        </div>

        {/* Query Parameters */}
        {hasQueryParams && (
          <div className="bg-white rounded-lg shadow mb-6">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">
                Query Parameters
              </h2>
            </div>
            <KeyValueTable entries={event.query_params} />
          </div>
        )}

        {/* Headers */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
            <h2 className="text-lg font-medium text-gray-900">Headers</h2>
            <CopyButton
              text={formatHeaders(event.headers)}
              label="headers"
            />
          </div>
          <KeyValueTable entries={event.headers} />
        </div>

        {/* Body */}
        {hasBody && (
          <div className="bg-white rounded-lg shadow mb-6">
            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-lg font-medium text-gray-900">
                Body{isJson && <span className="ml-2 text-sm text-gray-500">(JSON)</span>}
              </h2>
              <CopyButton text={event.body} label="body" />
            </div>
            <div className="p-6">
              <pre className="bg-gray-50 rounded-md p-4 text-sm font-mono text-gray-800 overflow-x-auto whitespace-pre-wrap break-all">
                {bodyContent}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
