import React, { useState } from 'react';
import { FileText, Sparkles } from 'lucide-react';

export const BeforeAfterComparison: React.FC = () => {
  const [selectedMpn, setSelectedMpn] = useState('DCB518ASTS06G');

  const samples: Record<string, any> = {
    DCB518ASTS06G: {
      mpn: 'DCB518ASTS06G',
      raw_desc: 'DCB518ASTS06G Diablo 1/2"x18" - Sanding Belt 6pc',
      raw_manuf: 'Freud Inc (2435)',
      raw_brand: '-- Unbranded --',
      enr_manuf: 'Freud Inc',
      enr_brand: 'Diablo®',
      classpath: 'Abrasives > Sanding & Finishing > Sanding Belts',
      invoice_desc: 'SANDING BELT 1/2 IN 18 IN',
      mobile_desc: 'Freud Inc, Diablo®, Sanding Belt, DCB518ASTS06G',
      attrs: ['Width: 1/2 in', 'Length: 18 in', 'Grit: 60'],
    },
    '49-94-0013': {
      mpn: '49-94-0013',
      raw_desc: '49-94-0013 Milw 5"x.045"x7/8" Metal Cut Off Disc',
      raw_manuf: 'Milwaukee Accessory (4031)',
      raw_brand: '-- No Unilog Brand --',
      enr_manuf: 'Milwaukee Tool',
      enr_brand: 'Milwaukee',
      classpath: 'Abrasives > Cutting & Grinding > Cut-Off Discs',
      invoice_desc: 'CUT OFF DISC 5 IN 0.045 IN 7/8 IN',
      mobile_desc: 'Milwaukee Tool, Milwaukee, Cut-Off Disc, 49-94-0013',
      attrs: ['Diameter: 5 in', 'Thickness: 0.045 in', 'Arbor Size: 7/8 in'],
    },
    '543140016': {
      mpn: '543140016',
      raw_desc: "543140016 Trex Lineage 1x6-16' Deck Board",
      raw_manuf: 'Boise Cascade Building Materials',
      raw_brand: '-- No DIB Brand --',
      enr_manuf: 'Trex Company, Inc.',
      enr_brand: 'Trex® Lineage',
      classpath: 'Decking & Railing > Deck Boards > Composite Decking',
      invoice_desc: 'DECK BOARD 1 IN 6 IN 16 FT',
      mobile_desc: 'Trex Company, Inc., Trex® Lineage, Deck Board',
      attrs: ['Thickness: 1 in', 'Width: 6 in', 'Length: 16 ft'],
    },
  };

  const sample = samples[selectedMpn] || samples['DCB518ASTS06G'];

  return (
    <div className="glass-card rounded-2xl p-6 space-y-6">
      <div className="border-b border-slate-800 pb-4 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">Raw vs Enriched Product Intelligence Comparison</h2>
          <p className="text-xs text-slate-400">
            Select any product sample to compare raw supplier input against normalized 252-column commerce output.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          {Object.keys(samples).map((mpn) => (
            <button
              key={mpn}
              onClick={() => setSelectedMpn(mpn)}
              className={`px-3 py-1 rounded text-xs font-mono transition-colors ${
                selectedMpn === mpn
                  ? 'bg-cyan-500 text-dark-900 font-bold'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              {mpn}
            </button>
          ))}
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
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
              <span className="text-white font-bold">{sample.mpn}</span>
            </div>
            <div>
              <span className="text-slate-500 text-[11px] block">Part_Desc:</span>
              <span className="text-amber-200 bg-amber-500/5 p-2 rounded block">{sample.raw_desc}</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <span className="text-slate-500 text-[11px] block">Part_Manuf:</span>
                <span className="text-slate-300">{sample.raw_manuf}</span>
              </div>
              <div>
                <span className="text-slate-500 text-[11px] block">E1_Brand:</span>
                <span className="text-slate-500 italic">{sample.raw_brand}</span>
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
                <span className="text-white font-semibold">{sample.enr_manuf}</span>
              </div>
              <div>
                <span className="text-slate-400 text-[11px] block">Brand Name:</span>
                <span className="text-cyan-400 font-semibold">{sample.enr_brand}</span>
              </div>
            </div>
            <div>
              <span className="text-slate-400 text-[11px] block">Classpath Taxonomy:</span>
              <span className="text-emerald-400 font-mono text-[11px]">{sample.classpath}</span>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <span className="text-slate-400 text-[11px] block">INVOICE_DESC (≤40 CAPS):</span>
                <span className="text-white font-mono font-bold bg-slate-800 px-2 py-1 rounded block">{sample.invoice_desc}</span>
              </div>
              <div>
                <span className="text-slate-400 text-[11px] block">MOBILE_DESC (60-80):</span>
                <span className="text-slate-200 font-mono text-[10px] bg-slate-800 px-2 py-1 rounded block">{sample.mobile_desc}</span>
              </div>
            </div>
            <div>
              <span className="text-slate-400 text-[11px] block">Extracted Dimension Triplets:</span>
              <div className="flex flex-wrap gap-2 pt-1">
                {sample.attrs.map((attr: string, idx: number) => (
                  <span key={idx} className="bg-slate-800 text-cyan-300 font-mono text-[10px] px-2 py-1 rounded border border-slate-700">
                    {attr}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
