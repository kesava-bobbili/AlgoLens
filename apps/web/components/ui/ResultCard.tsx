"use client";

import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import { LucideIcon } from "lucide-react";
import { CopyButton } from "./CopyButton";

export function ResultCard({
  title,
  icon: Icon,
  children,
  copyText,
  className,
  delay = 0,
}: {
  title: string;
  icon: LucideIcon;
  children: React.ReactNode;
  copyText?: string;
  className?: string;
  delay?: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay }}
      className={cn(
        "group rounded-2xl border border-border/80 bg-surface/60 p-6 shadow-xl backdrop-blur-md transition-shadow hover:border-accent/25 hover:shadow-accent/5",
        className
      )}
    >
      <div className="mb-4 flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-accent/20 to-accent-secondary/20 ring-1 ring-accent/30">
            <Icon className="h-5 w-5 text-accent" />
          </div>
          <h3 className="text-sm font-semibold tracking-wide text-foreground">
            {title}
          </h3>
        </div>
        {copyText && <CopyButton text={copyText} />}
      </div>
      <div className="border-t border-border/50 pt-4">{children}</div>
    </motion.div>
  );
}
