import React, { useState, useEffect } from 'react';
import { FileText, Sparkles, AlertCircle, Loader2 } from 'lucide-react';
import { fetchProducts, fetchProductDetail } from '../services/api';
import { ProductDetail, ProductSummary } from '../types';

export const BeforeAfterComparison: React.FC = () => {
  const [selectedMpn, setSelectedMpn] = useState('DCB518ASTS06G');
  const [allProducts, setAllProducts] = useState<ProductSummary[]>([]);
  const [detail, setDetail] = useState<ProductDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Quick sample MPNs required by benchmark tests
  const quickSamples = ['DCB518ASTS06G', '49-94-0013', '543140016'];

  // Load list of all benchmark MPNs on component mount
  useEffect(() => {
    async function loadAllProducts() {
      try {
        const res = await fetchProducts({ limit: 1000 });
        if (res && res.products) {
          setAllProducts(res.products);
        }
      } catch (err) {
        console.error('Failed to load benchmark products list:', err);
      }
    }
    loadAllProducts();
  }, []);

  // Fetch 1:1 detail record for selected MPN
  useEffect(() => {
    async function loadDetail() {
      if (!selectedMpn) return;
      setLoading(true);
      setError(null);
      try {
        const data = await fetchProductDetail(selectedMpn);
        setDetail(data);
      } catch (err: any) {
        console.error(`Failed to load product detail for ${selectedMpn}:`, err);
        setError(err.message || 'Failed to load product comparison data');
      } finally {
        setLoading(false);
      }
    }
    loadDetail();
  }, [selectedMpn]);

  const isUnresolved = !detail?.delivery_row?.Classpath || detail?.delivery_row?.Classpath === 'UNRESOLVED';

  return (
    <div className="glass-card rounded-2xl p-6 space-y-6">
      {/* HEADER SECTION */}
      <div className="border-b border-slate-800 pb-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white">Raw vs Enriched Product Intelligence Comparison</h2>
          <p className="text-xs text-slate-400 mt-1">
            Select any product from the benchmark to compare raw supplier input against normalized 252-column commerce output.
          </p>
        </div>

        {/* SELECTOR CONTROLS */}
        <div className="flex flex-wrap items-center gap-2">
          {/* Quick sample buttons */}
          <div className="flex items-center space-x-1">
            {quickSamples.map((mpn) => (
              <button
                key={mpn}
                onClick={() => setSelectedMpn(mpn)}
                className={`px-2.5 py-1 rounded text-xs font-mono transition-colors ${
                  selectedMpn === mpn
                    ? 'bg-cyan-500 text-dark-900 font-bold'
                    : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                }`}
              >
                {mpn}
              </button>
            ))}
          </div>

          {/* All 1,000 benchmark products selector */}
          <select
            value={selectedMpn}
            onChange={(e) => setSelectedMpn(e.target.value)}
            className="bg-slate-900 border border-slate-700 text-slate-200 text-xs font-mono rounded px-3 py-1 focus:outline-none focus:border-cyan-500 max-w-[260px] truncate"
          >
            {allProducts.length > 0 ? (
              allProducts.map((p) => (
                <option key={p.mpn} value={p.mpn}>
                  {p.mpn} - {p.raw_desc ? p.raw_desc.slice(0, 35) : 'Product'}
                </option>
              ))
            ) : (
              <option value={selectedMpn}>{selectedMpn}</option>
            )}
          </select>
        </div>
      </div>

      {/* ERROR STATE */}
      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-xs flex items-center space-x-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* COMPARISON GRID */}
      <div className="relative grid lg:grid-cols-2 gap-6">
        {loading && (
          <div className="absolute inset-0 bg-dark-950/70 backdrop-blur-sm z-10 rounded-xl flex items-center justify-center space-x-2 text-cyan-400 text-xs font-mono">
            <Loader2 className="w-5 h-5 animate-spin" />
            <span>Loading comparison for {selectedMpn}...</span>
          </div>
        )}

        {/* LEFT: RAW SUPPLIER INPUT */}
        <div className="bg-dark-900 border border-slate-800 rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="text-xs font-bold text-amber-400 flex items-center space-x-1.5">
              <FileText className="w-4 h-4" />
              <span>RAW SUPPLIER INPUT</span>
            </span>
            <span className="text-[10px] bg-amber-500/10 text-amber-400 px-2 py-0.5 rounded">Unstructured / Abbreviated</span>
          </div>

          <div className="space-y-3 font-mono text-xs">
            <div>
              <span className="text-slate-500 text-[11px] block">Mfg_Part_Num:</span>
              <span className="text-white font-bold">
                {detail?.raw_input?.Mfg_Part_Num || selectedMpn}
              </span>
            </div>
            <div>
              <span className="text-slate-500 text-[11px] block">Part_Desc:</span>
              <span className="text-amber-200 bg-amber-500/5 p-2 rounded block break-words">
                {detail?.raw_input?.Part_Desc || 'Not provided'}
              </span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <span className="text-slate-500 text-[11px] block">Part_Manuf:</span>
                <span className="text-slate-300">
                  {detail?.raw_input?.Part_Manuf || 'Not provided'}
                </span>
              </div>
              <div>
                <span className="text-slate-500 text-[11px] block">E1_Brand:</span>
                <span className="text-slate-500 italic">
                  {detail?.raw_input?.E1_Brand || 'Not provided'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT: ENRICHED CANONICAL OUTPUT */}
        <div className="bg-dark-900 border border-cyan-500/30 rounded-xl p-5 space-y-4 shadow-lg shadow-cyan-500/5">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <span className="text-xs font-bold text-cyan-400 flex items-center space-x-1.5">
              <Sparkles className="w-4 h-4" />
              <span>STRUCTURED PRODUCT INTELLIGENCE</span>
            </span>
            <span className="text-[10px] bg-cyan-500/10 text-cyan-400 px-2 py-0.5 rounded border border-cyan-500/20">
              252-Column Schema Compliant
            </span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <span className="text-slate-400 text-[11px] block">Manufacturer Name:</span>
                <span className="text-white font-semibold">
                  {detail?.delivery_row?.MANUFACTURER_NAME || 'Not provided'}
                </span>
              </div>
              <div>
                <span className="text-slate-400 text-[11px] block">Brand Name:</span>
                <span className="text-cyan-400 font-semibold">
                  {detail?.delivery_row?.BRAND_NAME || 'Not provided'}
                </span>
              </div>
            </div>
            <div>
              <span className="text-slate-400 text-[11px] block">Classpath Taxonomy:</span>
              {isUnresolved ? (
                <span className="text-amber-400 font-mono text-[11px] bg-amber-500/10 px-2 py-0.5 rounded border border-amber-500/20 inline-block">
                  Classification: UNRESOLVED
                </span>
              ) : (
                <span className="text-emerald-400 font-mono text-[11px] break-words">
                  {detail?.delivery_row?.Classpath}
                </span>
              )}
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <span className="text-slate-400 text-[11px] block">INVOICE_DESC (≤40 CAPS):</span>
                <span className="text-white font-mono font-bold bg-slate-800 px-2 py-1 rounded block break-words">
                  {detail?.delivery_row?.INVOICE_DESC || 'Not provided'}
                </span>
              </div>
              <div>
                <span className="text-slate-400 text-[11px] block">MOBILE_DESC (60-80):</span>
                <span className="text-slate-200 font-mono text-[10px] bg-slate-800 px-2 py-1 rounded block break-words">
                  {detail?.delivery_row?.MOBILE_DESC || 'Not provided'}
                </span>
              </div>
            </div>
            <div>
              <span className="text-slate-400 text-[11px] block">Extracted Dimension Triplets:</span>
              <div className="flex flex-wrap gap-2 pt-1">
                {detail?.attributes && detail.attributes.length > 0 ? (
                  detail.attributes.map((attr, idx) => (
                    <span
                      key={idx}
                      className="bg-slate-800 text-cyan-300 font-mono text-[10px] px-2 py-1 rounded border border-slate-700"
                    >
                      {attr.label}: {attr.value}
                      {attr.uom ? ` ${attr.uom}` : ''}
                    </span>
                  ))
                ) : (
                  <span className="text-slate-500 italic text-[11px]">
                    No dimensional attributes extracted
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
