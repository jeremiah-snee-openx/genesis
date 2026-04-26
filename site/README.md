# Genesis doc site

Astro Starlight site for Genesis. Deploys to <https://danielmeppiel.github.io/genesis>.

## Stack

- [Astro](https://astro.build) 5 + [Starlight](https://starlight.astro.build) 0.36
- [astro-mermaid](https://github.com/robatipoor/astro-mermaid) for diagrams (client-side render)
- Pagefind search (Starlight default)
- npm

Stack rationale: see `WIP/doc-site/STACK.md`. Sample-validated quirks (notably the `@astrojs/sitemap` 3.6.1 pin in `package.json` `overrides`): see `WIP/doc-site/SAMPLE.md`.

## Local development

```bash
cd site
npm install
npm run dev
```

Astro will print the dev URL (default `http://localhost:4321/genesis/`).

## Build

```bash
npm run build
```

Output goes to `site/dist/`. Pagefind search index is generated at the end of the build.

## Preview the production build

```bash
npm run preview
```

## Deploy

Pushes to `main` that touch `site/**` or `.github/workflows/pages.yml` trigger the GitHub Pages workflow at `.github/workflows/pages.yml`. The workflow uses `withastro/action@v3` (build) + `actions/deploy-pages@v4` (publish).

### One-time GitHub setup

1. **Settings -> Pages -> Source: "GitHub Actions"** (not "Deploy from a branch").
2. **Settings -> Actions -> General -> Workflow permissions:** confirm `pages: write` and `id-token: write` are allowed (default).

No `gh-pages` branch is needed -- the action uses Pages' native artifact upload.

## Site structure

```
site/
|-- astro.config.mjs            # site, base, sidebar, integrations
|-- package.json                # @astrojs/sitemap pin lives here
|-- src/
|   |-- content.config.ts       # Starlight 0.36+ content collection
|   |-- assets/
|   |   `-- logo.svg
|   `-- content/
|       `-- docs/
|           |-- index.mdx       # landing page (splash)
|           |-- guides/
|           |   |-- quick-start.md
|           |   `-- install.md
|           `-- reference/
|               |-- primitives/  (index + 6 detail pages)
|               `-- harnesses/   (index + 6 detail pages)
`-- public/                      # static assets (favicon, etc.)
```

## Adding pages

1. Add the markdown / mdx file under `src/content/docs/<path>.md`.
2. Add the entry to the `sidebar` in `astro.config.mjs` (we use explicit sidebar, not autogen).
3. Use absolute paths in cross-links: `/genesis/reference/primitives/`. The leading `/genesis` matches the configured `base`.
4. Run `npm run build` to verify the page builds and links resolve.

## Information architecture

Full IA + page list: `WIP/doc-site/IA.md` (22 pages total). The foundation layer (this scaffold) ships:

- 1 landing page
- 2 guides (Quick start, Install)
- 13 reference pages (1 primitives index + 6 primitive details + 1 harnesses index + 6 harness details)

The catalogue agent will add the remaining pages: design patterns (B1-B23), architectural patterns (A1-A10), refactor patterns (R1-R4), pattern tradeoffs, composition substrate, architect's loop, runtime affordances, harness adapters (deeper than the harness setup pages here), trigger surface, APM adapter, mermaid conventions, examples gallery (5 detail pages + index), and the Resources page for the external corpus.

## Conventions

- **All cross-links use absolute paths starting with `/genesis/`** so they resolve under the project sub-path.
- **No emoji or non-ASCII characters in content** (cross-platform safety; tooling pipelines downstream still expect ASCII).
- **Mermaid diagrams** go in fenced ```` ```mermaid ```` blocks; they render client-side.
- **Page frontmatter** uses Starlight's standard fields (`title`, `description`, `sidebar.order`, `sidebar.label`, `sidebar.badge`).
