"use client";

import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

const LEVELS: Record<string, number> = {
  High: 92,
  Medium: 62,
  Low: 34,
};

export function ConfidenceMeter({
  confidence,
  className,
}: {
  confidence: string;
  className?: string;
}) {
  const level = confidence.replace(/\s*confidence/i, "").trim();
  const value = LEVELS[level] ?? 50;

  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex items-center justify-between text-xs">
        <span className="text-muted">Classifier confidence</span>
        <span className="font-medium text-foreground">
          {level} · {value}%
        </span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-background">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className={cn(
            "h-full rounded-full bg-gradient-to-r",
            value >= 80
              ? "from-emerald-500 to-teal-400"
              : value >= 50
                ? "from-amber-500 to-orange-400"
                : "from-rose-500 to-pink-400"
          )}
        />
      </div>
    </div>
  );
}
