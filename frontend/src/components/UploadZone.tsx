import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, Image as ImageIcon, AlertCircle } from 'lucide-react';

interface UploadZoneProps {
  onFileSelect: (file: File) => void;
  selectedFile: File | null;
  isProcessing: boolean;
}

export const UploadZone: React.FC<UploadZoneProps> = ({
  onFileSelect,
  selectedFile,
  isProcessing,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const supportedFormats = ['.png', '.jpg', '.jpeg', '.webp', '.tiff', '.bmp', '.pdf'];

  const validateAndSelect = (file: File) => {
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!supportedFormats.includes(ext)) {
      setErrorMsg(`Unsupported file type '${ext}'. Allowed: PNG, JPG, WEBP, TIFF, BMP, PDF.`);
      return;
    }
    setErrorMsg(null);
    onFileSelect(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    if (isProcessing) return;
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSelect(e.dataTransfer.files[0]);
    }
  };

  return (
    <div className="w-full">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          if (!isProcessing) setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        onClick={() => !isProcessing && fileInputRef.current?.click()}
        className={`relative cursor-pointer rounded-2xl border-2 border-dashed p-8 text-center transition-all ${
          isDragOver
            ? 'border-blue-500 bg-blue-500/10 shadow-lg shadow-blue-500/20'
            : selectedFile
            ? 'border-emerald-500/50 bg-emerald-500/5'
            : 'border-slate-700 bg-slate-800/40 hover:border-slate-600 hover:bg-slate-800/60'
        } ${isProcessing ? 'pointer-events-none opacity-60' : ''}`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".png,.jpg,.jpeg,.webp,.tiff,.bmp,.pdf"
          className="hidden"
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) {
              validateAndSelect(e.target.files[0]);
            }
          }}
        />

        <div className="flex flex-col items-center justify-center space-y-4">
          <div
            className={`p-4 rounded-2xl ${
              selectedFile
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                : 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
            }`}
          >
            {selectedFile?.name.toLowerCase().endsWith('.pdf') ? (
              <FileText className="w-10 h-10" />
            ) : selectedFile ? (
              <ImageIcon className="w-10 h-10" />
            ) : (
              <UploadCloud className="w-10 h-10" />
            )}
          </div>

          {selectedFile ? (
            <div>
              <h3 className="text-lg font-semibold text-white">{selectedFile.name}</h3>
              <p className="text-xs text-slate-400 mt-1">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • Click or drag another file to replace
              </p>
            </div>
          ) : (
            <div>
              <h3 className="text-lg font-semibold text-white">
                Drag and drop your document here, or <span className="text-blue-400 hover:underline">browse</span>
              </h3>
              <p className="text-xs text-slate-400 mt-1">
                Supports printed & handwritten documents, scanned pages, assignment notes, and multi-page PDFs
              </p>
            </div>
          )}

          {/* Supported Format Badges */}
          <div className="flex flex-wrap justify-center gap-2 pt-2">
            {['PNG', 'JPG', 'WEBP', 'TIFF', 'BMP', 'PDF'].map((fmt) => (
              <span
                key={fmt}
                className="px-2.5 py-1 text-[10px] font-bold rounded-md bg-slate-700/60 text-slate-300 border border-slate-600/50"
              >
                {fmt}
              </span>
            ))}
          </div>
        </div>
      </div>

      {errorMsg && (
        <div className="mt-3 flex items-center space-x-2 text-rose-400 bg-rose-500/10 border border-rose-500/20 px-4 py-2.5 rounded-xl text-xs">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}
    </div>
  );
};
