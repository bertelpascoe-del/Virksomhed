
import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

const ScoreTrendChart = ({ data = [] }) => {
  if (!data || data.length === 0) {
    return (
      <div className="bg-white p-6 rounded-xl shadow-lg">
        <p className="text-gray-500 text-sm">
          No time-based score data was detected. Upload a file with rows for months,
          quarters, or years.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-xl shadow-lg">
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="period" />
          <YAxis domain={[0, 100]} />
          <Tooltip />
          <ReferenceLine y={75} stroke="#22c55e" strokeDasharray="4 4" />
          <ReferenceLine y={60} stroke="#eab308" strokeDasharray="4 4" />
          <ReferenceLine y={40} stroke="#ef4444" strokeDasharray="4 4" />
          <Line
            type="monotone"
            dataKey="score"
            stroke="#4f46e5"
            strokeWidth={3}
            dot={{ r: 4 }}
            name="Financial Health Score"
          />
        </LineChart>
      </ResponsiveContainer>

      <p className="text-sm text-gray-500 mt-4 italic">
        Green line: good range. Yellow line: attention range. Red line: risk range.
      </p>
    </div>
  );
};

export default ScoreTrendChart;
