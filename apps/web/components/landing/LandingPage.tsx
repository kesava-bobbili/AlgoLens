"use client";

import { BRAND } from "@/lib/brand";
import { motion } from "framer-motion";
import {
  ArrowRight,
  BookOpen,
  Brain,
  Code2,
  Github,
  Library,
  MessageSquare,
  Sparkles,
  Upload,
  Zap,
} from "lucide-react";
import Image from "next/image";
import Link from "next/link";

const features = [
  {
    icon: Sparkles,
    title: "Code Intelligence",
    description:
      "Pattern detection, complexity analysis, and Groq-powered explanations for any coding problem.",
    href: "/analyze",
  },
  {
    icon: Code2,
    title: "Execution Visualizer",
    description:
      "Step through Python with line highlighting, variables, call stack, and recursion depth.",
    href: "/visualize",
  },
  {
    icon: MessageSquare,
    title: "Interview Simulator",
    description:
      "Realistic follow-ups on optimization, edge cases, and complexity—with scored feedback.",
    href: "/interview",
  },
  {
    icon: Github,
    title: "GitHub Analyzer",
    description:
      "Architecture review, code quality insights, and README suggestions from any public repo.",
    href: "/github",
  },
  {
    icon: Library,
    title: "Knowledge Base",
    description:
      "Upload notes and editorials, then ask grounded questions with source citations via RAG.",
    href: "/knowledge",
  },
];

const workflow = [
  {
    step: "01",
    icon: Upload,
    title: "Input",
    text: "Paste a problem, Python code, GitHub URL, or upload your study notes.",
  },
  {
    step: "02",
    icon: Brain,
    title: "Analyze",
    text: "Classifier + LangGraph pipeline routes your request to the right AI workflow.",
  },
  {
    step: "03",
    icon: BookOpen,
    title: "Learn",
    text: "Get structured insights, visual traces, and source-backed answers for interview prep.",
  },
];

const previews = [
  {
    title: "Visualizer",
    desc: "Monaco editor + step controls + variable panel",
    gradient: "from-cyan-500/20 to-blue-600/10",
    image: "/previews/visualize.png",
    href: "/visualize",
  },
  {
    title: "GitHub Analyzer",
    desc: "Repo metadata, file tree, AI architecture review",
    gradient: "from-violet-500/20 to-purple-600/10",
    image: "/previews/repo.png",
    href: "/github",
  },
  {
    title: "Interview Mode",
    desc: "Multi-turn Q&A with score and follow-ups",
    gradient: "from-emerald-500/20 to-teal-600/10",
    image: "/previews/interview.png",
    href: "/interview",
  },
];

export function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="hero-gradient pointer-events-none fixed inset-0" />

      <header className="relative z-10 border-b border-border/50 bg-background/60 backdrop-blur-xl">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-accent to-accent-secondary">
              <Zap className="h-5 w-5 text-white" />
            </div>
            <span className="font-bold text-foreground">{BRAND.name}</span>
          </Link>
          <nav className="hidden items-center gap-6 text-sm text-muted md:flex">
            <a href="#features" className="hover:text-foreground">
              Features
            </a>
            <a href="#workflow" className="hover:text-foreground">
              How it works
            </a>
            <a href="#previews" className="hover:text-foreground">
              Product
            </a>
          </nav>
          <Link
            href="/analyze"
            className="rounded-lg bg-gradient-to-r from-accent to-accent-secondary px-4 py-2 text-sm font-semibold text-white shadow-lg shadow-accent/25 transition hover:opacity-90"
          >
            Open App
          </Link>
        </div>
      </header>

      <section className="relative z-10 mx-auto max-w-6xl px-6 pb-24 pt-20 text-center">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <p className="mb-4 inline-flex items-center gap-2 rounded-full border border-accent/30 bg-accent/10 px-4 py-1.5 text-xs font-medium text-accent">
            <Brain className="h-3.5 w-3.5" />
            {BRAND.tagline}
          </p>
          <h1 className="mx-auto max-w-4xl text-4xl font-bold tracking-tight md:text-6xl">
            <span className="gradient-text">{BRAND.fullTitle}</span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-muted">
            {BRAND.description}
          </p>
          <p className="mt-3 text-sm text-muted/80">
            Pattern detection · Code tracing · RAG knowledge base · GitHub review
          </p>
          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Link
              href="/analyze"
              className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-accent to-accent-secondary px-6 py-3 text-sm font-semibold text-white shadow-xl shadow-accent/30 transition hover:scale-[1.02]"
            >
              Start analyzing
              <ArrowRight className="h-4 w-4" />
            </Link>
            <Link
              href="/visualize"
              className="inline-flex items-center gap-2 rounded-xl border border-border bg-surface/80 px-6 py-3 text-sm font-semibold backdrop-blur transition hover:border-accent/40"
            >
              Try visualizer
            </Link>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
          className="mx-auto mt-16 max-w-4xl animate-float overflow-hidden rounded-2xl border border-border/60 bg-surface/40 p-1 shadow-2xl shadow-accent/10 backdrop-blur-xl"
        >
          <div className="overflow-hidden rounded-xl border border-border/40 bg-[#0d0d14]">
            <div className="flex items-center gap-2 border-b border-border/40 px-4 py-2.5">
              <span className="h-2.5 w-2.5 rounded-full bg-red-500/80" />
              <span className="h-2.5 w-2.5 rounded-full bg-amber-500/80" />
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-500/80" />
              <span className="ml-2 text-xs text-muted">AlgoLens — Code Intelligence</span>
            </div>
            <Image
              src="/previews/analyze.png"
              alt="AlgoLens analyze screen showing pattern detection and AI explanation"
              width={1200}
              height={675}
              className="h-auto w-full"
              priority
            />
          </div>
        </motion.div>
      </section>

      <section id="features" className="relative z-10 border-t border-border/50 py-24">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="text-center text-3xl font-bold">Features</h2>
          <p className="mx-auto mt-3 max-w-xl text-center text-muted">
            Everything you need for technical interview prep and code intelligence.
          </p>
          <div className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((f, i) => (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 16 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.08 }}
              >
                <Link
                  href={f.href}
                  className="group block h-full rounded-2xl border border-border/60 bg-surface/50 p-6 backdrop-blur transition hover:border-accent/40 hover:shadow-lg hover:shadow-accent/5"
                >
                  <f.icon className="h-8 w-8 text-accent" />
                  <h3 className="mt-4 text-lg font-semibold">{f.title}</h3>
                  <p className="mt-2 text-sm text-muted">{f.description}</p>
                  <span className="mt-4 inline-flex items-center gap-1 text-sm text-accent opacity-0 transition group-hover:opacity-100">
                    Explore <ArrowRight className="h-3.5 w-3.5" />
                  </span>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      <section id="workflow" className="relative z-10 py-24">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="text-center text-3xl font-bold">How it works</h2>
          <p className="mx-auto mt-3 max-w-xl text-center text-muted">
            From input to insight in three steps.
          </p>
          <div className="mt-12 grid gap-8 md:grid-cols-3">
            {workflow.map((w) => (
              <div
                key={w.step}
                className="rounded-2xl border border-border/50 bg-surface/30 p-6 text-center backdrop-blur"
              >
                <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-accent/10">
                  <w.icon className="h-6 w-6 text-accent" />
                </div>
                <span className="mt-4 block text-sm font-semibold uppercase tracking-wider text-accent/60">
                  Step {w.step}
                </span>
                <h3 className="mt-1 font-semibold">{w.title}</h3>
                <p className="mt-2 text-sm text-muted">{w.text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="previews" className="relative z-10 border-t border-border/50 py-24">
        <div className="mx-auto max-w-6xl px-6">
          <h2 className="text-center text-3xl font-bold">AI workflows</h2>
          <p className="mx-auto mt-3 max-w-xl text-center text-muted">
            Explore the core product surfaces — click any card to try it live.
          </p>
          <div className="mt-12 grid gap-6 md:grid-cols-3">
            {previews.map((p) => (
              <Link
                key={p.title}
                href={p.href}
                className={`group block rounded-2xl border border-border/50 bg-gradient-to-br ${p.gradient} p-4 backdrop-blur transition hover:border-accent/40 hover:shadow-lg hover:shadow-accent/5`}
              >
                <div className="overflow-hidden rounded-lg border border-border/40 bg-background/60 shadow-inner">
                  <Image
                    src={p.image}
                    alt={`${p.title} preview`}
                    width={640}
                    height={360}
                    className="aspect-video w-full object-cover object-top transition duration-300 group-hover:scale-[1.02]"
                  />
                </div>
                <h3 className="mt-4 font-semibold">{p.title}</h3>
                <p className="mt-1 text-sm text-muted">{p.desc}</p>
                <span className="mt-3 inline-flex items-center gap-1 text-sm text-accent opacity-0 transition group-hover:opacity-100">
                  Open {p.title.toLowerCase()} <ArrowRight className="h-3.5 w-3.5" />
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <footer className="relative z-10 border-t border-border/50 py-12 text-center text-sm text-muted">
        <p>
          {BRAND.name} · {BRAND.tagline}
        </p>
        <p className="mt-2 text-xs text-muted/70">
          Groq · FastAPI · LangGraph · ChromaDB · Next.js
        </p>
      </footer>
    </div>
  );
}
