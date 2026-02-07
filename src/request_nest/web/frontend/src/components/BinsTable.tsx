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
        <h3 className="font-medium text-gray-900">
          {bin.name || <span className="text-gray-400">Unnamed</span>}
        </h3>
        <span className="text-xs text-gray-500 font-mono">{bin.id}</span>
      </div>
      <div className="text-sm text-gray-600 mb-2">
        Created: {formatDate(bin.created_at)}
      </div>
      <div
        className="flex items-center gap-2 bg-gray-50 rounded px-2 py-1"
        onClick={(e) => e.stopPropagation()}
      >
        <code className="text-sm text-gray-700 truncate flex-1">
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
      <div className="text-center py-12 bg-white rounded-lg shadow">
        <p className="text-gray-500">No bins yet. Create one to get started.</p>
      </div>
    );
  }

  const handleBinClick = (binId: string) => {
    navigate(`/bins/${binId}`);
  };

  return (
    <>
      {/* Mobile: Card layout */}
      <div className="md:hidden space-y-4">
        {bins.map((bin) => (
          <BinCard key={bin.id} bin={bin} onClick={() => handleBinClick(bin.id)} />
        ))}
      </div>

      {/* Desktop: Table layout */}
      <div className="hidden md:block bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Ingest URL
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {bins.map((bin) => (
              <tr
                key={bin.id}
                className="hover:bg-gray-50 cursor-pointer"
                onClick={() => handleBinClick(bin.id)}
              >
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="text-sm text-gray-900">
                    {bin.name || (
                      <span className="text-gray-400 italic">Unnamed</span>
                    )}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <code className="text-sm text-gray-600 font-mono">
                    {bin.id}
                  </code>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                  {formatDate(bin.created_at)}
                </td>
                <td
                  className="px-6 py-4 whitespace-nowrap"
                  onClick={(e) => e.stopPropagation()}
                >
                  <div className="flex items-center gap-2">
                    <code className="text-sm text-gray-600 font-mono truncate max-w-xs">
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
