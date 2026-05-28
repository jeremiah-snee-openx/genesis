// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import mermaid from 'astro-mermaid';

// Production config for the Genesis doc site.
// Deploys to https://danielmeppiel.github.io/genesis (project sub-path).
// Stack decisions: WIP/doc-site/STACK.md.
// Sample-validated quirks: WIP/doc-site/SAMPLE.md (notably the
// @astrojs/sitemap pin in package.json `overrides`).
export default defineConfig({
  site: 'https://danielmeppiel.github.io',
  base: '/genesis',
  integrations: [
    // astro-mermaid must be registered BEFORE starlight per its README.
    mermaid({
      theme: 'default',
      autoTheme: true,
    }),
    starlight({
      title: 'Genesis',
      description:
        'Markdown that steers an LLM is code. Design it before you write it.',
      logo: {
        src: './src/assets/logo.svg',
        alt: 'Genesis',
      },
      social: [
        {
          icon: 'github',
          label: 'GitHub',
          href: 'https://github.com/danielmeppiel/genesis',
        },
      ],
      editLink: {
        baseUrl:
          'https://github.com/danielmeppiel/genesis/edit/main/site/',
      },
      lastUpdated: true,
      sidebar: [
        {
          label: 'Guides',
          items: [
            { label: 'Quick start', link: '/guides/quick-start/' },
            { label: 'Install', link: '/guides/install/' },
          ],
        },
        {
          label: 'Reference',
          items: [
            {
              label: 'Patterns',
              items: [
                { label: 'Catalogue', link: '/reference/patterns/' },
                {
                  label: 'Architectural (A1-A10)',
                  link: '/reference/patterns/architectural/',
                },
                {
                  label: 'Design (C/S/B)',
                  link: '/reference/patterns/design/',
                },
                {
                  label: 'Refactor (R1-R4)',
                  link: '/reference/patterns/refactor/',
                },
                {
                  label: 'A1. PANEL',
                  link: '/reference/patterns/a1-panel/',
                },
                {
                  label: 'A10. GOVERNED OUTER LOOP',
                  link: '/reference/patterns/a10-governed-outer-loop/',
                },
                {
                  label: 'B8. ATTENTION ANCHOR',
                  link: '/reference/patterns/b8-attention-anchor/',
                },
              ],
            },
            {
              label: 'Primitives',
              items: [
                { label: 'Overview', link: '/reference/primitives/' },
                {
                  label: 'Persona Scoping File',
                  link: '/reference/primitives/persona-scoping-file/',
                },
                {
                  label: 'Module Entrypoint',
                  link: '/reference/primitives/module-entrypoint/',
                },
                {
                  label: 'Scope-Attached Rule File',
                  link: '/reference/primitives/scope-attached-rule-file/',
                },
                {
                  label: 'Child-Thread Spawn',
                  link: '/reference/primitives/child-thread-spawn/',
                },
                {
                  label: 'Trigger Orchestrator',
                  link: '/reference/primitives/trigger-orchestrator/',
                },
                {
                  label: 'Plan Persistence',
                  link: '/reference/primitives/plan-persistence/',
                },
              ],
            },
            {
              label: 'Token Economics',
              items: [
                {
                  label: 'Overview',
                  link: '/reference/token-economics/',
                },
                {
                  label: 'Operator stance & cap',
                  link: '/reference/token-economics/stance-and-cap/',
                },
                {
                  label: 'Cost projection artifact',
                  link: '/reference/token-economics/cost-projection/',
                },
                {
                  label: 'Cost patterns',
                  link: '/reference/token-economics/patterns/',
                },
              ],
            },
            {
              label: 'Harnesses',
              items: [
                { label: 'Overview', link: '/reference/harnesses/' },
                {
                  label: 'GitHub Copilot',
                  link: '/reference/harnesses/copilot/',
                },
                {
                  label: 'Claude Code',
                  link: '/reference/harnesses/claude-code/',
                },
                { label: 'Cursor', link: '/reference/harnesses/cursor/' },
                { label: 'Codex', link: '/reference/harnesses/codex/' },
                {
                  label: 'OpenCode',
                  link: '/reference/harnesses/opencode/',
                },
                { label: 'Gemini', link: '/reference/harnesses/gemini/' },
              ],
            },
          ],
        },
        {
          label: 'Resources',
          items: [
            { label: 'Overview', link: '/resources/' },
            {
              label: 'Examples',
              items: [
                { label: 'Gallery', link: '/resources/examples/' },
                {
                  label: '01. README iteration',
                  link: '/resources/examples/01-readme-iteration/',
                },
                {
                  label: '02. Review panel architecture',
                  link: '/resources/examples/02-review-panel-architecture/',
                },
                {
                  label: '03. Release notes (single skill)',
                  link: '/resources/examples/03-release-notes-single-skill/',
                },
                {
                  label: '04. PR review (advisory)',
                  link: '/resources/examples/04-pr-review-advisory/',
                },
                {
                  label: '05. PR review (verdict)',
                  link: '/resources/examples/05-pr-review-verdict/',
                },
                {
                  label: '06. Cost-aware panel',
                  link: '/resources/examples/06-cost-aware-panel/',
                },
              ],
            },
            {
              label: 'External corpus',
              link: '/resources/external-corpus/',
            },
          ],
        },
      ],
    }),
  ],
});
