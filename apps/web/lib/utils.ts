import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function parseSections(text: string): Record<string, string> {
  // Normalize "### SECTION_NAME:" (markdown) so section splitting works
  const normalized = text
    .replace(/^#{1,6}\s+(?=[A-Z][A-Z _]+:)/gm, "")
    .trim();

  const sections: Record<string, string> = {};
  const parts = normalized.split(/\n(?=[A-Z][A-Z _]+:)/);
  for (const part of parts) {
    const match = part.match(/^([A-Z][A-Z _]+):\s*([\s\S]*)/);
    if (match) {
      sections[match[1].trim()] = match[2].trim();
    }
  }
  if (Object.keys(sections).length === 0) {
    sections["RESPONSE"] = text;
  }
  return sections;
}

/** Merge legacy / alternate LLM headings for GitHub intelligence UI */
export function normalizeGithubSections(
  sections: Record<string, string>
): Record<string, string> {
  const out = { ...sections };
  const alias = (from: string, to: string) => {
    if (out[from] && !out[to]) out[to] = out[from];
  };
  alias("SUMMARY", "OVERVIEW");
  alias("IMPROVEMENTS", "RECOMMENDATIONS");
  alias("BEST_PRACTICES", "RECOMMENDATIONS");
  return out;
}
