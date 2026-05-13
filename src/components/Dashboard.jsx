import React from 'react';
import ScoreCard from './ScoreCard';
import MetricsGrid from './MetricsGrid';
import Recommendations from './Recommendations';
import FinancialCharts from './FinancialCharts';
import ScoreTrendChart from './ScoreTrendChart';

const Dashboard = ({ results }) => {
  const {
    score,
    description,
    metrics,
    warnings = [],
    summary,
    strengths = [],
    weaknesses = [],
    recommendations = [],
    raw_metrics,
    score_over_time = [],
  } = results;

  return (
    <div className="space-y-10">
      <ScoreCard score={score} description={description} />

      <section className="grid lg:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-xl font-bold mb-3">Financial Summary</h2>
          <p>{summary}</p>

          <h3 className="mt-4 font-bold">Warnings</h3>
          {warnings.length ? (
            <ul className="text-red-500 list-disc list-inside">
              {warnings.map((warning, index) => (
                <li key={index}>{warning}</li>
              ))}
            </ul>
          ) : (
            <p className="text-green-600">No major data issues detected.</p>
          )}
        </div>

        <div className="bg-white p-6 rounded-xl shadow-lg">
          <h2 className="text-xl font-bold mb-3">Key Analysis</h2>

          <h3 className="font-bold text-green-700">Strengths</h3>
          <ul className="list-disc list-inside">
            {strengths.map((strength, index) => (
              <li key={index}>{strength}</li>
            ))}
          </ul>

          <h3 className="font-bold text-red-700 mt-4">Weaknesses</h3>
          <ul className="list-disc list-inside">
            {weaknesses.map((weakness, index) => (
              <li key={index}>{weakness}</li>
            ))}
          </ul>
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          Key Financial Ratios
        </h2>
        <MetricsGrid metrics={metrics} />
      </section>

      <section>
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          Actionable Recommendations
        </h2>
        <Recommendations recommendations={recommendations} />
      </section>

      <section>
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          Score Over Time
        </h2>
        <ScoreTrendChart data={score_over_time} />
      </section>

      <section>
        <h2 className="text-2xl font-bold text-gray-800 mb-4">
          Performance Visualization
        </h2>
        <FinancialCharts rawMetrics={raw_metrics} />
      </section>

      <div className="p-4 bg-yellow-50 border-l-4 border-yellow-500 text-sm">
        Disclaimer: This is an estimated analysis, not professional financial advice.
      </div>
    </div>
  );
};

export default Dashboard;