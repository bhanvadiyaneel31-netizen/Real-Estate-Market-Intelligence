import React from 'react';
import { render, screen, cleanup } from '@testing-library/react';
import { Explorer } from '../pages/Explorer';
import { expect, test, vi, beforeEach } from 'vitest';

// Mock hook
vi.mock('../hooks/useRealEstate', () => ({
  useListings: vi.fn(),
}));

import { useListings } from '../hooks/useRealEstate';

beforeEach(() => {
  cleanup();
  vi.clearAllMocks();
});

test('renders Explorer loading state', () => {
  vi.mocked(useListings).mockReturnValue({
    data: undefined,
    isLoading: true,
    error: null,
  } as any);

  const { container } = render(<Explorer />);
  expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
});

test('renders Explorer empty state when no listings found', () => {
  vi.mocked(useListings).mockReturnValue({
    data: { listings: [], total: 0 },
    isLoading: false,
    error: null,
  } as any);

  render(<Explorer />);
  expect(screen.getByText('No Listings Found')).toBeInTheDocument();
});

test('renders Explorer success state table data', () => {
  vi.mocked(useListings).mockReturnValue({
    data: {
      listings: [
        {
          id: 1,
          external_id: '123',
          price: 245000,
          bedrooms: 3,
          area: 1750,
          neighborhood: 'Somerst',
          has_central_air: 1,
          has_garage: 1,
          has_pool: 0,
          fireplace_count: 1,
          price_per_sqft: 140.0,
          is_below_market_value: true,
          feature_set_version: '1.0.0',
        },
      ],
      total: 1,
    },
    isLoading: false,
    error: null,
  } as any);

  render(<Explorer />);
  expect(screen.getByText('Neighborhood: Somerst')).toBeInTheDocument();
  expect(screen.getByText('$245,000')).toBeInTheDocument();
  expect(screen.getByText('Under-Market Value')).toBeInTheDocument();
});

test('renders Explorer error state card', () => {
  vi.mocked(useListings).mockReturnValue({
    data: undefined,
    isLoading: false,
    error: new Error('Failed to fetch from DB') as any,
  } as any);

  render(<Explorer />);
  expect(screen.getByText('Failed to load listings')).toBeInTheDocument();
  expect(screen.getByText('Failed to fetch from DB')).toBeInTheDocument();
});
