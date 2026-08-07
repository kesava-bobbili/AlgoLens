import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: {
    default: "AlgoLens — AI Engineering Copilot",
    template: "%s · AlgoLens",
  },
  description:
    "An AI-powered developer productivity and code intelligence platform. Pattern detection, execution visualization, interview simulation, and GitHub analysis.",
  keywords: [
    "AI",
    "coding interview",
    "DSA",
    "FastAPI",
    "Groq",
    "developer tools",
  ],
  openGraph: {
    title: "AlgoLens — AI Engineering Copilot",
    description:
      "Pattern detection, code tracing, RAG knowledge base, and GitHub review — powered by Groq and LangGraph.",
    images: [{ url: "/previews/analyze.png", width: 1200, height: 675 }],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} font-sans`}
      >
        {children}
      </body>
    </html>
  );
}
