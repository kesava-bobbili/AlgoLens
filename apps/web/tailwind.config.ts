import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#0a0a0f",
        surface: "#12121a",
        "surface-elevated": "#1a1a26",
        border: "#2a2a3d",
        accent: "#6366f1",
        "accent-secondary": "#8b5cf6",
        muted: "#94a3b8",
        foreground: "#e2e8f0",
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)", "system-ui", "sans-serif"],
        mono: ["var(--font-geist-mono)", "monospace"],
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(ellipse at top, rgba(99,102,241,0.15), transparent 50%)",
      },
    },
  },
  plugins: [],
};

export default config;
