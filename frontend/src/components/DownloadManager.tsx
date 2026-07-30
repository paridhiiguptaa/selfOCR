import React from 'react';
import { Download, FileText, Code2, FileJson } from 'lucide-react';
import type { OCRResponse } from '../types/ocr';

interface DownloadManagerProps {
  ocrResult: OCRResponse;
  onExportDocument?: () => void;
}

export const DownloadManager: React.FC<DownloadManagerProps> = ({ ocrResult, onExportDocument }) => {
  const baseName = ocrResult.document_name || 'transcription';

  const downloadFile = (content: string, filename: string, mimeType: string) => {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    if (onExportDocument) {
      onExportDocument();
    }
  };

  const handleDownloadTxt = () => {
    downloadFile(ocrResult.transcription.plain_text, `${baseName}.txt`, 'text/plain;charset=utf-8');
  };

  const handleDownloadMd = () => {
    downloadFile(ocrResult.transcription.markdown, `${baseName}.md`, 'text/markdown;charset=utf-8');
  };

  const handleDownloadJson = () => {
    const jsonStr = JSON.stringify(ocrResult, null, 2);
    downloadFile(jsonStr, `${baseName}.json`, 'application/json;charset=utf-8');
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 mt-6">
      <h4 className="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3 flex items-center space-x-2">
        <Download className="w-4 h-4 text-blue-400" />
        <span>Download Export Formats</span>
      </h4>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <button
          onClick={handleDownloadTxt}
          className="flex items-center justify-center space-x-2 p-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl border border-slate-700 transition-colors text-xs font-semibold"
        >
          <FileText className="w-4 h-4 text-blue-400" />
          <span>Plain Text (.txt)</span>
        </button>

        <button
          onClick={handleDownloadMd}
          className="flex items-center justify-center space-x-2 p-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl border border-slate-700 transition-colors text-xs font-semibold"
        >
          <Code2 className="w-4 h-4 text-indigo-400" />
          <span>Markdown (.md)</span>
        </button>

        <button
          onClick={handleDownloadJson}
          className="flex items-center justify-center space-x-2 p-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-xl border border-slate-700 transition-colors text-xs font-semibold"
        >
          <FileJson className="w-4 h-4 text-emerald-400" />
          <span>Structured JSON (.json)</span>
        </button>
      </div>
    </div>
  );
};

