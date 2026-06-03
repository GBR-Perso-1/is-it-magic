---
paths:
  - "app/**"
---

# Frontend App Architecture Rules — Extended (pending merge into `_app-archi.md`)

> **Holding file.** Extracted from `rules/app-lang.md` (now `typescript-lang.md`) when that rule was
> trimmed to language-only concerns. Merge into `_app-archi.md`, rewire the consumers
> (`project-implement` / `architect` / `developer` to load the archi doc), then delete this file.

## Component Structure

- Composition API only (no Options API)
- Script setup syntax: `<script setup lang="ts">`
- One component per file
- Props defined inline with `defineProps<{ ... }>()` — no separate interface

## Naming (Vue)

- Components: PascalCase (`PropertyCard.vue`), PascalCase in templates too (`<PageLayout>` not `<page-layout>`)
- Composables: camelCase with `use` prefix (`usePropertyApi.ts`)
- Stores: camelCase with `use` prefix (`usePropertyStore.ts`)

## Code Style (Vue / Quasar / stack)

- Axios only — never `fetch()`
- Quasar components preferred over custom CSS
- Never add raw CSS outside the SCSS files — use Quasar utilities or the SCSS files
- Split components at 200–300 lines — extract to `useXxx.ts` composable
- CSS variables (`--q-primary`, etc.) not hardcoded colours — dark mode depends on it
- Never use raw `rgba()` — define a palette variable in `:root` first, then reference via `var()`
- `<prefix>-styles.scss` = shared org/project design system (e.g. `ekla-styles.scss` — prefix matches the project prefix); `app-styles.scss` = app-specific only
