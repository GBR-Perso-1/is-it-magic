---
name: project-implement
description: >
  Implement a requirement or fix with configurable rigour.
  Four modes:
  no arg or "full" = architect → developer → test → review pipeline (default);
  "draft" = architect + developer, no test loop, no review (fast iteration / POC);
  "quick" = developer only, no architect, no test, no review (lightweight fix);
  "increment" = developer + test loop, no architect, no review (tested change to live code).
  Never commits — always leaves the user to review the diff.
---

## Important rules

Read and follow all rules in `${CLAUDE_PLUGIN_ROOT}/skills/shared/_ux-rules.md`.

## Input

`$ARGUMENTS` determines the mode and carries the requirement text:

| Value | Mode | Input treatment |
|---|---|---|
| Empty | Ask | Prompt for mode, then prompt for requirement |
| `full <text>` or `full` | **Full** | Treat remainder as the requirement; ask if blank |
| `draft <text>` or `draft` | **Draft** | Treat remainder as the requirement; ask if blank |
| `quick <text>` or `quick` | **Quick** | Treat remainder as the requirement; ask if blank |
| `increment <text>` or `increment` | **Increment** | Treat remainder as the requirement; ask if blank |

If `$ARGUMENTS` is a non-empty string that does not start with a recognised mode keyword, treat the entire string as the requirement and prompt for the mode.

---

## Phase 0 — Mode selection and input gathering

1. Parse `$ARGUMENTS`:
   - Extract the mode keyword if present (`full`, `draft`, `quick`, `increment`).
   - Extract the remainder as the requirement text (may be a path to a requirements document or an inline description).
2. If no mode keyword was found, ask via `AskUserQuestion`:
   - Question: "Which implementation mode?"
   - Options:
     - `full — architect → dev → test → review (Recommended)`
     - `draft — architect + dev only, no test or review`
     - `quick — dev only, no ceremony`
     - `increment — dev + test, no architect, no review (tested change to live code)`
3. If the requirement text is blank (regardless of mode), ask via `AskUserQuestion`:
   - Question: "What would you like to implement? Provide an inline description or a path to a requirements document."
   - Option: `I'll describe it`
4. If a file path was provided, read the file now.
5. Restate the requirement as a short implementation brief:
   - What needs to change and where (component, layer, or file if known)
   - Expected outcome
   - Any constraints or edge cases mentioned
6. Present the brief and confirm with the user via `AskUserQuestion`:
   - `Looks right — proceed` *(label this as Recommended)*
   - `Let me clarify`

---

## Full mode (default)

*Architect → developer → test loop → review loop*

### Phase 1 — Architecture (Architect Agent)

1. Spawn the agent defined in `${CLAUDE_PLUGIN_ROOT}/agents/architect.md`.
   - Pass it the full requirement text and instruct it to produce a concrete implementation plan.
   - The plan must include: affected files, new files to create, data model changes, API changes, UI changes, a step-by-step implementation order, and a `## Blocking Requirement Issues` section (containing either a list of blocking items or the single word `None`).
2. Inspect the architect's plan for the `## Blocking Requirement Issues` section:
   - **If the section contains `None`** (or is absent) → proceed directly to Phase 2. Do not ask the user to approve the plan.
   - **If the section lists one or more blocking issues** → present the plan and the blocking issues to the user, then ask via `AskUserQuestion`:
     - `I'll clarify — here are my answers` *(the user provides clarification via the free-text "Other" input)*
     - `Start over with different requirements`
     Relay the user's clarification answers to the architect agent via `SendMessage`, instructing it to revise the plan. Repeat step 2 until the section contains `None`.

### Phase 2 — Implementation (Developer Agent)

3. Spawn the agent defined in `${CLAUDE_PLUGIN_ROOT}/agents/developer.md`.
   - Pass it the **architecture plan** and the **original requirements**.
   - Instruct it to implement all changes described in the plan, then **run the project's test suite inline** before returning (using the project's own test command, detected from its toolchain). It should report which tests passed, failed, or were skipped — this is a quick smoke check, not a full test pass.
4. Wait for the developer agent to complete. Collect its summary of changes made and the inline test results.

### Phase 3 — Testing (Test Agent)

5. If the developer's inline test run from Phase 2 showed failures unrelated to missing test coverage (i.e. source bugs), pass the failures back to the **developer agent** via `SendMessage` to fix them before proceeding. Skip directly to Phase 4 if the inline run was clean.

6. Spawn the agent defined in `${CLAUDE_PLUGIN_ROOT}/agents/test-writer.md`.
   - Pass it: (1) the **original requirements**, (2) the **Test Strategy section** from the architect's plan.
   - The test-writer derives test scenarios from the requirements — not from what the developer coded.
7. Evaluate the test report:
   - **All pass** → proceed to Phase 4.
   - **Failures due to source bugs** → pass the failing test details back to the **developer agent** via `SendMessage` to fix. Then re-run Phase 3 (spawn a fresh test-writer agent).
   - **Maximum 2 iterations** of the dev↔test loop. If tests still fail after 2 rounds, present via `AskUserQuestion`:
     - `Continue iterating`
     - `Skip failing tests and proceed to review`
     - `Stop here — I'll fix manually`

### Phase 4 — Review (Quality + Design Agents)

8. **Relevance check** — decide whether the performance reviewer is needed:
    - If the change touches **executable code** (back-end logic, data access, or front-end logic) → **perf review applies**, spawn all three reviewers.
    - If the change is **docs/config-only** with no runtime code → **perf review skipped**, spawn quality + design only.

    (The performance reviewer is stack-aware — it reads the project's convention bundles to apply the relevant perf lens — so it self-limits when little applies.)

9. Spawn reviewers in parallel (two or three per the relevance check):
    - **Code-quality reviewer**: `${CLAUDE_PLUGIN_ROOT}/agents/reviewer-quality.md` — linting, style, rule compliance.
    - **Design reviewer**: `${CLAUDE_PLUGIN_ROOT}/agents/reviewer-design.md` — requirement coverage, architectural boundaries, abstraction quality, consistency.
    - **Performance reviewer** *(when runtime code changed)*: `${CLAUDE_PLUGIN_ROOT}/agents/reviewer-perf.md` — slow queries, N+1, unbounded loads, expensive loops, missing caching, front-end perf.

10. Collect all reports. Record which reviewers **passed** and which **flagged issues**. Present findings to the user.

11. Evaluate findings:
    - **No violations or warnings** → proceed to Phase 5.
    - **Implementation errors only** (code quality issues, bugs, style) → pass findings to the **developer agent** via `SendMessage` for corrections. Re-run Phase 3 (testing), then **re-run only the reviewers that previously flagged issues** — skip reviewers that already passed.
    - **Design errors** (wrong abstraction, domain boundary violation, requirement mismatch, missing functionality) → pass findings back to the **architect agent** via `SendMessage` to revise the plan. Re-run from Phase 2 with all reviewers reset.
    - **Maximum 2 iterations** of the full review loop. If issues persist, present via `AskUserQuestion`:
      - `Continue iterating`
      - `Accept current state — I'll handle remaining issues`
      - `Stop and roll back`

### Phase 5 — Done

12. Present a final summary to the user:
    - What was implemented (files created/modified)
    - Test results (pass/fail counts)
    - Review outcome (clean / accepted with notes)
13. Ask via `AskUserQuestion`:
    - `Commit these changes (Recommended)`
    - `I want to review the changes manually`

---

## Draft mode

*Architect + developer — no test loop, no review*

### Phase 1 — Architecture (Architect Agent)

1. Spawn the agent defined in `${CLAUDE_PLUGIN_ROOT}/agents/architect.md`.
   - Pass it the full requirement text and instruct it to produce a concrete implementation plan.
   - The plan must include a `## Blocking Requirement Issues` section (containing either a list of blocking items or the single word `None`).
2. Inspect the architect's plan for the `## Blocking Requirement Issues` section:
   - **If the section contains `None`** (or is absent) → proceed directly to Phase 2. Do not ask the user to approve the plan.
   - **If the section lists one or more blocking issues** → present the plan and the blocking issues to the user, then ask via `AskUserQuestion`:
     - `I'll clarify — here are my answers` *(the user provides clarification via the free-text "Other" input)*
     - `Start over with different requirements`
     Relay the user's clarification answers to the architect agent via `SendMessage`, instructing it to revise the plan. Repeat step 2 until the section contains `None`.

### Phase 2 — Implementation (Developer Agent)

3. Spawn the agent defined in `${CLAUDE_PLUGIN_ROOT}/agents/developer.md`.
   - Pass it the **architecture plan** and the **original requirements**.
   - Instruct it to implement all changes described in the plan. No inline test run is required in Draft mode.
4. Wait for the developer agent to complete. Collect its summary of changes made.

### Phase 3 — Done

5. Present a final summary to the user:
   - What was implemented (files created/modified)
   - A reminder that no tests or reviews were run — this output is draft quality
6. Ask via `AskUserQuestion`:
   - `Promote to full — run tests and review now (Recommended)`
   - `Leave as draft — I'll review manually`

> Selecting "Promote to full" re-enters this skill at Full mode Phase 3 (testing), carrying forward both the developer agent's output and the architect's plan from Draft Phase 1 — the test-writer needs the architect's Test Strategy section to derive test scenarios.

---

## Quick mode

*Developer only — no architect, no test loop, no review*

### Phase 1 — Implementation (Developer Agent)

1. Spawn the agent defined in `${CLAUDE_PLUGIN_ROOT}/agents/developer.md`.
   - Pass it the implementation brief from Phase 0.
   - Instruct it to implement only what is described — no scope creep.
2. Wait for the developer agent to complete. Collect its summary of changes made.

### Phase 2 — Done

3. Present a final summary to the user:
   - What was changed (files modified)
   - A reminder to review the diff before committing

> Quick mode ends here — no confirmation prompt. Review the diff and commit when ready.

**Never commit.** Always end here and leave the user to review and commit.

---

## Increment mode

*Developer + test loop — no architect, no review*

### Phase 1 — Implementation (Developer Agent)

1. Spawn the agent defined in `${CLAUDE_PLUGIN_ROOT}/agents/developer.md`.
   - Pass it the implementation brief from Phase 0.
   - Instruct it to implement only what is described — no scope creep.
   - Instruct it to **run the project's test suite inline** before returning (using the project's own test command, detected from its toolchain). It should report which tests passed, failed, or were skipped — this is a quick smoke check, not a full test pass.
2. Wait for the developer agent to complete. Collect its summary of changes made and the inline test results.

### Phase 2 — Testing (Test Agent)

3. If the developer's inline test run from Phase 1 showed failures unrelated to missing test coverage (i.e. source bugs), pass the failures back to the **developer agent** via `SendMessage` to fix them before proceeding. Skip directly to Phase 3 if the inline run was clean.

4. Spawn the agent defined in `${CLAUDE_PLUGIN_ROOT}/agents/test-writer.md`.
   - Pass it: (1) the **original requirements**, and (2) this explicit instruction: **"There is no architect plan for this run. Derive your test scenarios directly from the requirement brief alone — treat the brief as the sole authoritative specification of what the system must do. Do not invent scenarios from the implementation."**
   - The test-writer derives test scenarios from the requirement brief — not from what the developer coded.
5. Evaluate the test report:
   - **All pass** → proceed to Phase 3.
   - **Failures due to source bugs** → pass the failing test details back to the **developer agent** via `SendMessage` to fix. Then re-run Phase 2 (spawn a fresh test-writer agent).
   - **Maximum 2 iterations** of the dev↔test loop. If tests still fail after 2 rounds, present via `AskUserQuestion`:
     - `Continue iterating`
     - `Promote to full — add review now`
     - `Stop here — I'll fix manually`

### Phase 3 — Done

6. Present a final summary to the user:
   - What was implemented (files created/modified)
   - Test results (pass/fail counts)
   - A reminder that no architectural review or code review was run
7. Ask via `AskUserQuestion`:
   - `Promote to full — add review now (run the review phase)`
   - `Leave as-is — I'll review the diff manually`

> Selecting "Promote to full — add review now" re-enters this skill at Full mode Phase 4 (Review), carrying forward the developer agent's output and the test results. The test-writer does **not** re-run — the tests from Phase 2 stand.

**Never commit.** Always end here and leave the user to review and commit.

---

## Orchestration Rules

- **Always use `SendMessage`** to continue an existing agent rather than spawning a new one (except for the test-writer, which should always be spawned fresh each iteration since it re-analyses changes from scratch).
- **Never apply fixes yourself** — always delegate to the appropriate agent.
- **Track iteration counts** and enforce the maximum of **2 per loop** to avoid infinite cycles.
- **Only re-run reviewers that flagged issues** in iteration 2 — do not re-spawn reviewers that already passed.
- When routing errors back to agents, include the **specific findings** and **file/line references** so the agent has full context.
- Use British English throughout.

## Conversation Style

- Be a **project manager** — coordinate, summarise progress, and keep things moving.
- After each phase, give the user a brief status update before proceeding.
- In Quick mode, be brief and direct — this is a quick-fix flow, not a project.
- In Increment mode, be concise — this is a targeted, tested change, not a full project pipeline.
- If an agent produces unexpected output, flag it to the user rather than guessing.
