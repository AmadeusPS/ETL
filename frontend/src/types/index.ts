export type PlanTier = "basic" | "pro" | "enterprise";
export type AlertType =
  | "price_drop"
  | "price_increase"
  | "new_product"
  | "out_of_stock"
  | "back_in_stock";
export type RecommendationStatus = "pending" | "accepted" | "rejected" | "applied";

export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
}

export interface Subscription {
  plan: PlanTier;
  status: string;
  current_period_end: string | null;
}

export interface Product {
  id: number;
  name: string;
  sku: string | null;
  category: string | null;
  current_price: number | null;
  currency: string;
  target_margin: number | null;
  created_at: string;
}

export interface CompetitorProduct {
  id: number;
  store_id: number;
  url: string;
  name: string | null;
  current_price: number | null;
  previous_price: number | null;
  currency: string;
  in_stock: boolean | null;
  last_scraped_at: string | null;
}

export interface Alert {
  id: number;
  alert_type: AlertType;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface AIRecommendation {
  id: number;
  product_id: number;
  suggested_price: number | null;
  reasoning: string | null;
  status: RecommendationStatus;
  created_at: string;
}
