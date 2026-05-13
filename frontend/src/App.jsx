import React, { useState } from 'react';
import FileUploader from './components/FileUploader';
import Dashboard from './components/Dashboard';
import { Loader } from 'lucide-react';

const fallback = { score: 0, description: 'Analysis Failure', metrics: { GrossProfit:0, NetProfit:0, GrossMarginPct:0, NetMarginPct:0, ExpenseRatioPct:0, DebtToRevenueRatioPct:0, CurrentRatio:0, CashFlowMarginPct:0 }, raw_metrics: { revenue:0, cogs:0, expenses:0, debt:0, assets:0, liabilities:0, cashflow:0 }, warnings: ['Analysis failed. Check that backend is running.'], summary: 'Analysis failed.', strengths: [], weaknesses: [], recommendations: [] };

function App(){
  const [results,setResults]=useState(null);
  const [loading,setLoading]=useState(false);
  const handleAnalysis=async(files)=>{
    if(!files.length)return;
    setLoading(true); setResults(null);
    const fd=new FormData(); files.forEach(f=>fd.append('files',f));
    try{
      const res=await fetch('http://localhost:5000/api/analyze',{method:'POST',body:fd});
      if(!res.ok){const e=await res.json(); throw new Error(e.error || 'Analysis failed');}
      setResults(await res.json());
    }catch(e){console.error(e); setResults(fallback);} finally{setLoading(false);}
  };
  return <div className="min-h-screen bg-gray-50"><header className="bg-white shadow-md p-4"><div className="max-w-6xl mx-auto"><h1 className="text-3xl font-extrabold text-indigo-700">SMB Financial Health Analyzer</h1></div></header><main className="p-4 md:p-10 max-w-6xl mx-auto"><div className="grid lg:grid-cols-3 gap-8"><div><FileUploader onAnalyze={handleAnalysis}/></div><div className="lg:col-span-2">{loading ? <div className="p-12 bg-white shadow-xl rounded-xl flex flex-col items-center"><Loader className="w-12 h-12 animate-spin text-indigo-600"/><p className="mt-4">Analyzing...</p></div> : results ? <Dashboard results={results}/> : <div className="p-12 bg-white shadow-xl rounded-xl text-center text-gray-500"><h2 className="text-2xl font-semibold">Awaiting Analysis</h2><p>Upload files to begin.</p></div>}</div></div></main></div>;
}
export default App;
