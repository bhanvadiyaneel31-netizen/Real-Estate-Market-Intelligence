import React from 'react';
import { render, screen, cleanup } from '@testing-library/react';
import { Overview } from '../pages/Overview';
import { expect, test, vi, beforeEach } from 'vitest';

// Mock hook
vi.mock('../hooks/useRealEstate', () => ({
  useMarketTrends: vi.fn(),
}));

import { useMarketTrends } from '../hooks/useRealEstate';

beforeEach(() => {
  cleanup();
  vi.clearAllMocks();
});

test('renders Overview loading state Skeletons', () => {
  vi.mocked(useMarketTrends).mockReturnValue({
    data: undefined,
    isLoading: true,
    error: null,
  } as any);

  const { container } = render(<Overview />);
  expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
});

test('renders Overview success state data', () => {
  vi.mocked(useMarketTrends).mockReturnValue({
    data: {
      neighborhood_trends: [
        { neighborhood: 'CollgCr', median_price: 185000, total_listings: 1460, median_price_per_sqft: 120.5 },
      ],
    },
    isLoading: false,
    error: null,
  } as any);

  render(<Overview />);
  expect(screen.getByText('$185,000')).toBeInTheDocument();
  expect(screen.getByText('1,460')).toBeInTheDocument();
  expect(screen.getByText('$120.5/sqft')).toBeInTheDocument();
  expect(screen.getByText('Median Price by Neighborhood')).toBeInTheDocument();
});

test('renders Overview error state card', () => {
  vi.mocked(useMarketTrends).mockReturnValue({
    data: undefined,
    isLoading: false,
    error: { message: 'Network failure' } as any,
  } as any);

  render(<Overview />);
  expect(screen.getByText('Error Loading Market Overview')).toBeInTheDocument();
  expect(screen.getByText('Network failure')).toBeInTheDocument();
});
