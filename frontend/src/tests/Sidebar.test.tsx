import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Sidebar } from '../components/Sidebar';
import { expect, test, vi } from 'vitest';

test('renders Sidebar and handles page changes', () => {
  const setActivePage = vi.fn();
  render(<Sidebar activePage="overview" setActivePage={setActivePage} />);

  // Asserts navigation links render
  expect(screen.getByText('Market Overview')).toBeInTheDocument();
  expect(screen.getByText('Price Predictor')).toBeInTheDocument();
  expect(screen.getByText('Similar Properties')).toBeInTheDocument();
  expect(screen.getByText('Listing Explorer')).toBeInTheDocument();
  expect(screen.getByText('Model Comparison')).toBeInTheDocument();

  // Clicking an inactive link triggers callback
  fireEvent.click(screen.getByText('Price Predictor'));
  expect(setActivePage).toHaveBeenCalledWith('predictor');
});
