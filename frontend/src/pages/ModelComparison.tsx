import React, { useState } from 'react';
import { useModelMetrics } from '../hooks/useRealEstate';
import { MODEL_COLORS, MODEL_NAMES } from '../api/constants';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell
} from 'recharts';

export const ModelComparison: React.FC = () => {
  const [version, setVersion] = useState<string>('latest');
  const { data, isLoading, error } = useModelMetrics(version);

  // loading skeleton
  if (isLoading) {
    return (
      <div className="p-6 space-y-6 animate-pulse">
        <div className="h-10 w-64 bg-slate-200 rounded"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="h-[400px] bg-slate-200 rounded-xl"></div>
          <div className="h-[400px] bg-slate-200 rounded-xl"></div>
        </div>
        <div className="h-80 bg-slate-200 rounded-xl"></div>
      </div>
    );
  }

  // error state
  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-danger/20 p-6 rounded-xl flex flex-col items-center justify-center text-center space-y-3">
          <span className="material-symbols-outlined text-danger text-4xl">error</span>
          <h3 className="text-lg font-bold text-text-primary">Error Loading Model Metrics</h3>
          <p className="text-sm text-text-secondary max-w-md">
            {(error as any).message || 'Server connection error.'}
          </p>
        </div>
      </div>
    );
  }

  // Extract and format data for Recharts
  const metricsMap = data || {};
  const modelKeys = Object.keys(metricsMap);

  if (modelKeys.length === 0) {
    return (
      <div className="p-6">
        <div className="bg-white border border-border p-12 rounded-xl flex flex-col items-center justify-center text-center space-y-4">
          <span className="material-symbols-outlined text-text-secondary text-5xl">search_off</span>
          <h3 className="text-lg font-bold text-text-primary">No Metrics Found</h3>
          <p className="text-sm text-text-secondary max-w-sm">
            We couldn't find any metrics in metrics.json for version {version}.
          </p>
        </div>
      </div>
    );
  }

  // Split into regression and classification models
  const regressionModels = modelKeys
    .filter(k => metricsMap[k].metrics.r2 !== undefined || metricsMap[k].metrics.rmse !== undefined)
    .map(k => ({
      id: k,
      name: MODEL_NAMES[k] || k,
      r2: metricsMap[k].metrics.r2 || 0,
      rmse: metricsMap[k].metrics.rmse || 0,
      trainedAt: metricsMap[k].trained_at,
      version: metricsMap[k].feature_set_version,
      color: MODEL_COLORS[k] || '#64748B',
    }))
    .sort((a, b) => b.r2 - a.r2);

  const classificationModels = modelKeys
    .filter(k => metricsMap[k].metrics.accuracy !== undefined)
    .map(k => ({
      id: k,
      name: MODEL_NAMES[k] || k,
      accuracy: metricsMap[k].metrics.accuracy || 0,
      f1: metricsMap[k].metrics.f1 || metricsMap[k].metrics.f1_weighted || 0,
      trainedAt: metricsMap[k].trained_at,
      version: metricsMap[k].feature_set_version,
      color: MODEL_COLORS[k] || '#64748B',
    }))
    .sort((a, b) => b.accuracy - a.accuracy);

  return (
    <div className="p-6 space-y-6">
      {/* Top Controls */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-text-primary tracking-tight">Model Comparison</h1>
          <p className="text-xs text-text-secondary">Compare testing evaluation statistics across all 10 models.</p>
        </div>
        <div className="flex gap-3">
          <div className="px-4 py-2 bg-white border border-border rounded-lg flex items-center gap-2">
            <span className="text-xs font-bold text-text-secondary">RUN VERSION:</span>
            <select
              value={version}
              onChange={(e) => setVersion(e.target.value)}
              className="text-sm border-none bg-transparent font-bold p-0 focus:ring-0 outline-none cursor-pointer"
            >
              <option value="latest">Latest Trained Run</option>
              <option value="1.0.0">Version 1.0.0</option>
              <option value="1.0.1">Version 1.0.1</option>
              <option value="1.0.2">Version 1.0.2</option>
            </select>
          </div>
        </div>
      </div>

      {/* Regression Charts Row */}
      {regressionModels.length > 0 && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* R2 Score chart */}
          <div className="bg-white p-6 border border-border rounded-xl shadow-sm">
            <div className="mb-4">
              <h3 className="text-sm font-bold text-text-primary">R² Score Comparison (Higher is better)</h3>
              <p className="text-[11px] text-text-secondary">Coefficient of determination on held-out test split</p>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={regressionModels} layout="vertical" margin={{ top: 10, right: 20, left: 20, bottom: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" domain={[0, 1.0]} tick={{ fontSize: 10 }} />
                  <YAxis dataKey="name" type="category" tick={{ fontSize: 9 }} width={120} />
                  <Tooltip
                    formatter={(value: any) => [value.toFixed(4), 'R² Score']}
                    contentStyle={{ fontSize: '12px' }}
                  />
                  <Bar dataKey="r2" radius={[0, 4, 4, 0]}>
                    {regressionModels.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* RMSE Score chart */}
          <div className="bg-white p-6 border border-border rounded-xl shadow-sm">
            <div className="mb-4">
              <h3 className="text-sm font-bold text-text-primary">RMSE Comparison (Lower is better)</h3>
              <p className="text-[11px] text-text-secondary">Root Mean Square Error in dollar amount deviation</p>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={regressionModels} layout="vertical" margin={{ top: 10, right: 20, left: 20, bottom: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" tick={{ fontSize: 10 }} tickFormatter={(v) => `$${v / 1000}k`} />
                  <YAxis dataKey="name" type="category" tick={{ fontSize: 9 }} width={120} />
                  <Tooltip
                    formatter={(value: any) => [`$${value.toLocaleString()}`, 'RMSE']}
                    contentStyle={{ fontSize: '12px' }}
                  />
                  <Bar dataKey="rmse" radius={[0, 4, 4, 0]}>
                    {regressionModels.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* Grid of all models */}
      <div className="space-y-4">
        <h3 className="text-xs font-bold text-text-secondary uppercase tracking-wider">Detailed Model Parameters</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Regression Cards */}
          {regressionModels.map((model) => (
            <div key={model.id} className="bg-white border border-border rounded-xl p-5 shadow-sm hover:border-primary/20 transition-all flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: model.color }}></div>
                  <h4 className="text-sm font-bold text-text-primary">{model.name}</h4>
                </div>
                <div className="space-y-1.5 text-xs text-text-secondary">
                  <div className="flex justify-between">
                    <span>R² Score:</span>
                    <span className="font-bold text-text-primary tabular-nums">{model.r2.toFixed(4)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Test RMSE:</span>
                    <span className="font-bold text-text-primary tabular-nums">${model.rmse.toLocaleString('en-US', { maximumFractionDigits: 0 })}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Version:</span>
                    <span className="font-semibold text-text-primary">{model.version}</span>
                  </div>
                </div>
              </div>
              <div className="mt-4 pt-3 border-t border-border flex justify-between items-center text-[10px] text-text-secondary">
                <span>Trained At:</span>
                <span className="font-medium">{model.trainedAt ? new Date(model.trainedAt).toLocaleDateString() : 'N/A'}</span>
              </div>
            </div>
          ))}

          {/* Classification Cards */}
          {classificationModels.map((model) => (
            <div key={model.id} className="bg-white border border-border rounded-xl p-5 shadow-sm hover:border-primary/20 transition-all flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-2 mb-3">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: model.color }}></div>
                  <h4 className="text-sm font-bold text-text-primary">{model.name}</h4>
                </div>
                <div className="space-y-1.5 text-xs text-text-secondary">
                  <div className="flex justify-between">
                    <span>Accuracy:</span>
                    <span className="font-bold text-text-primary tabular-nums">{(model.accuracy * 100).toFixed(2)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>F1 Score:</span>
                    <span className="font-bold text-text-primary tabular-nums">{(model.f1 * 100).toFixed(2)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Version:</span>
                    <span className="font-semibold text-text-primary">{model.version}</span>
                  </div>
                </div>
              </div>
              <div className="mt-4 pt-3 border-t border-border flex justify-between items-center text-[10px] text-text-secondary">
                <span>Trained At:</span>
                <span className="font-medium">{model.trainedAt ? new Date(model.trainedAt).toLocaleDateString() : 'N/A'}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
