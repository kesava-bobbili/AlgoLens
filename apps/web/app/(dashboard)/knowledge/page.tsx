"use client";

import { PageHeader } from "@/components/layout/PageHeader";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { Skeleton } from "@/components/ui/Skeleton";
import {
  api,
  type KnowledgeQueryResult,
  type KnowledgeSource,
  type KnowledgeStatsResult,
  type SimilarProblemResult,
} from "@/lib/api";
import { AnimatePresence, motion } from "framer-motion";
import {
  Database,
  FileSearch,
  Loader2,
  Search,
  UploadCloud,
} from "lucide-react";
import { useEffect, useMemo, useState } from "react";

function SourceList({ sources }: { sources: KnowledgeSource[] }) {
  if (!sources.length) {
    return (
      <p className="rounded-lg border border-border/60 bg-background/50 px-3 py-2 text-sm text-muted">
        No matching source chunks yet.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      {sources.map((source) => (
        <div
          key={`${source.source_id}-${source.chunk_index}-${source.score}`}
          className="rounded-lg border border-border/60 bg-background/60 p-4"
        >
          <div className="mb-2 flex flex-wrap items-center gap-2">
            <Badge variant="pattern">{source.filename}</Badge>
            <Badge variant="confidence">Score {(source.score * 100).toFixed(0)}%</Badge>
            <span className="text-xs text-muted">
              {source.file_type.toUpperCase()} · chunk {source.chunk_index + 1}
            </span>
          </div>
          <p className="line-clamp-5 whitespace-pre-wrap text-sm leading-relaxed text-foreground/85">
            {source.text}
          </p>
        </div>
      ))}
    </div>
  );
}

function ResultPanel({ result }: { result: KnowledgeQueryResult | null }) {
  if (!result) return null;
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="space-y-4"
    >
      <Card className="border-border/60 bg-surface/40 p-5">
        <div className="mb-3 flex items-center gap-2">
          <Database className="h-4 w-4 text-accent" />
          <h2 className="text-lg font-semibold text-foreground">Grounded Answer</h2>
          <Badge>{result.retrieval_count} chunks</Badge>
        </div>
        <p className="whitespace-pre-wrap text-sm leading-7 text-foreground/90">
          {result.answer}
        </p>
      </Card>

      <Card className="border-border/60 bg-surface/40 p-5">
        <h2 className="mb-4 text-lg font-semibold text-foreground">Retrieved Sources</h2>
        <SourceList sources={result.sources} />
      </Card>
    </motion.div>
  );
}

function SimilarPanel({ result }: { result: SimilarProblemResult | null }) {
  if (!result) return null;
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
    >
      <Card className="border-border/60 bg-surface/40 p-5">
        <div className="mb-4 flex items-center gap-2">
          <FileSearch className="h-4 w-4 text-accent" />
          <h2 className="text-lg font-semibold text-foreground">Similar Knowledge Matches</h2>
        </div>
        <SourceList sources={result.matches} />
      </Card>
    </motion.div>
  );
}

export default function KnowledgePage() {
  const [files, setFiles] = useState<File[]>([]);
  const [question, setQuestion] = useState("");
  const [problem, setProblem] = useState("");
  const [uploading, setUploading] = useState(false);
  const [asking, setAsking] = useState(false);
  const [matching, setMatching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [stats, setStats] = useState<KnowledgeStatsResult | null>(null);
  const [answer, setAnswer] = useState<KnowledgeQueryResult | null>(null);
  const [similar, setSimilar] = useState<SimilarProblemResult | null>(null);

  const selectedNames = useMemo(
    () => files.map((file) => file.name).join(", "),
    [files]
  );

  async function refreshStats() {
    try {
      setStats(await api.knowledgeStats());
    } catch {
      setStats(null);
    }
  }

  useEffect(() => {
    refreshStats();
  }, []);

  async function handleUpload() {
    if (!files.length) {
      setError("Choose at least one file to index.");
      return;
    }
    setUploading(true);
    setError(null);
    setNotice(null);
    try {
      const result = await api.knowledgeIngest(files);
      const skipped = result.skipped_files.length
        ? ` Skipped: ${result.skipped_files.join("; ")}`
        : "";
      setNotice(
        `${result.message}: ${result.chunks_indexed} chunks from ${result.files_processed} files.${skipped}`
      );
      setFiles([]);
      await refreshStats();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to index files.");
    } finally {
      setUploading(false);
    }
  }

  async function handleAsk() {
    const text = question.trim();
    if (!text) {
      setError("Ask a question about your indexed knowledge.");
      return;
    }
    setAsking(true);
    setError(null);
    setAnswer(null);
    try {
      setAnswer(await api.knowledgeQuery(text, 6));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Question failed.");
    } finally {
      setAsking(false);
    }
  }

  async function handleSimilar() {
    const text = problem.trim();
    if (!text) {
      setError("Paste a coding problem to find similar notes or editorials.");
      return;
    }
    setMatching(true);
    setError(null);
    setSimilar(null);
    try {
      setSimilar(await api.similarProblem(text, 6));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Similarity search failed.");
    } finally {
      setMatching(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="Knowledge Base"
        subtitle="RAG pipeline · vector search · grounded answers"
        description="Index notes, editorials, PDFs, docs, spreadsheets, slides, and code files, then ask questions or retrieve similar problem patterns with source-backed context."
      />

      <div className="mb-6 grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
        <Card className="border-border/60 bg-surface/40 p-5 backdrop-blur-xl">
          <div className="mb-4 flex items-center gap-2">
            <UploadCloud className="h-5 w-5 text-accent" />
            <h2 className="text-lg font-semibold text-foreground">Index Files</h2>
          </div>
          <label className="flex min-h-36 cursor-pointer flex-col items-center justify-center rounded-xl border border-dashed border-border/80 bg-background/60 px-4 py-6 text-center transition-colors hover:border-accent/70 hover:bg-background/80">
            <UploadCloud className="mb-3 h-8 w-8 text-accent" />
            <span className="text-sm font-medium text-foreground">
              Choose notes, PDFs, docs, slides, sheets, code, or text files
            </span>
            <span className="mt-1 max-w-xl text-xs text-muted">
              Files are chunked with LangChain, embedded via HuggingFace API, and stored in ChromaDB.
            </span>
            <input
              type="file"
              multiple
              className="sr-only"
              onChange={(event) =>
                setFiles(Array.from(event.target.files ?? []))
              }
            />
          </label>
          {selectedNames && (
            <p className="mt-3 text-xs text-muted">Selected: {selectedNames}</p>
          )}
          <div className="mt-4 flex flex-wrap items-center gap-3">
            <Button onClick={handleUpload} disabled={uploading}>
              {uploading ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Database className="mr-2 h-4 w-4" />
              )}
              Index knowledge
            </Button>
            {stats && (
              <div className="flex flex-wrap gap-2 text-xs text-muted">
                <Badge>{stats.chunks} chunks</Badge>
                <Badge>{stats.vector_store}</Badge>
                <Badge>{stats.embedding_model.split("/").pop()}</Badge>
              </div>
            )}
          </div>
        </Card>

        <Card className="border-border/60 bg-surface/40 p-5 backdrop-blur-xl">
          <div className="mb-3 flex items-center gap-2">
            <Search className="h-5 w-5 text-accent" />
            <h2 className="text-lg font-semibold text-foreground">What This Adds</h2>
          </div>
          <div className="space-y-3 text-sm text-foreground/85">
            <p>RAG ingestion, chunking, embeddings, vector persistence, semantic retrieval, and source-grounded LLM answers.</p>
            <p>Also includes similar-problem search, which makes the vector DB useful inside AlgoLens instead of feeling like a tutorial feature.</p>
          </div>
        </Card>
      </div>

      {(error || notice) && (
        <div className="mb-6 space-y-2">
          {error && (
            <p className="rounded-lg border border-red-500/20 bg-red-500/10 px-3 py-2 text-sm text-red-400">
              {error}
            </p>
          )}
          {notice && (
            <p className="rounded-lg border border-emerald-500/20 bg-emerald-500/10 px-3 py-2 text-sm text-emerald-300">
              {notice}
            </p>
          )}
        </div>
      )}

      <div className="mb-6 grid gap-6 lg:grid-cols-2">
        <Card className="border-border/60 bg-surface/40 p-5 backdrop-blur-xl">
          <h2 className="mb-3 text-lg font-semibold text-foreground">Ask Your Knowledge Base</h2>
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Example: Explain sliding window from my notes and mention the key edge cases."
            className="h-36 w-full resize-y rounded-xl border border-border/60 bg-background/80 p-4 text-sm text-foreground outline-none transition-colors focus:border-accent focus:ring-2 focus:ring-accent/20"
          />
          <Button className="mt-4" onClick={handleAsk} disabled={asking}>
            {asking ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Search className="mr-2 h-4 w-4" />
            )}
            Ask with RAG
          </Button>
        </Card>

        <Card className="border-border/60 bg-surface/40 p-5 backdrop-blur-xl">
          <h2 className="mb-3 text-lg font-semibold text-foreground">Find Similar Problems</h2>
          <textarea
            value={problem}
            onChange={(event) => setProblem(event.target.value)}
            placeholder="Paste a coding problem and retrieve similar patterns, notes, or editorials from your indexed files."
            className="h-36 w-full resize-y rounded-xl border border-border/60 bg-background/80 p-4 text-sm text-foreground outline-none transition-colors focus:border-accent focus:ring-2 focus:ring-accent/20"
          />
          <Button className="mt-4" onClick={handleSimilar} disabled={matching}>
            {matching ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <FileSearch className="mr-2 h-4 w-4" />
            )}
            Retrieve matches
          </Button>
        </Card>
      </div>

      <AnimatePresence>
        {(asking || matching) && (
          <motion.div
            key="loading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="space-y-4"
          >
            <Skeleton className="h-44 w-full" />
            <Skeleton className="h-32 w-full" />
          </motion.div>
        )}
        {!asking && <ResultPanel key="answer" result={answer} />}
        {!matching && <SimilarPanel key="similar" result={similar} />}
      </AnimatePresence>
    </div>
  );
}
