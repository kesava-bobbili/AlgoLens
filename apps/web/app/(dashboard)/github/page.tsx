"use client";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { PageHeader } from "@/components/layout/PageHeader";
import { api, type GitHubAnalyzeResult } from "@/lib/api";
import { BRAND } from "@/lib/brand";
import { parseSections } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";
import { Github, Loader2, Star } from "lucide-react";
import { useState } from "react";

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

  const sections = result ? parseSections(result.ai_analysis) : {};

  return (
    <div>
      <PageHeader
        title="Repository Intelligence"
        subtitle={BRAND.fullTitle}
        description="Analyze any public repository — architecture summary, code quality insights, and README suggestions."
      />

      <Card className="mb-6">
        <div className="flex gap-3">
          <input
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://github.com/owner/repo"
            className="flex-1 rounded-lg border border-border bg-background px-4 py-2 text-sm outline-none focus:border-accent"
          />
          <Button onClick={handleAnalyze} disabled={loading}>
            {loading ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Github className="mr-2 h-4 w-4" />
            )}
            Analyze
          </Button>
        </div>
        {error && (
          <p className="mt-3 text-sm text-red-400">{error}</p>
        )}
      </Card>

      <AnimatePresence>
        {result && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-6"
          >
            <Card>
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <h2 className="text-xl font-bold">{result.meta.full_name}</h2>
                  <p className="mt-1 text-sm text-muted">
                    {result.meta.description ?? "No description"}
                  </p>
                </div>
                <div className="flex flex-wrap gap-2">
                  {result.meta.language && (
                    <Badge>{result.meta.language}</Badge>
                  )}
                  <Badge variant="time">
                    <Star className="mr-1 inline h-3 w-3" />
                    {result.meta.stars}
                  </Badge>
                  <Badge variant="space">{result.meta.forks} forks</Badge>
                </div>
              </div>
              {result.meta.topics.length > 0 && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {result.meta.topics.map((t) => (
                    <span
                      key={t}
                      className="rounded-md bg-surface-elevated px-2 py-0.5 text-xs text-muted"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              )}
            </Card>

            <Card>
              <h3 className="mb-3 text-sm font-semibold uppercase text-muted">
                File Tree (sample)
              </h3>
              <pre className="max-h-48 overflow-auto rounded-lg bg-background p-3 font-mono text-xs text-foreground/80">
                {result.file_tree.join("\n") || "(no files)"}
              </pre>
            </Card>

            <div className="grid gap-4 md:grid-cols-2">
              {Object.entries(sections).map(([title, content]) => (
                <Card key={title}>
                  <h3 className="mb-2 text-sm font-semibold text-accent">
                    {title.replace(/_/g, " ")}
                  </h3>
                  <pre className="whitespace-pre-wrap text-sm leading-relaxed text-foreground/90">
                    {content}
                  </pre>
                </Card>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
