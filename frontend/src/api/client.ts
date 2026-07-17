import axios from 'axios';
import type {
  PredictRequest,
  PredictResponse,
  SimilarPropertiesRequest,
  SimilarPropertiesResponse,
  MarketTrendsResponse,
  ModelMetricsResponse,
  ListingsResponse
} from '../types';

const baseURL = import.meta.env.VITE_API_BASE_URL;
if (!baseURL) {
  throw new Error("VITE_API_BASE_URL environment variable is not defined! Please configure it in your .env file.");
}

const apiClient = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const predictPrice = async (payload: PredictRequest): Promise<PredictResponse> => {
  const response = await apiClient.post<PredictResponse>('/predict/', payload);
  return response.data;
};

export const getSimilarProperties = async (payload: SimilarPropertiesRequest): Promise<SimilarPropertiesResponse> => {
  const response = await apiClient.post<SimilarPropertiesResponse>('/similar-properties/', payload);
  return response.data;
};

export const getMarketTrends = async (version: string = '1.0.0'): Promise<MarketTrendsResponse> => {
  const response = await apiClient.get<MarketTrendsResponse>(`/market-trend/?version=${version}`);
  return response.data;
};

export const getModelMetrics = async (version: string = 'latest'): Promise<ModelMetricsResponse> => {
  const response = await apiClient.get<ModelMetricsResponse>(`/model-metrics/?version=${version}`);
  return response.data;
};

export const getListings = async (params: {
  page?: number;
  limit?: number;
  neighborhood?: string;
  min_price?: number;
  max_price?: number;
  min_area?: number;
  max_area?: number;
  is_below_market_value?: number;
  version?: string;
}): Promise<ListingsResponse> => {
  const response = await apiClient.get<ListingsResponse>('/listings/', { params });
  return response.data;
};
