# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Hand-written static HTML/CSS portfolio: no build step, package manager, or tests. GitHub Pages (legacy Jekyll build) serves the root of `main` at https://arnavinator.github.io/portfolio/, so **pushing to `main` publishes the site**.

## Preview

`./serve.py [port]` serves at http://localhost:8000 and opens a browser tab (`--no-open` to skip). Opening pages via `file://` breaks the nav dropdown (it's loaded with `fetch()`), and plain `python3 -m http.server` lacks the Range support Safari needs to play the videos.

## How the HTML fits together

- `index.html` is a hero plus a "Selected Work" grid of cards (looping preview video + title, linking to `<project>/index.html`). `about.html` is the bio. Each project folder holds its `index.html` and its media, referenced as `./file`.
- No templating: every page carries its own copy of the CDN includes (Bootstrap 5, MathJax 3), navbar, Back-to-Top button + script, and footer. Changes to these must be repeated in every page. Project pages reach root files via `../`.
- The one shared fragment is the Selected Work dropdown list, which each page `fetch()`es into `#dropdown-content`. Root pages load `dropdown.html` (`./` links) and project pages load `dropdownL2.html` (`../` links), so keep both in sync. The menu opens on CSS `:hover` (in `style.css`), not Bootstrap JS.
- `style.css` is the only stylesheet (fonts, `#c20f0f` red theme, nav/hero/footer/back-to-top). Everything else is Bootstrap utility classes and inline styles.
- Project pages share one template: a `hero-section-proj` banner (title, subtitle, skills), then Overview, Table of Contents, and `<section id=…>` blocks that each start with `<hr>`. MathJax treats `$…$` and `$$…$$` as math, so write a literal dollar sign as `\$`.

To add a project, copy an existing project's `index.html` into a new folder, then add a card to the `index.html` grid and an entry to both dropdown files.

## Gotchas

- GitHub Pages paths are case-sensitive but macOS isn't, so local preview won't catch a mis-cased link (e.g. `tiny_LM`).
- Jekyll doesn't publish files or folders whose names start with `_` or `.`.
