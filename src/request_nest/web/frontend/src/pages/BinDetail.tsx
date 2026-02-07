import { useEffect, useCallback, useState } from "react";
import { useParams, useNavigate, Link } from "react-router";
import { useApi } from "../contexts";
import { hasToken, clearToken, formatDate, formatSize } from "../utils";
import { ApiError } from "../types";
import type { Bin, EventSummary } from "../types";
import { AuthPrompt, CopyButton } from "../components";

function EventCard({ event, onClick }: { event: EventSummary; onClick: () => void }) {
  return (
    <div
      className="bg-gray-900 border border-gray-800 rounded p-3 mb-3 cursor-pointer hover:border-gray-600 transition-colors"
      onClick={onClick}
      role="button"
      tabIndex={0}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          onClick();
        }
      }}
    >
      <div className="flex justify-between items-start mb-2">
        <span className="inline-flex items-center px-2 py-0.5 rounded font-mono text-xs font-medium bg-cyan-900/50 text-cyan-300">
          {event.method}
        </span>
        <span className="font-mono text-xs text-gray-600">{event.id}</span>
      </div>
      <div className="font-mono text-xs text-gray-300 mb-2 truncate">
        {event.path}
      </div>
      <div className="flex justify-between font-mono text-xs text-gray-600">
        <span>{formatDate(event.created_at)}</span>
        <span>{formatSize(event.size_bytes)}</span>
      </div>
    </div>
  );
}

function EventsTable({ events, onEventClick }: { events: EventSummary[]; onEventClick: (eventId: string) => void }) {
  if (events.length === 0) {
    return (
      <div className="text-center py-12 bg-gray-900 border border-gray-800 rounded">
        <p className="font-mono text-sm text-gray-500">No events captured yet.</p>
        <p className="font-mono text-xs text-gray-600 mt-2">
          Send a request to the ingest URL to capture events.
        </p>
      </div>
    );
  }

  return (
    <>
      {/* Mobile: Card layout */}
      <div className="md:hidden space-y-3">
        {events.map((event) => (
          <EventCard
            key={event.id}
            event={event}
            onClick={() => onEventClick(event.id)}
          />
        ))}
      </div>

      {/* Desktop: Table layout */}
      <div className="hidden md:block bg-gray-900 border border-gray-800 rounded overflow-hidden">
        <table className="min-w-full divide-y divide-gray-800">
          <thead className="bg-gray-900">
            <tr>
              <th className="px-4 py-3 text-left font-mono text-xs text-gray-500 uppercase tracking-wider">
                Timestamp
              </th>
              <th className="px-4 py-3 text-left font-mono text-xs text-gray-500 uppercase tracking-wider">
                Method
              </th>
              <th className="px-4 py-3 text-left font-mono text-xs text-gray-500 uppercase tracking-wider">
                Path
              </th>
              <th className="px-4 py-3 text-left font-mono text-xs text-gray-500 uppercase tracking-wider">
                Size
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {events.map((event) => (
              <tr
                key={event.id}
                className="hover:bg-gray-800/50 cursor-pointer"
                onClick={() => onEventClick(event.id)}
              >
                <td className="px-4 py-3 whitespace-nowrap font-mono text-xs text-gray-500">
                  {formatDate(event.created_at)}
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <span className="inline-flex items-center px-2 py-0.5 rounded font-mono text-xs font-medium bg-cyan-900/50 text-cyan-300">
                    {event.method}
                  </span>
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <code className="font-mono text-xs text-gray-300">
                    {event.path}
                  </code>
                </td>
                <td className="px-4 py-3 whitespace-nowrap font-mono text-xs text-gray-500">
                  {formatSize(event.size_bytes)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

export function BinDetail() {
  const { binId } = useParams<{ binId: string }>();
  const navigate = useNavigate();
  const api = useApi();

  const [bin, setBin] = useState<Bin | null>(null);
  const [events, setEvents] = useState<EventSummary[]>([]);
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

    if (!binId) {
      setError("No bin ID provided");
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);
    setNotFound(false);

    try {
      const [fetchedBin, fetchedEvents] = await Promise.all([
        api.getBin(binId),
        api.listEventsForBin(binId),
      ]);
      setBin(fetchedBin);
      setEvents(fetchedEvents);
      setNeedsAuth(false);
    } catch (err) {
      if (ApiError.isUnauthorized(err)) {
        clearToken();
        setNeedsAuth(true);
      } else if (ApiError.isNotFound(err)) {
        setNotFound(true);
      } else if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError("Failed to load bin details. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  }, [api, binId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleAuthenticated = () => {
    setNeedsAuth(false);
    fetchData();
  };

  const handleEventClick = (eventId: string) => {
    navigate(`/events/${eventId}`);
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
            bin not found
          </h1>
          <p className="font-mono text-xs text-gray-500 mb-6">
            The bin does not exist or has been deleted.
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

  if (!bin) {
    return null;
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
      {/* Back link */}
      <Link
        to="/"
        className="inline-flex items-center font-mono text-xs text-gray-500 hover:text-gray-300 mb-6"
      >
        <svg
          className="w-3 h-3 mr-1"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15 19l-7-7 7-7"
          />
        </svg>
        cd ..
      </Link>

      {/* Header */}
      <div className="bg-gray-900 border border-gray-800 rounded p-5 mb-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4">
          <h1 className="font-mono text-lg font-bold text-gray-100">
            {bin.name || <span className="text-gray-600">unnamed</span>}
          </h1>
          <code className="font-mono text-xs text-gray-500 mt-2 sm:mt-0">
            {bin.id}
          </code>
        </div>

        <div className="border-t border-gray-800 pt-4">
          <label className="block font-mono text-xs text-gray-500 mb-2">
            ingest_url
          </label>
          <div className="flex items-center gap-2 bg-gray-950 border border-gray-800 rounded px-3 py-2">
            <code className="font-mono text-sm text-emerald-400 flex-1 truncate">
              {bin.ingest_url}
            </code>
            <CopyButton text={bin.ingest_url} />
          </div>
          <p className="font-mono text-xs text-gray-600 mt-2">
            Send HTTP requests to this URL to capture them.
          </p>
        </div>
      </div>

      {/* Events section */}
      <div>
        <h2 className="font-mono text-sm font-medium text-gray-300 mb-4">
          <span className="text-emerald-400">$</span> events
        </h2>
        <EventsTable events={events} onEventClick={handleEventClick} />
      </div>
    </div>
  );
}
