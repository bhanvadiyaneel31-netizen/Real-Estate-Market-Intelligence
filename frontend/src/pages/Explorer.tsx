import React, { useState } from 'react';
import { useListings } from '../hooks/useRealEstate';
import { AMES_NEIGHBORHOODS } from '../api/constants';

export const Explorer: React.FC = () => {
  const [page, setPage] = useState<number>(1);
  const [neighborhood, setNeighborhood] = useState<string>('');
  const [minPrice, setMinPrice] = useState<string>('');
  const [maxPrice, setMaxPrice] = useState<string>('');
  const [belowMarketOnly, setBelowMarketOnly] = useState<boolean>(false);

  // Parse filters
  const limit = 15;
  const listingsQuery = useListings({
    page,
    limit,
    neighborhood: neighborhood || undefined,
    min_price: minPrice ? parseFloat(minPrice) : undefined,
    max_price: maxPrice ? parseFloat(maxPrice) : undefined,
    is_below_market_value: belowMarketOnly ? 1 : undefined,
  });

  const { data, isLoading, error } = listingsQuery;

  // loading skeleton
  const renderSkeleton = () => (
    <div className="bg-white rounded-xl border border-border overflow-hidden animate-pulse">
      <div className="h-12 bg-slate-200 border-b border-border"></div>
      {[...Array(6)].map((_, idx) => (
        <div key={idx} className="h-16 bg-slate-100 border-b border-border flex items-center justify-between px-6">
          <div className="h-6 w-1/3 bg-slate-200 rounded"></div>
          <div className="h-6 w-20 bg-slate-200 rounded"></div>
          <div className="h-6 w-16 bg-slate-200 rounded"></div>
          <div className="h-6 w-32 bg-slate-200 rounded"></div>
        </div>
      ))}
    </div>
  );

  return (
    <div className="p-6 space-y-6">
      {/* Header controls */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-text-primary tracking-tight">Listing Explorer</h1>
          <p className="text-xs text-text-secondary">Browse and filter cleaned training listings from the database.</p>
        </div>
      </div>

      {/* Filter Row */}
      <div className="bg-white border border-border p-5 rounded-xl shadow-sm space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          {/* Neighborhood Select */}
          <div>
            <label className="block text-[10px] font-bold text-text-secondary uppercase mb-1">Neighborhood</label>
            <select
              value={neighborhood}
              onChange={(e) => {
                setNeighborhood(e.target.value);
                setPage(1);
              }}
              className="w-full bg-neutral-background border border-border rounded px-3 py-2 text-xs focus:ring-1 focus:ring-primary outline-none transition-all cursor-pointer"
            >
              <option value="">All Neighborhoods</option>
              {AMES_NEIGHBORHOODS.map(n => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </div>

          {/* Min Price */}
          <div>
            <label className="block text-[10px] font-bold text-text-secondary uppercase mb-1">Min Price ($)</label>
            <input
              type="number"
              value={minPrice}
              onChange={(e) => {
                setMinPrice(e.target.value);
                setPage(1);
              }}
              placeholder="e.g. 100000"
              className="w-full bg-neutral-background border border-border rounded px-3 py-2 text-xs focus:ring-1 focus:ring-primary outline-none transition-all"
            />
          </div>

          {/* Max Price */}
          <div>
            <label className="block text-[10px] font-bold text-text-secondary uppercase mb-1">Max Price ($)</label>
            <input
              type="number"
              value={maxPrice}
              onChange={(e) => {
                setMaxPrice(e.target.value);
                setPage(1);
              }}
              placeholder="e.g. 500000"
              className="w-full bg-neutral-background border border-border rounded px-3 py-2 text-xs focus:ring-1 focus:ring-primary outline-none transition-all"
            />
          </div>

          {/* Under-market toggle */}
          <div className="flex items-end">
            <button
              onClick={() => {
                setBelowMarketOnly(prev => !prev);
                setPage(1);
              }}
              className={`w-full flex items-center justify-center gap-2 py-2 px-3 border rounded text-xs font-bold transition-all ${
                belowMarketOnly
                  ? 'border-success bg-success/5 text-success'
                  : 'border-border bg-white text-text-secondary'
              }`}
            >
              <span className="material-symbols-outlined text-sm">trending_down</span>
              <span>Under-Market Value Only</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Table */}
      {error ? (
        // Error state
        <div className="bg-red-50 border border-danger/10 p-6 rounded-xl text-center flex flex-col items-center justify-center space-y-2">
          <span className="material-symbols-outlined text-danger text-3xl">error</span>
          <h4 className="text-sm font-bold text-text-primary">Failed to load listings</h4>
          <p className="text-xs text-text-secondary">{(error as any).message || 'Server connection error.'}</p>
        </div>
      ) : isLoading ? (
        renderSkeleton()
      ) : !data || data.listings.length === 0 ? (
        // Empty State
        <div className="bg-white border border-border p-12 rounded-xl text-center flex flex-col items-center justify-center space-y-3">
          <span className="material-symbols-outlined text-text-secondary text-5xl">search_off</span>
          <h4 className="text-base font-bold text-text-primary">No Listings Found</h4>
          <p className="text-xs text-text-secondary">Try adjusting your filters or search keywords.</p>
        </div>
      ) : (
        // Real listings table
        <div className="bg-white rounded-xl border border-border overflow-hidden flex flex-col">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-neutral-background border-b border-border">
                  <th className="px-6 py-4 font-semibold text-text-secondary text-[11px] uppercase tracking-wider">Neighborhood & Specs</th>
                  <th className="px-6 py-4 font-semibold text-text-secondary text-[11px] uppercase tracking-wider">Price</th>
                  <th className="px-6 py-4 font-semibold text-text-secondary text-[11px] uppercase tracking-wider">Price/Sq Ft</th>
                  <th className="px-6 py-4 font-semibold text-text-secondary text-[11px] uppercase tracking-wider">Market Standing</th>
                  <th className="px-6 py-4 font-semibold text-text-secondary text-[11px] uppercase tracking-wider">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {data.listings.map((l) => (
                  <tr key={l.id} className="hover:bg-slate-50 transition-colors group">
                    {/* Specs */}
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-semibold text-text-primary">Neighborhood: {l.neighborhood}</p>
                        <p className="text-text-secondary text-[11px] mt-0.5">
                          {l.bedrooms} Bed • {l.area.toLocaleString()} Sq Ft • {l.fireplace_count} FP
                        </p>
                      </div>
                    </td>

                    {/* Price */}
                    <td className="px-6 py-4 tabular-nums font-medium text-text-primary">
                      ${l.price.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                    </td>

                    {/* Price per sq ft */}
                    <td className="px-6 py-4 tabular-nums text-text-secondary text-xs">
                      ${l.price_per_sqft.toFixed(2)}/sqft
                    </td>

                    {/* Below Market Value status */}
                    <td className="px-6 py-4">
                      {l.is_below_market_value ? (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-success/10 text-success">
                          <span className="material-symbols-outlined text-xs">trending_down</span>
                          Under-Market Value
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-text-secondary">
                          <span className="material-symbols-outlined text-xs">trending_up</span>
                          Normal/Above
                        </span>
                      )}
                    </td>

                    {/* Amenities Details */}
                    <td className="px-6 py-4 text-xs text-text-secondary">
                      <div className="flex gap-1.5 flex-wrap">
                        {l.has_central_air === 1 && <span className="bg-slate-100 px-2 py-0.5 rounded text-[10px]">Air</span>}
                        {l.has_garage === 1 && <span className="bg-slate-100 px-2 py-0.5 rounded text-[10px]">Garage</span>}
                        {l.has_pool === 1 && <span className="bg-slate-100 px-2 py-0.5 rounded text-[10px]">Pool</span>}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination controls */}
          <div className="bg-neutral-background px-6 py-4 border-t border-border flex items-center justify-between">
            <span className="text-xs text-text-secondary">
              Showing <strong>{data.listings.length}</strong> of <strong>{data.total}</strong> properties
            </span>
            <div className="flex items-center gap-3">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1.5 border border-border rounded text-xs font-semibold hover:bg-white transition-all disabled:opacity-50 disabled:pointer-events-none"
              >
                Previous
              </button>
              <span className="text-xs text-text-primary font-medium">Page {page}</span>
              <button
                onClick={() => setPage(p => p + 1)}
                disabled={data.listings.length < limit}
                className="px-3 py-1.5 border border-border rounded text-xs font-semibold hover:bg-white transition-all disabled:opacity-50 disabled:pointer-events-none"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
