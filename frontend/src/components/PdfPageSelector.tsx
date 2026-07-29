import React from 'react';
import { ChevronLeft, ChevronRight, FileText } from 'lucide-react';

interface PdfThumbnail {
  page_number: number;
  image_base64: string;
  width: number;
  height: number;
}

interface PdfPageSelectorProps {
  totalPages: number;
  currentPage: number;
  thumbnails: PdfThumbnail[];
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
    <div className="bg-slate-800/80 border border-slate-700/80 rounded-2xl p-4 mb-6 shadow-md">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2 text-xs font-semibold text-slate-300">
          <FileText className="w-4 h-4 text-blue-400" />
          <span>Multi-Page PDF Document ({totalPages} Pages)</span>
        </div>

        {/* Navigation Buttons */}
        <div className="flex items-center space-x-2">
          <button
            disabled={currentPage <= 1}
            onClick={() => onPageChange(currentPage - 1)}
            className="p-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 disabled:opacity-40 text-white transition-colors"
            title="Previous Page"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="text-xs font-mono text-slate-300 px-2">
            Page {currentPage} / {totalPages}
          </span>
          <button
            disabled={currentPage >= totalPages}
            onClick={() => onPageChange(currentPage + 1)}
            className="p-1.5 rounded-lg bg-slate-700 hover:bg-slate-600 disabled:opacity-40 text-white transition-colors"
            title="Next Page"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Page Thumbnails Carousel */}
      <div className="flex space-x-3 overflow-x-auto pb-2 pt-1">
        {thumbnails.map((thumb) => {
          const isSelected = thumb.page_number === currentPage;
          return (
            <button
              key={thumb.page_number}
              onClick={() => onPageChange(thumb.page_number)}
              className={`flex-shrink-0 flex flex-col items-center space-y-1.5 p-2 rounded-xl transition-all border ${
                isSelected
                  ? 'bg-blue-600/20 border-blue-500 shadow-md shadow-blue-500/20 scale-105'
                  : 'bg-slate-900/60 border-slate-700/60 hover:border-slate-500'
              }`}
            >
              <div className="w-16 h-20 bg-slate-950 rounded-lg overflow-hidden flex items-center justify-center">
                {thumb.image_base64 ? (
                  <img
                    src={thumb.image_base64}
                    alt={`Page ${thumb.page_number}`}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <span className="text-xs text-slate-500">P.{thumb.page_number}</span>
                )}
              </div>
              <span className={`text-[11px] font-medium ${isSelected ? 'text-blue-400 font-bold' : 'text-slate-400'}`}>
                Page {thumb.page_number}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
