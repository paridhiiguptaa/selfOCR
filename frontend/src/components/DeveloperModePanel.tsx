import React from 'react';
import type { PageMetadata, DeveloperTelemetry } from '../types/ocr';
import { Cpu, Clock, Terminal, Activity, Layers } from 'lucide-react';

interface DeveloperModePanelProps {
  pageMeta: PageMetadata;
  telemetry?: DeveloperTelemetry;
}

export const DeveloperModePanel: React.FC<DeveloperModePanelProps> = ({
  pageMeta,
  telemetry,
}) => {
  const quality = pageMeta.preprocessing.quality_metrics;
  const orient = pageMeta.orientation;
  const prep = pageMeta.preprocessing;

  return (
    <div className="bg-slate-900/90 border border-amber-500/30 rounded-2xl p-6 shadow-2xl space-y-6">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center space-x-2 text-amber-400 font-bold text-sm">
          <Terminal className="w-5 h-5" />
          <span>Developer Telemetry & Diagnostics</span>
        </div>
        <span className="px-2.5 py-1 bg-amber-500/10 text-amber-300 border border-amber-500/30 rounded-md text-xs font-mono font-bold">
          DEV MODE ACTIVE
        </span>
      </div>

      {/* Grid of Telemetry Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 block mb-1 flex items-center space-x-1">
            <Clock className="w-3.5 h-3.5 text-blue-400" />
            <span>Total Time</span>
          </span>
          <span className="text-xl font-bold font-mono text-blue-400">
            {telemetry?.total_processing_time_sec ?? 0}s
          </span>
        </div>

        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 block mb-1 flex items-center space-x-1">
            <Cpu className="w-3.5 h-3.5 text-emerald-400" />
            <span>Device</span>
          </span>
          <span className="text-xl font-bold font-mono text-emerald-400 uppercase">
            {telemetry?.device ?? 'CPU'}
          </span>
        </div>

        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 block mb-1 flex items-center space-x-1">
            <Layers className="w-3.5 h-3.5 text-indigo-400" />
            <span>Handwritten OCR</span>
          </span>
          <span className="text-xs font-bold font-mono text-indigo-300 truncate block">
            {telemetry?.trocr_model ?? 'trocr-small'}
          </span>
        </div>

        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 block mb-1 flex items-center space-x-1">
            <Activity className="w-3.5 h-3.5 text-amber-400" />
            <span>Quality Skip</span>
          </span>
          <span className="text-xl font-bold font-mono text-amber-400">
            {prep.skipped ? 'YES (Clean)' : 'NO (Enhanced)'}
          </span>
        </div>
      </div>

      {/* Quality Metrics & Geometry Table */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
          <h5 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">
            Geometry & Orientation Telemetry
          </h5>
          <dl className="space-y-2 text-xs font-mono">
            <div className="flex justify-between py-1 border-b border-slate-900">
              <dt className="text-slate-400">Rotation Angle:</dt>
              <dd className="font-bold text-blue-400">{orient.rotation_angle}°</dd>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-900">
              <dt className="text-slate-400">Fine Skew Angle:</dt>
              <dd className="font-bold text-blue-400">{orient.skew_angle.toFixed(2)}°</dd>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-900">
              <dt className="text-slate-400">Perspective Rectified:</dt>
              <dd className="font-bold text-emerald-400">
                {orient.perspective_corrected ? 'True' : 'False'}
              </dd>
            </div>
            <div className="flex justify-between py-1">
              <dt className="text-slate-400">Border Scan Trimming:</dt>
              <dd className="font-bold text-slate-300">
                {prep.border_removed ? 'Applied' : 'None'}
              </dd>
            </div>
          </dl>
        </div>

        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
          <h5 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">
            Image Quality Metrics
          </h5>
          <dl className="space-y-2 text-xs font-mono">
            <div className="flex justify-between py-1 border-b border-slate-900">
              <dt className="text-slate-400">Contrast StdDev:</dt>
              <dd className="font-bold text-blue-400">{quality.contrast.toFixed(2)}</dd>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-900">
              <dt className="text-slate-400">Noise StdDev (MAD):</dt>
              <dd className="font-bold text-blue-400">{quality.noise_std.toFixed(2)}</dd>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-900">
              <dt className="text-slate-400">Mean Brightness:</dt>
              <dd className="font-bold text-slate-300">{quality.brightness_mean.toFixed(2)}</dd>
            </div>
            <div className="flex justify-between py-1">
              <dt className="text-slate-400">CLAHE Applied:</dt>
              <dd className="font-bold text-slate-300">
                {prep.clahe_applied ? 'True' : 'False'}
              </dd>
            </div>
          </dl>
        </div>
      </div>

      {/* Stage Execution Timing Table */}
      {telemetry?.stages_executed && (
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
          <h5 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">
            Per-Stage Execution Timing Breakdown
          </h5>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="text-slate-500 border-b border-slate-800">
                  <th className="py-2 px-2">Pipeline Stage</th>
                  <th className="py-2 px-2">Status</th>
                  <th className="py-2 px-2">Duration</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-900">
                {telemetry.stages_executed.map((stg, idx) => (
                  <tr key={idx}>
                    <td className="py-2 px-2 text-slate-300 font-sans">{stg.stage}</td>
                    <td className="py-2 px-2">
                      <span className="text-emerald-400 font-bold">{stg.status}</span>
                    </td>
                    <td className="py-2 px-2 text-blue-400 font-bold">{stg.duration_sec}s</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
