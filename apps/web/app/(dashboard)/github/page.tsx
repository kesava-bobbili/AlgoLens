"use client";

import { GitHubAnalyzeResults } from "@/components/github/GitHubAnalyzeResults";
import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import { api, type GitHubAnalyzeResult } from "@/lib/api";
import { BRAND } from "@/lib/brand";
import { AnimatePresence, motion } from "framer-motion";
import { Github, Loader2 } from "lucide-react";
import { useState } from "react";

function GitHubResultsSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-36 w-full" />
      <Skeleton className="h-24 w-full" />
      <Skeleton className="h-48 w-full" />
      <div className="grid gap-4 md:grid-cols-2">
        <Skeleton className="h-40" />
        <Skeleton className="h-40" />
      </div>
      <Skeleton className="h-32 w-full" />
    </div>
  );
}

export default function GitHubPage() {
  const [url, setUrl] = useState("https://github.com/kesava-bobbili/AlgoLens");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<GitHubAnalyzeResult | null>(null);

  async function handleAnalyze() {
    if (!url.trim()) {
      setError("Enter a GitHub repository URL.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await api.githubAnalyze(url.trim());
      setResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Analysis failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="Repository Intelligence"
        subtitle={BRAND.fullTitle}
        description="Analyze any public repository — architecture summary, code quality insights, and README suggestions."
      />

      <Card className="mb-6 border-border/60 bg-surface/40 backdrop-blur-xl">
        <div className="flex flex-col gap-3 sm:flex-row">
          <input
            type="text"
            inputMode="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://github.com/owner/repo"
            className="flex-1 rounded-xl border border-border/60 bg-background px-4 py-2.5 text-sm outline-none transition-colors focus:border-accent focus:ring-2 focus:ring-accent/20"
          />
          <Button
            className="sm:w-auto"
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Github className="mr-2 h-4 w-4" />
            )}
            Analyze repository
          </Button>
        </div>
        <p className="mt-2 text-xs text-muted">
          Supports trailing slashes, optional .git, and bare{" "}
          <code className="rounded bg-background px-1">github.com/org/repo</code>{" "}
          URLs. Anonymous GitHub API quotas are limited — set{" "}
          <code className="rounded bg-background px-1">GITHUB_TOKEN</code> on the
          backend for reliability.
        </p>
        {error && (
          <p className="mt-3 rounded-lg border border-red-500/20 bg-red-500/10 px-3 py-2 text-sm text-red-400">
            {error}
          </p>
        )}
      </Card>

      <AnimatePresence mode="wait">
        {loading && (
          <motion.div
            key="sk"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <GitHubResultsSkeleton />
          </motion.div>
        )}
        {result && !loading && (
          <motion.div
            key="res"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
          >
            <GitHubAnalyzeResults result={result} />
          </motion.div>
        )}
        {!loading && !result && (
          <motion.div
            key="empty"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="rounded-2xl border border-dashed border-border/60 bg-surface/20 p-8 text-center"
          >
            <Github className="mx-auto h-10 w-10 text-muted/50" />
            <h3 className="mt-4 font-semibold text-foreground">Ready to analyze</h3>
            <p className="mx-auto mt-2 max-w-md text-sm text-muted">
              Paste any public GitHub URL above to get an AI architecture review,
              language breakdown, file tree, and README improvement suggestions.
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
