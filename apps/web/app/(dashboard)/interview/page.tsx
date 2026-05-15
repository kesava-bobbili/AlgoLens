"use client";

import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { PageHeader } from "@/components/layout/PageHeader";
import { api } from "@/lib/api";
import { BRAND } from "@/lib/brand";
import { motion, AnimatePresence } from "framer-motion";
import { Loader2, MessageSquare, Send } from "lucide-react";
import { useState } from "react";

interface Turn {
  role: "interviewer" | "candidate" | "feedback";
  content: string;
  score?: number | null;
}

export default function InterviewPage() {
  const [problem, setProblem] = useState("");
  const [answer, setAnswer] = useState("");
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [pattern, setPattern] = useState<string | null>(null);
  const [turns, setTurns] = useState<Turn[]>([]);
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function startInterview() {
    const text = problem.trim();
    if (!text) {
      setError("Enter a problem to start the interview.");
      return;
    }
    setLoading(true);
    setError(null);
    setTurns([]);
    setDone(false);
    try {
      const data = await api.interviewStart(text);
      setSessionId(data.session_id);
      setPattern(data.pattern);
      setTurns([{ role: "interviewer", content: data.question }]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to start interview");
    } finally {
      setLoading(false);
    }
  }

  async function submitAnswer() {
    if (!sessionId || !answer.trim()) return;
    setLoading(true);
    setError(null);
    const userAnswer = answer.trim();
    setTurns((t) => [...t, { role: "candidate", content: userAnswer }]);
    setAnswer("");
    try {
      const data = await api.interviewRespond(sessionId, userAnswer);
      setTurns((t) => [
        ...t,
        {
          role: "feedback",
          content: data.feedback,
          score: data.score,
        },
      ]);
      if (data.done) {
        setDone(true);
        setSessionId(null);
      } else if (data.follow_up) {
        setTurns((t) => [
          ...t,
          { role: "interviewer", content: data.follow_up! },
        ]);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to submit answer");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <PageHeader
        title="Interview Simulator"
        subtitle={BRAND.fullTitle}
        description="Practice technical interviews with follow-up questions on optimization, edge cases, and complexity."
      />

      {!sessionId && !done && (
        <Card className="mb-6">
          <textarea
            value={problem}
            onChange={(e) => setProblem(e.target.value)}
            placeholder="Enter the DSA problem for your mock interview..."
            className="h-32 w-full resize-y rounded-lg border border-border bg-background p-4 text-sm outline-none focus:border-accent"
          />
          <Button className="mt-4" onClick={startInterview} disabled={loading}>
            {loading ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <MessageSquare className="mr-2 h-4 w-4" />
            )}
            Start Interview
          </Button>
        </Card>
      )}

      {pattern && (
        <Badge variant="pattern" className="mb-4">
          Detected: {pattern}
        </Badge>
      )}

      {error && (
        <p className="mb-4 rounded-lg bg-red-500/10 px-4 py-2 text-sm text-red-400">
          {error}
        </p>
      )}

      <AnimatePresence>
        {turns.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="space-y-4"
          >
            {turns.map((turn, i) => (
              <Card
                key={i}
                className={
                  turn.role === "interviewer"
                    ? "border-l-4 border-l-accent"
                    : turn.role === "feedback"
                      ? "border-l-4 border-l-emerald-500"
                      : "border-l-4 border-l-sky-500"
                }
              >
                <div className="mb-1 flex items-center justify-between">
                  <span className="text-xs font-semibold uppercase text-muted">
                    {turn.role === "interviewer"
                      ? "Interviewer"
                      : turn.role === "candidate"
                        ? "You"
                        : "Feedback"}
                  </span>
                  {turn.score != null && (
                    <span className="rounded-full bg-emerald-500/15 px-2 py-0.5 text-xs text-emerald-300">
                      Score: {turn.score}/10
                    </span>
                  )}
                </div>
                <p className="whitespace-pre-wrap text-sm leading-relaxed">
                  {turn.content}
                </p>
              </Card>
            ))}

            {sessionId && !done && (
              <Card>
                <textarea
                  value={answer}
                  onChange={(e) => setAnswer(e.target.value)}
                  placeholder="Type your answer..."
                  className="h-28 w-full resize-y rounded-lg border border-border bg-background p-3 text-sm outline-none focus:border-accent"
                />
                <Button
                  className="mt-3"
                  onClick={submitAnswer}
                  disabled={loading || !answer.trim()}
                >
                  {loading ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="mr-2 h-4 w-4" />
                  )}
                  Submit Answer
                </Button>
              </Card>
            )}

            {done && (
              <Card className="text-center">
                <p className="text-lg font-semibold text-foreground">
                  Interview complete
                </p>
                <p className="mt-2 text-sm text-muted">
                  Great practice session. Start a new interview to try another
                  problem.
                </p>
                <Button
                  className="mt-4"
                  variant="secondary"
                  onClick={() => {
                    setDone(false);
                    setTurns([]);
                    setPattern(null);
                    setProblem("");
                  }}
                >
                  New Interview
                </Button>
              </Card>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
