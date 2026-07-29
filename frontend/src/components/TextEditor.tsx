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
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-2xl">
      {/* Action Header & Copy Button */}
      <div className="flex flex-wrap items-center justify-between gap-4 mb-4 pb-4 border-b border-slate-800">
        <div className="flex items-center space-x-3">
          {/* Mode Switcher Buttons */}
          <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800 text-xs">
            <button
              onClick={() => setMode('plain')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg font-semibold transition-all ${
                mode === 'plain'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Plain Text</span>
            </button>
            <button
              onClick={() => setMode('markdown')}
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg font-semibold transition-all ${
                mode === 'markdown'
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Code2 className="w-3.5 h-3.5" />
              <span>Markdown</span>
            </button>
          </div>

          {/* Telemetry Pills */}
          <div className="hidden sm:flex items-center space-x-3 text-xs text-slate-400">
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
          className={`flex items-center space-x-2 px-5 py-2.5 rounded-xl font-bold text-xs transition-all shadow-lg ${
            copied
              ? 'bg-emerald-600 text-white border border-emerald-400 shadow-emerald-500/20'
              : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white border border-blue-400/30 shadow-blue-500/20'
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
              <span>Copy to Clipboard</span>
            </>
          )}
        </button>
      </div>

      {/* Main Textarea */}
      <textarea
        value={activeText}
        onChange={(e) => onTextChange(e.target.value)}
        rows={18}
        placeholder="Transcription output will appear here..."
        className="w-full bg-slate-950 text-slate-100 p-4 rounded-xl border border-slate-800 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none font-mono text-sm leading-relaxed resize-y"
      />
    </div>
  );
};
