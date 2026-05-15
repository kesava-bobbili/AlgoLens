"use client";

import { Button } from "@/components/ui/Button";
import { cn } from "@/lib/utils";
import {
  ChevronLeft,
  ChevronRight,
  Pause,
  Play,
  SkipBack,
  SkipForward,
} from "lucide-react";

export function ExecutionControls({
  stepIndex,
  totalSteps,
  playing,
  speed,
  onPlayPause,
  onStep,
  onSpeedChange,
  onSlider,
}: {
  stepIndex: number;
  totalSteps: number;
  playing: boolean;
  speed: number;
  onPlayPause: () => void;
  onStep: (index: number) => void;
  onSpeedChange: (speed: number) => void;
  onSlider: (index: number) => void;
}) {
  const progress = totalSteps > 1 ? (stepIndex / (totalSteps - 1)) * 100 : 0;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between text-xs text-muted">
        <span>
          Step {stepIndex + 1} / {totalSteps}
        </span>
        <span>{Math.round(progress)}% complete</span>
      </div>

      <input
        type="range"
        min={0}
        max={Math.max(0, totalSteps - 1)}
        value={stepIndex}
        onChange={(e) => onSlider(Number(e.target.value))}
        className="h-1.5 w-full cursor-pointer appearance-none rounded-full bg-background accent-accent"
      />

      <div className="h-1 overflow-hidden rounded-full bg-background">
        <div
          className="h-full rounded-full bg-gradient-to-r from-accent to-accent-secondary transition-all duration-300"
          style={{ width: `${progress}%` }}
        />
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex gap-1">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => onStep(0)}
            disabled={stepIndex === 0}
            aria-label="First step"
          >
            <SkipBack className="h-4 w-4" />
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => onStep(stepIndex - 1)}
            disabled={stepIndex === 0}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <Button variant="secondary" size="sm" onClick={onPlayPause}>
            {playing ? (
              <Pause className="h-4 w-4" />
            ) : (
              <Play className="h-4 w-4" />
            )}
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => onStep(stepIndex + 1)}
            disabled={stepIndex >= totalSteps - 1}
          >
            <ChevronRight className="h-4 w-4" />
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => onStep(totalSteps - 1)}
            disabled={stepIndex >= totalSteps - 1}
          >
            <SkipForward className="h-4 w-4" />
          </Button>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-xs text-muted">Speed</span>
          {[0.5, 1, 1.5, 2].map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => onSpeedChange(s)}
              className={cn(
                "rounded-md px-2 py-1 text-xs font-medium transition",
                speed === s
                  ? "bg-accent text-white"
                  : "bg-surface-elevated text-muted hover:text-foreground"
              )}
            >
              {s}x
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
