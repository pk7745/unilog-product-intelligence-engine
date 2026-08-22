import React, { useEffect, useState } from 'react';
import { QualityGate } from '../types';
import { fetchQualityGates } from '../services/api';
import { ShieldCheck } from 'lucide-react';

export const QualityGovernanceCenter: React.FC = () => {
  const [gates, setGates] = useState<QualityGate[]>([]);
  const [allPassed, setAllPassed] = useState(true);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchQualityGates()
      .then((res) => {
        setGates(res.gates);
        setAllPassed(res.all_passed);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="glass-card rounded-2xl p-6 space-y-6">
      <div className="border-b border-slate-800 pb-4 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Automated Quality Gates & Governance Audit</h2>
          <p className="text-xs text-slate-400">8 non-negotiable automated quality gates enforced before delivery acceptance.</p>
        </div>
        <span className="bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold px-3 py-1.5 rounded-full flex items-center space-x-1.5">
          <ShieldCheck className="w-4 h-4" />
          <span>{allPassed ? '100% Quality Compliance' : 'Gate Violations Found'}</span>
        </span>
      </div>

      {loading ? (
        <div className="text-center py-12 text-slate-500">Evaluating quality gates...</div>
      ) : (
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {gates.map((g) => (
            <div
              key={g.gate_id}
              className={`bg-dark-900 border ${
                g.status === 'PASS' ? 'border-emerald-500/30' : 'border-red-500/30'
              } p-4 rounded-xl space-y-2`}
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-white">Gate {g.gate_id}</span>
                <span
                  className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                    g.status === 'PASS' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'
                  }`}
                >
                  {g.status}
                </span>
              </div>
              <h4 className="text-xs font-semibold text-slate-200">{g.name}</h4>
              <p className="text-[11px] text-slate-400 font-mono">{g.details}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
