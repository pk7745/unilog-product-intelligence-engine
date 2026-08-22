import React, { useState, useEffect } from 'react';
import { OverviewData } from './types';
import { fetchOverview, fetchReviewQueue, runPipeline } from './services/api';
import { Navbar } from './components/Navbar';
import { OverviewDashboard } from './components/OverviewDashboard';
import { CatalogImport } from './components/CatalogImport';
import { ProductWorkspace } from './components/ProductWorkspace';
import { ProductDetailModal } from './components/ProductDetailModal';
import { BeforeAfterComparison } from './components/BeforeAfterComparison';
import { QualityGovernanceCenter } from './components/QualityGovernanceCenter';
import { HumanReviewQueue } from './components/HumanReviewQueue';
import { ExportCenter } from './components/ExportCenter';

export function App() {
  const [currentTab, setCurrentTab] = useState('overview');
  const [overviewData, setOverviewData] = useState<OverviewData | null>(null);
  const [reviewCount, setReviewCount] = useState<number>(0);
  const [isDark, setIsDark] = useState(true);
  const [isRunningPipeline, setIsRunningPipeline] = useState(false);
  const [inspectMpn, setInspectMpn] = useState<string | null>(null);

  const loadOverview = async () => {
    try {
      const data = await fetchOverview();
      setOverviewData(data);
    } catch (err) {
      console.error(err);
    }
  };

  const loadReviewCount = async () => {
    try {
      const res = await fetchReviewQueue();
      setReviewCount(res.total_in_queue || 0);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadOverview();
    loadReviewCount();
  }, []);

  const handleToggleTheme = () => {
    setIsDark(!isDark);
    document.documentElement.classList.toggle('dark');
  };

  const handleRunPipeline = async () => {
    if (!window.confirm('Run full 1,000-row enrichment pipeline and quality gates check?')) return;
    setIsRunningPipeline(true);
    try {
      const res = await runPipeline();
      alert(`Pipeline completed in ${res.elapsed_seconds}s! Processed ${res.rows_processed} rows.`);
      loadOverview();
      loadReviewCount();
    } catch (err: any) {
      alert(`Pipeline execution error: ${err.message}`);
    } finally {
      setIsRunningPipeline(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col font-sans">
      <Navbar
        currentTab={currentTab}
        onTabChange={setCurrentTab}
        onRunPipeline={handleRunPipeline}
        isDark={isDark}
        onToggleTheme={handleToggleTheme}
        reviewCount={reviewCount}
      />

      <main className="flex-1 p-4 lg:p-8 max-w-[1600px] w-full mx-auto space-y-8">
        {currentTab === 'overview' && (
          <OverviewDashboard data={overviewData} onNavigate={setCurrentTab} />
        )}
        {currentTab === 'import' && (
          <CatalogImport onRunPipeline={handleRunPipeline} isRunning={isRunningPipeline} />
        )}
        {currentTab === 'products' && (
          <ProductWorkspace onInspectProduct={(mpn) => setInspectMpn(mpn)} />
        )}
        {currentTab === 'comparison' && <BeforeAfterComparison />}
        {currentTab === 'quality' && <QualityGovernanceCenter />}
        {currentTab === 'review' && (
          <HumanReviewQueue
            onDecisionApplied={() => {
              loadOverview();
              loadReviewCount();
            }}
            onQueueUpdated={(count) => setReviewCount(count)}
          />
        )}
        {currentTab === 'export' && <ExportCenter />}
      </main>

      <ProductDetailModal mpn={inspectMpn} onClose={() => setInspectMpn(null)} />
    </div>
  );
}
