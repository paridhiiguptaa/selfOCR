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
    <div className="w-full select-none">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          if (!isProcessing) setIsDragOver(true);
        }}
        onDragLeave={() => setIsDragOver(false)}
        onDrop={handleDrop}
        onClick={() => !isProcessing && fileInputRef.current?.click()}
        className={`relative cursor-pointer rounded-3xl border-2 border-dashed p-8 sm:p-12 text-center transition-all duration-200 ${
          isDragOver
            ? 'border-blue-600 bg-blue-50/70 shadow-saas-lg scale-[1.01]'
            : selectedFile
            ? 'border-emerald-500/60 bg-emerald-50/30 shadow-saas'
            : 'border-slate-300 bg-slate-50/50 hover:border-blue-400 hover:bg-blue-50/30 hover:shadow-saas'
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
            className={`p-4 rounded-2xl transition-transform duration-200 ${
              selectedFile
                ? 'bg-emerald-100 text-emerald-700 border border-emerald-200'
                : 'bg-blue-100 text-blue-700 border border-blue-200'
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
              <h3 className="text-base sm:text-lg font-extrabold text-slate-900">{selectedFile.name}</h3>
              <p className="text-xs text-slate-500 font-semibold mt-1">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • Click or drag another file to replace
              </p>
            </div>
          ) : (
            <div>
              <h3 className="text-base sm:text-lg font-extrabold text-slate-900">
                Drag and drop your document here, or <span className="text-blue-600 hover:underline">browse</span>
              </h3>
              <p className="text-xs text-slate-500 font-medium mt-1">
                Supports printed & handwritten documents, scanned pages, assignment notes, and multi-page PDFs
              </p>
            </div>
          )}

          {/* Supported Format Badges */}
          <div className="flex flex-wrap justify-center gap-2 pt-2">
            {['PNG', 'JPG', 'WEBP', 'TIFF', 'BMP', 'PDF'].map((fmt) => (
              <span
                key={fmt}
                className="px-2.5 py-1 text-[10px] font-extrabold rounded-md bg-white text-slate-600 border border-slate-200 shadow-2xs"
              >
                {fmt}
              </span>
            ))}
          </div>
        </div>
      </div>

      {errorMsg && (
        <div className="mt-3 flex items-center space-x-2 text-rose-700 bg-rose-50 border border-rose-200 px-4 py-2.5 rounded-2xl text-xs font-semibold">
          <AlertCircle className="w-4 h-4 flex-shrink-0 text-rose-600" />
          <span>{errorMsg}</span>
        </div>
      )}
    </div>
  );
};
