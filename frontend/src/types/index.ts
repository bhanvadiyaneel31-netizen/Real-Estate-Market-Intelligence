export interface PredictRequest {
  bedrooms: number;
  area: number;
  neighborhood: string;
  has_central_air: number; // 0 or 1
  has_garage: number;      // 0 or 1
  has_pool: number;        // 0 or 1
  fireplace_count: number;
  description_text?: string;
}

export interface FeatureFactor {
  feature: string;
  impact: number;
}

export interface PredictResponse {
  estimated_price: number;
  confidence: number; // 0.50 to 0.98
  proxy_explainability_factors: FeatureFactor[];
  is_below_market_value: boolean;
  price_tier: 'Low' | 'Medium' | 'High' | string;
  models_used: Record<string, string>;
}

export interface SimilarPropertiesRequest extends PredictRequest {
  k?: number;
}

export interface ComparableProperty {
  external_id: string;
  title: string;
  price: string;
  location: string;
  bedrooms: string;
  area: string;
  amenities?: string | null;
  description_text?: string | null;
  distance: number;
}

export interface SimilarPropertiesResponse {
  similar_properties: ComparableProperty[];
  model_used: string;
}

export interface NeighborhoodTrend {
  neighborhood: string;
  median_price: number;
  median_price_per_sqft: number;
  total_listings: number;
}

export interface MarketTrendsResponse {
  feature_set_version: string;
  neighborhood_trends: NeighborhoodTrend[];
}

export interface ModelMetric {
  rmse?: number;
  r2?: number;
  accuracy?: number;
  f1?: number;
  f1_weighted?: number;
  mean_neighbor_distance?: number;
}

export interface ModelMetricsEntry {
  metrics: ModelMetric;
  trained_at: string | null;
  feature_set_version: string;
}

export type ModelMetricsResponse = Record<string, ModelMetricsEntry>;

export interface CleanedListing {
  id: number;
  external_id: string;
  price: number;
  bedrooms: number;
  area: number;
  neighborhood: string;
  has_central_air: number;
  has_garage: number;
  has_pool: number;
  fireplace_count: number;
  price_per_sqft: number;
  is_below_market_value: boolean;
  feature_set_version: string;
}

export interface ListingsResponse {
  total: number;
  page: number;
  limit: number;
  feature_set_version: string;
  listings: CleanedListing[];
  error?: string;
}
