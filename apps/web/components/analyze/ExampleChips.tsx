"use client";

import { EXAMPLE_PROBLEMS } from "@/lib/examples";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";

export function ExampleChips({
  onSelect,
  disabled,
}: {
  onSelect: (text: string) => void;
  disabled?: boolean;
}) {
  return (
    <div className="space-y-2">
      <p className="text-xs font-medium uppercase tracking-wider text-muted">
        Example problems
      </p>
      <div className="flex flex-wrap gap-2">
        {EXAMPLE_PROBLEMS.map((ex, i) => (
          <motion.button
            key={ex.id}
            type="button"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.04 }}
            disabled={disabled}
            onClick={() => onSelect(ex.text)}
            className={cn(
              "rounded-full border border-border/80 bg-surface-elevated/80 px-3.5 py-1.5 text-xs font-medium text-foreground/90 backdrop-blur-sm transition-all",
              "hover:border-accent/50 hover:bg-accent/10 hover:text-accent hover:shadow-md hover:shadow-accent/10",
              "disabled:pointer-events-none disabled:opacity-50"
            )}
          >
            {ex.label}
          </motion.button>
        ))}
      </div>
    </div>
  );
}
