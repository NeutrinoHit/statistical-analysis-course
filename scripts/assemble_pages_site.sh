#!/usr/bin/env bash
set -euo pipefail

root_dir="$(cd "$(dirname "$0")/.." && pwd)"
site_dir="$root_dir/.make-tmp/pages-site"

rm -rf "$site_dir"
mkdir -p "$site_dir"

cp "$root_dir/pages/index.html" "$site_dir/index.html"
cp "$root_dir/pages/applets.html" "$site_dir/applets.html"
cp "$root_dir/pages/robots.txt" "$site_dir/robots.txt"
touch "$site_dir/.nojekyll"

mkdir -p "$site_dir/ru/book" "$site_dir/ru/slides" "$site_dir/en/book" "$site_dir/en/slides" "$site_dir/shared/analytics" "$site_dir/shared/figures" "$site_dir/shared/styles"
cp -R "$root_dir/ru/book/_book/." "$site_dir/ru/book/"
cp -R "$root_dir/en/book/_book/." "$site_dir/en/book/"
cp -R "$root_dir/ru/slides/_site/." "$site_dir/ru/slides/"
cp -R "$root_dir/en/slides/_site/." "$site_dir/en/slides/"
cp -R "$root_dir/shared/analytics/." "$site_dir/shared/analytics/"
cp -R "$root_dir/shared/figures/." "$site_dir/shared/figures/"
cp -R "$root_dir/shared/styles/." "$site_dir/shared/styles/"
