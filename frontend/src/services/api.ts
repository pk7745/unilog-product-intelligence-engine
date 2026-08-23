import { OverviewData, ProductsResponse, ProductDetail, ReviewQueueResponse, QualityGate } from '../types';

const API_BASE = '/api';

export async function fetchOverview(): Promise<OverviewData> {
  const res = await fetch(`${API_BASE}/overview`);
  if (!res.ok) throw new Error('Failed to fetch overview data');
  return res.json();
}

export async function fetchProducts(params: {
  page?: number;
  limit?: number;
  search?: string;
  category?: string;
  confidence_band?: string;
  needs_review?: string;
  tier?: string;
}): Promise<ProductsResponse> {
  const query = new URLSearchParams();
  if (params.page) query.set('page', params.page.toString());
  if (params.limit) query.set('limit', params.limit.toString());
  if (params.search) query.set('search', params.search);
  if (params.category) query.set('category', params.category);
  if (params.confidence_band) query.set('confidence_band', params.confidence_band);
  if (params.needs_review) query.set('needs_review', params.needs_review);
  if (params.tier) query.set('tier', params.tier);

  const res = await fetch(`${API_BASE}/products?${query}`);
  if (!res.ok) throw new Error('Failed to fetch products');
  return res.json();
}

export async function fetchProductMpns(): Promise<Array<{ mpn: string; raw_desc: string }>> {
  const res = await fetch(`${API_BASE}/products/mpns`);
  if (!res.ok) return [];
  return res.json();
}

export async function fetchProductDetail(mpn: string): Promise<ProductDetail> {
  const res = await fetch(`${API_BASE}/products/${encodeURIComponent(mpn)}`);
  if (!res.ok) throw new Error(`Failed to fetch detail for MPN ${mpn}`);
  return res.json();
}

export async function runPipeline(): Promise<{
  status: string;
  elapsed_seconds: number;
  rows_processed: number;
  quality_gates_passed: boolean;
}> {
  const res = await fetch(`${API_BASE}/pipeline/run`, { method: 'POST' });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Pipeline run error' }));
    throw new Error(err.detail || 'Pipeline execution failed');
  }
  return res.json();
}

export async function fetchQualityGates(): Promise<{
  all_passed: boolean;
  stats: Record<string, any>;
  gates: QualityGate[];
}> {
  const res = await fetch(`${API_BASE}/quality/gates`);
  if (!res.ok) throw new Error('Failed to fetch quality gates');
  return res.json();
}

export async function fetchReviewQueue(): Promise<ReviewQueueResponse> {
  const res = await fetch(`${API_BASE}/review/queue`);
  if (!res.ok) throw new Error('Failed to fetch review queue');
  return res.json();
}

export async function submitReviewDecision(mpn: string, action: 'RESOLVE' | 'LEAVE_BLANK'): Promise<{
  status: string;
  message: string;
}> {
  const res = await fetch(`${API_BASE}/review/decision`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mpn, action }),
  });
  if (!res.ok) throw new Error('Failed to submit review decision');
  return res.json();
}
