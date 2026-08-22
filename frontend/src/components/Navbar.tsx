import React from 'react';
import { Layers, Play, Database, Sun, Moon } from 'lucide-react';

interface NavbarProps {
  currentTab: string;
  onTabChange: (tab: string) => void;
  onRunPipeline: () => void;
  isDark: boolean;
  onToggleTheme: () => void;
  reviewCount: number;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  onTabChange,
  onRunPipeline,
  isDark,
  onToggleTheme,
  reviewCount,
}) => {
  const tabs = [
    { id: 'overview', label: 'Overview' },
    { id: 'import', label: 'Catalog Import' },
    { id: 'products', label: 'Product Results', badge: '1,000' },
    { id: 'comparison', label: 'Before / After' },
    { id: 'quality', label: 'Quality & Governance' },
    { id: 'review', label: 'Review Queue', badge: reviewCount.toString() },
    { id: 'export', label: 'Exports' },
  ];

  return (
    <header className="sticky top-0 z-50 bg-dark-900/90 backdrop-blur-md border-b border-slate-800">
      {/* TOP LOGO & BRAND BAR */}
      <div className="px-4 lg:px-8 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => onTabChange('overview')}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-cyan-500 to-emerald-400 p-[1px] flex items-center justify-center shadow-lg shadow-indigo-500/20">
            <div className="w-full h-full bg-dark-900 rounded-[11px] flex items-center justify-center">
              <Layers className="w-5 h-5 text-cyan-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">UNILOG</span>
              <span className="text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">v2.0 Enterprise</span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">Product Intelligence & Enrichment Engine</p>
          </div>
        </div>

        {/* CENTER SYSTEM PILL */}
        <div className="hidden md:flex items-center space-x-4">
          <div className="flex items-center space-x-2 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1.5 rounded-full text-xs text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 pulse-dot"></span>
            <span className="font-medium">8/8 Quality Gates PASS</span>
          </div>
          <div className="text-xs text-slate-400 border-l border-slate-800 pl-4 flex items-center space-x-2">
            <Database className="w-3.5 h-3.5 text-cyan-400" />
            <span>1,000 Catalog Items</span>
            <span className="text-slate-600">•</span>
            <span>252 Delivery Schema Cols</span>
          </div>
        </div>

        {/* RIGHT ACTIONS */}
        <div className="flex items-center space-x-3">
          <button
            onClick={onRunPipeline}
            className="flex items-center space-x-2 bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white text-xs font-semibold px-4 py-2 rounded-lg transition-all shadow-md shadow-cyan-500/20 active:scale-95"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Run Pipeline</span>
          </button>

          <button
            onClick={onToggleTheme}
            className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
          >
            {isDark ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* NAVIGATION TABS */}
      <div className="bg-dark-800/80 border-t border-slate-800/80 px-4 lg:px-8 overflow-x-auto">
        <div className="flex space-x-1 min-w-max">
          {tabs.map((tab) => {
            const isActive = currentTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`flex items-center space-x-2 px-4 py-3 text-xs font-medium border-b-2 transition-colors ${
                  isActive
                    ? 'border-cyan-400 text-cyan-400'
                    : 'border-transparent text-slate-400 hover:text-slate-200'
                }`}
              >
                <span>{tab.label}</span>
                {tab.badge !== undefined && (
                  <span
                    className={`ml-1 text-[10px] px-1.5 py-0.5 rounded-full font-mono border transition-colors ${
                      isActive
                        ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30 font-semibold'
                        : 'bg-slate-800/80 text-slate-400 border-slate-700/60'
                    }`}
                  >
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
};
