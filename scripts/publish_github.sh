#!/usr/bin/env bash
# Create a public GitHub repo from this folder (requires GitHub CLI: https://cli.github.com/).
set -euo pipefail
cd "$(dirname "$0")/.."

if ! command -v gh >/dev/null; then
  echo "Install GitHub CLI first: https://cli.github.com/"
  echo "Then run: gh auth login"
  exit 1
fi

gh auth status

NAME="${1:-omop-public-health-showcase}"
git add -A
if ! git diff --cached --quiet || ! git diff --quiet; then
  git commit -m "Add OMOP public-health data mart showcase" || true
fi

if git remote get-url origin >/dev/null 2>&1; then
  echo "Remote origin already exists. Pushing current branch."
  git push -u origin HEAD
  exit 0
fi

gh repo create "$NAME" --public --source=. --remote=origin --push
echo
echo "Public repo:"
gh repo view --web --json url -q .url
