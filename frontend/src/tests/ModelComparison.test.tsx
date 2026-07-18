import React from 'react';
import { render, screen, cleanup } from '@testing-library/react';
import { ModelComparison } from '../pages/ModelComparison';
import { expect, test, vi, beforeEach } from 'vitest';

// Mock hook
vi.mock('../hooks/useRealEstate', () => ({
  useModelMetrics: vi.fn(),
}));

import { useModelMetrics } from '../hooks/useRealEstate';

beforeEach(() => {
  cleanup();
  vi.clearAllMocks();
});

test('renders ModelComparison loading state', () => {
  vi.mocked(useModelMetrics).mockReturnValue({
    data: undefined,
    isLoading: true,
    error: null,
  } as any);

  const { container } = render(<ModelComparison />);
  expect(container.querySelector('.animate-pulse')).toBeInTheDocument();
});

test('renders ModelComparison empty state when no metrics found', () => {
  vi.mocked(useModelMetrics).mockReturnValue({
    data: {},
    isLoading: false,
    error: null,
  } as any);

  render(<ModelComparison />);
  expect(screen.getByText('No Metrics Found')).toBeInTheDocument();
});

test('renders ModelComparison success state chart and parameters', () => {
  vi.mocked(useModelMetrics).mockReturnValue({
    data: {
      xgboost_regression: {
        feature_set_version: '1.0.0',
        trained_at: '2026-07-17T12:00:00Z',
        metrics: { r2: 0.8123, rmse: 28000.5 },
      },
      logistic_classification: {
        feature_set_version: '1.0.0',
        trained_at: '2026-07-17T12:00:00Z',
        metrics: { accuracy: 0.85, f1: 0.845 },
      },
    },
    isLoading: false,
    error: null,
  } as any);

  render(<ModelComparison />);
  expect(screen.getByText('XGBoost Regressor (Production)')).toBeInTheDocument();
  expect(screen.getByText('Logistic Regression Classifier')).toBeInTheDocument();
  expect(screen.getByText('0.8123')).toBeInTheDocument();
  expect(screen.getByText('85.00%')).toBeInTheDocument();
});

test('renders ModelComparison error state message', () => {
  vi.mocked(useModelMetrics).mockReturnValue({
    data: undefined,
    isLoading: false,
    error: new Error('Metrics DB missing') as any,
  } as any);

  render(<ModelComparison />);
  expect(screen.getByText('Error Loading Model Metrics')).toBeInTheDocument();
  expect(screen.getByText('Metrics DB missing')).toBeInTheDocument();
});
