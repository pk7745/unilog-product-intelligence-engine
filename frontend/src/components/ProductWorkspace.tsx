import React, { useState, useEffect } from 'react';
import { ProductsResponse, ProductSummary } from '../types';
import { fetchProducts } from '../services/api';
import { Search } from 'lucide-react';

interface ProductWorkspaceProps {
  onInspectProduct: (mpn: string) => void;
}

export const ProductWorkspace: React.FC<ProductWorkspaceProps> = ({ onInspectProduct }) => {
  const [data, setData] = useState<ProductsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [confidenceBand, setConfidenceBand] = useState('');
  const [needsReview, setNeedsReview] = useState('');

  const loadData = async () => {
    setLoading(true);
    try {
      const res = await fetchProducts({
        page,
        limit: 15,
        search,
        category,
        confidence_band: confidenceBand,
        needs_review: needsReview,
      });
      setData(res);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [page, category, confidenceBand, needsReview]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
    setPage(1);
    loadData();
  };

  const resetFilters = () => {
    setSearch('');
    setCategory('');
    setConfidenceBand('');
    setNeedsReview('');
    setPage(1);
    loadData();
  };

  return (
    <div className="space-y-6">
      {/* CONTROLS & FILTER BAR */}
      <div className="glass-card rounded-xl p-4 flex flex-col md:flex-row gap-4 items-center justify-between">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 absolute left-3 top-3 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={handleSearchChange}
            placeholder="Search MPN, description, manufacturer, category..."
            className="w-full bg-dark-900 border border-slate-700 rounded-lg pl-9 pr-4 py-2 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-400"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3 w-full md:w-auto">
          <select
            value={category}
            onChange={(e) => { setCategory(e.target.value); setPage(1); }}
            className="bg-dark-900 border border-slate-700 text-xs text-slate-300 rounded-lg px-3 py-2 focus:outline-none"
          >
            <option value="">All Categories</option>
            <option value="Deck Boards">Deck Boards</option>
            <option value="Cordless Power Tools">Cordless Power Tools</option>
            <option value="Cut-Off Discs">Cut-Off Discs</option>
            <option value="Fascia Boards">Fascia Boards</option>
            <option value="Railing Kits">Railing Kits</option>
            <option value="Saw Blades">Saw Blades</option>
          </select>

          <select
            value={confidenceBand}
            onChange={(e) => { setConfidenceBand(e.target.value); setPage(1); }}
            className="bg-dark-900 border border-slate-700 text-xs text-slate-300 rounded-lg px-3 py-2 focus:outline-none"
          >
            <option value="">All Quality Bands</option>
            <option value="HIGH">HIGH Confidence</option>
            <option value="MEDIUM">MEDIUM Confidence</option>
            <option value="LOW">LOW Confidence</option>
          </select>

          <select
            value={needsReview}
            onChange={(e) => { setNeedsReview(e.target.value); setPage(1); }}
            className="bg-dark-900 border border-slate-700 text-xs text-slate-300 rounded-lg px-3 py-2 focus:outline-none"
          >
            <option value="">All Review Status</option>
            <option value="Yes">Needs Review (Flagged)</option>
            <option value="No">No Review Required</option>
          </select>

          <button onClick={resetFilters} className="text-xs text-slate-400 hover:text-white px-2 py-1">
            Reset
          </button>
        </div>
      </div>

      {/* RESULTS DATA TABLE */}
      <div className="glass-card rounded-xl overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-300">
            <thead className="bg-dark-900/90 text-slate-400 font-semibold border-b border-slate-800 uppercase tracking-wider text-[10px]">
              <tr>
                <th className="py-3.5 px-4">MPN</th>
                <th className="py-3.5 px-4">Raw Description</th>
                <th className="py-3.5 px-4">Manufacturer (Brand)</th>
                <th className="py-3.5 px-4">Taxonomy (Fine)</th>
                <th className="py-3.5 px-4">INVOICE_DESC (≤40)</th>
                <th className="py-3.5 px-4">Tier / Provenance</th>
                <th className="py-3.5 px-4">Quality Score</th>
                <th className="py-3.5 px-4 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {loading ? (
                <tr>
                  <td colSpan={8} className="text-center py-8 text-slate-500">Loading products...</td>
                </tr>
              ) : !data || !data.products.length ? (
                <tr>
                  <td colSpan={8} className="text-center py-8 text-slate-500">No matching products found.</td>
                </tr>
              ) : (
                data.products.map((p) => (
                  <tr key={p.mpn} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 px-4 font-mono font-bold text-cyan-400">{p.mpn}</td>
                    <td className="py-3 px-4 text-slate-300 max-w-xs truncate" title={p.raw_desc}>{p.raw_desc}</td>
                    <td className="py-3 px-4 text-slate-200 font-medium">
                      <span>{p.manufacturer_name || 'Unresolved'}</span>{' '}
                      <span className="text-slate-400 text-[10px] bg-slate-800/60 px-1.5 py-0.5 rounded border border-slate-700/50">
                        {p.brand_name ? p.brand_name : 'Unbranded'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-emerald-400 font-mono text-[11px]">{p.fine || 'UNRESOLVED'}</td>
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-200 font-semibold bg-slate-900/50 px-2 py-1 rounded border border-slate-800">
                      {p.invoice_desc}
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                          p.evidence_tier.includes('Tier 1')
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : p.fine
                            ? 'bg-indigo-500/10 text-indigo-400 border border-indigo-500/20'
                            : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        {p.evidence_tier}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <span
                        className={`font-mono text-xs font-bold ${
                          p.overall_confidence_band === 'HIGH'
                            ? 'text-emerald-400'
                            : p.overall_confidence_band === 'MEDIUM'
                            ? 'text-cyan-400'
                            : 'text-amber-400'
                        }`}
                      >
                        {Math.round(p.overall_confidence * 100)}%
                      </span>
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button
                        onClick={() => onInspectProduct(p.mpn)}
                        className="text-xs bg-slate-800 hover:bg-slate-700 text-cyan-300 px-2.5 py-1 rounded border border-slate-700 transition-colors"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {data && (
          <div className="bg-dark-900/90 border-t border-slate-800 px-4 py-3 flex items-center justify-between text-xs text-slate-400">
            <span>
              Showing {(page - 1) * 15 + 1}-{Math.min(page * 15, data.total)} of {data.total.toLocaleString()} products
            </span>
            <div className="flex items-center space-x-2">
              <button
                disabled={page <= 1}
                onClick={() => setPage(page - 1)}
                className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded disabled:opacity-50"
              >
                Prev
              </button>
              <span className="font-mono text-cyan-400">
                Page {page} of {data.total_pages}
              </span>
              <button
                disabled={page >= data.total_pages}
                onClick={() => setPage(page + 1)}
                className="px-3 py-1 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded disabled:opacity-50"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
