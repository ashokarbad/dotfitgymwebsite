# Deploying this site on GitHub Pages

## The problem
GitHub Pages only looks for `index.html` in one of two places: the **root**
of the branch, or a folder literally named **`docs`**. Your `index.html` was
sitting inside a folder called `site`, and GitHub Pages doesn't know to look
there — so it never found it.

## The fix
The `site` folder has been renamed to `docs` in this package. Nothing inside
it changed — every link, stylesheet and script reference in this project is
a *relative* path (`assets/css/dotfit.css`, `about.html`, and so on, never
`/assets/...`), so renaming the parent folder doesn't break anything. I
checked every `.html`, `.css` and `.js` file for absolute paths before doing
this — there were none.

### Steps
1. Unzip this package. You'll have `docs/`, `content/`, `tools/` and this
   README at the top level.
2. Push the whole thing to your GitHub repository — `docs/`, `content/`,
   `tools/`, all of it. (`content/` and `tools/` are your editing workflow;
   GitHub Pages will simply ignore them since they're not the source folder.)
3. On GitHub: **Settings → Pages → Build and deployment → Source** →
   "Deploy from a branch". **Branch** → your default branch (usually `main`).
   **Folder** → select **`/docs`** from the dropdown (not `/ (root)`).
4. Save. GitHub will build and give you a URL, usually
   `https://<username>.github.io/<repo-name>/` — it can take a minute or two
   the first time.

### One more thing already handled
`docs/.nojekyll` is included. GitHub Pages runs everything through Jekyll by
default, and Jekyll silently ignores any file or folder starting with an
underscore — which includes `_redirects` in this project (a Netlify-specific
file, harmless here but Jekyll doesn't know that). The empty `.nojekyll`
file tells GitHub Pages to skip Jekyll entirely and serve the files exactly
as they are. Without it you likely wouldn't notice a problem immediately,
but it's the kind of thing that causes a confusing partial-break later.

## If you'd rather not use a `/docs` folder
Some people prefer the site files sitting directly in the repo root with no
wrapper folder — for instance if this repo is dedicated entirely to the
website. In that case:

1. Move everything *inside* `docs/` up to the repository root instead
   (so `index.html`, `assets/`, `about.html` etc. sit next to `content/`
   and `tools/`, not inside a `docs` folder).
2. Settings → Pages → Folder → **`/ (root)`** instead of `/docs`.

Both approaches work identically — pick whichever keeps your repo tidier.
There's no functional difference; GitHub Pages doesn't care which one you
use, and the folder name never shows up in the live URL either way.

## Local content-editing workflow doesn't change
`content/team.json`, `content/services.json` and so on, plus the scripts in
`tools/`, still work exactly as documented in
`README-GALLERY-AND-SELECTOR.md`. Run them from the folder containing
`docs/` (or wherever `site/` used to be), same as before — only the output
folder's name changed, not how you generate it.
