import { useEffect, useCallback, useState } from "react";
import { useParams, useNavigate, Link } from "react-router";
import { useApi } from "../contexts";
import { hasToken, clearToken, formatDate, formatSize } from "../utils";
import { ApiError } from "../types";
import type { Bin, EventSummary } from "../types";
import { AuthPrompt, CopyButton } from "../components";

interface EventCardProps {
  event: EventSummary;
  onClick: () => void;
}

function EventCard({ event, onClick }: EventCardProps) {
  return (
    <div
      className="bg-white rounded-lg shadow p-4 mb-4 cursor-pointer hover:shadow-md transition-shadow"
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
        <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
          {event.method}
        </span>
        <span className="text-xs text-gray-500 font-mono">{event.id}</span>
      </div>
      <div className="text-sm text-gray-900 font-mono mb-2 truncate">
        {event.path}
      </div>
      <div className="flex justify-between text-xs text-gray-500">
        <span>{formatDate(event.created_at)}</span>
        <span>{formatSize(event.size_bytes)}</span>
      </div>
    </div>
  );
}

interface EventsTableProps {
  events: EventSummary[];
  onEventClick: (eventId: string) => void;
}

function EventsTable({ events, onEventClick }: EventsTableProps) {
  if (events.length === 0) {
    return (
      <div className="text-center py-12 bg-white rounded-lg shadow">
        <p className="text-gray-500">No events captured yet.</p>
        <p className="text-sm text-gray-400 mt-2">
          Send a request to the ingest URL to capture events.
        </p>
      </div>
    );
  }

  return (
    <>
      {/* Mobile: Card layout */}
      <div className="md:hidden space-y-4">
        {events.map((event) => (
          <EventCard
            key={event.id}
            event={event}
            onClick={() => onEventClick(event.id)}
          />
        ))}
      </div>

      {/* Desktop: Table layout */}
      <div className="hidden md:block bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Timestamp
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Method
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Path
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Size
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {events.map((event) => (
              <tr
                key={event.id}
                className="hover:bg-gray-50 cursor-pointer"
                onClick={() => onEventClick(event.id)}
              >
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {formatDate(event.created_at)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                    {event.method}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <code className="text-sm text-gray-600 font-mono">
                    {event.path}
                  </code>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
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
              Bin Not Found
            </h1>
            <p className="text-gray-600 mb-6">
              The bin you are looking for does not exist or has been deleted.
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

  if (!bin) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Back link */}
        <Link
          to="/"
          className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 mb-6"
        >
          <svg
            className="w-4 h-4 mr-1"
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
          Back to bins
        </Link>

        {/* Header */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4">
            <h1 className="text-2xl font-bold text-gray-900">
              {bin.name || <span className="text-gray-400">Unnamed Bin</span>}
            </h1>
            <code className="text-sm text-gray-500 font-mono mt-2 sm:mt-0">
              {bin.id}
            </code>
          </div>

          <div className="border-t border-gray-200 pt-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Ingest URL
            </label>
            <div className="flex items-center gap-2 bg-gray-50 rounded-md px-3 py-2">
              <code className="text-sm text-gray-700 font-mono flex-1 truncate">
                {bin.ingest_url}
              </code>
              <CopyButton text={bin.ingest_url} />
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Send HTTP requests to this URL to capture them in this bin.
            </p>
          </div>
        </div>

        {/* Events section */}
        <div>
          <h2 className="text-lg font-medium text-gray-900 mb-4">
            Captured Events
          </h2>
          <EventsTable events={events} onEventClick={handleEventClick} />
        </div>
      </div>
    </div>
  );
}
