export interface QualityGate {
  gate_id: number;
  name: string;
  status: 'PASS' | 'FAIL';
  details: string;
}

export interface CategoryMetric {
  Category_Fine: string;
  Assigned_Rows: string;
  Pct_Dataset: string;
  High_Conf_Count: string;
  Med_Conf_Count: string;
  Low_Conf_Count: string;
  Tier1_Verified_Count: string;
  Tier3_Candidate_Count: string;
  Total_Attributes_Populated: string;
  Unresolved_Conflicts: string;
  Representative_MPNs: string;
}

export interface OverviewData {
  status: string;
  total_rows: number;
  classified_count: number;
  classification_rate: number;
  unresolved_count: number;
  unresolved_rate: number;
  tier1_verified_count: number;
  tier3_candidate_count: number;
  open_conflicts_count: number;
  needs_review_count: number;
  quality_gates: {
    all_passed: boolean;
    passed_count: number;
    total_count: number;
    details: QualityGate[];
  };
  compliance: {
    invoice_desc_pct: number;
    mobile_desc_pct: number;
    placeholder_leakage_count: number;
    schema_columns: number;
    schema_contract_status: string;
  };
  population: {
    manufacturer_populated: number;
    manufacturer_pct: number;
    brand_populated: number;
    brand_pct: number;
    attribute_triplets_count: number;
    features_count: number;
    field_provenance_records: number;
  };
  categories: CategoryMetric[];
}

export interface ProductSummary {
  mpn: string;
  raw_desc: string;
  raw_manuf: string;
  manufacturer_name: string;
  brand_name: string;
  trade_name: string;
  department: string;
  class: string;
  fine: string;
  classpath: string;
  invoice_desc: string;
  mobile_desc: string;
  short_desc: string;
  long_desc1: string;
  mfr_url: string;
  overall_confidence: number;
  overall_confidence_band: 'HIGH' | 'MEDIUM' | 'LOW';
  needs_review: 'Yes' | 'No';
  review_reasons: string;
  num_conflicts: number;
  num_attributes_fused: number;
  evidence_tier: string;
  live_evidence_sources: string;
}

export interface ProductsResponse {
  total: number;
  page: number;
  limit: number;
  total_pages: number;
  products: ProductSummary[];
}

export interface AttributeSlot {
  slot: number;
  label: string;
  value: string;
  uom: string;
}

export interface ProvenanceFact {
  mpn: string;
  field: string;
  value: string;
  uom?: string;
  status: string;
  method: string;
  source_url?: string;
  evidence_quote?: string;
  confidence: number;
}

export interface ProductDetail {
  mpn: string;
  raw_input: Record<string, string>;
  delivery_row: Record<string, string>;
  qa_metadata: Record<string, string>;
  provenance_facts: ProvenanceFact[];
  evidence_cache: Record<string, any>;
  attributes: AttributeSlot[];
  features: Array<{ slot: number; feature: string }>;
  evidence_tier: string;
  quality_score: number;
}

export interface ReviewQueueItem {
  mpn: string;
  fine: string;
  overall_confidence: number;
  num_conflicts: number;
  review_reasons: string;
  delivery_row: Record<string, string>;
  provenance_facts: ProvenanceFact[];
}

export interface ReviewQueueResponse {
  total_in_queue: number;
  items: ReviewQueueItem[];
}
