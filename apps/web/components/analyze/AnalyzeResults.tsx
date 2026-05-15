"use client";

import { CodeBlock } from "@/components/ui/CodeBlock";
import { ComplexityBadge } from "@/components/ui/ComplexityBadge";
import { ConfidenceMeter } from "@/components/ui/ConfidenceMeter";
import { ResultCard } from "@/components/ui/ResultCard";
import type { AnalysisResult } from "@/lib/api";
import { parseSections } from "@/lib/utils";
import { motion } from "framer-motion";
import {
  AlertTriangle,
  Brain,
  GitBranch,
  Lightbulb,
  Puzzle,
  Rocket,
  Sparkles,
} from "lucide-react";

function Prose({ children }: { children: string }) {
  return (
    <p className="whitespace-pre-wrap text-sm leading-relaxed text-foreground/85">
      {children}
    </p>
  );
}

export function AnalyzeResults({ result }: { result: AnalysisResult }) {
  const sections = parseSections(result.ai_explanation);
  const approach = sections.APPROACH ?? sections.RESPONSE ?? "";
  const pseudocode = sections.PSEUDOCODE ?? "";
  const insight = sections["KEY INSIGHT"] ?? "";
  const optimization =
    sections.OPTIMIZATION ?? sections["OPTIMIZATION SUGGESTIONS"] ?? "";
  const edgeCases = sections["EDGE CASES"] ?? sections["EDGE CASES:"] ?? "";
  const similar =
    sections["SIMILAR PROBLEMS"] ??
    sections["SIMILAR LEETCODE PROBLEMS"] ??
    "";

  const topScore = Math.max(...Object.values(result.all_matches), 1);

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="space-y-5"
    >
      <div className="grid gap-5 lg:grid-cols-2">
        <ResultCard
          title="Pattern Detection"
          icon={Puzzle}
          copyText={result.pattern}
          delay={0.05}
        >
          <p className="mb-4 text-2xl font-bold gradient-text">
            {result.pattern}
          </p>
          <ConfidenceMeter confidence={result.confidence} />
          {Object.keys(result.all_matches).length > 0 && (
            <div className="mt-5 space-y-2.5">
              <p className="text-xs font-medium uppercase tracking-wider text-muted">
                Match scores
              </p>
              {Object.entries(result.all_matches).map(([name, score]) => (
                <div key={name} className="flex items-center gap-3">
                  <span className="w-40 truncate text-xs text-muted">
                    {name}
                  </span>
                  <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-background">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{
                        width: `${Math.min(100, (score / topScore) * 100)}%`,
                      }}
                      transition={{ duration: 0.6 }}
                      className="h-full rounded-full bg-gradient-to-r from-accent to-accent-secondary"
                    />
                  </div>
                  <span className="w-4 text-xs tabular-nums text-muted">
                    {score}
                  </span>
                </div>
              ))}
            </div>
          )}
        </ResultCard>

        <ResultCard
          title="Complexity Analysis"
          icon={GitBranch}
          copyText={`Time: ${result.time_complexity}\nSpace: ${result.space_complexity}`}
          delay={0.1}
        >
          <div className="grid gap-3 sm:grid-cols-2">
            <ComplexityBadge type="time" value={result.time_complexity} />
            <ComplexityBadge type="space" value={result.space_complexity} />
          </div>
        </ResultCard>
      </div>

      {approach && (
        <ResultCard
          title="AI Explanation"
          icon={Brain}
          copyText={approach}
          delay={0.15}
        >
          <Prose>{approach}</Prose>
          {insight && (
            <div className="mt-4 flex gap-3 rounded-xl border border-amber-500/20 bg-amber-500/5 p-4">
              <Lightbulb className="mt-0.5 h-5 w-5 shrink-0 text-amber-400" />
              <div>
                <p className="text-xs font-semibold uppercase text-amber-400/90">
                  Key insight
                </p>
                <p className="mt-1 text-sm text-foreground/90">{insight}</p>
              </div>
            </div>
          )}
        </ResultCard>
      )}

      {pseudocode && (
        <ResultCard
          title="Pseudocode"
          icon={Sparkles}
          copyText={pseudocode}
          delay={0.2}
          className="lg:col-span-2"
        >
          <CodeBlock code={pseudocode} language="pseudocode" />
        </ResultCard>
      )}

      <div className="grid gap-5 md:grid-cols-2">
        {optimization && (
          <ResultCard
            title="Optimization Suggestions"
            icon={Rocket}
            copyText={optimization}
            delay={0.25}
          >
            <Prose>{optimization}</Prose>
          </ResultCard>
        )}

        {edgeCases && (
          <ResultCard
            title="Edge Cases"
            icon={AlertTriangle}
            copyText={edgeCases}
            delay={0.3}
          >
            <Prose>{edgeCases}</Prose>
          </ResultCard>
        )}
      </div>

      {similar && (
        <ResultCard title="Similar Problems" icon={Puzzle} delay={0.35}>
          <Prose>{similar}</Prose>
        </ResultCard>
      )}
    </motion.div>
  );
}
