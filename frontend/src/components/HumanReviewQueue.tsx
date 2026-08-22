import React, { useEffect, useState } from 'react';
import { ReviewQueueItem } from '../types';
import { fetchReviewQueue, submitReviewDecision } from '../services/api';
import {
  ShieldAlert,
  CheckCircle2,
  AlertTriangle,
  ExternalLink,
  RefreshCw,
  FileText,
  Layers,
  ArrowRight,
  Database,
  Info,
  HelpCircle,
  Sparkles,
} from 'lucide-react';

interface HumanReviewQueueProps {
  onDecisionApplied?: () => void;
  onQueueUpdated?: (count: number) => void;
}

export const HumanReviewQueue: React.FC<HumanReviewQueueProps> = ({
  onDecisionApplied,
  onQueueUpdated,
}) => {
  const [items, setItems] = useState<ReviewQueueItem[]>([]);
  const [totalInQueue, setTotalInQueue] = useState<number>(0);
  const [selectedMpn, setSelectedMpn] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  // Modal confirmation state
  const [pendingAction, setPendingAction] = useState<'RESOLVE' | 'LEAVE_BLANK' | null>(null);

  const loadQueue = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchReviewQueue();
      setItems(res.items || []);
      const count = res.total_in_queue || 0;
      setTotalInQueue(count);
      if (onQueueUpdated) {
        onQueueUpdated(count);
      }

      // Auto-select first item if none selected or if previously selected item was removed
      if (res.items && res.items.length > 0) {
        if (!selectedMpn || !res.items.some((i) => i.mpn === selectedMpn)) {
          setSelectedMpn(res.items[0].mpn);
        }
      } else {
        setSelectedMpn(null);
      }
    } catch (err: any) {
      setError(err.message || 'Unable to connect to review queue API');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadQueue();
  }, []);

  const selectedItem = items.find((i) => i.mpn === selectedMpn) || null;

  const handleConfirmDecision = async () => {
    if (!selectedItem || !pendingAction) return;
    const mpn = selectedItem.mpn;
    const action = pendingAction;

    setSubmitting(true);
    setPendingAction(null);

    try {
      await submitReviewDecision(mpn, action);
      setSelectedMpn(null);
      await loadQueue();
      if (onDecisionApplied) {
        onDecisionApplied();
      }
    } catch (err: any) {
      alert(`Failed to submit decision: ${err.message}`);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* HEADER SECTION */}
      <div className="glass-card rounded-2xl p-6 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center space-x-3">
            <h1 className="text-2xl font-extrabold text-white tracking-tight">Human Review Center</h1>
            <span className="bg-amber-500/10 text-amber-400 border border-amber-500/20 text-xs font-semibold px-3 py-1 rounded-full flex items-center space-x-1.5">
              <ShieldAlert className="w-3.5 h-3.5" />
              <span>{loading ? 'Loading...' : `${totalInQueue} Decisions Requiring Attention`}</span>
            </span>
          </div>
          <p className="text-xs text-slate-400">
            Resolve product intelligence decisions that require human judgment. UNILOG automatically holds ambiguous or conflicting records rather than fabricating product data.
          </p>
        </div>

        <button
          onClick={loadQueue}
          disabled={loading}
          className="bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs font-semibold px-3.5 py-2 rounded-lg flex items-center space-x-2 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh Queue</span>
        </button>
      </div>

      {/* ERROR STATE */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 text-red-400 p-6 rounded-2xl space-y-3">
          <div className="flex items-center space-x-2 font-bold text-sm">
            <AlertTriangle className="w-5 h-5" />
            <span>Unable to load review queue</span>
          </div>
          <p className="text-xs text-red-300">{error}</p>
          <button
            onClick={loadQueue}
            className="bg-red-500/20 hover:bg-red-500/30 text-red-200 border border-red-500/40 text-xs font-semibold px-4 py-2 rounded-lg"
          >
            Try Again
          </button>
        </div>
      )}

      {/* EMPTY QUEUE STATE */}
      {!loading && !error && items.length === 0 && (
        <div className="glass-card rounded-2xl p-12 text-center space-y-4 max-w-xl mx-auto border border-slate-800">
          <div className="w-16 h-16 bg-emerald-500/10 text-emerald-400 rounded-2xl flex items-center justify-center mx-auto border border-emerald-500/20 shadow-lg shadow-emerald-500/10">
            <CheckCircle2 className="w-8 h-8" />
          </div>
          <div className="space-y-1">
            <h3 className="text-xl font-extrabold text-white">All Clear</h3>
            <p className="text-xs text-slate-400">
              No products currently require human review. All catalog items have passed evidence verification quality gates.
            </p>
          </div>
        </div>
      )}

      {/* QUEUE WORKSPACE (2-COLUMN SPLIT LAYOUT) */}
      {!loading && !error && items.length > 0 && (
        <div className="grid lg:grid-cols-12 gap-6 items-start">
          {/* LEFT COLUMN: QUEUE ITEM LIST (4 COLS) */}
          <div className="lg:col-span-4 glass-card rounded-2xl overflow-hidden border border-slate-800 space-y-0">
            <div className="bg-dark-900/90 px-4 py-3 border-b border-slate-800 flex items-center justify-between">
              <span className="text-xs font-bold text-slate-300 uppercase tracking-wider">Pending Items ({items.length})</span>
              <span className="text-[10px] text-amber-400 font-mono">Ranked by Priority</span>
            </div>

            <div className="divide-y divide-slate-800/80 max-h-[750px] overflow-y-auto">
              {items.map((item) => {
                const isSelected = item.mpn === selectedMpn;
                return (
                  <div
                    key={item.mpn}
                    onClick={() => setSelectedMpn(item.mpn)}
                    className={`p-4 cursor-pointer transition-all ${
                      isSelected
                        ? 'bg-indigo-950/40 border-l-4 border-l-cyan-400'
                        : 'hover:bg-slate-800/40 border-l-4 border-l-transparent'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-sm font-bold text-cyan-400">{item.mpn}</span>
                      <span className="text-[10px] bg-amber-500/10 text-amber-400 border border-amber-500/20 px-2 py-0.5 rounded font-mono font-semibold">
                        {item.num_conflicts} Conflict
                      </span>
                    </div>

                    <p className="text-xs text-slate-300 mt-1 line-clamp-1 font-medium">
                      {item.delivery_row?.Part_Desc || item.delivery_row?.INVOICE_DESC || 'Product Review Item'}
                    </p>

                    <div className="flex items-center justify-between text-[11px] text-slate-400 mt-2">
                      <span className="font-mono text-slate-400">{item.fine || 'UNRESOLVED'}</span>
                      <span className="font-mono text-slate-400">
                        Score: <strong className="text-amber-400">{Math.round(item.overall_confidence * 100)}%</strong>
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* RIGHT COLUMN: DETAILED REVIEW WORKSPACE (8 COLS) */}
          <div className="lg:col-span-8 glass-card rounded-2xl border border-slate-800 overflow-hidden shadow-2xl">
            {selectedItem ? (
              <div className="space-y-6 p-6">
                {/* ITEM WORKSPACE HEADER */}
                <div className="border-b border-slate-800 pb-4 flex flex-wrap items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-3">
                      <h2 className="text-2xl font-extrabold font-mono text-cyan-400">{selectedItem.mpn}</h2>
                      <span className="text-xs bg-amber-500/10 text-amber-400 border border-amber-500/20 px-3 py-1 rounded-full font-semibold">
                        CONFLICT HOLD
                      </span>
                      <span className="text-xs bg-slate-800 text-slate-300 px-3 py-1 rounded-full font-mono">
                        {selectedItem.fine}
                      </span>
                    </div>
                    <p className="text-xs text-slate-300 font-medium">{selectedItem.delivery_row?.Part_Desc}</p>
                  </div>

                  <div className="text-right">
                    <span className="text-[10px] text-slate-400 block uppercase tracking-wider font-semibold">Confidence Score</span>
                    <span className="text-xl font-extrabold font-mono text-amber-400">
                      {Math.round(selectedItem.overall_confidence * 100)}%
                    </span>
                  </div>
                </div>

                {/* REASON FOR REVIEW BANNER */}
                <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 space-y-2">
                  <div className="flex items-center space-x-2 text-amber-400 text-xs font-bold uppercase tracking-wider">
                    <AlertTriangle className="w-4 h-4" />
                    <span>Reason for Review Hold</span>
                  </div>
                  <p className="text-xs text-amber-200 leading-relaxed font-sans">
                    {selectedItem.review_reasons}
                  </p>
                </div>

                {/* PRODUCT DATA SUMMARY GRID */}
                <div className="grid sm:grid-cols-3 gap-4">
                  <div className="bg-dark-900 border border-slate-800 p-3 rounded-xl">
                    <span className="text-[10px] text-slate-500 block font-semibold uppercase">Legal Manufacturer</span>
                    <span className="text-xs font-bold text-white">{selectedItem.delivery_row?.MANUFACTURER_NAME || 'Unknown'}</span>
                  </div>
                  <div className="bg-dark-900 border border-slate-800 p-3 rounded-xl">
                    <span className="text-[10px] text-slate-500 block font-semibold uppercase">Commercial Brand</span>
                    <span className="text-xs font-bold text-cyan-300">{selectedItem.delivery_row?.BRAND_NAME || 'None'}</span>
                  </div>
                  <div className="bg-dark-900 border border-slate-800 p-3 rounded-xl">
                    <span className="text-[10px] text-slate-500 block font-semibold uppercase">INVOICE_DESC (≤40)</span>
                    <span className="text-xs font-bold font-mono text-emerald-400">{selectedItem.delivery_row?.INVOICE_DESC || 'Blank'}</span>
                  </div>
                </div>

                {/* EVIDENCE COMPARISON & PROVENANCE TRACES */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                    <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center space-x-2">
                      <Layers className="w-4 h-4 text-cyan-400" />
                      <span>Retrieved Evidence & Provenance Facts</span>
                    </h3>
                    <span className="text-[10px] text-slate-400 font-mono">
                      {selectedItem.provenance_facts?.length || 0} Facts Evaluated
                    </span>
                  </div>

                  {selectedItem.provenance_facts && selectedItem.provenance_facts.length > 0 ? (
                    <div className="grid md:grid-cols-2 gap-4">
                      {selectedItem.provenance_facts.map((fact, idx) => {
                        const isVerified = fact.status === 'VERIFIED';
                        const isConflict = fact.status === 'CONFLICT';

                        return (
                          <div
                            key={idx}
                            className={`bg-dark-900 border ${
                              isVerified
                                ? 'border-emerald-500/30'
                                : isConflict
                                ? 'border-amber-500/40'
                                : 'border-slate-800'
                            } rounded-xl p-4 space-y-2`}
                          >
                            <div className="flex items-center justify-between">
                              <span className="text-xs font-bold text-white">{fact.field}</span>
                              <span
                                className={`text-[10px] font-bold px-2 py-0.5 rounded font-mono ${
                                  isVerified
                                    ? 'bg-emerald-500/20 text-emerald-400'
                                    : 'bg-amber-500/20 text-amber-400'
                                }`}
                              >
                                {fact.status} ({fact.method})
                              </span>
                            </div>

                            <div className="font-mono text-sm font-extrabold text-cyan-300">
                              {fact.value} {fact.uom || ''}
                            </div>

                            {fact.evidence_quote && (
                              <p className="text-[11px] text-slate-400 italic bg-slate-900/60 p-2 rounded border border-slate-800/80">
                                "{fact.evidence_quote}"
                              </p>
                            )}

                            {fact.source_url && (
                              <a
                                href={fact.source_url}
                                target="_blank"
                                rel="noreferrer"
                                className="inline-flex items-center space-x-1 text-[10px] text-cyan-400 hover:text-cyan-300 underline font-mono truncate"
                              >
                                <span>{fact.source_url}</span>
                                <ExternalLink className="w-3 h-3 flex-shrink-0" />
                              </a>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="bg-dark-900 border border-slate-800 rounded-xl p-4 text-xs text-slate-400 italic">
                      No direct live web evidence retrieved. Record was flagged due to raw text extraction ambiguity.
                    </div>
                  )}
                </div>

                {/* DECISION ACTION PANEL */}
                <div className="bg-dark-900 border border-slate-800 rounded-xl p-5 space-y-4 pt-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-xs font-bold text-white uppercase tracking-wider">Human Expert Decision Action</h4>
                      <p className="text-[11px] text-slate-400">Select an action to resolve or defer this item in the catalog pipeline.</p>
                    </div>
                    {submitting && (
                      <span className="text-xs text-cyan-400 font-semibold flex items-center space-x-2">
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                        <span>Updating Pipeline...</span>
                      </span>
                    )}
                  </div>

                  <div className="grid sm:grid-cols-2 gap-4">
                    <button
                      onClick={() => setPendingAction('RESOLVE')}
                      disabled={submitting}
                      className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white font-bold text-xs py-3 px-4 rounded-xl shadow-lg shadow-emerald-600/20 flex items-center justify-center space-x-2 transition-transform active:scale-95 disabled:opacity-50"
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      <span>Resolve & Accept Decision</span>
                    </button>

                    <button
                      onClick={() => setPendingAction('LEAVE_BLANK')}
                      disabled={submitting}
                      className="bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold text-xs py-3 px-4 rounded-xl border border-slate-700 flex items-center justify-center space-x-2 transition-colors disabled:opacity-50"
                    >
                      <Info className="w-4 h-4 text-amber-400" />
                      <span>Leave Unresolved (Hold Blank)</span>
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-12 text-center text-slate-500 text-xs">Select an item from the queue to review details.</div>
            )}
          </div>
        </div>
      )}

      {/* CONFIRMATION MODAL */}
      {pendingAction && selectedItem && (
        <div className="fixed inset-0 z-50 bg-dark-900/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="glass-card rounded-2xl max-w-md w-full p-6 space-y-6 border border-slate-700 shadow-2xl">
            <div className="space-y-2 text-center">
              <div className="w-12 h-12 rounded-xl bg-cyan-500/10 text-cyan-400 flex items-center justify-center mx-auto border border-cyan-500/20">
                <HelpCircle className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-extrabold text-white">
                {pendingAction === 'RESOLVE' ? 'Confirm Resolution & Verification' : 'Confirm Deferred Hold'}
              </h3>
              <p className="text-xs text-slate-300">
                You are about to record a human decision for product:
                <strong className="font-mono text-cyan-400 block text-sm mt-1">{selectedItem.mpn}</strong>
              </p>
            </div>

            <div className="bg-dark-900 p-4 rounded-xl text-xs text-slate-400 space-y-2 border border-slate-800 font-mono">
              {pendingAction === 'RESOLVE' ? (
                <>
                  <p className="text-emerald-400 font-semibold">✓ Action: RESOLVE</p>
                  <p>• Verification Status: VERIFIED</p>
                  <p>• Provenance Method: HUMAN</p>
                  <p>• Confidence: 1.0 (100%)</p>
                </>
              ) : (
                <>
                  <p className="text-amber-400 font-semibold">⚠ Action: LEAVE_BLANK</p>
                  <p>• Verification Status: CONFLICT</p>
                  <p>• Provenance Method: HUMAN_DEFERRED</p>
                  <p>• Confidence: 0.0 (Preserve Hold)</p>
                </>
              )}
            </div>

            <div className="flex items-center space-x-3 pt-2">
              <button
                onClick={() => setPendingAction(null)}
                className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold py-2.5 rounded-xl border border-slate-700 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleConfirmDecision}
                className="flex-1 bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white text-xs font-bold py-2.5 rounded-xl shadow-lg shadow-cyan-500/20 transition-transform active:scale-95"
              >
                Confirm Decision
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
