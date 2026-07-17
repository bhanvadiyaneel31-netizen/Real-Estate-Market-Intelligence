import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useSimilarProperties } from '../hooks/useRealEstate';
import { AMES_NEIGHBORHOODS } from '../api/constants';
import type { PredictRequest } from '../types';

interface ComparablesProps {
  prefilledSpecs: PredictRequest | null;
  clearPrefilledSpecs: () => void;
}

export const Comparables: React.FC<ComparablesProps> = ({ prefilledSpecs, clearPrefilledSpecs }) => {
  const similarMutation = useSimilarProperties();

  const {
    register,
    handleSubmit,
    setValue,
    reset,
  } = useForm<PredictRequest>({
    defaultValues: {
      bedrooms: 3,
      area: 1800,
      neighborhood: 'Somerst',
      has_central_air: 1,
      has_garage: 1,
      has_pool: 0,
      fireplace_count: 1,
      description_text: '',
    }
  });

  // Automatically submit if prefilled specs are passed from the Predictor page
  useEffect(() => {
    if (prefilledSpecs) {
      reset(prefilledSpecs);
      similarMutation.mutate({ ...prefilledSpecs, k: 5 });
      clearPrefilledSpecs(); // Clear in-memory state after consumption
    }
  }, [prefilledSpecs, reset]);

  const onSubmit = (data: PredictRequest) => {
    similarMutation.mutate({ ...data, k: 5 });
  };

  const results = similarMutation.data?.similar_properties || [];
  const isPending = similarMutation.isPending;
  const submitError = similarMutation.error as any;

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Query specifications form */}
          <div className="lg:col-span-4 bg-white border border-border rounded-xl p-6 shadow-sm h-fit">
            <div className="mb-4">
              <h3 className="text-base font-bold text-text-primary">Find Comparables</h3>
              <p className="text-xs text-text-secondary mt-1">
                Retrieve similar properties using KNN distance search on key physical characteristics.
              </p>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              {/* Area */}
              <div>
                <label className="block text-[11px] font-bold text-text-primary mb-1">Living Area (Sq Ft)</label>
                <input
                  type="number"
                  {...register('area', { valueAsNumber: true, required: true })}
                  placeholder="e.g. 1800"
                  className="w-full bg-neutral-background border border-border rounded px-3 py-1.5 text-xs focus:ring-1 focus:ring-primary outline-none transition-all"
                />
              </div>

              {/* Neighborhood */}
              <div>
                <label className="block text-[11px] font-bold text-text-primary mb-1">Neighborhood</label>
                <select
                  {...register('neighborhood', { required: true })}
                  className="w-full bg-neutral-background border border-border rounded px-3 py-1.5 text-xs focus:ring-1 focus:ring-primary outline-none transition-all cursor-pointer"
                >
                  {AMES_NEIGHBORHOODS.map(n => (
                    <option key={n} value={n}>{n}</option>
                  ))}
                </select>
              </div>

              {/* Bedrooms */}
              <div>
                <label className="block text-[11px] font-bold text-text-primary mb-1">Bedrooms</label>
                <select
                  {...register('bedrooms', { valueAsNumber: true })}
                  className="w-full bg-neutral-background border border-border rounded px-3 py-1.5 text-xs focus:ring-1 focus:ring-primary outline-none transition-all cursor-pointer"
                >
                  {[0, 1, 2, 3, 4, 5].map(b => (
                    <option key={b} value={b}>{b}</option>
                  ))}
                </select>
              </div>

              {/* Fireplaces */}
              <div>
                <label className="block text-[11px] font-bold text-text-primary mb-1">Fireplace Count</label>
                <select
                  {...register('fireplace_count', { valueAsNumber: true })}
                  className="w-full bg-neutral-background border border-border rounded px-3 py-1.5 text-xs focus:ring-1 focus:ring-primary outline-none transition-all cursor-pointer"
                >
                  {[0, 1, 2, 3].map(f => (
                    <option key={f} value={f}>{f}</option>
                  ))}
                </select>
              </div>

              {/* Switches */}
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => setValue('has_central_air', 1)}
                  className="py-1 px-2 border border-border rounded text-[10px] bg-slate-50 text-text-primary"
                >
                  Central Air
                </button>
                <button
                  type="button"
                  onClick={() => setValue('has_garage', 1)}
                  className="py-1 px-2 border border-border rounded text-[10px] bg-slate-50 text-text-primary"
                >
                  Garage
                </button>
                <button
                  type="button"
                  onClick={() => setValue('has_pool', 1)}
                  className="py-1 px-2 border border-border rounded text-[10px] bg-slate-50 text-text-primary"
                >
                  Pool
                </button>
              </div>

              <button
                type="submit"
                disabled={isPending}
                className="w-full bg-primary text-white py-2.5 rounded font-bold text-xs hover:opacity-90 active:scale-[0.98] transition-all"
              >
                {isPending ? 'Searching...' : 'Search Comparables'}
              </button>
            </form>

            {submitError && (
              <div className="mt-4 p-3 bg-red-50 border border-danger/10 text-danger text-xs rounded-lg flex items-center gap-2">
                <span className="material-symbols-outlined text-sm">error</span>
                <span>{submitError.message || 'Error executing KNN search.'}</span>
              </div>
            )}
          </div>

          {/* Results grid */}
          <div className="lg:col-span-8 space-y-4">
            {isPending ? (
              // Loading Skeleton
              <div className="space-y-4 animate-pulse">
                <div className="h-28 bg-slate-200 rounded-xl"></div>
                <div className="h-28 bg-slate-200 rounded-xl"></div>
                <div className="h-28 bg-slate-200 rounded-xl"></div>
              </div>
            ) : results.length > 0 ? (
              // Result Listings
              <div className="space-y-4">
                <div className="flex justify-between items-center px-2">
                  <h4 className="text-xs font-bold text-text-secondary uppercase tracking-wider">Top 5 Matching Listings Found</h4>
                  <span className="text-[10px] bg-slate-100 text-text-secondary px-2.5 py-1 rounded-full font-medium">
                    Engine: knn_retrieval
                  </span>
                </div>

                <div className="space-y-3">
                  {results.map((prop, idx) => (
                    <div
                      key={prop.external_id || idx}
                      className="bg-white border border-border p-5 rounded-xl shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4 hover:border-primary/20 transition-colors"
                    >
                      <div>
                        <div className="flex items-center gap-2.5 mb-1.5">
                          <span className="text-xs font-bold bg-primary/5 text-primary px-2.5 py-0.5 rounded-full">
                            Match Rank #{idx + 1}
                          </span>
                          <span className="text-[10px] text-text-secondary font-medium">
                            Distance Index: {prop.distance.toFixed(4)}
                          </span>
                        </div>
                        <h4 className="text-sm font-bold text-text-primary">{prop.title}</h4>
                        <p className="text-[11px] text-text-secondary mt-1 flex items-center gap-1.5">
                          <span className="material-symbols-outlined text-xs">location_on</span>
                          {prop.location} • {prop.bedrooms} Bed • {prop.area} Sq Ft
                        </p>
                      </div>

                      <div className="text-right">
                        <span className="text-lg font-extrabold text-primary tabular-nums block">
                          {prop.price}
                        </span>
                        <span className="text-[10px] text-text-secondary block mt-1">
                          Estimated asking value
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              // Empty/Idle State
              <div className="h-full bg-white border border-border rounded-xl p-8 flex flex-col items-center justify-center text-center space-y-4 min-h-[400px]">
                <span className="material-symbols-outlined text-text-secondary text-5xl">location_searching</span>
                <div>
                  <h3 className="text-base font-bold text-text-primary">KNN Retrieval Idle</h3>
                  <p className="text-xs text-text-secondary max-w-sm mt-1">
                    Provide property specifications on the left to pull comparable listings from our database.
                  </p>
                </div>
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
};
