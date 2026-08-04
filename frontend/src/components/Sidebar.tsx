import React from 'react';
import {
  LayoutDashboard,
  Upload,
  Cpu,
  FileText,
  Sparkles,
  GraduationCap,
  Clock,
  BarChart3,
  Settings,
  LogOut,
  BookOpen,
  X
} from 'lucide-react';

export type NavModule =
  | 'dashboard'
  | 'upload'
  | 'processing'
  | 'transcription'
  | 'proofreading'
  | 'flashcards'
  | 'history'
  | 'analytics'
  | 'settings';

interface SidebarProps {
  currentModule: NavModule;
  onSelectModule: (module: NavModule) => void;
  backendConnected: boolean;
  developerMode: boolean;
  onToggleDeveloperMode: () => void;
  onLogout: () => void;
  isMobileOpen: boolean;
  onToggleMobile: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentModule,
  onSelectModule,
  backendConnected,
  developerMode,
  onToggleDeveloperMode,
  onLogout,
  isMobileOpen,
  onToggleMobile,
}) => {
  const navItems: { id: NavModule; label: string; icon: React.ElementType; badge?: string }[] = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'upload', label: 'Upload Document', icon: Upload },
    { id: 'processing', label: 'OCR Processing', icon: Cpu },
    { id: 'transcription', label: 'OCR Transcription', icon: FileText },
    { id: 'proofreading', label: 'AI Proofreading', icon: Sparkles, badge: 'AI' },
    { id: 'flashcards', label: 'Flashcards Hub', icon: GraduationCap },
    { id: 'history', label: 'Document History', icon: Clock },
    { id: 'analytics', label: 'Analytics', icon: BarChart3 },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  const sidebarContent = (
    <div className="flex flex-col h-full bg-white border-r border-slate-200 w-64 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-100 flex items-center justify-between">
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => onSelectModule('dashboard')}>
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <BookOpen className="w-5.5 h-5.5" />
          </div>
          <div>
            <div className="flex items-center space-x-1.5">
              <h1 className="text-base font-extrabold text-slate-900 tracking-tight">EduAI Studio</h1>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-blue-50 text-blue-600 border border-blue-100">
                v2.5
              </span>
            </div>
            <p className="text-xs text-slate-500 font-medium">Educational AI Platform</p>
          </div>
        </div>

        <button
          onClick={onToggleMobile}
          className="lg:hidden p-1.5 text-slate-400 hover:text-slate-600 rounded-lg"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Backend Status Banner */}
      <div className="px-5 py-3 bg-slate-50/70 border-b border-slate-100 flex items-center justify-between text-xs">
        <div className="flex items-center space-x-2">
          {backendConnected ? (
            <>
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              <span className="font-semibold text-slate-700">API Active</span>
            </>
          ) : (
            <>
              <span className="relative flex h-2 w-2">
                <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-500"></span>
              </span>
              <span className="font-semibold text-rose-600">API Offline</span>
            </>
          )}
        </div>

        <button
          onClick={onToggleDeveloperMode}
          className={`text-[11px] font-bold px-2 py-0.5 rounded transition-all ${
            developerMode
              ? 'bg-amber-100 text-amber-800 border border-amber-300'
              : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-100'
          }`}
          title="Toggle Developer Telemetry"
        >
          {developerMode ? 'Dev: ON' : 'Dev Mode'}
        </button>
      </div>

      {/* Primary Navigation Menu */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-1">
        <div className="px-3 mb-2 text-[11px] font-extrabold uppercase tracking-wider text-slate-400">
          Navigation
        </div>

        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentModule === item.id;
          return (
            <button
              key={item.id}
              onClick={() => {
                onSelectModule(item.id);
                if (isMobileOpen) onToggleMobile();
              }}
              className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl font-semibold text-sm transition-all duration-150 group cursor-pointer ${
                isActive
                  ? 'bg-blue-50 text-blue-700 shadow-xs border-r-4 border-blue-600 font-bold'
                  : 'text-slate-600 hover:bg-slate-100/80 hover:text-slate-900'
              }`}
            >
              <div className="flex items-center space-x-3">
                <Icon
                  className={`w-4.5 h-4.5 transition-colors ${
                    isActive ? 'text-blue-600' : 'text-slate-400 group-hover:text-slate-600'
                  }`}
                />
                <span>{item.label}</span>
              </div>

              {item.badge && (
                <span className="text-[10px] font-extrabold px-1.5 py-0.5 rounded bg-blue-100 text-blue-700">
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* User Profile & Logout Footer */}
      <div className="p-4 border-t border-slate-100 bg-slate-50/50">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-blue-500 to-indigo-600 text-white font-bold flex items-center justify-center text-xs shadow-xs">
              AR
            </div>
            <div className="text-left">
              <p className="text-xs font-bold text-slate-800 leading-tight">Alex Rivers</p>
              <p className="text-[11px] text-slate-500 font-medium">Educator Pro</p>
            </div>
          </div>

          <button
            onClick={onLogout}
            className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors cursor-pointer"
            title="Sign Out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Desktop Persistent Sidebar */}
      <aside className="hidden lg:block h-screen sticky top-0 z-30 flex-shrink-0">
        {sidebarContent}
      </aside>

      {/* Mobile Drawer Backdrop */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs z-40 lg:hidden"
          onClick={onToggleMobile}
        />
      )}

      {/* Mobile Sidebar Drawer */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 transform transition-transform duration-200 ease-in-out lg:hidden ${
          isMobileOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {sidebarContent}
      </aside>
    </>
  );
};
