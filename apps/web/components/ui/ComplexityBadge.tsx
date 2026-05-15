import { cn } from "@/lib/utils";
import { Clock, HardDrive } from "lucide-react";

export function ComplexityBadge({
  type,
  value,
}: {
  type: "time" | "space";
  value: string;
}) {
  const Icon = type === "time" ? Clock : HardDrive;
  const gradient =
    type === "time"
      ? "from-sky-500/20 to-cyan-500/10 border-sky-500/30 text-sky-200"
      : "from-fuchsia-500/20 to-pink-500/10 border-fuchsia-500/30 text-fuchsia-200";

  return (
    <div
      className={cn(
        "flex items-center gap-3 rounded-xl border bg-gradient-to-br px-4 py-3 shadow-lg backdrop-blur-sm",
        gradient
      )}
    >
      <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-white/5">
        <Icon className="h-4 w-4" />
      </div>
      <div>
        <p className="text-[10px] font-semibold uppercase tracking-wider opacity-70">
          {type === "time" ? "Time" : "Space"}
        </p>
        <p className="font-mono text-sm font-semibold">{value}</p>
      </div>
    </div>
  );
}
