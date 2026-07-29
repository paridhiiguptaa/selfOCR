import React from 'react';
import { ScanText, Settings, Code, CheckCircle, XCircle } from 'lucide-react';

interface NavbarProps {
  backendConnected: boolean;
  developerMode: boolean;
  onToggleDeveloperMode: () => void;
  onOpenSettings: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  backendConnected,
  developerMode,
  onToggleDeveloperMode,
  onOpenSettings,
}) => {
  return (
    <header className="sticky top-0 z-40 bg-slate-900/90 backdrop-blur-md border-b border-slate-800 px-6 py-3.5 shadow-md">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand Logo & Name */}
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-blue-600/20 text-blue-400 rounded-xl border border-blue-500/30">
            <ScanText className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-indigo-300 bg-clip-text text-transparent">
              SelfOCR Pipeline
            </h1>
            <p className="text-xs text-slate-400 font-medium">
              Hybrid Printed & Handwritten Transcription Engine
            </p>
          </div>
        </div>

        {/* Action Controls & Backend Status */}
        <div className="flex items-center space-x-4">
          {/* Connection Status Badge */}
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-800/80 border border-slate-700 text-xs">
            {backendConnected ? (
              <>
                <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-emerald-300 font-medium">API Connected</span>
              </>
            ) : (
              <>
                <XCircle className="w-3.5 h-3.5 text-rose-400" />
                <span className="text-rose-300 font-medium">API Offline</span>
              </>
            )}
          </div>

          {/* Developer Mode Toggle */}
          <button
            onClick={onToggleDeveloperMode}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              developerMode
                ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40 shadow-sm shadow-amber-500/10'
                : 'bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700'
            }`}
            title="Toggle Developer Telemetry & Logging"
          >
            <Code className="w-4 h-4" />
            <span>Dev Mode</span>
          </button>

          {/* Settings Modal Button */}
          <button
            onClick={onOpenSettings}
            className="p-2 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded-lg border border-slate-700 transition-colors"
            title="Pipeline Settings"
          >
            <Settings className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
