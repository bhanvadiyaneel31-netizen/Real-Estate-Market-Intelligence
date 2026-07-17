import React, { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { Overview } from './pages/Overview';
import { Predictor } from './pages/Predictor';
import { Comparables } from './pages/Comparables';
import { Explorer } from './pages/Explorer';
import { ModelComparison } from './pages/ModelComparison';
import type { PredictRequest } from './types';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: false,
    },
  },
});

export const AppContent: React.FC = () => {
  const [activePage, setActivePage] = useState<string>('overview');
  const [prefilledSpecs, setPrefilledSpecs] = useState<PredictRequest | null>(null);

  // Navigates from Predictor results card to Comparables tab, setting pre-filled specifications
  const handleFindSimilar = (specs: PredictRequest) => {
    setPrefilledSpecs(specs);
    setActivePage('comparables');
  };

  const getPageTitle = () => {
    switch (activePage) {
      case 'overview':
        return 'Market Overview';
      case 'predictor':
        return 'Price Predictor';
      case 'comparables':
        return 'Similar Properties Finder';
      case 'explorer':
        return 'Listing Explorer';
      case 'comparison':
        return 'Model Comparison';
      default:
        return 'EstateAnalytics';
    }
  };

  const renderActivePage = () => {
    switch (activePage) {
      case 'overview':
        return <Overview />;
      case 'predictor':
        return <Predictor onFindSimilar={handleFindSimilar} />;
      case 'comparables':
        return (
          <Comparables
            prefilledSpecs={prefilledSpecs}
            clearPrefilledSpecs={() => setPrefilledSpecs(null)}
          />
        );
      case 'explorer':
        return <Explorer />;
      case 'comparison':
        return <ModelComparison />;
      default:
        return <Overview />;
    }
  };

  return (
    <div className="bg-neutral-background text-text-primary min-h-screen">
      {/* Sidebar Panel */}
      <Sidebar activePage={activePage} setActivePage={setActivePage} />

      {/* Main Page Layout */}
      <div className="ml-64 flex flex-col min-h-screen">
        {/* Top Header bar */}
        <Header title={getPageTitle()} />

        {/* Content Canvas */}
        <main className="flex-1 bg-neutral-background overflow-y-auto">
          {renderActivePage()}
        </main>
      </div>
    </div>
  );
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
}

export default App;
