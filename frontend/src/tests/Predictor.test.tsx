import React from 'react';
import { render, screen, cleanup } from '@testing-library/react';
import { Predictor } from '../pages/Predictor';
import { expect, test, vi, beforeEach } from 'vitest';

// Mock hook
vi.mock('../hooks/useRealEstate', () => ({
  usePredictPrice: vi.fn(),
}));

import { usePredictPrice } from '../hooks/useRealEstate';

beforeEach(() => {
  cleanup();
  vi.clearAllMocks();
});

test('renders Predictor specs form in idle state', () => {
  const mockOnFindSimilar = vi.fn();
  vi.mocked(usePredictPrice).mockReturnValue({
    mutate: vi.fn(),
    data: undefined,
    isPending: false,
    error: null,
  } as any);

  render(<Predictor onFindSimilar={mockOnFindSimilar} />);

  expect(screen.getByText('Property Valuation Specifications')).toBeInTheDocument();
  expect(screen.getByText('Living Area (Sq Ft)')).toBeInTheDocument();
  expect(screen.getByText('Bedrooms')).toBeInTheDocument();
  expect(screen.getByRole('button', { name: 'Run Valuation' })).toBeInTheDocument();
});

test('renders Predictor loading state', () => {
  const mockOnFindSimilar = vi.fn();
  vi.mocked(usePredictPrice).mockReturnValue({
    mutate: vi.fn(),
    data: undefined,
    isPending: true,
    error: null,
  } as any);

  render(<Predictor onFindSimilar={mockOnFindSimilar} />);
  expect(screen.getByRole('button', { name: 'Calculating...' })).toBeInTheDocument();
});

test('renders Predictor success state', () => {
  const mockOnFindSimilar = vi.fn();
  vi.mocked(usePredictPrice).mockReturnValue({
    mutate: vi.fn(),
    data: {
      estimated_price: 250000,
      confidence: 0.88,
      price_tier: 'Above-Median',
      is_below_market_value: false,
      proxy_explainability_factors: [
        { feature: 'area', impact: 12000 },
      ],
    },
    isPending: false,
    error: null,
  } as any);

  render(<Predictor onFindSimilar={mockOnFindSimilar} />);
  expect(screen.getByText('$250,000')).toBeInTheDocument();
  expect(screen.getByText(/Estimated Accuracy/i)).toBeInTheDocument();
  expect(screen.getByText(/Surrogate Proxy Price Drivers/i)).toBeInTheDocument();
});

test('renders Predictor error state', () => {
  const mockOnFindSimilar = vi.fn();
  vi.mocked(usePredictPrice).mockReturnValue({
    mutate: vi.fn(),
    data: undefined,
    isPending: false,
    error: { message: 'Internal server error' } as any,
  } as any);

  render(<Predictor onFindSimilar={mockOnFindSimilar} />);
  expect(screen.getByText('Internal server error')).toBeInTheDocument();
});
