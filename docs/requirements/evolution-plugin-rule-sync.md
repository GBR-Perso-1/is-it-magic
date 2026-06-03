# is-it-magic + rise-dev-plugin — Rule Sync Requirements

> **Superseded (2026-06-03).** The standalone `rules-sync` skill (Epic 1) and the standalone `rules-sync-project` skill (Epic 2) described below have been merged into single, richer skills:
>
> - **Epic 1 → `devbox-init`** (in `is-it-magic`): syncs all plugin rules to `~/.claude/rules/` **and** enables favoured language LSPs in `~/.claude/settings.json`. Replaces the standalone `rules-sync` skill.
> - **Epic 2 → `project-init`** (in `it--claude-rise-plugin`): bootstraps or refreshes a project's `.claude/` directory — rule sync, `CLAUDE.md`, `project-context.md`, and per-stack LSP settings. Replaces the standalone `rules-sync-project` skill.
>
> All SB-* shared sync behaviours described below remain in force; they are implemented by both new skills. The original requirements are retained below for historical context.



## Vision

Both plugins bundle rule files but Claude Code has no native way to ship them into the directories it loads (`~/.claude/rules/`, `<project>/.claude/rules/`). Each plugin will provide a **dedicated sync skill** that copies its bundled rules into the right directory using one **shared, agreed behaviour**. The perso plugin syncs **globally** (rules apply everywhere); the company plugin syncs **into the current project** (rules apply only in that repo, absent elsewhere). This gives the desired composition: generic rules always on, company rules conditional-by-location.

## Shared Sync Behaviour *(applies to both plugins' sync skills)*

- **SB-1**: Copies **all** rule files from the plugin's bundled `rules/` directory into the target rules directory.
- **SB-2**: Creates the target directory if it does not exist.
- **SB-3**: **Always overwrites** existing rule files with the bundled version — the plugin is the source of truth. No merge, no prompt.
- **SB-4**: **Idempotent** — re-running produces the same result; safe to re-run any time to refresh after a plugin update. (Because overwrite is unconditional, there is no separate "first run" vs "refresh" mode.)
- **SB-5**: Preserves each rule file's `paths:` frontmatter unchanged, so Claude Code's native scoping keeps working.
- **SB-6**: Reports a summary listing which rule files were written.
- **SB-7**: Touches only the target rule files — never stages, commits, or modifies anything else.

## Epics

### Epic 1: Perso plugin — global rule sync

**Goal**: A user can install the perso plugin and, with one command, have its generic rules loaded in every project on the machine.

#### Requirements

- **REQ-1.1**: The perso plugin (`is-it-magic`) provides a dedicated skill that syncs its bundled rules into `~/.claude/rules/`, following all SB-* behaviours.
- **REQ-1.2**: Intended to be run **once per machine** after install, and re-run to refresh after the plugin updates its rules.
- **REQ-1.3**: All bundled rules are synced (`general.md` plus the language rules). Language rules retain their `paths:` frontmatter, so they stay dormant until a matching file is in context.
- **REQ-1.4**: After syncing, the rules load globally in every session/project, composing with any project-level rules present.

#### Decisions & Assumptions

- Always-overwrite means local hand-edits to files in `~/.claude/rules/` are **not** preserved — users edit the rule *source* in the plugin, not the synced copies (mirrors the existing `project-init` guardrail "never edit synced rule files").

### Epic 2: Company plugin — project-scoped rule sync

**Goal**: A user working inside a company project can, with one command, install the company's rules into that project so they apply there and nowhere else.

#### Requirements

- **REQ-2.1**: The company plugin (`rise-dev-plugin`) provides a dedicated skill that syncs its bundled rules into the **current project's** `<project>/.claude/rules/`, following all SB-* behaviours.
- **REQ-2.2**: Because the rules land in the project directory, they apply **only** in that repo and are absent in non-company projects — achieving conditional scoping by location, with no repo-identity detection needed.
- **REQ-2.3**: Intended to be run **once per company repo**, and re-run to refresh.

#### Decisions & Assumptions

- **Prerequisite**: the company plugin has no `rules/` directory today. Authoring/migrating the company rule content into the plugin's `rules/` dir is a dependency for this epic (tracked separately — see Out of Scope).

## Priorities

| Priority | Epic / Requirement | Rationale |
| -------- | ------------------ | --------- |
| 1 | Shared Sync Behaviour + Epic 1 (perso) | Proven pattern, immediate value, no external dependency; once-per-machine. |
| 2 | Epic 2 (company) | Same behaviour, but blocked on company rule content existing in the plugin first. |

## Out of Scope

- **`SessionStart` hook / automatic syncing** — deferred (the decision report's Option 3); manual run required for v1.
- **Authoring the company rule content** — a separate effort; this document covers the *sync capability*, not which company rules to write.
- **Orphan/stale-rule pruning** — if the plugin later removes a bundled rule, the sync does not delete previously-synced copies in v1. Revisit if stale rules become a problem.
- **Repo-identity runtime detection** (git remote/name) — not used; scoping is by file location and `paths:` globs only.
- **Merge/conflict resolution** of locally edited synced files — excluded by the always-overwrite decision.

## Delivery Phases

| Phase | Scope | Repo affected |
| ----- | ----- | ------------- |
| 1 | Shared behaviour defined + perso global sync skill (Epic 1) | `is-it-magic` |
| 2 | Company rule content bundled into a `rules/` dir + company project sync skill (Epic 2) | `it--claude-rise-plugin` |
