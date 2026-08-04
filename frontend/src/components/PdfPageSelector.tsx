import React from 'react';
import { FileText, CheckCircle2 } from 'lucide-react';

interface PdfPageSelectorProps {
  totalPages: number;
  currentPage: number;
  thumbnails: Array<{ page: number; image: string }>;
  onPageChange: (page: number) => void;
}

export const PdfPageSelector: React.FC<PdfPageSelectorProps> = ({
  totalPages,
  currentPage,
  thumbnails,
  onPageChange,
}) => {
  if (totalPages <= 1) return null;

  return (
    <div className="w-full space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-extrabold text-slate-800 uppercase tracking-wider flex items-center space-x-2">
          <FileText className="w-4 h-4 text-blue-600" />
          <span>Multi-Page PDF Selection ({totalPages} Pages)</span>
        </h4>
        <span className="text-xs font-semibold text-blue-600 bg-blue-50 px-2.5 py-0.5 rounded-full border border-blue-100">
          Page {currentPage} selected
        </span>
      </div>

      <div className="flex space-x-3 overflow-x-auto pb-2 pt-1 scrollbar-thin">
        {thumbnails.map((t) => {
          const isSelected = currentPage === t.page;
          return (
            <button
              key={t.page}
              onClick={() => onPageChange(t.page)}
              className={`relative flex-shrink-0 w-24 sm:w-28 rounded-2xl border-2 overflow-hidden transition-all duration-150 text-left bg-white shadow-xs cursor-pointer ${
                isSelected
                  ? 'border-blue-600 ring-2 ring-blue-500/30 scale-105 shadow-saas-md'
                  : 'border-slate-200 hover:border-slate-300 opacity-80 hover:opacity-100'
              }`}
            >
              <div className="h-28 bg-slate-100 flex items-center justify-center p-1.5 overflow-hidden">
                <img
                  src={t.image}
                  alt={`Page ${t.page}`}
                  className="max-h-full max-w-full object-contain rounded border border-slate-200"
                />
              </div>

              <div className="p-2 bg-white flex items-center justify-between border-t border-slate-100 text-[11px] font-bold text-slate-700">
                <span>Page {t.page}</span>
                {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 flex-shrink-0" />}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
};
