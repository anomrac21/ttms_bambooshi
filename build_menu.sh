#!/usr/bin/env bash
set -euo pipefail

# Sync submodule URLs from .gitmodules to ensure HTTPS URLs are used
git submodule sync --recursive

# Initialize submodules (Netlify also sets GIT_SUBMODULE_STRATEGY=recursive)
git submodule update --init --recursive

# Refresh theme from remote only on local/dev builds — Netlify must use the submodule SHA pinned in this repo
if [ -z "${NETLIFY:-}" ] && [ -z "${CI:-}" ]; then
  echo "Updating theme submodule to latest master..."
  (
    cd themes/_menus_ttms
    git fetch origin master
    git checkout master
    git pull origin master
  )
fi

echo "Running Hugo build with minification..."
hugo --gc --minify

if [ ! -f public/index.html ]; then
  echo "ERROR: Hugo did not produce public/index.html — home page will be broken on deploy."
  exit 1
fi

echo "Build OK: public/index.html ($(wc -c < public/index.html | tr -d ' ') bytes)"
