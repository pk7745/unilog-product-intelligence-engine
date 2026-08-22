import React from 'react';
import { FileSpreadsheet, ClipboardCheck, FileCode } from 'lucide-react';

export const ExportCenter: React.FC = () => {
  return (
    <div className="glass-card rounded-2xl p-8 max-w-3xl mx-auto space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-white">Deliverable Export Center</h2>
        <p className="text-xs text-slate-400">
          Download canonical 252-column delivery files, quality audit logs, and field evidence provenance traces.
        </p>
      </div>

      <div className="grid sm:grid-cols-3 gap-4 pt-4">
        <div className="bg-dark-900 border border-slate-800 rounded-xl p-5 space-y-3 text-center hover:border-cyan-400 transition-colors">
          <FileSpreadsheet className="w-8 h-8 text-cyan-400 mx-auto" />
          <div>
            <h4 className="text-xs font-bold text-white">Final Delivery CSV</h4>
            <p className="text-[11px] text-slate-400">1,000 rows x 252 cols</p>
          </div>
          <a
            href="/api/export/final_delivery"
            download
            className="block bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 text-xs font-semibold py-2 rounded-lg transition-colors"
          >
            Download CSV
          </a>
        </div>

        <div className="bg-dark-900 border border-slate-800 rounded-xl p-5 space-y-3 text-center hover:border-indigo-400 transition-colors">
          <ClipboardCheck className="w-8 h-8 text-indigo-400 mx-auto" />
          <div>
            <h4 className="text-xs font-bold text-white">QA Quality Report</h4>
            <p className="text-[11px] text-slate-400">Confidence & Review flags</p>
          </div>
          <a
            href="/api/export/qa_report"
            download
            className="block bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-xs font-semibold py-2 rounded-lg transition-colors"
          >
            Download QA CSV
          </a>
        </div>

        <div className="bg-dark-900 border border-slate-800 rounded-xl p-5 space-y-3 text-center hover:border-emerald-400 transition-colors">
          <FileCode className="w-8 h-8 text-emerald-400 mx-auto" />
          <div>
            <h4 className="text-xs font-bold text-white">Field Provenance Log</h4>
            <p className="text-[11px] text-slate-400">JSONL Evidence Traces</p>
          </div>
          <a
            href="/api/export/field_provenance"
            download
            className="block bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 text-xs font-semibold py-2 rounded-lg transition-colors"
          >
            Download JSONL
          </a>
        </div>
      </div>
    </div>
  );
};
