import React, { useState } from 'react';
import { useMarketTrends } from '../hooks/useRealEstate';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

export const Overview: React.FC = () => {
  const [version, setVersion] = useState<string>('1.0.0');
  const { data, isLoading, error } = useMarketTrends(version);

  // loading skeleton
  if (isLoading) {
    return (
      <div className="p-6 space-y-6 animate-pulse">
        <div className="h-10 w-64 bg-slate-200 rounded"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="h-32 bg-slate-200 rounded-xl"></div>
          <div className="h-32 bg-slate-200 rounded-xl"></div>
          <div className="h-32 bg-slate-200 rounded-xl"></div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="h-[400px] bg-slate-200 rounded-xl"></div>
          <div className="h-[400px] bg-slate-200 rounded-xl"></div>
        </div>
      </div>
    );
  }

  // error state
  if (error) {
    const apiError = error as any;
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-danger/20 p-6 rounded-xl flex flex-col items-center justify-center text-center space-y-3">
          <span className="material-symbols-outlined text-danger text-4xl">error</span>
          <h3 className="text-lg font-bold text-text-primary">Error Loading Market Overview</h3>
          <p className="text-sm text-text-secondary max-w-md">
            {apiError.message || 'Something went wrong. Please check your backend connection.'}
          </p>
        </div>
      </div>
    );
  }

  const trends = data?.neighborhood_trends || [];

  // empty state
  if (trends.length === 0) {
    return (
      <div className="p-6">
        <div className="bg-white border border-border p-12 rounded-xl flex flex-col items-center justify-center text-center space-y-4">
          <span className="material-symbols-outlined text-text-secondary text-5xl">search_off</span>
          <h3 className="text-lg font-bold text-text-primary">No Data Available</h3>
          <p className="text-sm text-text-secondary max-w-sm">
            We couldn't find any neighborhood trends for version {version}.
          </p>
        </div>
      </div>
    );
  }

  // Calculate high-level aggregates
  const totalListings = trends.reduce((sum, item) => sum + item.total_listings, 0);
  const medianPrice = trends.length > 0
    ? trends.map(t => t.median_price).sort((a, b) => a - b)[Math.floor(trends.length / 2)]
    : 0;
  const avgPricePerSqft = trends.length > 0
    ? trends.reduce((sum, t) => sum + t.median_price_per_sqft, 0) / trends.length
    : 0;

  // Prepare chart data (top 12 neighborhoods by listings count to keep it legible)
  const chartData = [...trends]
    .sort((a, b) => b.total_listings - a.total_listings)
    .slice(0, 12);

  return (
    <div className="p-6 space-y-6">
      {/* Top Controls */}
      <div className="flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2 text-text-secondary mb-1">
            <span className="material-symbols-outlined text-sm">location_on</span>
            <span className="text-xs font-medium uppercase tracking-widest">Ames Region • Iowa</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-text-primary">Market Overview</h1>
        </div>
        <div className="flex gap-3">
          <div className="px-4 py-2 bg-white border border-border rounded-lg flex items-center gap-2">
            <span className="text-xs font-bold text-text-secondary">VERSION:</span>
            <select
              value={version}
              onChange={(e) => setVersion(e.target.value)}
              className="text-sm border-none bg-transparent font-bold p-0 focus:ring-0 outline-none cursor-pointer"
            >
              <option value="1.0.0">Version 1.0.0</option>
              <option value="1.0.1">Version 1.0.1</option>
              <option value="1.0.2">Version 1.0.2</option>
            </select>
          </div>
        </div>
      </div>

      {/* Bento Grid Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Median Price */}
        <div className="bg-white border border-border p-6 rounded-xl shadow-sm hover:border-primary/20 transition-all">
          <div className="flex justify-between items-start mb-4">
            <div className="bg-primary/5 p-2 rounded text-primary">
              <span className="material-symbols-outlined">payments</span>
            </div>
            <span className="text-success flex items-center text-xs font-bold bg-success/10 px-2 py-0.5 rounded">
              Active
            </span>
          </div>
          <p className="text-text-secondary text-xs font-medium uppercase mb-1">Median Price</p>
          <h3 className="text-2xl font-bold text-text-primary tabular-nums">
            ${medianPrice.toLocaleString('en-US', { maximumFractionDigits: 0 })}
          </h3>
          <p className="text-[11px] text-text-secondary mt-2">Overall middle tier benchmark</p>
        </div>

        {/* Avg Price per Sq Ft */}
        <div className="bg-white border border-border p-6 rounded-xl shadow-sm hover:border-primary/20 transition-all">
          <div className="flex justify-between items-start mb-4">
            <div className="bg-secondary/5 p-2 rounded text-secondary">
              <span className="material-symbols-outlined">grid_view</span>
            </div>
            <span className="text-text-secondary flex items-center text-xs font-bold bg-slate-100 px-2 py-0.5 rounded">
              Stable
            </span>
          </div>
          <p className="text-text-secondary text-xs font-medium uppercase mb-1">Avg Price / Sq Ft</p>
          <h3 className="text-2xl font-bold text-text-primary tabular-nums">
            ${avgPricePerSqft.toLocaleString('en-US', { maximumFractionDigits: 2 })}/sqft
          </h3>
          <p className="text-[11px] text-text-secondary mt-2">Aggregated across all properties</p>
        </div>

        {/* Total Listings */}
        <div className="bg-white border border-border p-6 rounded-xl shadow-sm hover:border-primary/20 transition-all">
          <div className="flex justify-between items-start mb-4">
            <div className="bg-amber-50 p-2 rounded text-warning">
              <span className="material-symbols-outlined">storefront</span>
            </div>
            <span className="text-success flex items-center text-xs font-bold bg-success/10 px-2 py-0.5 rounded">
              Verified
            </span>
          </div>
          <p className="text-text-secondary text-xs font-medium uppercase mb-1">Cleaned Listings</p>
          <h3 className="text-2xl font-bold text-text-primary tabular-nums">
            {totalListings.toLocaleString()}
          </h3>
          <p className="text-[11px] text-text-secondary mt-2">Available in training feature set</p>
        </div>
      </div>

      {/* Recharts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Median Price Chart */}
        <div className="bg-white p-6 border border-border rounded-xl shadow-sm">
          <div className="mb-6">
            <h3 className="text-base font-bold text-text-primary">Median Price by Neighborhood</h3>
            <p className="text-xs text-text-secondary">Comparing top 12 neighborhoods by listing volume</p>
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="neighborhood" tick={{ fontSize: 10 }} angle={-25} textAnchor="end" height={50} />
                <YAxis tick={{ fontSize: 10 }} tickFormatter={(v) => `$${v / 1000}k`} />
                <Tooltip
                  formatter={(value: any) => [`$${value.toLocaleString()}`, 'Median Price']}
                  contentStyle={{ fontSize: '12px' }}
                />
                <Bar dataKey="median_price" fill="#1E3A8A" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Listings Count Chart */}
        <div className="bg-white p-6 border border-border rounded-xl shadow-sm">
          <div className="mb-6">
            <h3 className="text-base font-bold text-text-primary">Listing Volume by Neighborhood</h3>
            <p className="text-xs text-text-secondary">Comparing top 12 neighborhoods by active inventory</p>
          </div>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="neighborhood" tick={{ fontSize: 10 }} angle={-25} textAnchor="end" height={50} />
                <YAxis tick={{ fontSize: 10 }} />
                <Tooltip
                  formatter={(value: any) => [value, 'Total Listings']}
                  contentStyle={{ fontSize: '12px' }}
                />
                <Bar dataKey="total_listings" fill="#0D9488" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
