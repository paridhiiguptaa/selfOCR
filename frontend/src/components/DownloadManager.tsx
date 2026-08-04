import React from 'react';
import { Download, FileText, Code2, FileJson, CheckCircle2 } from 'lucide-react';
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

  const exportCards = [
    {
      id: 'txt',
      title: 'Plain Text (.txt)',
      desc: 'Clean unformatted plain text for quick copying and notes',
      icon: FileText,
      color: 'bg-blue-50 text-blue-600 border-blue-100 hover:border-blue-300',
      action: handleDownloadTxt,
    },
    {
      id: 'md',
      title: 'Markdown (.md)',
      desc: 'Formatted markdown document with headers & bullet lists',
      icon: Code2,
      color: 'bg-purple-50 text-purple-600 border-purple-100 hover:border-purple-300',
      action: handleDownloadMd,
    },
    {
      id: 'json',
      title: 'Structured JSON (.json)',
      desc: 'Full OCR payload with bounding boxes & developer telemetry',
      icon: FileJson,
      color: 'bg-emerald-50 text-emerald-600 border-emerald-100 hover:border-emerald-300',
      action: handleDownloadJson,
    },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h4 className="text-xs font-extrabold text-slate-800 uppercase tracking-wider flex items-center space-x-2">
          <Download className="w-4 h-4 text-blue-600" />
          <span>Available Export Formats</span>
        </h4>
        <span className="text-xs text-slate-500 font-semibold">{baseName}</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {exportCards.map((card) => {
          const Icon = card.icon;
          return (
            <div
              key={card.id}
              onClick={card.action}
              className={`p-5 rounded-2xl border bg-white shadow-xs hover:shadow-saas-md transition-all duration-200 cursor-pointer space-y-3 flex flex-col justify-between group ${card.color}`}
            >
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="p-2.5 rounded-xl bg-white shadow-2xs border border-slate-200">
                    <Icon className="w-5 h-5" />
                  </div>
                  <CheckCircle2 className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
                <h5 className="text-sm font-extrabold text-slate-900 group-hover:text-blue-600 transition-colors">
                  {card.title}
                </h5>
                <p className="text-xs text-slate-500 font-medium">{card.desc}</p>
              </div>

              <button className="w-full py-2 px-3 rounded-xl bg-slate-900 group-hover:bg-blue-600 text-white font-bold text-xs shadow-xs transition-colors flex items-center justify-center space-x-1.5">
                <Download className="w-3.5 h-3.5" />
                <span>Download File</span>
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
};
