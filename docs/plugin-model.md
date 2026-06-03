# Plugin Model — Direction & Where Things Belong

> Source of truth for how the plugins are structured. Every plugin's `CLAUDE.md` points here. Read this to decide where any skill, agent, or rule belongs.

## The layered model

The plugins follow a **base + specialized** layering, along two axes:

| Axis | Base | Specialized |
|---|---|---|
| **Purpose** | General — how I work on *any* project | Specific — one company, stack, or philosophy |
| **Install** | User-level (`~/.claude`), always present | Per-project, only where it fits |

## The base — `is-it-magic`

My broad, general-purpose toolkit — the way I work regardless of stack, company, or ecosystem. General skills, agents, and rules.

- Installed **user-level (`~/.claude`)** — present in every session, on every project.
- The foundation everything else builds on.
- Stays **clean and universal**: nothing here may assume a particular company, tenant, repo, or tech stack (generic, portable tool preferences are fine — see the litmus test).

## Specialized plugins (layered on top of the base)

Each one narrows the base to a specific world. The scoping axis is open:

- **Company-scoped** — e.g. `rise-plugin`: the conventions, infra, and tooling of a specific organisation.
- **Ecosystem/stack-scoped** — e.g. `enterprise-grade-app-plugin`: a proven stack and the philosophy that goes with it (.NET/C# clean-architecture API + Vue front end, etc.).

A specialized plugin is **not necessarily tied to a company** — its identity is the *world* it targets (a company, a stack, a philosophy). A company may map onto one, but so can a pure tech-stack philosophy.

- Installed **per-project** — only the specialized plugins that fit the project in front of me are enabled for it.
- Each **owns its own specifics** and **composes on top of the base**.
- Several can be installed at once alongside the base.

## The litmus test

> **How I work, everywhere → base (`is-it-magic`).**
> **Specific to a company, a stack, or a philosophy → that specialized plugin.**

If a skill/agent/rule assumes a particular org, tenant, repo, company/ecosystem-specific name (a product, resource, or prefix *value*), or an assembled-for-a-purpose tech stack (code stack + repo layout), it belongs in a specialized plugin — not the base.

**Tooling nuance.** A rule may be *about* a specific tool (Terraform, Docker, a test runner) and still belong in the base — provided it only encodes a generic, portable *preference* for using that tool (style, naming discipline, structure) and carries **no** ecosystem specifics: no company product/resource names, no org module layouts. (Provider-specific conventions are governed separately — see *Cloud substrate* below.) The tool being named doesn't make a rule specialized; *ecosystem-specific usage* does. These rules are `paths:`-scoped so they only load inside that tool's files. The moment a rule names a tenant, company resource, or org convention, it moves to the specialized plugin.

**Cloud substrate.** A single cloud provider you deploy to on *every* project is part of your universal substrate, not a per-project choice — so provider-specific conventions (e.g. an Azure resource-naming scheme) may live in the base, provided they are **parameterised, not hardcoded**: the *scheme* is generic, while company/project-specific values (prefixes, product names, resource names) are resolved per-project (e.g. from `project-context.md`) or live in the specialized plugin. This carve-out is deliberately narrow — it covers the one cloud you universally target, *not* code stacks (.NET/Node) or repo layouts (`api/app`), which genuinely vary per project and stay in specialized plugins.

## Cross-plugin note

`${CLAUDE_PLUGIN_ROOT}` and `@`-imports resolve **within** a plugin, not across plugin boundaries. So specialized plugins reference this document as a plain human-readable pointer (path + name), not a hard import.
