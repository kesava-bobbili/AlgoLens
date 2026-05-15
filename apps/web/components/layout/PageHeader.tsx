"use client";

import { motion } from "framer-motion";

export function PageHeader({
  title,
  subtitle,
  description,
}: {
  title: string;
  subtitle?: string;
  description: string;
}) {
  return (
    <motion.header
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      className="mb-8"
    >
      {subtitle && (
        <p className="mb-1 text-xs font-semibold uppercase tracking-widest text-accent/90">
          {subtitle}
        </p>
      )}
      <h1 className="text-3xl font-bold tracking-tight gradient-text md:text-4xl">
        {title}
      </h1>
      <p className="mt-3 max-w-2xl text-base text-muted">{description}</p>
    </motion.header>
  );
}
