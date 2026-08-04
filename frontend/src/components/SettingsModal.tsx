import React from 'react';
import { Settings, X, Check, Code } from 'lucide-react';
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

  React.useEffect(() => {
    setLocalSettings(settings);
  }, [settings]);

  if (!isOpen) return null;

  const handleSave = () => {
    onSaveSettings(localSettings);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-xs animate-fadeIn">
      <div className="bg-white rounded-3xl border border-slate-200 shadow-saas-lg max-w-lg w-full overflow-hidden flex flex-col max-h-[90vh]">
        {/* Header */}
        <div className="p-6 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 rounded-xl bg-blue-50 text-blue-600 border border-blue-100">
              <Settings className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-extrabold text-slate-900">Pipeline & Engine Settings</h3>
              <p className="text-xs text-slate-500 font-medium">Configure TrOCR model and image pre-processing</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-slate-600 rounded-lg hover:bg-slate-100"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-5 flex-1">
          {/* Render DPI */}
          <div className="space-y-2">
            <label className="text-xs font-extrabold text-slate-800 flex justify-between">
              <span>PDF Render DPI</span>
              <span className="text-blue-600">{localSettings.pdf_render_dpi} DPI</span>
            </label>
            <input
              type="range"
              min="100"
              max="400"
              step="50"
              value={localSettings.pdf_render_dpi}
              onChange={(e) =>
                setLocalSettings({ ...localSettings, pdf_render_dpi: Number(e.target.value) })
              }
              className="w-full accent-blue-600"
            />
            <p className="text-[11px] text-slate-500">Higher DPI improves small handwriting text accuracy.</p>
          </div>

          {/* Model Selector */}
          <div className="space-y-2">
            <label className="text-xs font-extrabold text-slate-800">
              Hugging Face TrOCR Model
            </label>
            <select
              value={localSettings.trocr_model_name || 'microsoft/trocr-small-handwritten'}
              onChange={(e) =>
                setLocalSettings({ ...localSettings, trocr_model_name: e.target.value })
              }
              className="w-full px-3.5 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-xs font-bold text-slate-800 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:outline-none"
            >
              <option value="microsoft/trocr-small-handwritten">microsoft/trocr-small-handwritten (Default)</option>
              <option value="microsoft/trocr-base-handwritten">microsoft/trocr-base-handwritten (High Precision)</option>
              <option value="microsoft/trocr-large-handwritten">microsoft/trocr-large-handwritten (Maximum Quality)</option>
            </select>
          </div>

          {/* Preprocessing Toggles */}
          <div className="space-y-3 pt-2 border-t border-slate-100">
            <span className="text-xs font-extrabold text-slate-800 block">Pre-processing Pipeline</span>

            <label className="flex items-center justify-between p-3 rounded-xl border border-slate-200 hover:bg-slate-50 cursor-pointer text-xs">
              <span className="font-semibold text-slate-800">Auto Orientation Detection</span>
              <input
                type="checkbox"
                checked={localSettings.enable_orientation_correction}
                onChange={(e) =>
                  setLocalSettings({ ...localSettings, enable_orientation_correction: e.target.checked })
                }
                className="rounded text-blue-600 focus:ring-blue-500"
              />
            </label>

            <label className="flex items-center justify-between p-3 rounded-xl border border-slate-200 hover:bg-slate-50 cursor-pointer text-xs">
              <span className="font-semibold text-slate-800">Deskew & Perspective Correction</span>
              <input
                type="checkbox"
                checked={localSettings.enable_deskew}
                onChange={(e) =>
                  setLocalSettings({ ...localSettings, enable_deskew: e.target.checked })
                }
                className="rounded text-blue-600 focus:ring-blue-500"
              />
            </label>

            <label className="flex items-center justify-between p-3 rounded-xl border border-slate-200 hover:bg-slate-50 cursor-pointer text-xs">
              <span className="font-semibold text-slate-800">CLAHE Contrast & Denoise</span>
              <input
                type="checkbox"
                checked={localSettings.enable_quality_enhancement}
                onChange={(e) =>
                  setLocalSettings({ ...localSettings, enable_quality_enhancement: e.target.checked })
                }
                className="rounded text-blue-600 focus:ring-blue-500"
              />
            </label>

            <label className="flex items-center justify-between p-3 rounded-xl border border-amber-200 bg-amber-50/50 hover:bg-amber-50 cursor-pointer text-xs">
              <span className="font-bold text-amber-900 flex items-center space-x-1.5">
                <Code className="w-4 h-4 text-amber-600" />
                <span>Developer Diagnostic Telemetry</span>
              </span>
              <input
                type="checkbox"
                checked={localSettings.developer_mode}
                onChange={(e) =>
                  setLocalSettings({ ...localSettings, developer_mode: e.target.checked })
                }
                className="rounded text-amber-600 focus:ring-amber-500"
              />
            </label>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-slate-100 bg-slate-50/50 flex justify-end space-x-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-bold text-slate-600 hover:bg-slate-200/60"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="flex items-center space-x-1.5 px-5 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs shadow-xs"
          >
            <Check className="w-4 h-4" />
            <span>Save Preferences</span>
          </button>
        </div>
      </div>
    </div>
  );
};
