# make_redirects_to_archive.py
# Creates /<slug>/index.html in your main repo that redirects to /archive/<slug>.html
# Pulls <title> from the target page in the archive for cleaner SEO.
#
# Run this from the root of your main repo (spiritualblues.github.io):
#   python make_redirects_to_archive.py

import os
import re
from pathlib import Path
from html import unescape

# --- CONFIG ---
ARCHIVE_SOURCE = "../archive"        # relative path from main repo to your archive repo
PUBLIC_BASE   = "https://spi.blue"   # your domain
EXCLUDE_FILES = {"index.html", "404.html"}  # archive pages to skip
# -------------


def find_title(html_text, fallback):
    """
    Extract <title> ... </title> (robust-ish), else use fallback.
    """
    m = re.search(r"<title[^>]*>(.*?)</title>", html_text, flags=re.IGNORECASE | re.DOTALL)
    if m:
        # Clean whitespace and entities
        title = unescape(re.sub(r"\s+", " ", m.group(1)).strip())
        # Trim overly long titles just in case
        return title[:140] if len(title) > 140 else title
    return fallback


def main():
    archive_path = Path(ARCHIVE_SOURCE).resolve()
    if not archive_path.exists():
        raise SystemExit(f"Archive path not found: {archive_path}")

    # Collect top-level .html files in archive
    html_files = [p for p in archive_path.iterdir() if p.is_file() and p.suffix.lower() == ".html" and p.name not in EXCLUDE_FILES]
    html_files.sort()

    created = 0
    for page in html_files:
        slug = page.stem  # e.g., 'my-post' from 'my-post.html'
        target_rel = f"/archive/{page.name}"
        target_abs = f"{PUBLIC_BASE}{target_rel}"

        # Read the archive page to extract <title>
        try:
            text = page.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            text = ""
        title = find_title(text, fallback=slug.replace("-", " ").title())

        # Make /slug/index.html in the MAIN REPO working directory
        out_dir = Path(slug)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file = out_dir / "index.html"

        # Minimal, fast redirect + canonical + accessibility fallback
        html = f"""<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>{title}</title>
    <link rel="canonical" href="{target_abs}">
    <meta http-equiv="refresh" content="0; url={target_rel}">
    <meta name="robots" content="noarchive">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script>location.replace("{target_rel}");</script>
  </head>
  <body>
    <p>If you are not redirected, <a href="{target_rel}">click here</a>.</p>
  </body>
</html>
"""
        out_file.write_text(html, encoding="utf-8")
        created += 1

    print(f"✅ Created {created} redirect stub(s) in this repo.")
    print("   Each /<slug>/index.html points to /archive/<slug>.html")


if __name__ == "__main__":
    main()
