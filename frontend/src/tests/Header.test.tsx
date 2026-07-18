import React from 'react';
import { render, screen } from '@testing-library/react';
import { Header } from '../components/Header';
import { expect, test } from 'vitest';

test('renders Header and displays active view title', () => {
  render(<Header title="Price Predictor" />);

  // Asserts active view title is displayed
  expect(screen.getByRole('heading', { name: 'Price Predictor' })).toBeInTheDocument();
  
  // Asserts search placeholder and profile elements render
  expect(screen.getByPlaceholderText('Search markets, zip codes...')).toBeInTheDocument();
  expect(screen.getByText('notifications')).toBeInTheDocument();
  expect(screen.getByText('account_circle')).toBeInTheDocument();
});
