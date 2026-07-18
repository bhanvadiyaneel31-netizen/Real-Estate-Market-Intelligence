import React from 'react';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { usePredictPrice } from '../hooks/useRealEstate';
import * as api from '../api/client';
import { expect, test, vi } from 'vitest';

vi.mock('../api/client', () => ({
  predictPrice: vi.fn(),
  getSimilarProperties: vi.fn(),
  getMarketTrends: vi.fn(),
  getModelMetrics: vi.fn(),
  getListings: vi.fn(),
}));

// Mock axios.isAxiosError
vi.mock('axios', async (importOriginal) => {
  const original = await importOriginal<typeof import('axios')>();
  return {
    default: original,
    ...original,
    isAxiosError: (error: any) => !!error.isAxiosError,
  };
});

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    React.createElement(QueryClientProvider, { client: queryClient }, children)
  );
};

test('usePredictPrice handles 400/422 validation error branching', async () => {
  const mockError = {
    isAxiosError: true,
    response: {
      status: 400,
      data: { detail: 'Invalid parameters' },
    },
  };

  vi.mocked(api.predictPrice).mockRejectedValue(mockError);

  const wrapper = createWrapper();
  const { result } = renderHook(() => usePredictPrice(), { wrapper });

  result.current.mutate({
    bedrooms: -1,
    area: 1200,
    neighborhood: 'Somerst',
    has_central_air: 1,
    has_garage: 1,
    has_pool: 0,
    fireplace_count: 0
  });

  await waitFor(() => expect(result.current.isError).toBe(true));
  expect(result.current.error).toEqual({
    type: 'validation',
    message: 'Invalid input data. Please verify your entries.',
    details: 'Invalid parameters',
  });
});

test('usePredictPrice handles 404 not found error branching', async () => {
  const mockError = {
    isAxiosError: true,
    response: {
      status: 404,
    },
  };

  vi.mocked(api.predictPrice).mockRejectedValue(mockError);

  const wrapper = createWrapper();
  const { result } = renderHook(() => usePredictPrice(), { wrapper });

  result.current.mutate({
    bedrooms: 3,
    area: 1200,
    neighborhood: 'Somerst',
    has_central_air: 1,
    has_garage: 1,
    has_pool: 0,
    fireplace_count: 0
  });

  await waitFor(() => expect(result.current.isError).toBe(true));
  expect(result.current.error).toEqual({
    type: 'not_found',
    message: 'The requested resource could not be found.',
  });
});

test('usePredictPrice handles 500 server error branching', async () => {
  const mockError = {
    isAxiosError: true,
    response: {
      status: 500,
    },
  };

  vi.mocked(api.predictPrice).mockRejectedValue(mockError);

  const wrapper = createWrapper();
  const { result } = renderHook(() => usePredictPrice(), { wrapper });

  result.current.mutate({
    bedrooms: 3,
    area: 1200,
    neighborhood: 'Somerst',
    has_central_air: 1,
    has_garage: 1,
    has_pool: 0,
    fireplace_count: 0
  });

  await waitFor(() => expect(result.current.isError).toBe(true));
  expect(result.current.error).toEqual({
    type: 'server',
    message: 'Something went wrong on our end. Please try again later.',
  });
});
