"use client";

import { BRAND } from "@/lib/brand";
import { cn } from "@/lib/utils";
import {
  Brain,
  Code2,
  Github,
  Home,
  MessageSquare,
  Sparkles,
  Zap,
} from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const nav = [
  { href: "/", label: "Home", icon: Home, exact: true },
  { href: "/analyze", label: "Analyze", icon: Sparkles },
  { href: "/visualize", label: "Visualizer", icon: Code2 },
  { href: "/interview", label: "Interview", icon: MessageSquare },
  { href: "/github", label: "GitHub", icon: Github },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-64 flex-col border-r border-border/80 bg-surface/90 backdrop-blur-xl">
      <div className="border-b border-border/60 px-5 py-6">
        <Link href="/" className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-accent to-accent-secondary shadow-lg shadow-accent/20">
            <Zap className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-lg font-bold text-foreground">{BRAND.name}</h1>
            <p className="text-[11px] text-muted">{BRAND.tagline}</p>
          </div>
        </Link>
      </div>

      <nav className="flex-1 space-y-0.5 px-3 py-4">
        {nav.map(({ href, label, icon: Icon, exact }) => {
          const active = exact
            ? pathname === href
            : pathname === href || pathname.startsWith(`${href}/`);
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all",
                active
                  ? "bg-accent/15 text-accent shadow-sm"
                  : "text-muted hover:bg-surface-elevated hover:text-foreground"
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-border/60 p-4">
        <div className="flex items-center gap-2 rounded-lg bg-surface-elevated/80 px-3 py-2 text-[11px] text-muted">
          <Brain className="h-3.5 w-3.5 shrink-0 text-accent" />
          Groq · FastAPI · Next.js
        </div>
      </div>
    </aside>
  );
}
