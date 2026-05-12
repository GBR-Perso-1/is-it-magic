---
name: project-sync
description: >
  Sync files between sibling projects in a <Scope>.Applications/ folder.
  Resolves the target and direction from natural language, resolves files
  from session context and search, asks for confirmation, then merges or
  copies intelligently. Never stages or commits.
---

## Important rules

Read and follow all rules in [`../shared/_ux-rules.md`](../shared/_ux-rules.md).

## Input

`$ARGUMENTS` — a free-text sync intent, e.g.:
  "sync the splashscreen mechanism to project2"
  "bring NumberInput.vue in from the template project"
  "push *.vue to Perso/MyOtherApp"

If `$ARGUMENTS` is empty, use `AskUserQuestion` to ask the user what they want to sync and between which projects before proceeding.

## Phase 1 — Scope & Target Discovery

### Step 1.1: Resolve SCOPE_ROOT

- Derive SCOPE_ROOT as the parent directory of the current working directory (cwd)
- Example: cwd = `/workspace/Acme.Applications/Project1/` → SCOPE_ROOT = `/workspace/Acme.Applications/`
- Verify SCOPE_ROOT's directory name ends with `.Applications`
  - If it does: proceed silently
  - If it does not: warn "The parent directory '<name>' does not follow the <Name>.Applications naming convention — continuing anyway." then continue
- Check whether the user's argument contains an explicit scope name (e.g. "Perso" or "Perso.Applications")
  - If found: locate a sibling directory matching `<scope>.Applications` relative to SCOPE_ROOT's parent and use that as SCOPE_ROOT
  - If that named scope directory does not exist: stop with "Scope directory '<name>.Applications' not found. Verify the name and try again."

### Step 1.2: List candidate targets

- List all immediate subdirectories of SCOPE_ROOT, excluding the current project (cwd basename)
- If the candidate list is empty: stop with "No sibling projects found in '<SCOPE_ROOT>'. Nothing to sync."

### Step 1.3: Resolve target

- Inspect `$ARGUMENTS` for a target name or phrase (e.g. "to project2", "into the template", "from MyOtherApp")
- If a candidate name is clearly implied (case-insensitive substring match): select it and proceed to Phase 2 with a note showing the selected target
- If ambiguous or not mentioned: present the full candidate list via `AskUserQuestion` and ask the user to pick one
- If the resolved target directory does not exist on disk: stop with "Target directory '<path>' does not exist."

## Phase 2 — Direction Resolution

Analyse `$ARGUMENTS` for directional keywords:
- Keywords "to", "into", "push to", "sync to", "copy to" → SOURCE = current project; DESTINATION = target
- Keywords "from", "bring in from", "pull from", "sync from" → SOURCE = target; DESTINATION = current project

State the resolved direction: "Direction: <SOURCE_PATH> → <DESTINATION_PATH>"

If direction cannot be determined: ask once via `AskUserQuestion` with these options:
- "Push from current project to <target>" (current → target)
- "Pull from <target> into current project" (target → current)

The resolved direction is shown as part of the Phase 3 confirmation — not a separate prompt.

## Phase 3 — Intent & File Resolution

### Step 3.1: Classify the file argument

- Extract the file/concept portion from `$ARGUMENTS` (everything that is not a direction keyword or target name)
- **Glob pattern** (contains `*` or `?`): use `Glob` against the SOURCE project file tree, list all matching files
- **Specific filename** (e.g. `NumberInput.vue`, `UserService.ts`): use `Glob` to search SOURCE project for files matching that name, present resolved path(s)
- **Concept phrase** (everything else): proceed to Step 3.2

### Step 3.2: Concept-based resolution (concept phrases only)

Apply two signals in parallel:
- Signal A — Session context: scan the current conversation for files, paths, and component names mentioned or discussed that exist within the SOURCE project's directory
- Signal B — File search: use `Glob` and `Grep` to search the SOURCE project for filenames, import references, and content strings matching key nouns from the concept phrase
- Merge both signal lists, deduplicate by path, produce a candidate file list
- If the merged list is empty: stop with "No files could be resolved for '<concept>'. Please clarify — name specific files or describe the feature using terms visible in the codebase."

### Step 3.3: Present resolved file list for confirmation

Present via `AskUserQuestion`:
```
Sync plan:
  Direction: <SOURCE> → <DESTINATION>

  Files to sync:
    <relative-path-in-source>  — <one-line rationale>
    ...

Proceed?
```
Options:
1. "Proceed with all files (Recommended)"
2. "Remove some files from the list"
3. "Cancel"

If "Remove some files": ask the user to name the files to drop, remove them, re-present the final list with options "Confirm final list" or "Cancel".
If the final list is empty after removals: stop with "No files remaining. Sync cancelled."

## Phase 4 — Sync Execution

### Step 4.1: Determine action per file

For each SOURCE file:
- Compute the corresponding DESTINATION path by replacing the SOURCE root prefix with the DESTINATION root prefix, preserving the relative sub-path
- Check whether the DESTINATION file exists:
  - Exists → AI Merge (Step 4.2)
  - Does not exist → Copy (Step 4.3)

### Step 4.2: AI Merge (file exists in destination)

- Read both the SOURCE file and the DESTINATION file in full
- Perform an AI merge: bring in all changes from SOURCE while preserving destination-specific additions, domain-specific identifiers, and any logic unique to the DESTINATION project (different component names, namespaces, local config values)
- Write the merged result to the DESTINATION path
- Record action as "merged — review recommended"

### Step 4.3: Copy (file does not exist in destination)

- Copy the SOURCE file to the DESTINATION path verbatim, creating any intermediate directories that do not exist
- Record action as "copied"

### Step 4.4: Never stage or commit

- Do not run `git add`, `git commit`, or any staging command at any point

## Phase 5 — Post-apply Summary

Print:
```
Sync complete — <SOURCE_BASENAME> → <DESTINATION_BASENAME>

| File | Action | Review |
|------|--------|--------|
| <relative dest path> | copied / merged | — / Recommended |
...

Run `git diff` in <DESTINATION_PATH> to review all changes before committing.
```

## Guardrails

- Never stage, commit, or push any file.
- Never create a directory at SCOPE_ROOT or target level — only create intermediate directories within an already-existing target project when copying a file into a subdirectory that doesn't exist yet.
- Never overwrite a destination file without an AI merge step — if a destination file exists, always merge rather than overwrite blindly.
- Never proceed with an empty file list.
- Always confirm with the user before any file is written (Phase 3 gate).

## Conversation Style

- Be direct and specific — show paths, not descriptions.
- Keep rationale lines in the file list to one sentence maximum.
- Use British English throughout.
