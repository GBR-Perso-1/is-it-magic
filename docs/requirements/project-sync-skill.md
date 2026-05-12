# `project-sync` — Requirements

## Vision

A general-purpose, intent-driven sync skill that lets a developer push or pull any set of files between sibling projects within a `<Scope>.Applications/` folder hierarchy. Unlike `project-sync-template` (which is Rise-specific and unidirectional), this skill works with any project type, infers both target and direction from natural language, uses the active conversation session to resolve vague concepts into concrete files, and always asks for confirmation before touching anything.

---

## Epics

### Epic 1: Scope & Target Discovery

**Goal**: The user should never need to type a full path. The skill navigates the folder hierarchy automatically based on where the user is sitting and what they say.

#### Requirements

- **REQ-1.1**: When invoked, the skill resolves `SCOPE_ROOT` by going up one level from the current working directory (e.g., sitting in `Rise.Applications/Project1/` → scope root is `Rise.Applications/`).
- **REQ-1.2**: The skill lists all immediate sub-directories of `SCOPE_ROOT` as candidate targets, excluding the current project.
- **REQ-1.3**: If the user's argument names or clearly implies a target (e.g., "into project2", "to the template"), the skill selects that candidate and asks for confirmation rather than presenting the full list.
- **REQ-1.4**: If the target is ambiguous or not mentioned, the skill presents the full sibling list and asks the user to pick.
- **REQ-1.5**: If the user specifies a scope name (e.g., "Perso" or "Perso.Applications"), the skill resolves `SCOPE_ROOT` from that name instead of the current project's parent. It navigates to the named scope folder and applies the same discovery logic there.
- **REQ-1.6**: If the resolved `SCOPE_ROOT` or target directory does not exist, the skill stops with a clear error message rather than creating directories.

#### Decisions & Assumptions

- Scope folder naming convention is `<Name>.Applications` — the skill matches by the `.Applications` suffix to confirm it has found a scope folder. If the parent folder doesn't match this pattern, the skill warns but continues.
- "Template" as a target name is treated like any other sibling — no special meaning baked in.

---

### Epic 2: Intent & File Resolution

**Goal**: The user can say something as vague as "the splashscreen mechanism" or as specific as "NumberInput.vue" and the skill correctly resolves which files to sync.

#### Requirements

- **REQ-2.1**: For **specific file targets** (e.g., `NumberInput.vue`, `UserService.ts`), the skill searches for the file by name in the source project and presents the resolved path for confirmation.
- **REQ-2.2**: For **concept-based targets** (e.g., "the splashscreen mechanism", "the access rights feature"), the skill uses two signals to resolve files:
  1. **Session context** — files, topics, or paths mentioned or discussed in the current conversation.
  2. **File search** — grep/glob across the source project for names, imports, or content related to the concept.
- **REQ-2.3**: The skill always presents the resolved file list to the user before any sync operation, showing source paths and a one-line rationale for each file's inclusion.
- **REQ-2.4**: The user can remove files from the resolved list before confirming. The skill re-presents the final list after any adjustments.
- **REQ-2.5**: If no files can be resolved for a given concept, the skill reports this clearly and asks the user to clarify rather than proceeding with an empty set.

#### Decisions & Assumptions

- "Session context" means the current Claude Code conversation only — no persistent memory is used for file resolution.
- If the user's argument is a file glob (e.g., `*.vue`), it is treated as a pattern against the source project's file tree.

---

### Epic 3: Direction Resolution

**Goal**: The user signals direction through natural language; the skill infers it without flags.

#### Requirements

- **REQ-3.1**: The skill infers sync direction from the user's phrasing:
  - "sync X **to** [target]" or "push X **to** [target]" → current project is **source**, target is **destination**
  - "sync X **from** [target]" or "bring in X **from** [target]" or "sync [target]'s X **into this project**" → target is **source**, current project is **destination**
- **REQ-3.2**: If direction cannot be inferred with confidence, the skill asks one clarifying question before resolving files.
- **REQ-3.3**: The resolved direction (SOURCE → DESTINATION) is shown to the user as part of the confirmation step (Epic 2), not as a separate prompt.

---

### Epic 4: Sync Execution

**Goal**: Files are merged intelligently, never overwritten blindly, and the user always has a clear picture of what changed.

#### Requirements

- **REQ-4.1**: For files that **exist in the destination**: the skill uses AI merge — source changes are brought in while destination-specific additions and domain logic are preserved. The merged result is flagged for review.
- **REQ-4.2**: For files that **do not exist in the destination**: the file is copied from source to destination as-is.
- **REQ-4.3**: The skill never stages or commits any changes.
- **REQ-4.4**: After applying all changes, the skill presents a post-apply summary table: file path, action taken (copied / merged), and whether manual review is recommended.
- **REQ-4.5**: The summary ends with a reminder to run `git diff` to review all changes before committing.

---

## Priorities

| Priority | Epic / Requirement | Rationale |
|---|---|---|
| 1 | Epic 1 — Discovery | Without correct scope/target resolution, nothing else works |
| 2 | Epic 3 — Direction | Must know which way files flow before resolving them |
| 3 | Epic 2 — Intent & File Resolution | The core differentiator vs. existing tools |
| 4 | Epic 4 — Sync Execution | Builds directly on the existing project-sync-template merge patterns |

---

## Out of Scope

- Rise-specific file classifications (Core / Feature-gated / Composite) — handled by `project-sync-template` in the Rise plugin
- Dependency compatibility checks (csproj / package.json diffing) — Rise-specific concern
- Committing or staging changes
- Syncing across machines or remote repositories
- Multi-hop sync (A → B → C in one command)
