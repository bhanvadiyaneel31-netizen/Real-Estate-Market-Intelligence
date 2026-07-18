import React from 'react';
import { render, screen, cleanup } from '@testing-library/react';
import { Comparables } from '../pages/Comparables';
import { expect, test, vi, beforeEach } from 'vitest';

// Mock hook
vi.mock('../hooks/useRealEstate', () => ({
  useSimilarProperties: vi.fn(),
}));

import { useSimilarProperties } from '../hooks/useRealEstate';

beforeEach(() => {
  cleanup();
  vi.clearAllMocks();
});

test('renders Comparables in idle state', () => {
  const mockClearPrefilledSpecs = vi.fn();
  vi.mocked(useSimilarProperties).mockReturnValue({
    mutate: vi.fn(),
    data: undefined,
    isPending: false,
    error: null,
  } as any);

  render(<Comparables prefilledSpecs={null} clearPrefilledSpecs={mockClearPrefilledSpecs} />);
  expect(screen.getByText('Find Comparables')).toBeInTheDocument();
  expect(screen.getByText('KNN Retrieval Idle')).toBeInTheDocument();
});

test('renders Comparables loading state', () => {
  const mockClearPrefilledSpecs = vi.fn();
  vi.mocked(useSimilarProperties).mockReturnValue({
    mutate: vi.fn(),
    data: undefined,
    isPending: true,
    error: null,
  } as any);

  const { container } = render(<Comparables prefilledSpecs={null} clearPrefilledSpecs={mockClearPrefilledSpecs} />);
  expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
});

test('renders Comparables success state listings', () => {
  const mockClearPrefilledSpecs = vi.fn();
  vi.mocked(useSimilarProperties).mockReturnValue({
    mutate: vi.fn(),
    data: {
      similar_properties: [
        { title: 'Ames Villa', price: '$240,000', location: 'Somerst', bedrooms: 3, area: 1800, distance: 0.123 },
      ],
    },
    isPending: false,
    error: null,
  } as any);

  render(<Comparables prefilledSpecs={null} clearPrefilledSpecs={mockClearPrefilledSpecs} />);
  expect(screen.getByText('Ames Villa')).toBeInTheDocument();
  expect(screen.getByText('$240,000')).toBeInTheDocument();
  expect(screen.getByText('Distance Index: 0.1230')).toBeInTheDocument();
});

test('renders Comparables error state alert', () => {
  const mockClearPrefilledSpecs = vi.fn();
  vi.mocked(useSimilarProperties).mockReturnValue({
    mutate: vi.fn(),
    data: undefined,
    isPending: false,
    error: new Error('KNN failure') as any,
  } as any);

  render(<Comparables prefilledSpecs={null} clearPrefilledSpecs={mockClearPrefilledSpecs} />);
  expect(screen.getByText('KNN failure')).toBeInTheDocument();
});
