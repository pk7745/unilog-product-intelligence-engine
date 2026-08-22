import React, { useEffect, useState } from 'react';
import { ProductDetail } from '../types';
import { fetchProductDetail } from '../services/api';
import { X } from 'lucide-react';

interface ProductDetailModalProps {
  mpn: string | null;
  onClose: () => void;
}

export const ProductDetailModal: React.FC<ProductDetailModalProps> = ({ mpn, onClose }) => {
  const [detail, setDetail] = useState<ProductDetail | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!mpn) {
      setDetail(null);
      return;
    }
    setLoading(true);
    fetchProductDetail(mpn)
      .then(setDetail)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [mpn]);

  if (!mpn) return null;

  return (
    <div className="fixed inset-0 z-50 bg-dark-900/80 backdrop-blur-md flex items-center justify-center p-4">
      <div className="glass-card rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col shadow-2xl border border-slate-700">
        {/* MODAL HEADER */}
        <div className="bg-dark-900 px-6 py-4 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <span className="text-lg font-bold font-mono text-cyan-400">{mpn}</span>
            {detail && (
              <span className="text-xs bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2.5 py-0.5 rounded-full font-medium">
                {detail.evidence_tier}
              </span>
            )}
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-white p-1">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* MODAL BODY */}
        <div className="p-6 overflow-y-auto space-y-6 text-xs text-slate-300">
          {loading || !detail ? (
            <div className="text-center py-12 text-slate-500">Loading product intelligence details...</div>
          ) : (
            <>
              <div className="grid md:grid-cols-2 gap-6">
                {/* RAW INPUT */}
                <div className="bg-dark-900/90 border border-slate-800 p-4 rounded-xl space-y-2">
                  <h4 className="text-xs font-bold text-amber-400 uppercase tracking-wider">Raw Input Data</h4>
                  <p className="text-slate-200 font-mono text-[11px]">{detail.raw_input.Part_Desc || ''}</p>
                  <div className="text-[11px] text-slate-400">
                    Manufacturer: <span className="text-slate-200">{detail.raw_input.Part_Manuf || ''}</span>
                  </div>
                </div>

                {/* ENRICHED SUMMARY */}
                <div className="bg-dark-900/90 border border-slate-800 p-4 rounded-xl space-y-2">
                  <div className="flex items-center justify-between">
                    <h4 className="text-xs font-bold text-cyan-400 uppercase tracking-wider">Canonical Entity & Taxonomy</h4>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        detail.evidence_tier.includes('Tier 1')
                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                          : detail.delivery_row.Fine
                          ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {detail.evidence_tier}
                    </span>
                  </div>
                  <div className="text-[11px] text-slate-300">
                    Legal Manufacturer: <span className="font-semibold text-white">{detail.delivery_row.MANUFACTURER_NAME || 'Unresolved'}</span>
                  </div>
                  <div className="text-[11px] text-slate-300">
                    Commercial Brand: <span className="font-semibold text-cyan-300">{detail.delivery_row.BRAND_NAME || 'Unbranded'}</span>
                  </div>
                  <div className="text-[11px] text-slate-300">
                    Classpath: <span className="font-mono text-emerald-400">{detail.delivery_row.Classpath || 'UNRESOLVED'}</span>
                  </div>
                </div>
              </div>

              {/* DESCRIPTIONS */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold text-white border-b border-slate-800 pb-1">Multichannel Generated Descriptions</h4>
                <div className="grid gap-2 font-mono text-[11px]">
                  <div className="bg-slate-800/80 p-2.5 rounded border border-slate-700">
                    <span className="text-slate-400 text-[10px] block">INVOICE_DESC (≤ 40 CAPS):</span>
                    <span className="text-white font-bold">{detail.delivery_row.INVOICE_DESC || ''}</span>
                  </div>
                  <div className="bg-slate-800/80 p-2.5 rounded border border-slate-700">
                    <span className="text-slate-400 text-[10px] block">MOBILE_DESC (60-80 Chars):</span>
                    <span className="text-slate-200">{detail.delivery_row.MOBILE_DESC || ''}</span>
                  </div>
                </div>
              </div>

              {/* ATTRIBUTES GRID */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold text-white border-b border-slate-800 pb-1">Enriched Attribute Triplets</h4>
                <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-2">
                  {detail.attributes.length ? (
                    detail.attributes.map((a) => (
                      <div key={a.slot} className="bg-dark-900 p-2 rounded border border-slate-800">
                        <span className="text-slate-400 text-[10px] block">{a.label}:</span>
                        <span className="text-cyan-300 font-bold">{a.value} {a.uom}</span>
                      </div>
                    ))
                  ) : (
                    <span className="text-slate-500 text-xs">No extra attribute triplets populated.</span>
                  )}
                </div>
              </div>

              {/* PROVENANCE TRACES */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold text-white border-b border-slate-800 pb-1">Field Evidence Provenance Traces</h4>
                <div className="space-y-2 font-mono text-[11px]">
                  {detail.provenance_facts.length ? (
                    detail.provenance_facts.map((pf, idx) => (
                      <div key={idx} className="bg-dark-900 p-2 rounded border border-slate-800 space-y-1">
                        <div className="flex justify-between text-slate-300">
                          <span>
                            {pf.field}: <strong className="text-white">{pf.value} {pf.uom || ''}</strong>
                          </span>
                          <span className="text-emerald-400">{pf.status} ({pf.method})</span>
                        </div>
                        {pf.source_url && (
                          <a
                            href={pf.source_url}
                            target="_blank"
                            rel="noreferrer"
                            className="text-cyan-400 underline text-[10px] block truncate"
                          >
                            {pf.source_url}
                          </a>
                        )}
                      </div>
                    ))
                  ) : (
                    <span className="text-slate-500 text-xs">Derived from raw candidate extraction.</span>
                  )}
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
