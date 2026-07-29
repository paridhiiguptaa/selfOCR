import React, { useState } from 'react';
import type { TextRegionData } from '../types/ocr';
import { Tag, Sparkles } from 'lucide-react';

interface BoundingBoxViewerProps {
  annotatedImage: string;
  regions: TextRegionData[];
}

export const BoundingBoxViewer: React.FC<BoundingBoxViewerProps> = ({
  annotatedImage,
  regions,
}) => {
  const [selectedRegionId, setSelectedRegionId] = useState<number | null>(null);
  const [hoveredRegionId, setHoveredRegionId] = useState<number | null>(null);

  return (
    <div className="flex flex-col lg:flex-row gap-6">
      {/* Annotated Image Column */}
      <div className="flex-1 flex flex-col space-y-3">
        {/* Color Legend Bar */}
        <div className="flex flex-wrap items-center gap-4 bg-slate-900/60 p-3 rounded-xl border border-slate-800 text-xs">
          <span className="font-semibold text-slate-400">Legend:</span>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded-sm bg-blue-500 inline-block border border-blue-400" />
            <span className="text-slate-300 font-medium">Printed Text</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded-sm bg-emerald-500 inline-block border border-emerald-400" />
            <span className="text-slate-300 font-medium">Handwritten Text</span>
          </div>
          <div className="flex items-center space-x-1.5">
            <span className="w-3 h-3 rounded-sm bg-amber-500 inline-block border border-amber-400" />
            <span className="text-slate-300 font-medium">Fallback Recovered</span>
          </div>
        </div>

        {/* Annotated Image */}
        <div className="relative bg-slate-950 rounded-2xl overflow-hidden border border-slate-800 flex items-center justify-center p-2 min-h-[480px]">
          <img
            src={annotatedImage}
            alt="Detected Regions"
            className="max-h-[600px] w-auto object-contain rounded-lg"
          />
        </div>
      </div>

      {/* Synchronized Side Panel */}
      <div className="w-full lg:w-80 bg-slate-900/80 border border-slate-800 rounded-2xl p-4 flex flex-col h-[580px]">
        <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3 flex items-center justify-between">
          <span>Detected Text Regions ({regions.length})</span>
          <Tag className="w-3.5 h-3.5 text-blue-400" />
        </h4>

        {/* Region List Scrollable */}
        <div className="flex-1 overflow-y-auto space-y-2 pr-1">
          {regions.map((reg) => {
            const isSelected = reg.region_id === selectedRegionId;
            const isHovered = reg.region_id === hoveredRegionId;

            return (
              <div
                key={reg.region_id}
                onClick={() => setSelectedRegionId(reg.region_id)}
                onMouseEnter={() => setHoveredRegionId(reg.region_id)}
                onMouseLeave={() => setHoveredRegionId(null)}
                className={`p-3 rounded-xl border text-xs cursor-pointer transition-all ${
                  isSelected
                    ? 'bg-blue-600/20 border-blue-500 shadow-md shadow-blue-500/10'
                    : isHovered
                    ? 'bg-slate-800 border-slate-700'
                    : 'bg-slate-950/60 border-slate-800/80 hover:bg-slate-800/60'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono font-bold text-slate-300 bg-slate-800 px-1.5 py-0.5 rounded text-[11px]">
                      #{reg.region_id}
                    </span>

                    {/* Text Type Badge */}
                    <span
                      className={`px-2 py-0.5 rounded-full font-bold text-[10px] ${
                        reg.text_type === 'handwritten'
                          ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                          : 'bg-blue-500/20 text-blue-300 border border-blue-500/30'
                      }`}
                    >
                      {reg.text_type}
                    </span>
                  </div>

                  {/* Confidence Badge */}
                  <span
                    className={`font-mono font-bold text-[11px] ${
                      reg.confidence >= 0.8
                        ? 'text-emerald-400'
                        : reg.confidence >= 0.6
                        ? 'text-amber-400'
                        : 'text-rose-400'
                    }`}
                  >
                    {(reg.confidence * 100).toFixed(0)}%
                  </span>
                </div>

                <p className="text-slate-200 font-medium line-clamp-2 bg-slate-900/60 p-2 rounded-lg border border-slate-800 font-mono text-[11px]">
                  {reg.text || '<Empty region>'}
                </p>

                {reg.fallback_triggered && (
                  <div className="mt-1.5 flex items-center space-x-1 text-[10px] text-amber-400">
                    <Sparkles className="w-3 h-3 flex-shrink-0" />
                    <span>Fallback Recovery Applied</span>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
