#!/usr/bin/env bash
set -e

REMOTE="$1"

echo "Running Git LFS setup and push helper..."

git lfs install

echo "Ensuring .gitattributes is added"
git add .gitattributes

echo "Staging all changes"
git add -A

if [ -n "$(git status --porcelain)" ]; then
  git commit -m "Prepare repo and track large files with Git LFS" || true
else
  echo "No changes to commit"
fi

if [ -n "$REMOTE" ]; then
  if ! git remote | grep -q origin; then
    git remote add origin "$REMOTE"
    echo "Added remote origin: $REMOTE"
  else
    echo "Remote 'origin' already exists"
  fi
fi

BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)
echo "Pushing to origin/$BRANCH (you may be prompted for credentials)"
git push -u origin $BRANCH

echo "Done. If push failed, verify the remote URL and your credentials."
