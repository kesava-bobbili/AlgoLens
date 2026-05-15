"use client";

import { cn } from "@/lib/utils";
import { CopyButton } from "./CopyButton";

const KEYWORDS = new Set([
  "def",
  "return",
  "if",
  "else",
  "elif",
  "for",
  "while",
  "in",
  "and",
  "or",
  "not",
  "class",
  "import",
  "from",
  "True",
  "False",
  "None",
  "break",
  "continue",
]);

function highlightLine(line: string): React.ReactNode[] {
  const tokens = line.split(/(\s+|[(),[\]:=+\-*/<>])/g).filter(Boolean);
  return tokens.map((token, i) => {
    if (KEYWORDS.has(token)) {
      return (
        <span key={i} className="text-violet-400">
          {token}
        </span>
      );
    }
    if (/^\d+$/.test(token)) {
      return (
        <span key={i} className="text-amber-300">
          {token}
        </span>
      );
    }
    if (
      (token.startsWith('"') && token.endsWith('"')) ||
      (token.startsWith("'") && token.endsWith("'"))
    ) {
      return (
        <span key={i} className="text-emerald-400">
          {token}
        </span>
      );
    }
    if (token.startsWith("#")) {
      return (
        <span key={i} className="text-slate-500">
          {token}
        </span>
      );
    }
    return <span key={i}>{token}</span>;
  });
}

export function CodeBlock({
  code,
  language = "python",
  showCopy = true,
  className,
}: {
  code: string;
  language?: string;
  showCopy?: boolean;
  className?: string;
}) {
  const lines = code.split("\n");

  return (
    <div
      className={cn(
        "group relative overflow-hidden rounded-xl border border-border/80 bg-[#0d0d14] shadow-inner",
        className
      )}
    >
      <div className="flex items-center justify-between border-b border-border/60 bg-surface-elevated/50 px-3 py-2">
        <span className="text-[10px] font-medium uppercase tracking-wider text-muted">
          {language}
        </span>
        {showCopy && <CopyButton text={code} />}
      </div>
      <pre className="max-h-80 overflow-auto p-4 font-mono text-[13px] leading-relaxed">
        {lines.map((line, idx) => (
          <div key={idx} className="table-row">
            <span className="table-cell select-none pr-4 text-right text-xs text-muted/50">
              {idx + 1}
            </span>
            <code className="table-cell text-foreground/90">
              {highlightLine(line)}
            </code>
          </div>
        ))}
      </pre>
    </div>
  );
}
