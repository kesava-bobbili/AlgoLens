import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function parseSections(text: string): Record<string, string> {
  const sections: Record<string, string> = {};
  const parts = text.split(/\n(?=[A-Z][A-Z _]+:)/);
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
