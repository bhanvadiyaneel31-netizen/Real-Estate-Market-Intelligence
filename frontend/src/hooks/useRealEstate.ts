import { useQuery, useMutation } from '@tanstack/react-query';
import axios from 'axios';
import * as api from '../api/client';
import type {
  PredictRequest,
  SimilarPropertiesRequest,
  ListingsResponse
} from '../types';

export interface ApiError {
  type: 'validation' | 'not_found' | 'server';
  message: string;
  details?: any;
}

const handleApiError = (error: unknown): ApiError => {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    if (status === 400 || status === 422) {
      return {
        type: 'validation',
        message: 'Invalid input data. Please verify your entries.',
        details: error.response?.data?.detail,
      };
    }
    if (status === 404) {
      return {
        type: 'not_found',
        message: 'The requested resource could not be found.',
      };
    }
  }
  return {
    type: 'server',
    message: 'Something went wrong on our end. Please try again later.',
  };
};

export const usePredictPrice = () => {
  return useMutation({
    mutationFn: async (payload: PredictRequest) => {
      try {
        return await api.predictPrice(payload);
      } catch (error) {
        throw handleApiError(error);
      }
    },
  });
};

export const useSimilarProperties = () => {
  return useMutation({
    mutationFn: async (payload: SimilarPropertiesRequest) => {
      try {
        return await api.getSimilarProperties(payload);
      } catch (error) {
        throw handleApiError(error);
      }
    },
  });
};

export const useMarketTrends = (version: string) => {
  return useQuery({
    queryKey: ['marketTrends', version],
    queryFn: async () => {
      try {
        return await api.getMarketTrends(version);
      } catch (error) {
        throw handleApiError(error);
      }
    },
    retry: false,
  });
};

export const useModelMetrics = (version: string) => {
  return useQuery({
    queryKey: ['modelMetrics', version],
    queryFn: async () => {
      try {
        return await api.getModelMetrics(version);
      } catch (error) {
        throw handleApiError(error);
      }
    },
    retry: false,
  });
};

export const useListings = (params: {
  page: number;
  limit: number;
  neighborhood?: string;
  min_price?: number;
  max_price?: number;
  min_area?: number;
  max_area?: number;
  is_below_market_value?: number;
  version?: string;
}) => {
  return useQuery<ListingsResponse, ApiError>({
    queryKey: ['listings', params],
    queryFn: async () => {
      try {
        return await api.getListings(params);
      } catch (error) {
        throw handleApiError(error);
      }
    },
    retry: false,
  });
};
