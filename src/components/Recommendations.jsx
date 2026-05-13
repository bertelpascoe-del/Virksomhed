import React from 'react';
const Recommendations=({recommendations=[]})=><div className="bg-white p-6 rounded-xl shadow-lg"><h2 className="text-2xl font-bold mb-4">Recommendations</h2>{recommendations.map((r,i)=><div key={i} className="p-4 mb-3 bg-indigo-50 border-l-4 border-indigo-400 rounded"><h3 className="font-bold">{r.title}</h3><p>{r.text}</p></div>)}</div>;
export default Recommendations;
