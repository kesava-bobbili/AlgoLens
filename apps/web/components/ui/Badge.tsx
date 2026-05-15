import { cn } from "@/lib/utils";

const variants = {
  pattern: "bg-violet-500/15 text-violet-300 border-violet-500/30",
  confidence: "bg-emerald-500/15 text-emerald-300 border-emerald-500/30",
  time: "bg-sky-500/15 text-sky-300 border-sky-500/30",
  space: "bg-pink-500/15 text-pink-300 border-pink-500/30",
  default: "bg-surface-elevated text-muted border-border",
};

export function Badge({
  children,
  variant = "default",
  className,
}: {
  children: React.ReactNode;
  variant?: keyof typeof variants;
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-3 py-1 text-xs font-medium",
        variants[variant],
        className
      )}
    >
      {children}
    </span>
  );
}
