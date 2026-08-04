import React, { useState } from 'react';
import { Copy, Check, FileText, Code2 } from 'lucide-react';

interface TextEditorProps {
  plainText: string;
  markdownText: string;
  onTextChange: (newText: string) => void;
}

export const TextEditor: React.FC<TextEditorProps> = ({
  plainText,
  markdownText,
  onTextChange,
}) => {
  const [mode, setMode] = useState<'plain' | 'markdown'>('plain');
  const [copied, setCopied] = useState(false);

  const activeText = mode === 'plain' ? plainText : markdownText;

  const handleCopy = () => {
    navigator.clipboard.writeText(activeText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const wordCount = activeText.trim().split(/\s+/).filter(Boolean).length;
  const lineCount = activeText.split('\n').length;
  const charCount = activeText.length;

  return (
    <div className="bg-white border border-slate-200/80 rounded-3xl p-6 shadow-saas">
      {/* Action Header & Copy Button */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-4 pb-4 border-b border-slate-100">
        <div className="flex items-center space-x-3">
          {/* Mode Switcher Buttons */}
          <div className="flex bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs">
            <button
              onClick={() => setMode('plain')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg font-bold transition-all ${
                mode === 'plain'
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Plain Text</span>
            </button>
            <button
              onClick={() => setMode('markdown')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg font-bold transition-all ${
                mode === 'markdown'
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              <Code2 className="w-3.5 h-3.5" />
              <span>Markdown</span>
            </button>
          </div>

          {/* Telemetry Pills */}
          <div className="hidden sm:flex items-center space-x-3 text-xs font-semibold text-slate-500">
            <span>{wordCount} words</span>
            <span>•</span>
            <span>{lineCount} lines</span>
            <span>•</span>
            <span>{charCount} characters</span>
          </div>
        </div>

        {/* Copy to Clipboard Prominent Button */}
        <button
          onClick={handleCopy}
          className={`flex items-center space-x-2 px-4 py-2 rounded-xl font-extrabold text-xs transition-all shadow-xs cursor-pointer ${
            copied
              ? 'bg-emerald-600 text-white'
              : 'bg-blue-600 hover:bg-blue-700 text-white'
          }`}
        >
          {copied ? (
            <>
              <Check className="w-4 h-4" />
              <span>Copied to Clipboard!</span>
            </>
          ) : (
            <>
              <Copy className="w-4 h-4" />
              <span>Copy Text</span>
            </>
          )}
        </button>
      </div>

      {/* Main Textarea */}
      <textarea
        value={activeText}
        onChange={(e) => onTextChange(e.target.value)}
        rows={16}
        placeholder="Transcription output will appear here..."
        className="w-full bg-slate-50 text-slate-900 p-4 rounded-2xl border border-slate-200 focus:bg-white focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 focus:outline-none font-mono text-sm leading-relaxed resize-y"
      />
    </div>
  );
};
