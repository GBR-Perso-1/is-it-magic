---
name: locate-project
description: >
  Resolve a project name to its local path and git metadata.
  Accepts a natural-language name (e.g. "Justifi", "kyriba bi", "estate hub")
  and returns the absolute path, scope, remote URL, branch, and confidence level.
---

## Important rules

Read and follow all rules in [`../shared/_ux-rules.md`](../shared/_ux-rules.md).

## Input

`$ARGUMENTS` — a natural-language project name, e.g. `Justifi`, `the wealth pilot project`, `kyriba bi`.

If `$ARGUMENTS` is empty, ask via `AskUserQuestion`:
- Question: "Which project would you like to locate? Enter a name or partial name."
- Option: `I'll type it` (user provides free-text via the automatic Other input)

---

### Phase 1 — Run the locator agent

Spawn the agent defined in `${CLAUDE_PLUGIN_ROOT}/agents/project-locator.md`.

Prompt it with:

```
Locate project: <$ARGUMENTS>
```

Wait for the agent to return its result block.

---

### Phase 2 — Present result

### Single match — High confidence

Display the result payload directly. No confirmation needed.

### Single match — Medium or Low confidence

Display the result payload, then ask via `AskUserQuestion`:

- Question: "The locator found `<folder-name>` in `<scope>` with **<confidence>** confidence (`<rationale>`). Is this the right project?"
- Options:
  - `Yes — this is correct`
  - `No — search again with a different name`

If the user selects **"No"**: ask for a revised name and re-run Phase 1 with the new input.

### Multiple matches

Display the ranked match table from the agent result, then ask via `AskUserQuestion`:

- Question: "The name `<input>` matched multiple projects. Which one did you mean?"
- Options: one per match — label is `<folder-name> (<scope>)`, description is the rationale

### No match

Display the agent's no-match output verbatim and stop.

---

## Conversation Style

- Be direct — show paths and names, not descriptions.
- Use British English throughout.
