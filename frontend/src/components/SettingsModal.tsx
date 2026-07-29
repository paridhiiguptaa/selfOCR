import React from 'react';
import { X, Sliders, Save } from 'lucide-react';
import type { PipelineSettings } from '../types/ocr';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  settings: PipelineSettings;
  onSaveSettings: (newSettings: PipelineSettings) => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  settings,
  onSaveSettings,
}) => {
  const [localSettings, setLocalSettings] = React.useState<PipelineSettings>(settings);

  if (!isOpen) return null;

  const handleSave = () => {
    onSaveSettings(localSettings);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg p-6 shadow-2xl space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div className="flex items-center space-x-2 text-blue-400 font-bold text-base">
            <Sliders className="w-5 h-5" />
            <span>Pipeline Settings & Configuration</span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-4 text-xs">
          {/* PDF Render DPI */}
          <div>
            <label className="block text-slate-300 font-semibold mb-1.5">
              PDF Render DPI Resolution
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[150, 300, 450].map((dpi) => (
                <button
                  key={dpi}
                  onClick={() => setLocalSettings({ ...localSettings, pdf_render_dpi: dpi })}
                  className={`p-2.5 rounded-xl border text-center font-bold font-mono transition-all ${
                    localSettings.pdf_render_dpi === dpi
                      ? 'bg-blue-600/20 border-blue-500 text-blue-400'
                      : 'bg-slate-800 border-slate-700 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {dpi} DPI
                </button>
              ))}
            </div>
          </div>

          {/* Confidence Threshold Slider */}
          <div>
            <div className="flex justify-between items-center mb-1.5">
              <label className="text-slate-300 font-semibold">
                Minimum Confidence Threshold
              </label>
              <span className="font-mono font-bold text-blue-400 text-sm">
                {(localSettings.min_confidence_threshold * 100).toFixed(0)}%
              </span>
            </div>
            <input
              type="range"
              min="0.50"
              max="0.95"
              step="0.05"
              value={localSettings.min_confidence_threshold}
              onChange={(e) =>
                setLocalSettings({ ...localSettings, min_confidence_threshold: parseFloat(e.target.value) })
              }
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
          </div>

          {/* TrOCR Model Selection */}
          <div>
            <label className="block text-slate-300 font-semibold mb-1.5">
              Handwritten TrOCR Model
            </label>
            <select
              value={localSettings.trocr_model_name}
              onChange={(e) =>
                setLocalSettings({ ...localSettings, trocr_model_name: e.target.value })
              }
              className="w-full bg-slate-950 text-slate-200 p-3 rounded-xl border border-slate-800 focus:border-blue-500 focus:outline-none font-mono text-xs"
            >
              <option value="microsoft/trocr-small-handwritten">
                microsoft/trocr-small-handwritten (Fast CPU)
              </option>
              <option value="microsoft/trocr-base-handwritten">
                microsoft/trocr-base-handwritten (High Precision)
              </option>
            </select>
          </div>

          {/* Feature Toggles */}
          <div className="space-y-2 pt-2">
            {[
              { key: 'enable_orientation_correction', label: 'Automatic Orientation Rotation (0°/90°/180°/270°)' },
              { key: 'enable_deskew', label: 'Automatic Fine Deskewing' },
              { key: 'enable_perspective_correction', label: 'Perspective Rectification' },
              { key: 'enable_quality_enhancement', label: 'Quality Enhancement (CLAHE / Denoise)' },
              { key: 'developer_mode', label: 'Enable Developer Diagnostics Mode' },
            ].map(({ key, label }) => (
              <label
                key={key}
                className="flex items-center justify-between p-3 rounded-xl bg-slate-950 border border-slate-800 cursor-pointer"
              >
                <span className="text-slate-300 font-medium">{label}</span>
                <input
                  type="checkbox"
                  checked={Boolean((localSettings as any)[key])}
                  onChange={(e) =>
                    setLocalSettings({ ...localSettings, [key]: e.target.checked })
                  }
                  className="w-4 h-4 text-blue-600 rounded bg-slate-800 border-slate-700 focus:ring-blue-500"
                />
              </label>
            ))}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex justify-end space-x-3 pt-4 border-t border-slate-800">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-xl font-semibold text-xs"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="flex items-center space-x-1.5 px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold text-xs shadow-lg shadow-blue-600/20"
          >
            <Save className="w-4 h-4" />
            <span>Save Settings</span>
          </button>
        </div>
      </div>
    </div>
  );
};
