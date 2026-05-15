"use client";

import { PageHeader } from "@/components/layout/PageHeader";
import { ExecutionControls } from "@/components/visualizer/ExecutionControls";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { api, type TraceStep, type VisualizeResult } from "@/lib/api";
import { BRAND } from "@/lib/brand";
import { cn } from "@/lib/utils";
import Editor, { type OnMount } from "@monaco-editor/react";
import type { editor } from "monaco-editor";
import { AnimatePresence, motion } from "framer-motion";
import { Loader2, Play } from "lucide-react";
import { useCallback, useEffect, useRef, useState } from "react";
import {
  Bar,
  BarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
} from "recharts";

const DEFAULT_CODE = `def fib(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

result = fib(8)
print(result)
`;

export default function VisualizePage() {
  const [code, setCode] = useState(DEFAULT_CODE);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [trace, setTrace] = useState<VisualizeResult | null>(null);
  const [stepIndex, setStepIndex] = useState(0);
  const [playing, setPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const decorationRef = useRef<string[]>([]);

  const steps = trace?.steps ?? [];
  const current: TraceStep | undefined = steps[stepIndex];

  const stackChartData =
    current?.call_stack.map((frame, i) => ({
      name: (frame.split(":")[0] ?? frame).slice(0, 12),
      depth: i + 1,
    })) ?? [];

  const goToStep = useCallback(
    (next: number) => {
      if (!steps.length) return;
      setStepIndex(Math.max(0, Math.min(steps.length - 1, next)));
    },
    [steps.length]
  );

  const highlightEditorLine = useCallback((line: number | undefined) => {
    const ed = editorRef.current;
    if (!ed || !line) return;
    const monaco = (
      window as unknown as {
        monaco?: typeof import("monaco-editor");
      }
    ).monaco;
    if (!monaco) return;
    decorationRef.current = ed.deltaDecorations(decorationRef.current, [
      {
        range: new monaco.Range(line, 1, line, 1),
        options: {
          isWholeLine: true,
          className: "monaco-active-line",
        },
      },
    ]);
    ed.revealLineInCenter(line);
  }, []);

  useEffect(() => {
    highlightEditorLine(current?.line_number);
  }, [current?.line_number, highlightEditorLine]);

  useEffect(() => {
    if (!playing || !steps.length) return;
    const ms = 800 / speed;
    const id = setInterval(() => {
      setStepIndex((i) => {
        if (i >= steps.length - 1) {
          setPlaying(false);
          return i;
        }
        return i + 1;
      });
    }, ms);
    return () => clearInterval(id);
  }, [playing, speed, steps.length]);

  const handleEditorMount: OnMount = (editor) => {
    editorRef.current = editor;
  };

  const runTrace = useCallback(async () => {
    setLoading(true);
    setError(null);
    setTrace(null);
    setStepIndex(0);
    setPlaying(false);
    try {
      const data = await api.visualize(code);
      setTrace(data);
      if (data.error && data.steps.length === 0) setError(data.error);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Visualization failed");
    } finally {
      setLoading(false);
    }
  }, [code]);

  return (
    <div>
      <PageHeader
        title="Execution Visualizer"
        subtitle={BRAND.fullTitle}
        description="Interactive line-by-line Python tracing with variables, call stack, and playback controls."
      />

      <div className="grid gap-6 xl:grid-cols-2">
        <Card className="overflow-hidden border-border/60 bg-surface/40 p-0 backdrop-blur-xl">
          <div className="flex items-center justify-between border-b border-border/60 px-4 py-2">
            <span className="text-xs font-medium text-muted">Python · Monaco</span>
            <Button size="sm" onClick={runTrace} disabled={loading}>
              {loading ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Play className="mr-2 h-4 w-4" />
              )}
              Run & Trace
            </Button>
          </div>
          <Editor
            height="420px"
            defaultLanguage="python"
            theme="vs-dark"
            value={code}
            onChange={(v) => setCode(v ?? "")}
            onMount={handleEditorMount}
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              fontFamily: "var(--font-geist-mono), monospace",
              scrollBeyondLastLine: false,
              padding: { top: 16 },
              lineNumbers: "on",
              renderLineHighlight: "none",
            }}
          />
        </Card>

        <Card className="border-border/60 bg-surface/40 backdrop-blur-xl">
          <h3 className="mb-3 text-sm font-semibold text-muted">
            Execution timeline
          </h3>
          {steps.length > 0 ? (
            <div className="mb-4 flex gap-1 overflow-x-auto pb-2">
              {steps.map((s, i) => (
                <button
                  key={s.step}
                  type="button"
                  onClick={() => goToStep(i)}
                  title={`Line ${s.line_number}: ${s.event}`}
                  className={cn(
                    "h-2.5 w-2.5 shrink-0 rounded-full bg-border transition-all",
                    i === stepIndex && "timeline-dot-active bg-accent"
                  )}
                />
              ))}
            </div>
          ) : (
            <p className="mb-4 text-xs text-muted">Run trace to see timeline</p>
          )}

          <div className="max-h-[320px] overflow-auto rounded-xl border border-border/50 bg-background/80 p-3 font-mono text-xs">
            {(trace?.source_lines ?? code.split("\n")).map((line, i) => {
              const lineNo = i + 1;
              const active = current?.line_number === lineNo;
              return (
                <div
                  key={lineNo}
                  className={cn(
                    "flex gap-3 rounded-md px-2 py-0.5 transition-colors",
                    active &&
                      "bg-accent/25 shadow-[0_0_20px_rgba(99,102,241,0.25)] ring-1 ring-accent/50"
                  )}
                >
                  <span className="w-6 shrink-0 text-right text-muted">
                    {lineNo}
                  </span>
                  <span className={cn(active && "font-medium text-accent")}>
                    {line || " "}
                  </span>
                </div>
              );
            })}
          </div>
        </Card>
      </div>

      {error && (
        <p className="mt-4 rounded-lg border border-red-500/20 bg-red-500/10 px-4 py-2 text-sm text-red-400">
          {error}
        </p>
      )}

      <AnimatePresence>
        {trace && steps.length > 0 && current && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-6 space-y-4"
          >
            <Card className="glass-panel">
              <ExecutionControls
                stepIndex={stepIndex}
                totalSteps={steps.length}
                playing={playing}
                speed={speed}
                onPlayPause={() => setPlaying((p) => !p)}
                onStep={goToStep}
                onSpeedChange={setSpeed}
                onSlider={goToStep}
              />
              <p className="mt-3 text-xs text-muted">
                Event: <span className="text-foreground">{current.event}</span>
                {" · "}
                Recursion depth: {trace.recursion_depth}
              </p>
            </Card>

            <div className="grid gap-4 lg:grid-cols-2">
              <Card className="glass-panel">
                <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted">
                  Variables
                </h4>
                <AnimatePresence mode="popLayout">
                  <motion.div
                    key={stepIndex}
                    initial={{ opacity: 0, x: -8 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="space-y-2 rounded-xl bg-background/60 p-4 font-mono text-xs"
                  >
                    {Object.entries(current.variables).length === 0 ? (
                      <span className="text-muted">No locals</span>
                    ) : (
                      Object.entries(current.variables).map(([k, v]) => (
                        <div
                          key={k}
                          className="flex gap-2 border-b border-border/30 pb-2 last:border-0"
                        >
                          <span className="text-accent">{k}</span>
                          <span className="text-muted">=</span>
                          <span className="text-foreground">{v}</span>
                        </div>
                      ))
                    )}
                  </motion.div>
                </AnimatePresence>
              </Card>

              <Card className="glass-panel">
                <h4 className="mb-3 text-xs font-semibold uppercase tracking-wider text-muted">
                  Call stack
                </h4>
                <div className="space-y-1 rounded-xl bg-background/60 p-4 font-mono text-xs">
                  {current.call_stack.map((frame, i) => (
                    <motion.div
                      key={`${frame}-${i}`}
                      initial={{ opacity: 0, x: -12 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.05 }}
                      className="border-l-2 border-accent/50 py-1 pl-3"
                      style={{ marginLeft: i * 10 }}
                    >
                      {frame}
                    </motion.div>
                  ))}
                </div>
                {stackChartData.length > 0 && (
                  <div className="mt-4 h-28">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={stackChartData}>
                        <XAxis dataKey="name" tick={{ fontSize: 9 }} />
                        <Tooltip />
                        <Bar
                          dataKey="depth"
                          fill="url(#stackGrad)"
                          radius={[4, 4, 0, 0]}
                        />
                        <defs>
                          <linearGradient id="stackGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#6366f1" />
                            <stop offset="100%" stopColor="#8b5cf6" />
                          </linearGradient>
                        </defs>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                )}
              </Card>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
