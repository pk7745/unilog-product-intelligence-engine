import React, { useState } from 'react';
import { UploadCloud, CheckCircle, Play } from 'lucide-react';

interface CatalogImportProps {
  onRunPipeline: () => void;
  isRunning: boolean;
}

export const CatalogImport: React.FC<CatalogImportProps> = ({ onRunPipeline, isRunning }) => {
  const [selectedFile, setSelectedFile] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0].name);
    }
  };

  return (
    <div className="glass-card rounded-2xl p-8 space-y-8 max-w-4xl mx-auto">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-white">Import & Enrich Product Catalog</h2>
        <p className="text-xs text-slate-400">
          Upload a raw supplier CSV to run through normalization, entity resolution, classification, and quality scoring.
        </p>
      </div>

      <div
        className="border-2 border-dashed border-slate-700 hover:border-cyan-400 bg-dark-900/50 rounded-2xl p-10 text-center transition-colors cursor-pointer space-y-4"
        onClick={() => document.getElementById('file-upload-input-react')?.click()}
      >
        <input
          type="file"
          id="file-upload-input-react"
          className="hidden"
          accept=".csv"
          onChange={handleFileChange}
        />
        <div className="w-14 h-14 bg-cyan-500/10 text-cyan-400 rounded-2xl flex items-center justify-center mx-auto shadow-lg shadow-cyan-500/10">
          <UploadCloud className="w-7 h-7" />
        </div>
        <div>
          <p className="text-sm font-semibold text-white">Click or drag raw supplier CSV file here</p>
          <p className="text-xs text-slate-400">
            Supports <span className="font-mono text-cyan-300">Mfg_Part_Num, Part_Desc, Part_Manuf, E1_Brand, DIB_Brand</span>
          </p>
        </div>
        <span className="inline-block bg-slate-800 text-slate-300 text-xs px-3 py-1.5 rounded-lg border border-slate-700">
          {selectedFile ? `Selected: ${selectedFile}` : 'Currently Loaded: Unihack__Sample_Dataset_-_Input.csv (1,000 Rows)'}
        </span>
      </div>

      <div className="space-y-4">
        <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Automated Enrichment Stages</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
          <div className="bg-dark-900 border border-slate-800 p-3 rounded-lg flex items-center space-x-2">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            <span>1. Normalization</span>
          </div>
          <div className="bg-dark-900 border border-slate-800 p-3 rounded-lg flex items-center space-x-2">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            <span>2. Entity Resolution</span>
          </div>
          <div className="bg-dark-900 border border-slate-800 p-3 rounded-lg flex items-center space-x-2">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            <span>3. Taxonomy Classifier</span>
          </div>
          <div className="bg-dark-900 border border-slate-800 p-3 rounded-lg flex items-center space-x-2">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            <span>4. Quality Scoring</span>
          </div>
        </div>
      </div>

      <div className="pt-4 flex justify-center">
        <button
          onClick={onRunPipeline}
          disabled={isRunning}
          className="bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white font-bold text-xs px-8 py-3 rounded-xl shadow-lg shadow-cyan-500/20 flex items-center space-x-2 transition-transform active:scale-95 disabled:opacity-50"
        >
          <Play className="w-4 h-4" />
          <span>{isRunning ? 'Running Pipeline...' : 'Execute Full Pipeline on Loaded Dataset'}</span>
        </button>
      </div>
    </div>
  );
};
