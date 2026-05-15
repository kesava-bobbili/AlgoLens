"use client";

import { AnalyzeResults } from "@/components/analyze/AnalyzeResults";
import { ExampleChips } from "@/components/analyze/ExampleChips";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { AnalyzeSkeleton } from "@/components/ui/Skeleton";
import { api, type AnalysisResult } from "@/lib/api";
import { BRAND } from "@/lib/brand";
import { AnimatePresence } from "framer-motion";
import { Loader2, Sparkles } from "lucide-react";
import { useState } from "react";

export default function AnalyzePage() {
  const [problem, setProblem] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);

  async function handleAnalyze() {
    const text = problem.trim();
    if (!text) {
      setError("Please paste a problem statement.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await api.analyze(text);
      setResult(data);
    } catch (e) {
      setError(
        e instanceof Error
          ? e.message
          : "Failed to connect to API. Is the backend running?"
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="Code Intelligence"
        subtitle={BRAND.fullTitle}
        description={BRAND.description}
      />

      <Card className="mb-6 border-border/60 bg-surface/40 backdrop-blur-xl">
        <textarea
          value={problem}
          onChange={(e) => setProblem(e.target.value)}
          placeholder="Paste a coding problem, interview question, or algorithm challenge..."
          className="h-44 w-full resize-y rounded-xl border border-border/60 bg-background/80 p-4 text-sm text-foreground outline-none transition-colors focus:border-accent focus:ring-2 focus:ring-accent/20"
        />
        <ExampleChips
          onSelect={setProblem}
          disabled={loading}
        />
        <div className="mt-4 flex flex-wrap gap-3">
          <Button onClick={handleAnalyze} disabled={loading} size="lg">
            {loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Analyzing with AI...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-4 w-4" />
                Run Analysis
              </>
            )}
          </Button>
        </div>
        {error && (
          <p className="mt-3 rounded-lg border border-red-500/20 bg-red-500/10 px-3 py-2 text-sm text-red-400">
            {error}
          </p>
        )}
      </Card>

      <AnimatePresence mode="wait">
        {loading && <AnalyzeSkeleton key="skeleton" />}
        {result && !loading && (
          <AnalyzeResults key="results" result={result} />
        )}
      </AnimatePresence>
    </div>
  );
}
