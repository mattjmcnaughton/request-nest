import type { ReactNode } from "react";

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      <div className="flex items-center border-b border-gray-800 bg-gray-950 px-4 py-2">
        <div className="flex items-center gap-2 font-mono text-xs text-emerald-400">
          <span className="inline-block h-2 w-2 rounded-full bg-emerald-400"></span>
          <span>request-nest</span>
        </div>
      </div>
      {children}
    </div>
  );
}
