import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { usePredictPrice } from '../hooks/useRealEstate';
import { AMES_NEIGHBORHOODS } from '../api/constants';
import type { PredictRequest } from '../types';

// Zod validation schema matching backend constraints
const predictSchema = z.object({
  bedrooms: z.number().int().min(0, "Bedrooms must be 0 or more").max(5, "Max 5 bedrooms"),
  area: z.number().positive("Living area must be greater than 0"),
  neighborhood: z.string().min(1, "Please select a neighborhood"),
  has_central_air: z.number().min(0).max(1),
  has_garage: z.number().min(0).max(1),
  has_pool: z.number().min(0).max(1),
  fireplace_count: z.number().int().min(0, "Fireplaces must be 0 or more").max(3, "Max 3 fireplaces"),
  description_text: z.string().optional(),
});

interface PredictorProps {
  onFindSimilar: (specs: PredictRequest) => void;
}

export const Predictor: React.FC<PredictorProps> = ({ onFindSimilar }) => {
  const predictMutation = usePredictPrice();

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors }
  } = useForm<PredictRequest>({
    resolver: zodResolver(predictSchema),
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

  const onSubmit = (data: PredictRequest) => {
    predictMutation.mutate(data);
  };

  const hasCentralAir = watch('has_central_air');
  const hasGarage = watch('has_garage');
  const hasPool = watch('has_pool');

  const result = predictMutation.data;
  const isPending = predictMutation.isPending;
  const submitError = predictMutation.error as any;

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Form Specs Panel */}
          <div className="lg:col-span-6 bg-white border border-border rounded-xl p-6 shadow-sm flex flex-col justify-between">
            <div>
              <div className="mb-6">
                <h3 className="text-lg font-bold text-text-primary">Property Valuation Specifications</h3>
                <p className="text-xs text-text-secondary">Provide the physical specs of the home to estimate its value via XGBoost.</p>
              </div>

              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  {/* Living Area */}
                  <div>
                    <label className="block text-xs font-semibold text-text-primary mb-1">Living Area (Sq Ft)</label>
                    <input
                      type="number"
                      {...register('area', { valueAsNumber: true })}
                      placeholder="e.g. 1800"
                      className="w-full bg-neutral-background border border-border rounded px-3 py-2 text-sm focus:ring-1 focus:ring-primary outline-none transition-all"
                    />
                    {errors.area && <p className="text-[11px] text-danger mt-1">{errors.area.message}</p>}
                  </div>

                  {/* Neighborhood */}
                  <div>
                    <label className="block text-xs font-semibold text-text-primary mb-1">Neighborhood</label>
                    <select
                      {...register('neighborhood')}
                      className="w-full bg-neutral-background border border-border rounded px-3 py-2 text-sm focus:ring-1 focus:ring-primary outline-none transition-all cursor-pointer"
                    >
                      <option value="">Select Neighborhood</option>
                      {AMES_NEIGHBORHOODS.map(n => (
                        <option key={n} value={n}>{n}</option>
                      ))}
                    </select>
                    {errors.neighborhood && <p className="text-[11px] text-danger mt-1">{errors.neighborhood.message}</p>}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  {/* Bedrooms */}
                  <div>
                    <label className="block text-xs font-semibold text-text-primary mb-1">Bedrooms</label>
                    <select
                      {...register('bedrooms', { valueAsNumber: true })}
                      className="w-full bg-neutral-background border border-border rounded px-3 py-2 text-sm focus:ring-1 focus:ring-primary outline-none transition-all cursor-pointer"
                    >
                      {[0, 1, 2, 3, 4, 5].map(b => (
                        <option key={b} value={b}>{b}</option>
                      ))}
                    </select>
                    {errors.bedrooms && <p className="text-[11px] text-danger mt-1">{errors.bedrooms.message}</p>}
                  </div>

                  {/* Fireplace Count */}
                  <div>
                    <label className="block text-xs font-semibold text-text-primary mb-1">Fireplace Count</label>
                    <select
                      {...register('fireplace_count', { valueAsNumber: true })}
                      className="w-full bg-neutral-background border border-border rounded px-3 py-2 text-sm focus:ring-1 focus:ring-primary outline-none transition-all cursor-pointer"
                    >
                      {[0, 1, 2, 3].map(f => (
                        <option key={f} value={f}>{f}</option>
                      ))}
                    </select>
                    {errors.fireplace_count && <p className="text-[11px] text-danger mt-1">{errors.fireplace_count.message}</p>}
                  </div>
                </div>

                {/* Amenity Switches */}
                <div>
                  <label className="block text-xs font-semibold text-text-primary mb-2">Amenities</label>
                  <div className="flex gap-4">
                    {/* Central Air */}
                    <button
                      type="button"
                      onClick={() => setValue('has_central_air', hasCentralAir === 1 ? 0 : 1)}
                      className={`flex-1 py-2 px-3 border rounded text-xs font-bold transition-all ${
                        hasCentralAir === 1
                          ? 'border-primary bg-primary/5 text-primary'
                          : 'border-border bg-white text-text-secondary'
                      }`}
                    >
                      Central Air
                    </button>
                    {/* Garage */}
                    <button
                      type="button"
                      onClick={() => setValue('has_garage', hasGarage === 1 ? 0 : 1)}
                      className={`flex-1 py-2 px-3 border rounded text-xs font-bold transition-all ${
                        hasGarage === 1
                          ? 'border-primary bg-primary/5 text-primary'
                          : 'border-border bg-white text-text-secondary'
                      }`}
                    >
                      Garage
                    </button>
                    {/* Pool */}
                    <button
                      type="button"
                      onClick={() => setValue('has_pool', hasPool === 1 ? 0 : 1)}
                      className={`flex-1 py-2 px-3 border rounded text-xs font-bold transition-all ${
                        hasPool === 1
                          ? 'border-primary bg-primary/5 text-primary'
                          : 'border-border bg-white text-text-secondary'
                      }`}
                    >
                      Swimming Pool
                    </button>
                  </div>
                </div>

                {/* Description Text */}
                <div>
                  <label className="block text-xs font-semibold text-text-primary mb-1">
                    Property Description (Optional NLP analysis)
                  </label>
                  <textarea
                    rows={3}
                    {...register('description_text')}
                    placeholder="Enter descriptive text about the property..."
                    className="w-full bg-neutral-background border border-border rounded px-3 py-2 text-xs focus:ring-1 focus:ring-primary outline-none transition-all"
                  />
                </div>

                {/* Submit button */}
                <button
                  type="submit"
                  disabled={isPending}
                  className="w-full bg-primary text-white py-3 rounded-lg font-bold text-sm hover:opacity-90 active:scale-[0.98] transition-all shadow-md shadow-primary/10 flex items-center justify-center gap-2"
                >
                  {isPending ? 'Calculating...' : 'Run Valuation'}
                </button>
              </form>
            </div>

            {submitError && (
              <div className="mt-4 p-3 bg-red-50 border border-danger/10 text-danger text-xs rounded-lg flex items-center gap-2">
                <span className="material-symbols-outlined text-sm">error</span>
                <span>{submitError.message || 'Valuation failed. Check backend service.'}</span>
              </div>
            )}
          </div>

          {/* Results Display Panel */}
          <div className="lg:col-span-6 space-y-6">
            {isPending ? (
              // Loading Skeleton
              <div className="bg-white border border-border rounded-xl p-6 shadow-sm space-y-6 animate-pulse">
                <div className="h-6 w-32 bg-slate-200 rounded"></div>
                <div className="h-16 w-full bg-slate-200 rounded"></div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="h-20 bg-slate-200 rounded"></div>
                  <div className="h-20 bg-slate-200 rounded"></div>
                </div>
                <div className="h-40 w-full bg-slate-200 rounded"></div>
              </div>
            ) : result ? (
              // Real Results Card
              <div className="space-y-6">
                {/* Main Prediction Details */}
                <div className="bg-white border border-border rounded-xl p-6 shadow-sm">
                  <div className="mb-4">
                    <h3 className="text-sm font-bold text-text-secondary uppercase tracking-wider">Estimated Property Value</h3>
                    <h2 className="text-4xl font-extrabold text-primary tabular-nums mt-1">
                      ${result.estimated_price.toLocaleString('en-US', { maximumFractionDigits: 2 })}
                    </h2>
                  </div>

                  <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border">
                    {/* Estimated Accuracy */}
                    <div>
                      <p className="text-[10px] text-text-secondary font-bold uppercase">Estimated Accuracy</p>
                      <p className="text-base font-bold text-text-primary tabular-nums mt-0.5">
                        {(result.confidence * 100).toFixed(2)}%
                      </p>
                      <p className="text-[9px] text-text-secondary mt-0.5 leading-tight">
                        Based on model's typical prediction error (test RMSE).
                      </p>
                    </div>

                    {/* Price Tier */}
                    <div>
                      <p className="text-[10px] text-text-secondary font-bold uppercase">Estimated Tier</p>
                      <p className="text-base font-bold text-text-primary mt-0.5">
                        {result.price_tier}
                      </p>
                      <p className="text-[9px] text-text-secondary mt-0.5 leading-tight">
                        Calculated price tertile relative to dataset.
                      </p>
                    </div>
                  </div>

                  {/* Below Market Value Status */}
                  <div className="mt-6">
                    {result.is_below_market_value ? (
                      <div className="p-3 bg-success/10 border border-success/20 rounded-lg flex items-center gap-2.5 text-success">
                        <span className="material-symbols-outlined text-base">verified</span>
                        <div className="text-xs">
                          <p className="font-bold">Under-Market Value</p>
                          <p className="opacity-90">This estimate is below the median asking price for listings in this neighborhood.</p>
                        </div>
                      </div>
                    ) : (
                      <div className="p-3 bg-warning/10 border border-warning/20 rounded-lg flex items-center gap-2.5 text-warning">
                        <span className="material-symbols-outlined text-base">error_outline</span>
                        <div className="text-xs">
                          <p className="font-bold">Above neighborhood median value</p>
                          <p className="opacity-90">This estimate exceeds the current median price in this neighborhood.</p>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Surrogate Explainability Card */}
                <div className="bg-white border border-border rounded-xl p-6 shadow-sm">
                  <div className="mb-4">
                    <h3 className="text-xs font-bold text-text-secondary uppercase tracking-wider">
                      Surrogate Proxy Price Drivers
                    </h3>
                    <p className="text-[10px] text-text-secondary leading-normal">
                      Decision Tree Explanation (local surrogate mapping of XGBoost estimators, not raw model weights).
                    </p>
                  </div>

                  <div className="space-y-3">
                    {result.proxy_explainability_factors.map((factor, index) => {
                      const isPositive = factor.impact >= 0;
                      return (
                        <div key={index} className="flex justify-between items-center text-xs">
                          <span className="capitalize text-text-secondary font-medium w-1/3 truncate">
                            {factor.feature.replace('_count', '').replace('has_', '').replace('_', ' ')}
                          </span>
                          <span className={`w-1/4 text-right font-bold tabular-nums ${isPositive ? 'text-success' : 'text-danger'}`}>
                            {isPositive ? '+' : ''}${factor.impact.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                          </span>
                        </div>
                      );
                    })}
                  </div>

                  <div className="mt-6 pt-4 border-t border-border flex justify-end">
                    <button
                      onClick={() => onFindSimilar(watch() as PredictRequest)}
                      className="px-4 py-2 border border-primary text-primary font-bold text-xs rounded hover:bg-primary/5 transition-all flex items-center gap-1.5"
                    >
                      <span className="material-symbols-outlined text-sm">location_searching</span>
                      <span>Find 5 Similar Listings</span>
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              // Empty/Idle State
              <div className="h-full bg-white border border-border rounded-xl p-8 flex flex-col items-center justify-center text-center space-y-4 min-h-[400px]">
                <span className="material-symbols-outlined text-text-secondary text-5xl">analytics</span>
                <div>
                  <h3 className="text-base font-bold text-text-primary">Ready for Evaluation</h3>
                  <p className="text-xs text-text-secondary max-w-sm mt-1">
                    Input specifications on the left and run valuation to display pricing benchmarks, price driving factors, and comparisons.
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
