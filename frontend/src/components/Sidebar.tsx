import React from 'react';

interface SidebarProps {
  activePage: string;
  setActivePage: (page: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activePage, setActivePage }) => {
  const navItems = [
    { id: 'overview', label: 'Market Overview', icon: 'dashboard' },
    { id: 'predictor', label: 'Price Predictor', icon: 'query_stats' },
    { id: 'comparables', label: 'Similar Properties', icon: 'location_searching' },
    { id: 'explorer', label: 'Listing Explorer', icon: 'list_alt' },
    { id: 'comparison', label: 'Model Comparison', icon: 'analytics' },
  ];

  return (
    <aside className="h-screen w-64 fixed left-0 top-0 bg-white border-r border-border flex flex-col py-6 px-4 z-50">
      <div className="mb-10 px-2">
        <h1 className="text-xl font-bold text-primary font-headline-md leading-tight">EstateAnalytics</h1>
        <p className="text-[10px] text-text-secondary uppercase tracking-widest mt-1">Enterprise Suite</p>
      </div>

      <nav className="flex-1 space-y-1">
        {navItems.map((item) => {
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActivePage(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-3 rounded text-left transition-colors duration-200 cursor-pointer ${
                isActive
                  ? 'text-primary font-bold border-r-4 border-primary bg-neutral-background'
                  : 'text-text-secondary hover:text-text-primary hover:bg-neutral-background'
              }`}
            >
              <span className="material-symbols-outlined">{item.icon}</span>
              <span className="text-sm font-medium">{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="mt-auto space-y-1 border-t border-border pt-6">
        <button
          onClick={() => window.print()}
          className="w-full mb-6 py-2.5 px-4 bg-primary text-white font-bold rounded hover:opacity-90 transition-opacity flex items-center justify-center gap-2 text-sm"
        >
          <span className="material-symbols-outlined text-sm">download</span>
          <span>Export Report</span>
        </button>
        <div className="mt-6 flex items-center gap-3 px-2">
          <div className="w-10 h-10 rounded-full bg-slate-200 flex items-center justify-center text-primary font-bold text-sm">
            AS
          </div>
          <div className="overflow-hidden">
            <p className="text-sm font-bold truncate">Alex Sterling</p>
            <p className="text-xs text-text-secondary">Senior Advisor</p>
          </div>
        </div>
      </div>
    </aside>
  );
};
