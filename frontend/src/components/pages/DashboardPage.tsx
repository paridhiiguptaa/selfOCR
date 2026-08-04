import React from 'react';
import {
  FileText,
  GraduationCap,
  Sparkles,
  Award,
  Upload,
  ArrowRight,
  Clock,
  BookOpen,
  ChevronRight
} from 'lucide-react';
import type { NavModule } from '../Sidebar';

interface DashboardPageProps {
  onNavigate: (module: NavModule) => void;
  hasActiveDocument: boolean;
  activeDocName?: string;
  activeDocPageCount?: number;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  onNavigate,
  hasActiveDocument,
  activeDocName,
  activeDocPageCount,
}) => {
  const metrics = [
    {
      title: 'Documents Processed',
      value: '18',
      change: '+4 this week',
      trend: 'up',
      icon: FileText,
      color: 'bg-blue-50 text-blue-600 border-blue-100',
    },
    {
      title: 'Flashcards Generated',
      value: '124',
      change: '+32 new words',
      trend: 'up',
      icon: GraduationCap,
      color: 'bg-purple-50 text-purple-600 border-purple-100',
    },
    {
      title: 'Vocabulary Words',
      value: '210',
      change: '88% mastered',
      trend: 'up',
      icon: BookOpen,
      color: 'bg-emerald-50 text-emerald-600 border-emerald-100',
    },
    {
      title: 'OCR Accuracy Avg',
      value: '98.4%',
      change: 'Dual TrOCR Engine',
      trend: 'neutral',
      icon: Award,
      color: 'bg-amber-50 text-amber-600 border-amber-100',
    },
  ];

  const recentDocuments = [
    {
      id: 'doc-1',
      title: activeDocName || 'Sample Science Class Notes - Photosynthesis.pdf',
      type: 'PDF Document',
      pages: activeDocPageCount || 3,
      date: 'Today, 10:14 AM',
      status: 'AI Proofread & Flashcards Ready',
      statusColor: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    },
    {
      id: 'doc-2',
      title: 'History Homework - Early Civilizations.png',
      type: 'Handwritten Image',
      pages: 1,
      date: 'Yesterday, 4:30 PM',
      status: 'Flashcards Mastered',
      statusColor: 'bg-blue-50 text-blue-700 border-blue-200',
    },
    {
      id: 'doc-3',
      title: 'English Essay Draft - Rotated Notes.jpg',
      type: 'Rotated Note',
      pages: 2,
      date: 'Aug 2, 2026',
      status: 'Proofread Complete',
      statusColor: 'bg-purple-50 text-purple-700 border-purple-200',
    },
    {
      id: 'doc-4',
      title: 'Math Workbook Exercises Page 12.png',
      type: 'Handwritten Worksheet',
      pages: 1,
      date: 'Jul 30, 2026',
      status: 'Exported as PDF',
      statusColor: 'bg-slate-100 text-slate-700 border-slate-200',
    },
  ];

  return (
    <div className="space-y-8 animate-fadeIn">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-blue-600 via-blue-700 to-indigo-700 rounded-3xl p-6 sm:p-8 text-white shadow-saas-lg flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative overflow-hidden">
        <div className="space-y-2 relative z-10 max-w-xl">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-white/10 text-blue-100 text-xs font-semibold backdrop-blur-xs">
            <Sparkles className="w-3.5 h-3.5 text-amber-300" />
            <span>Welcome back, Educator Alex!</span>
          </div>
          <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
            Ready to convert student notes into smart learning decks?
          </h2>
          <p className="text-xs sm:text-sm text-blue-100 font-normal leading-relaxed">
            Upload new handwritten or printed class notes, proofread transcription errors with AI, and review student flashcards.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3 relative z-10">
          <button
            onClick={() => onNavigate('upload')}
            className="flex items-center space-x-2.5 px-5 py-3 rounded-2xl bg-white hover:bg-blue-50 text-blue-700 font-bold text-sm shadow-md transition-all duration-150 transform hover:-translate-y-0.5"
          >
            <Upload className="w-4 h-4" />
            <span>Upload New Document</span>
          </button>
          {hasActiveDocument && (
            <button
              onClick={() => onNavigate('transcription')}
              className="flex items-center space-x-2 px-4 py-3 rounded-2xl bg-white/15 hover:bg-white/20 text-white font-semibold text-sm backdrop-blur-xs transition-all"
            >
              <span>Resume Active Doc</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Summary Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {metrics.map((m, idx) => {
          const Icon = m.icon;
          return (
            <div
              key={idx}
              className="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-saas hover:shadow-saas-md transition-all duration-200 flex flex-col justify-between"
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-xl border ${m.color}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
                  {m.change}
                </span>
              </div>
              <div>
                <p className="text-2xl font-black text-slate-900 tracking-tight">{m.value}</p>
                <p className="text-xs font-semibold text-slate-500 mt-0.5">{m.title}</p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Main Grid: Recent Activity & Learning Insights */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Recent Activity Table */}
        <div className="lg:col-span-8 bg-white p-6 rounded-3xl border border-slate-200/80 shadow-saas space-y-5">
          <div className="flex items-center justify-between border-b border-slate-100 pb-4">
            <div className="flex items-center space-x-2.5">
              <div className="p-2 rounded-xl bg-blue-50 text-blue-600">
                <Clock className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-base font-extrabold text-slate-900">Recent Document Activity</h3>
                <p className="text-xs text-slate-500 font-medium">Your processed class notes & study decks</p>
              </div>
            </div>
            <button
              onClick={() => onNavigate('history')}
              className="text-xs font-bold text-blue-600 hover:text-blue-700 flex items-center space-x-1"
            >
              <span>View All History</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>

          <div className="divide-y divide-slate-100">
            {recentDocuments.map((doc) => (
              <div
                key={doc.id}
                className="py-3.5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-slate-50/80 p-3 rounded-2xl transition-colors cursor-pointer"
                onClick={() => onNavigate(hasActiveDocument ? 'transcription' : 'upload')}
              >
                <div className="flex items-center space-x-3.5">
                  <div className="p-3 rounded-xl bg-slate-100 text-slate-600 font-bold text-xs flex-shrink-0">
                    <FileText className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <h4 className="text-xs font-bold text-slate-900 line-clamp-1">{doc.title}</h4>
                    <p className="text-[11px] text-slate-400 font-medium mt-0.5">
                      {doc.type} • {doc.pages} page{doc.pages > 1 ? 's' : ''} • {doc.date}
                    </p>
                  </div>
                </div>

                <div className="flex items-center space-x-3 self-end sm:self-center">
                  <span className={`text-[11px] font-bold px-2.5 py-1 rounded-full border ${doc.statusColor}`}>
                    {doc.status}
                  </span>
                  <ChevronRight className="w-4 h-4 text-slate-400" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Column: Student Learning Metrics & Quick Actions */}
        <div className="lg:col-span-4 space-y-6">
          {/* Quick Workflow Stepper */}
          <div className="bg-white p-6 rounded-3xl border border-slate-200/80 shadow-saas space-y-4">
            <h3 className="text-sm font-extrabold text-slate-900 flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-blue-600" />
              <span>Educational Workflow</span>
            </h3>

            <div className="space-y-3">
              {[
                { step: '1', title: 'Upload Notes', desc: 'PDF or rotated handwritten image', module: 'upload' },
                { step: '2', title: 'OCR & Transcribe', desc: 'Dual printed & TrOCR model', module: 'transcription' },
                { step: '3', title: 'AI Proofread', desc: 'Fix spelling & grammar suggestions', module: 'proofreading' },
                { step: '4', title: 'Study Flashcards', desc: 'Generate child vocabulary decks', module: 'flashcards' },
                { step: '5', title: 'Export & Share', desc: 'Download PDF, Word or Anki CSV', module: 'export' },
              ].map((item, idx) => (
                <div
                  key={idx}
                  onClick={() => onNavigate(item.module as NavModule)}
                  className="flex items-center space-x-3 p-2.5 rounded-xl hover:bg-blue-50/60 transition-colors cursor-pointer group"
                >
                  <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-700 font-extrabold text-xs flex items-center justify-center flex-shrink-0 group-hover:bg-blue-600 group-hover:text-white transition-colors">
                    {item.step}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-bold text-slate-800 group-hover:text-blue-700 leading-tight">
                      {item.title}
                    </p>
                    <p className="text-[11px] text-slate-400 truncate">{item.desc}</p>
                  </div>
                  <ChevronRight className="w-4 h-4 text-slate-300 group-hover:text-blue-600" />
                </div>
              ))}
            </div>
          </div>

          {/* Handwriting Score Widget */}
          <div className="bg-gradient-to-br from-indigo-50 to-blue-50 p-6 rounded-3xl border border-indigo-100 shadow-saas space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-extrabold text-indigo-900 uppercase tracking-wider">
                Student Handwriting Metric
              </span>
              <span className="text-xs font-extrabold text-emerald-600 bg-emerald-100 px-2 py-0.5 rounded-md">
                +14% Legibility
              </span>
            </div>
            <h4 className="text-lg font-black text-slate-900">TrOCR Confidence Score</h4>
            <div className="w-full bg-slate-200 h-2.5 rounded-full overflow-hidden">
              <div className="bg-gradient-to-r from-blue-600 to-indigo-600 h-full w-[94%]" />
            </div>
            <p className="text-[11px] text-slate-600 font-medium">
              Handwriting clarity score based on Microsoft TrOCR recognition metrics across 18 notes.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
