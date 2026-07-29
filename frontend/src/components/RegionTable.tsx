import React from 'react';
import type { TextRegionData } from '../types/ocr';
import { Sparkles } from 'lucide-react';

interface RegionTableProps {
  regions: TextRegionData[];
}

export const RegionTable: React.FC<RegionTableProps> = ({ regions }) => {
  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl overflow-hidden shadow-xl">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="bg-slate-800/80 text-slate-400 border-b border-slate-700 font-semibold uppercase tracking-wider">
              <th className="py-3 px-4"># ID</th>
              <th className="py-3 px-4">Order / Pos</th>
              <th className="py-3 px-4">BBox Coordinates</th>
              <th className="py-3 px-4">Text Classification</th>
              <th className="py-3 px-4">Confidence Score</th>
              <th className="py-3 px-4">Fallback Triggered</th>
              <th className="py-3 px-4">Recognized Text Snippet</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono">
            {regions.map((reg) => (
              <tr key={reg.region_id} className="hover:bg-slate-800/40 transition-colors">
                <td className="py-3 px-4 font-bold text-slate-300">#{reg.region_id}</td>
                <td className="py-3 px-4 text-slate-400">
                  L{reg.line_number}:C{reg.column_number} (Idx #{reg.reading_order_idx})
                </td>
                <td className="py-3 px-4 text-slate-400">
                  ({reg.bbox.join(', ')})
                </td>
                <td className="py-3 px-4">
                  <span
                    className={`px-2.5 py-1 rounded-full text-[10px] font-bold ${
                      reg.text_type === 'handwritten'
                        ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                        : 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                    }`}
                  >
                    {reg.text_type}
                  </span>
                </td>
                <td className="py-3 px-4">
                  <span
                    className={`font-bold ${
                      reg.confidence >= 0.8
                        ? 'text-emerald-400'
                        : reg.confidence >= 0.6
                        ? 'text-amber-400'
                        : 'text-rose-400'
                    }`}
                  >
                    {(reg.confidence * 100).toFixed(1)}%
                  </span>
                </td>
                <td className="py-3 px-4">
                  {reg.fallback_triggered ? (
                    <span className="flex items-center space-x-1 text-amber-400 font-sans font-medium text-[11px]">
                      <Sparkles className="w-3.5 h-3.5" />
                      <span>Recovered</span>
                    </span>
                  ) : (
                    <span className="text-slate-600 font-sans">-</span>
                  )}
                </td>
                <td className="py-3 px-4 text-slate-200 font-sans text-xs max-w-xs truncate">
                  {reg.text || '<Empty region>'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
