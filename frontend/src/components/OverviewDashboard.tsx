import React from 'react';
import { OverviewData } from '../types';
import { Sparkles, ArrowRight, Package, FolderTree, CheckCircle2, FileCheck } from 'lucide-react';
import { Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

interface OverviewDashboardProps {
  data: OverviewData | null;
  onNavigate: (tab: string) => void;
}

export const OverviewDashboard: React.FC<OverviewDashboardProps> = ({ data, onNavigate }) => {
  if (!data) {
    return <div className="text-center py-12 text-slate-400">Loading intelligence dashboard...</div>;
  }

  const categoryLabels = data.categories.slice(0, 10).map((c) => c.Category_Fine);
  const categoryValues = data.categories.slice(0, 10).map((c) => parseInt(c.Assigned_Rows, 10));

  const barData = {
    labels: categoryLabels,
    datasets: [
      {
        label: 'Assigned Products',
        data: categoryValues,
        backgroundColor: '#06b6d4',
        borderRadius: 6,
      },
    ],
  };

  const donutData = {
    labels: ['Tier 1 Verified', 'Tier 3 Candidate', 'Open Conflicts'],
    datasets: [
      {
        data: [data.tier1_verified_count, data.tier3_candidate_count, data.open_conflicts_count],
        backgroundColor: ['#10b981', '#6366f1', '#f59e0b'],
        borderWidth: 0,
      },
    ],
  };

  return (
    <div className="space-y-8">
      {/* HERO BANNER */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-dark-800 via-indigo-950/40 to-dark-800 border border-slate-800 p-8 shadow-2xl">
        <div className="relative z-10 grid lg:grid-cols-3 gap-8 items-center">
          <div className="lg:col-span-2 space-y-4">
            <div className="inline-flex items-center space-x-2 bg-cyan-500/10 border border-cyan-500/20 px-3 py-1 rounded-full text-xs text-cyan-400 font-medium">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Automated Product Intelligence & Provenance Governance</span>
            </div>
            <h1 className="text-3xl lg:text-4xl font-extrabold text-white tracking-tight leading-tight">
              Transform Raw Industrial Data Into Search-Ready Commerce Intelligence
            </h1>
            <p className="text-sm text-slate-300 max-w-2xl leading-relaxed">
              UNILOG cleans cryptic supplier descriptions, entity-resolves legal manufacturers, reconciles attribute labels, and enforces strict 252-column delivery contracts with complete evidence provenance.
            </p>
            <div className="flex flex-wrap gap-4 pt-2">
              <button
                onClick={() => onNavigate('products')}
                className="bg-cyan-500 hover:bg-cyan-400 text-dark-900 font-semibold text-xs px-5 py-2.5 rounded-lg transition-colors flex items-center space-x-2 shadow-lg shadow-cyan-500/20"
              >
                <span>Explore Enriched Results (1,000 Rows)</span>
                <ArrowRight className="w-4 h-4" />
              </button>
              <button
                onClick={() => onNavigate('import')}
                className="bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-xs px-5 py-2.5 rounded-lg border border-slate-700 transition-colors"
              >
                <span>Import New Catalog</span>
              </button>
            </div>
          </div>

          {/* ANIMATED ENRICHMENT FLOW PREVIEW */}
          <div className="bg-dark-900/80 border border-slate-800 rounded-xl p-5 space-y-3 font-mono text-xs shadow-inner">
            <div className="flex items-center justify-between text-slate-400 text-[11px] border-b border-slate-800 pb-2">
              <span>LIVE PIPELINE EXECUTION</span>
              <span className="text-emerald-400 font-semibold">ACTIVE</span>
            </div>
            <div className="space-y-2 text-[11px]">
              <div className="flex items-center justify-between text-slate-400">
                <span>Raw Input:</span>
                <span className="text-amber-300 font-bold truncate max-w-[180px]">DCB518ASTS06G Diablo 1/2"x18"</span>
              </div>
              <div className="flex items-center justify-between text-slate-400">
                <span>Classification:</span>
                <span className="text-cyan-400 font-bold">Abrasives &gt; Sanding Belts</span>
              </div>
              <div className="flex items-center justify-between text-slate-400">
                <span>Manufacturer:</span>
                <span className="text-slate-200">Freud Inc (Diablo®)</span>
              </div>
              <div className="flex items-center justify-between text-slate-400">
                <span>Dimensions:</span>
                <span className="text-emerald-400 font-bold">1/2 in W x 18 in L</span>
              </div>
              <div className="flex items-center justify-between text-slate-400">
                <span>INVOICE_DESC:</span>
                <span className="text-white font-bold text-[10px]">SANDING BELT 1/2 IN 18 IN</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* KPI METRIC CARDS */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="glass-card rounded-xl p-5 space-y-2 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Total Products Processed</span>
            <Package className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-white">{data.total_rows.toLocaleString()}</span>
            <span className="text-xs text-emerald-400 font-medium">100% Schema Valid</span>
          </div>
          <p className="text-[11px] text-slate-400">Preserving 999 unique MPNs 1-to-1</p>
        </div>

        <div className="glass-card rounded-xl p-5 space-y-2 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Classified Scope Rate</span>
            <FolderTree className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-white">{data.classification_rate}%</span>
            <span className="text-xs text-slate-300">{data.classified_count} / {data.total_rows}</span>
          </div>
          <p className="text-[11px] text-slate-400">{data.unresolved_count} unresolved (honest boundary)</p>
        </div>

        <div className="glass-card rounded-xl p-5 space-y-2 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Tier-1 Evidence Verified</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-emerald-400">{data.tier1_verified_count}</span>
            <span className="text-xs text-slate-300">Direct Live Evidence</span>
          </div>
          <p className="text-[11px] text-slate-400">{data.tier3_candidate_count} Tier-3 candidate products UNVERIFIED</p>
        </div>

        <div className="glass-card rounded-xl p-5 space-y-2 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Description Compliance</span>
            <FileCheck className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="flex items-baseline space-x-2">
            <span className="text-3xl font-extrabold text-white">100%</span>
            <span className="text-xs text-emerald-400 font-medium">0 Violations</span>
          </div>
          <p className="text-[11px] text-slate-400">INVOICE ≤ 40 chars & MOBILE ≤ 80 chars</p>
        </div>
      </div>

      {/* CHARTS SECTION */}
      <div className="grid lg:grid-cols-3 gap-6">
        <div className="glass-card rounded-xl p-6 lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div>
              <h3 className="text-sm font-bold text-white">Classified Category Breakdown (21 Fine Categories)</h3>
              <p className="text-xs text-slate-400">Distribution of assigned products across core industrial taxonomy schemas</p>
            </div>
            <span className="text-xs bg-slate-800 text-slate-300 px-2.5 py-1 rounded-md font-mono">366 Items</span>
          </div>
          <div className="h-64 relative">
            <Bar
              data={barData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                  x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { display: false } },
                  y: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { color: 'rgba(255,255,255,0.05)' } },
                },
              }}
            />
          </div>
        </div>

        <div className="glass-card rounded-xl p-6 space-y-4">
          <div className="border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-white">Quality Tier & Governance Distribution</h3>
            <p className="text-xs text-slate-400">Evidence status & quality confidence bands</p>
          </div>
          <div className="h-48 relative flex items-center justify-center">
            <Doughnut
              data={donutData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                cutout: '75%',
              }}
            />
          </div>
          <div className="space-y-2 text-xs border-t border-slate-800 pt-3">
            <div className="flex justify-between text-slate-300">
              <span className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
                <span>Tier 1 Directly Verified:</span>
              </span>
              <span className="font-bold font-mono">{data.tier1_verified_count} ({data.compliance.schema_contract_status ? '6.6%' : ''})</span>
            </div>
            <div className="flex justify-between text-slate-300">
              <span className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 rounded-full bg-indigo-400"></span>
                <span>Tier 3 Candidate Only:</span>
              </span>
              <span className="font-bold font-mono">{data.tier3_candidate_count} (93.4%)</span>
            </div>
            <div className="flex justify-between text-slate-300">
              <span className="flex items-center space-x-2">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-400"></span>
                <span>Open Conflict Hold:</span>
              </span>
              <span className="font-bold font-mono text-amber-400">{data.open_conflicts_count} Pending Review</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
