import React from 'react';
import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock Recharts responsive container as it has rendering issues in jsdom
vi.mock('recharts', async (importOriginal) => {
  const original = await importOriginal<typeof import('recharts')>();
  return {
    ...original,
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
      React.createElement('div', { style: { width: '100%', height: '100%' } }, children)
    ),
  };
});
