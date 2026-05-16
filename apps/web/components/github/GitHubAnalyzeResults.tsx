"use client";

import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { CodeBlock } from "@/components/ui/CodeBlock";
import { ResultCard } from "@/components/ui/ResultCard";
import type { GitHubAnalyzeResult } from "@/lib/api";
import { normalizeGithubSections, parseSections } from "@/lib/utils";
import { motion } from "framer-motion";
import {
  AlertTriangle,
  BookOpen,
  Boxes,
  Cpu,
  Github,
  Layers,
  ShieldAlert,
  Sparkles,
  TrendingUp,
  Wrench,
} from "lucide-react";

const SECTION_ORDER = [
  "OVERVIEW",
  "ARCHITECTURE",
  "TECH_STACK",
  "STRENGTHS",
  "WEAKNESSES",
  "SCALABILITY",
  "CODE_QUALITY",
  "README_SUGGESTIONS",
  "RECOMMENDATIONS",
] as const;

const SECTION_ICONS: Record<string, typeof Layers> = {
  OVERVIEW: Sparkles,
  ARCHITECTURE: Layers,
  TECH_STACK: Cpu,
  STRENGTHS: TrendingUp,
  WEAKNESSES: AlertTriangle,
  SCALABILITY: Boxes,
  CODE_QUALITY: ShieldAlert,
  README_SUGGESTIONS: BookOpen,
  RECOMMENDATIONS: Wrench,
};

export function GitHubAnalyzeResults({
  result,
}: {
  result: GitHubAnalyzeResult;
}) {
  const rawSections = parseSections(result.ai_analysis);
  const sections = normalizeGithubSections(rawSections);

  const orderedSections = SECTION_ORDER.filter((k) => sections[k]).map(
    (key) => ({
      key,
      title: key.replace(/_/g, " "),
      content: sections[key],
      icon: SECTION_ICONS[key] ?? Layers,
    })
  );

  const orphanKeys = Object.keys(sections).filter(
    (k) =>
      !SECTION_ORDER.includes(k as (typeof SECTION_ORDER)[number]) &&
      k !== "RESPONSE"
  );

  const langs = Object.entries(result.meta.languages ?? {}).sort(
    (a, b) => b[1] - a[1]
  );

  const treeText =
    result.file_tree.join("\n") || "(no paths collected)";

  const langCopy =
    langs.length > 0
      ? langs.map(([n, b]) => `${n}: ${b} bytes`).join("\n")
      : "";

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-5"
    >
      <Card className="border-border/60 bg-surface/40 backdrop-blur-xl">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Github className="h-5 w-5 text-accent" />
              <h2 className="text-xl font-bold">{result.meta.full_name}</h2>
            </div>
            <p className="max-w-2xl text-sm text-muted">
              {result.meta.description ?? "No GitHub description"}
            </p>
            <p className="text-xs text-muted">
              Default branch:{" "}
              <span className="text-foreground">{result.meta.default_branch}</span>
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            {result.meta.language && (
              <Badge variant="pattern">{result.meta.language}</Badge>
            )}
            <Badge variant="time">★ {result.meta.stars}</Badge>
            <Badge variant="space">{result.meta.forks} forks</Badge>
          </div>
        </div>
        {result.meta.topics.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2 border-t border-border/50 pt-4">
            {result.meta.topics.map((t) => (
              <span
                key={t}
                className="rounded-full bg-surface-elevated px-2.5 py-0.5 text-xs text-muted"
              >
                {t}
              </span>
            ))}
          </div>
        )}
      </Card>

      <ResultCard title="Tech stack (GitHub languages)" icon={Cpu} copyText={langCopy}>
        {langs.length === 0 ? (
          <p className="text-sm text-muted">
            Language breakdown unavailable (rate limit or empty repo).
          </p>
        ) : (
          <div className="flex flex-wrap gap-2">
            {langs.slice(0, 14).map(([name, bytes]) => (
              <Badge key={name} variant="default" className="font-mono text-xs">
                {name}{" "}
                <span className="text-muted">
                  (
                  {bytes >= 1000
                    ? `${Math.round(bytes / 1000)}k`
                    : bytes}{" "}
                  bytes)
                </span>
              </Badge>
            ))}
          </div>
        )}
      </ResultCard>

      <ResultCard title="Project structure" icon={Layers} copyText={treeText}>
        <CodeBlock code={treeText} language="plaintext" />
      </ResultCard>

      {orderedSections.map(({ key, title, content, icon }, i) => (
        <ResultCard
          key={key}
          title={title}
          icon={icon}
          copyText={content}
          delay={i * 0.05}
        >
          <pre className="whitespace-pre-wrap text-sm leading-relaxed text-foreground/90">
            {content}
          </pre>
        </ResultCard>
      ))}

      {orphanKeys.map((key) => (
        <ResultCard
          key={key}
          title={key.replace(/_/g, " ")}
          icon={Layers}
          copyText={sections[key]}
        >
          <pre className="whitespace-pre-wrap text-sm leading-relaxed text-foreground/90">
            {sections[key]}
          </pre>
        </ResultCard>
      ))}

      {sections.RESPONSE && orderedSections.length === 0 && (
        <ResultCard title="Analysis" icon={Sparkles} copyText={sections.RESPONSE}>
          <pre className="whitespace-pre-wrap text-sm leading-relaxed text-foreground/90">
            {sections.RESPONSE}
          </pre>
        </ResultCard>
      )}
    </motion.div>
  );
}
