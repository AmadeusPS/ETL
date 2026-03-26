import axios from "axios";
import { getIdToken } from "./cognito";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
});

// Attach Cognito JWT to every request
api.interceptors.request.use(async (config) => {
  const token = await getIdToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ---- Auth ----------------------------------------------------------------
export const registerUser = () => api.post("/auth/register");
export const getMe = () => api.get("/auth/me");

// ---- Products ------------------------------------------------------------
export const listProducts = () => api.get("/products/");
export const createProduct = (data: ProductCreate) => api.post("/products/", data);
export const updateProduct = (id: number, data: Partial<ProductCreate>) =>
  api.patch(`/products/${id}`, data);
export const deleteProduct = (id: number) => api.delete(`/products/${id}`);

export const listCompetitorProducts = (storeId: number) =>
  api.get("/products/competitors/", { params: { store_id: storeId } });
export const addCompetitorProduct = (data: CompetitorProductCreate) =>
  api.post("/products/competitors/", data);

// ---- Alerts --------------------------------------------------------------
export const listAlerts = (unreadOnly = false) =>
  api.get("/alerts/", { params: { unread_only: unreadOnly } });
export const markAlertRead = (id: number) => api.patch(`/alerts/${id}/read`);

// ---- Recommendations -----------------------------------------------------
export const listRecommendations = () => api.get("/recommendations/");
export const actionRecommendation = (id: number, status: string) =>
  api.patch(`/recommendations/${id}/action`, { status });

// ---- Types ---------------------------------------------------------------
interface ProductCreate {
  name: string;
  sku?: string;
  category?: string;
  current_price?: number;
  currency?: string;
  target_margin?: number;
}

interface CompetitorProductCreate {
  store_id: number;
  url: string;
  name?: string;
  sku?: string;
}

export default api;
