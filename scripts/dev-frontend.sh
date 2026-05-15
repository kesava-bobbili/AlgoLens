#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../apps/web"
if ! command -v npm >/dev/null 2>&1; then
  echo "npm not found. Install Node.js 20+ from https://nodejs.org"
  exit 1
fi
npm install
exec npm run dev
