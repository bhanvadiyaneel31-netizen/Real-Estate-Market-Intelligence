import React from 'react';

interface HeaderProps {
  title: string;
}

export const Header: React.FC<HeaderProps> = ({ title }) => {
  return (
    <header className="w-full h-16 sticky top-0 bg-white border-b border-border flex items-center justify-between px-6 z-40">
      <h2 className="text-lg font-bold text-primary font-headline-lg">{title}</h2>
      <div className="flex items-center gap-6">
        <div className="relative hidden lg:block">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-text-secondary text-sm">
            search
          </span>
          <input
            className="bg-neutral-background border-none rounded-full py-1.5 pl-10 pr-4 text-xs focus:ring-1 focus:ring-primary w-64 outline-none"
            placeholder="Search markets, zip codes..."
            type="text"
            disabled
          />
        </div>
        <div className="flex items-center gap-4 text-text-secondary">
          <button className="hover:text-primary transition-colors">
            <span className="material-symbols-outlined">notifications</span>
          </button>
          <button className="hover:text-primary transition-colors">
            <span className="material-symbols-outlined">account_circle</span>
          </button>
        </div>
      </div>
    </header>
  );
};
