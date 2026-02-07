import { useState, useEffect, useCallback } from "react";
import { useParams, Link } from "react-router";
import { useApi } from "../contexts";
import { hasToken, clearToken, formatDate } from "../utils";
import { ApiError } from "../types";
import type { Event, Bin } from "../types";
import { AuthPrompt, CopyButton } from "../components";

const METHOD_COLORS: Record<string, string> = {
  GET: "bg-green-900/50 text-green-300",
  POST: "bg-cyan-900/50 text-cyan-300",
  PUT: "bg-yellow-900/50 text-yellow-300",
  PATCH: "bg-orange-900/50 text-orange-300",
  DELETE: "bg-red-900/50 text-red-300",
};

function MethodBadge({ method }: { method: string }) {
  const colorClass = METHOD_COLORS[method] ?? "bg-gray-800 text-gray-300";
  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded font-mono text-xs font-semibold ${colorClass}`}
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

function KeyValueTable({ entries }: { entries: Record<string, string> }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-800">
        <thead className="bg-gray-900">
          <tr>
            <th className="px-4 py-2 text-left font-mono text-xs text-gray-500 uppercase tracking-wider">
              Key
            </th>
            <th className="px-4 py-2 text-left font-mono text-xs text-gray-500 uppercase tracking-wider">
              Value
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-800">
          {Object.entries(entries).map(([key, value]) => (
            <tr key={key}>
              <td className="px-4 py-2 font-mono text-xs text-emerald-400 whitespace-nowrap">
                {key}
              </td>
              <td className="px-4 py-2 font-mono text-xs text-gray-300 break-all">
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
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-emerald-400"></div>
        </div>
      </div>
    );
  }

  if (notFound) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <div className="text-center py-12">
          <h1 className="font-mono text-lg font-bold text-gray-100 mb-4">
            event not found
          </h1>
          <p className="font-mono text-xs text-gray-500 mb-6">
            The event you are looking for does not exist or has been deleted.
          </p>
          <Link
            to="/"
            className="font-mono text-xs text-emerald-400 hover:text-emerald-300 underline"
          >
            back to bins
          </Link>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <div className="bg-red-950/50 border border-red-800 rounded p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <span className="font-mono text-xs text-red-400">ERR</span>
            </div>
            <div className="ml-3">
              <p className="font-mono text-xs text-red-300">{error}</p>
              <button
                onClick={fetchData}
                className="mt-2 font-mono text-xs text-red-400 hover:text-red-300 underline"
              >
                retry
              </button>
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
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      {/* Breadcrumb */}
      <nav className="mb-6 font-mono text-xs text-gray-500">
        <ol className="flex items-center space-x-1">
          <li>
            <Link to="/" className="hover:text-gray-300 underline">
              bins
            </Link>
          </li>
          <li>
            <span className="text-gray-600">/</span>
          </li>
          <li>
            <Link
              to={`/bins/${event.bin_id}`}
              className="hover:text-gray-300 underline"
            >
              {bin?.name ?? event.bin_id}
            </Link>
          </li>
          <li>
            <span className="text-gray-600">/</span>
          </li>
          <li className="text-gray-300">{event.id}</li>
        </ol>
      </nav>

      {/* Header */}
      <div className="bg-gray-900 border border-gray-800 rounded p-5 mb-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4">
          <div className="flex items-center gap-3">
            <MethodBadge method={event.method} />
            <code className="font-mono text-sm text-gray-100">
              {event.path}
            </code>
          </div>
          <code className="font-mono text-xs text-gray-500 mt-2 sm:mt-0">
            {event.id}
          </code>
        </div>
        <div className="flex flex-col sm:flex-row sm:items-center gap-4 font-mono text-xs text-gray-500">
          <span>{formatDate(event.created_at)}</span>
          {event.remote_ip && (
            <span>{event.remote_ip}</span>
          )}
        </div>
      </div>

      {/* Query Parameters */}
      {hasQueryParams && (
        <div className="bg-gray-900 border border-gray-800 rounded mb-6">
          <div className="px-4 py-3 border-b border-gray-800">
            <h2 className="font-mono text-sm font-medium text-gray-300">
              query_params
            </h2>
          </div>
          <KeyValueTable entries={event.query_params} />
        </div>
      )}

      {/* Headers */}
      <div className="bg-gray-900 border border-gray-800 rounded mb-6">
        <div className="px-4 py-3 border-b border-gray-800 flex items-center justify-between">
          <h2 className="font-mono text-sm font-medium text-gray-300">
            headers
          </h2>
          <CopyButton
            text={formatHeaders(event.headers)}
            label="headers"
          />
        </div>
        <KeyValueTable entries={event.headers} />
      </div>

      {/* Body */}
      {hasBody && (
        <div className="bg-gray-900 border border-gray-800 rounded mb-6">
          <div className="px-4 py-3 border-b border-gray-800 flex items-center justify-between">
            <h2 className="font-mono text-sm font-medium text-gray-300">
              body{isJson && <span className="ml-2 text-xs text-gray-500">(json)</span>}
            </h2>
            <CopyButton text={event.body} label="body" />
          </div>
          <div className="p-4">
            <pre className="bg-gray-950 border border-gray-800 rounded p-4 font-mono text-xs text-gray-300 overflow-x-auto whitespace-pre-wrap break-all">
              {bodyContent}
            </pre>
          </div>
        </div>
      )}
    </div>
  );
}
