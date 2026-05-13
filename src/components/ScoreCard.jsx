import React from 'react';
const ScoreCard=({score,description})=><div className="p-8 rounded-xl shadow-2xl border-l-8 bg-white border-indigo-500"><p className="text-sm uppercase text-gray-500">Financial Health Score</p><div><span className="text-8xl font-extrabold text-indigo-700">{score}</span><span className="ml-2 text-xl text-gray-500">/100</span></div><h3 className="mt-3 text-2xl font-bold text-gray-800">{description}</h3></div>;
export default ScoreCard;
