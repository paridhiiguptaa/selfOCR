import React, { useState } from 'react';
import { Sliders } from 'lucide-react';

interface SideBySideSliderProps {
  originalImage: string;
  preprocessedImage: string;
  orientationAngle: number;
  skewAngle: number;
  perspectiveCorrected: boolean;
}

export const SideBySideSlider: React.FC<SideBySideSliderProps> = ({
  originalImage,
  preprocessedImage,
  orientationAngle,
  skewAngle,
  perspectiveCorrected,
}) => {
  const [sliderPos, setSliderPos] = useState<number>(50);

  return (
    <div className="flex flex-col space-y-4">
      {/* Correction Telemetry Pill Badges */}
      <div className="flex flex-wrap gap-2.5 bg-slate-900/60 p-3 rounded-xl border border-slate-800 text-xs">
        <div className="flex items-center space-x-1.5 px-3 py-1 bg-slate-800 rounded-lg text-slate-300 border border-slate-700">
          <span className="text-slate-400">Rotation Angle:</span>
          <span className="font-mono font-bold text-blue-400">{orientationAngle}°</span>
        </div>
        <div className="flex items-center space-x-1.5 px-3 py-1 bg-slate-800 rounded-lg text-slate-300 border border-slate-700">
          <span className="text-slate-400">Deskew Angle:</span>
          <span className="font-mono font-bold text-blue-400">{skewAngle.toFixed(2)}°</span>
        </div>
        <div className="flex items-center space-x-1.5 px-3 py-1 bg-slate-800 rounded-lg text-slate-300 border border-slate-700">
          <span className="text-slate-400">Perspective Rectified:</span>
          <span className={`font-semibold ${perspectiveCorrected ? 'text-emerald-400' : 'text-slate-400'}`}>
            {perspectiveCorrected ? 'Yes (4-Corner Fix)' : 'No (Already Rectified)'}
          </span>
        </div>
      </div>

      {/* Interactive Image Split View Container */}
      <div className="relative w-full h-[520px] bg-slate-950 rounded-2xl overflow-hidden border border-slate-800 select-none">
        {/* Preprocessed Image (Right Layer) */}
        <img
          src={preprocessedImage}
          alt="Preprocessed"
          className="absolute top-0 left-0 w-full h-full object-contain pointer-events-none"
        />

        {/* Original Image (Left Layer with Clip) */}
        <div
          className="absolute top-0 left-0 h-full overflow-hidden"
          style={{ width: `${sliderPos}%` }}
        >
          <img
            src={originalImage}
            alt="Original"
            className="w-full h-full object-contain pointer-events-none"
            style={{ width: '100%', minWidth: '100%' }}
          />
        </div>

        {/* Vertical Divider Slider */}
        <div
          className="absolute top-0 bottom-0 w-1 bg-blue-500 cursor-ew-resize flex items-center justify-center shadow-lg shadow-blue-500/50"
          style={{ left: `${sliderPos}%` }}
        >
          <div className="w-8 h-8 rounded-full bg-blue-600 border-2 border-white text-white flex items-center justify-center shadow-xl">
            <Sliders className="w-4 h-4" />
          </div>
        </div>

        {/* Native Range Slider Overlay */}
        <input
          type="range"
          min="0"
          max="100"
          value={sliderPos}
          onChange={(e) => setSliderPos(Number(e.target.value))}
          className="absolute inset-0 w-full h-full opacity-0 cursor-ew-resize"
        />

        {/* Corner Labels */}
        <div className="absolute top-3 left-3 bg-slate-900/80 backdrop-blur-md px-3 py-1 rounded-lg text-xs font-semibold text-slate-300 border border-slate-700">
          Original Image ({sliderPos}%)
        </div>
        <div className="absolute top-3 right-3 bg-slate-900/80 backdrop-blur-md px-3 py-1 rounded-lg text-xs font-semibold text-emerald-400 border border-emerald-500/30">
          Corrected & Enhanced ({100 - sliderPos}%)
        </div>
      </div>
    </div>
  );
};
