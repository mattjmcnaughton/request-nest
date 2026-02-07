import { useNavigate } from "react-router";
import type { Bin } from "../types";
import { formatDate } from "../utils";
import { CopyButton } from "./CopyButton";

interface BinsTableProps {
  bins: Bin[];
}

function BinCard({ bin, onClick }: { bin: Bin; onClick: () => void }) {
  return (
    <div
      className="bg-gray-900 border border-gray-800 rounded p-4 mb-3 cursor-pointer hover:border-gray-600 transition-colors"
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
        <h3 className="font-mono text-sm text-gray-100">
          {bin.name || <span className="text-gray-600">unnamed</span>}
        </h3>
        <span className="font-mono text-xs text-gray-600">{bin.id}</span>
      </div>
      <div className="font-mono text-xs text-gray-500 mb-2">
        {formatDate(bin.created_at)}
      </div>
      <div
        className="flex items-center gap-2 bg-gray-950 border border-gray-800 rounded px-2 py-1"
        onClick={(e) => e.stopPropagation()}
      >
        <code className="font-mono text-xs text-emerald-400 truncate flex-1">
          {bin.ingest_url}
        </code>
        <CopyButton text={bin.ingest_url} />
      </div>
    </div>
  );
}

export function BinsTable({ bins }: BinsTableProps) {
  const navigate = useNavigate();

  if (bins.length === 0) {
    return (
      <div className="text-center py-12 bg-gray-900 border border-gray-800 rounded">
        <p className="font-mono text-sm text-gray-500">No bins yet.</p>
        <p className="font-mono text-xs text-gray-600 mt-2">
          Create one to get started.
        </p>
      </div>
    );
  }

  const handleBinClick = (binId: string) => {
    navigate(`/bins/${binId}`);
  };

  return (
    <>
      {/* Mobile: Card layout */}
      <div className="md:hidden space-y-3">
        {bins.map((bin) => (
          <BinCard key={bin.id} bin={bin} onClick={() => handleBinClick(bin.id)} />
        ))}
      </div>

      {/* Desktop: Table layout */}
      <div className="hidden md:block bg-gray-900 border border-gray-800 rounded overflow-hidden">
        <table className="min-w-full divide-y divide-gray-800">
          <thead className="bg-gray-900">
            <tr>
              <th className="px-4 py-3 text-left font-mono text-xs text-gray-500 uppercase tracking-wider">
                Name
              </th>
              <th className="px-4 py-3 text-left font-mono text-xs text-gray-500 uppercase tracking-wider">
                ID
              </th>
              <th className="px-4 py-3 text-left font-mono text-xs text-gray-500 uppercase tracking-wider">
                Created
              </th>
              <th className="px-4 py-3 text-left font-mono text-xs text-gray-500 uppercase tracking-wider">
                Ingest URL
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800">
            {bins.map((bin) => (
              <tr
                key={bin.id}
                className="hover:bg-gray-800/50 cursor-pointer"
                onClick={() => handleBinClick(bin.id)}
              >
                <td className="px-4 py-3 whitespace-nowrap">
                  <span className="font-mono text-sm text-gray-100">
                    {bin.name || (
                      <span className="text-gray-600 italic">unnamed</span>
                    )}
                  </span>
                </td>
                <td className="px-4 py-3 whitespace-nowrap">
                  <code className="font-mono text-xs text-gray-400">
                    {bin.id}
                  </code>
                </td>
                <td className="px-4 py-3 whitespace-nowrap font-mono text-xs text-gray-500">
                  {formatDate(bin.created_at)}
                </td>
                <td
                  className="px-4 py-3 whitespace-nowrap"
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="flex items-center gap-2">
                    <code className="font-mono text-xs text-emerald-400 truncate max-w-xs">
                      {bin.ingest_url}
                    </code>
                    <CopyButton text={bin.ingest_url} />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}
