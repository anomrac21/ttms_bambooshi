#!/bin/sh
set -eu

# Submodule: https://github.com/anomrac21/_menus_ttms.git (same as _ttms_menu_demo/themes/_menus_ttms)
git submodule sync --recursive
git submodule update --init --recursive

echo "Updating submodules to latest master branch..."
cd themes/_menus_ttms
git fetch origin master
git checkout master
git pull origin master
cd ../..

echo "Running Hugo build with minification..."
hugo --gc --minify

if [ ! -f public/index.html ]; then
  echo "❌ Hugo build did not produce public/index.html"
  exit 1
fi

echo "✅ Build completed successfully!"
