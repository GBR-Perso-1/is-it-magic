# Vue App (Vue 3 / TypeScript) — Conventions

> How a Vue 3 front-end is organised, so changes land in the right place.
> Guidance for planning and implementation — not enforced line-rules.

## Components

- Composition API only (no Options API); `<script setup lang="ts">`.
- One component per file; props defined inline with `defineProps<{ ... }>()` — no separate interface.
- Components: PascalCase (`UserCard.vue`), PascalCase in templates too (`<PageLayout>` not `<page-layout>`).
- Split a component once it grows past ~200–300 lines — extract logic into a `useXxx.ts` composable.

## State (Pinia)

- One store per domain concern (`useUserStore`, `useCartStore`).
- Async operations (API calls) live in **actions**; derived state in **getters**.
- Never mutate state outside an action.

## Composables & API

- API calls live in composables (`useUserApi`) and return a `{ data, loading, error }` shape.
- Base URL comes from env config — never hardcoded.

## File organisation

- `views/` — route-level pages
- `components/` — reusable UI components
- `composables/` — shared logic (`useXxx`)
- `stores/` — Pinia stores
- `types/` — TypeScript interfaces/types
- `api/` — API client wrappers

## Component & composable placement

Code starts close to where it is used and migrates outward as reuse grows:

1. **Page-scoped** — lives next to the page that uses it
2. **Feature-scoped** — shared by nearby pages → move to the nearest common ancestor
3. **App-scoped** — used across feature paths
4. **Generic** — truly reusable, no business logic

## Styling

- Prefer the project's component library over hand-rolled CSS.
- Use design tokens / CSS variables, not hardcoded colours — theming and dark mode depend on it.
