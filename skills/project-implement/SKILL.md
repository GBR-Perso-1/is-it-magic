---
name: project-implement
description: >
  Implement a requirement or fix with configurable rigour.
  Four modes:
  no arg or "full" = architect → developer → test → review pipeline (default);
  "draft" = architect + developer, no test loop, no review (fast iteration / POC);
  "quick" = developer only, no architect, no test, no review (lightweight fix);
  "increment" = developer + test loop, no architect, no review (tested change to live code).
  Prefixing any mode with "isolated" (e.g. "isolated full <req>", or "isolated" alone) runs the whole pipeline inside a dedicated git worktree, for use alongside concurrent manual edits or a second session on the same project.
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

Prefixing any value with `isolated ` opts into worktree isolation (see `## Isolated mode`); omitting it leaves behaviour unchanged.

---

## Phase 0 — Mode selection and input gathering

1. Parse `$ARGUMENTS`:
   - **Isolated-token check** (before mode-keyword extraction): check whether `isolated` is the first token, or the token immediately following a first-token mode keyword (covers `isolated <req>`, `isolated full <req>`, `full isolated <req>`, `isolated draft/quick/increment <req>`). If found, strip that single token and set `ISOLATED = true` (default `false`). Pass the remaining string unchanged to the steps below.
   - **Already-in-worktree check**: also detect whether the session CWD is already inside a plugin-managed worktree (the same `.claude/worktrees/` / `.git/worktrees/` detection used in Isolated mode Setup step 1). If so, set `ISOLATED = true` regardless of whether the `isolated` token was supplied. This lets a follow-up run invoked from inside an existing worktree behave as isolated (no commit offer, handback note shown) without the user having to re-supply the token. This detection is path-based, not scoped to project-implement — if a future skill adopts the same worktree convention, running project-implement from inside one of its worktrees will also auto-activate isolated mode, which is the safe default (never auto-offers a commit inside a managed worktree).
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
   - If `ISOLATED = true`, state in the brief that this run will execute inside a dedicated (isolated) git worktree, so the user sees it before the run proceeds.
   - `Looks right — proceed` *(label this as Recommended)*
   - `Let me clarify`
7. If `ISOLATED = true`, perform the setup in `## Isolated mode` now, before entering the selected mode's Phase 1. This is the only place `EnterWorktree` is invoked.

---

## Isolated mode

*Runs the whole pipeline inside a dedicated git worktree, activated either by the `isolated` token detected in Phase 0 step 1, or automatically when the session is already inside a plugin-managed worktree (Phase 0's "Already-in-worktree check").*

### Activation

The `isolated` token is itself the explicit user request that satisfies `EnterWorktree`'s guardrail — no separate `AskUserQuestion` gate is needed before entering the worktree. Alternatively, when the session is already inside a plugin-managed worktree, Phase 0's "Already-in-worktree check" sets `ISOLATED = true` automatically — no new worktree is created in that case (`EnterWorktree` is skipped, per Setup step 1); the run simply proceeds under isolated behaviour.

### Setup procedure

1. **Detect an already-active worktree** — run `git rev-parse --show-toplevel` and `git rev-parse --git-dir`. If the toplevel path is under `.claude/worktrees/`, or the git-dir is under `.git/worktrees/`, the session is already inside a worktree: **skip steps 3 and 4** (the dirty-tree check and `EnterWorktree`) and go straight to step 5, telling the user the run continues in the current worktree. Step 2 still runs regardless (it is idempotent — append only if missing), and step 5 still runs, but states the *current* worktree's path/branch rather than a freshly created one.
2. **Exclude the worktrees directory from the review surface** — ensure `.claude/worktrees/` is listed in `.git/info/exclude` (append it if missing). Use `.git/info/exclude`, **not** the tracked `.gitignore` — the exclusion must never appear as a diff on the review surface.
3. **Check for uncommitted changes before entering a new worktree** — run `git status --porcelain` on the current tree. If it is dirty, tell the user (informational, not a hard gate — proceed after telling them): the isolated worktree branches from a committed baseline, so their current uncommitted main-tree changes will **not** be carried into it and will remain untouched in the main tree; if they want that specific work isolated, they should commit it first.
4. **Derive a deterministic name and enter the worktree** — derive `NAME` from the requirement brief: lowercase, hyphenated, stopwords stripped, first ~5 significant words, ≤40 characters, de-duplicated with a numeric suffix if `.claude/worktrees/<NAME>` already exists. Call `EnterWorktree` with `name: NAME`, and record the **actual** returned path/branch — never assume the branch name equals `NAME` verbatim.
5. **State it once** — tell the user the worktree path and branch. If step 3 found a dirty tree, fold in a one-line reminder here too: uncommitted changes left behind in the main tree were not carried into this worktree and remain there untouched, since the worktree branches from the committed baseline governed by the `worktree.baseRef` setting (`head` recommended).

### Base-ref note

`worktree.baseRef` is a platform setting, not controllable from within this skill — recommend the user set it to `head` rather than `fresh`. Either way, the worktree starts from a **committed** baseline: to isolate work that builds on currently-uncommitted changes in the main tree, commit them first.

### During the run

No agent spawn may set `isolation:"worktree"` — the CWD move performed by `EnterWorktree` is what shares the worktree with every agent in the pipeline, and per-agent isolation would fragment the tree that the relay's git diff/status scope discovery needs. The Phase 4 `CHECKPOINT_SHA` step is unmodified in isolated mode (see `Full mode Phase 4, step 7`). Note the Windows shared-cache contention risk: the global NuGet packages folder and global npm/pnpm store are shared across worktrees, but a fresh worktree's `node_modules`/`obj`/`bin` are not — an install/restore may be needed before the developer agent's build/verify step.

### Handback

At each mode's final Done phase, when `ISOLATED = true`, append this note:
- The worktree path and branch.
- "Commit + merge into `<original-branch>` yourself — this skill performs no commit and no merge-back."
- The session stays in the worktree for follow-ups.

### Ending isolation

`ExitWorktree` is never called automatically. Only call it in a later turn, once the user explicitly says they are finished, and always with `action:"keep"`.

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
3. **Test-first policy check** — determine whether this change is governed by a test-first (RED→GREEN) policy:
   - Read `.claude/CLAUDE.md`. If it is absent, or has no `## Stack Conventions` section → `TEST_FIRST_ACTIVE = false`; proceed to Phase 2 unchanged.
   - For each `@./conventions/<B>.md` import line under `## Stack Conventions`, resolve to `.claude/conventions/<B>.md` and read it if it exists.
   - For each bundle read, check for a `## Testing Policy` heading. If present, extract the `**Governed layers**:` comma-separated list into `GOVERNED_LAYERS` (deduplicated, case-insensitive, across all bundles).
   - If `GOVERNED_LAYERS` is empty → `TEST_FIRST_ACTIVE = false`; proceed to Phase 2 unchanged.
   - Otherwise, collect the distinct `Area / Layer` value per step from the architect's `## File Changes` section as `CHANGE_SURFACE`.
   - `TEST_FIRST_ACTIVE = true` iff any `CHANGE_SURFACE` entry case-insensitively contains (or is contained by) any `GOVERNED_LAYERS` entry. Record the files of matching steps as `MATCHED_FILES`; all other plan files as `OTHER_FILES`.
   - If `TEST_FIRST_ACTIVE` → print a one-line status note: *"Applying test-first policy (RED→GREEN) for: `<matched layers>`."* No `AskUserQuestion` gate — this policy is automatic, not a user decision point.
   - **Default**: `TEST_FIRST_ACTIVE` starts `false` and is only ever set `true` by this step. Any entry into Full mode that skips this step inherits `false`.

### Phase 2 — Implementation (Developer Agent)

4. Spawn the agent defined in `${CLAUDE_PLUGIN_ROOT}/agents/developer.md`.
   - **`TEST_FIRST_ACTIVE = false`** — pass it the **architecture plan** and the **original requirements**. Instruct it to implement all changes described in the plan, then **run the project's test suite inline** before returning (using the project's own test command, detected from its toolchain). It should report which tests passed, failed, or were skipped — this is a quick smoke check, not a full test pass.
   - **`TEST_FIRST_ACTIVE = true`** — pass it the **architecture plan** and the **original requirements**, plus an instruction to scaffold-only `MATCHED_FILES` (compiling signatures/stubs, no real behaviour) while implementing `OTHER_FILES` fully, in the same pass. Do **not** run the inline smoke-check against the stubbed area — RED confirmation happens in Phase 3.
5. Wait for the developer agent to complete. Collect its summary of changes made (and, when `TEST_FIRST_ACTIVE` is `false`, the inline test results).

### Phase 3 — Testing (Test Agent)

6. Branch on `TEST_FIRST_ACTIVE` (determined in Phase 1):

   **`TEST_FIRST_ACTIVE = false`** — unchanged dev↔test loop:
   - If the developer's inline test run from Phase 2 showed failures unrelated to missing test coverage (i.e. source bugs), pass the failures back to the **developer agent** via `SendMessage` to fix them before proceeding. Skip directly to Phase 4 if the inline run was clean.
   - Spawn the agent defined in `${CLAUDE_PLUGIN_ROOT}/agents/test-writer.md`. Pass it: (1) the **original requirements**, (2) the **Test Strategy section** from the architect's plan. The test-writer derives test scenarios from the requirements — not from what the developer coded.
   - Evaluate the test report:
     - **All pass** → proceed to Phase 4.
     - **Failures due to source bugs** → pass the failing test details back to the **developer agent** via `SendMessage` to fix. Then re-run Phase 3 (spawn a fresh test-writer agent).
     - **Maximum 2 iterations** of the dev↔test loop. If tests still fail after 2 rounds, present via `AskUserQuestion`:
       - `Continue iterating`
       - `Skip failing tests and proceed to review`
       - `Stop here — I'll fix manually`

   **`TEST_FIRST_ACTIVE = true`** — RED-confirmation sub-flow, then the GREEN dev↔test loop:
   a. Spawn a fresh test-writer agent. Pass it: (1) the **original requirements**, (2) the **Test Strategy section**, (3) `MATCHED_FILES` as the stub-only file list. It classifies each result as PASS / RED-expected / test-issue (its normal retry allowance) / scaffold-defect.

   Read the test-writer's **RED Confirmation** verdict line directly — do not re-derive it from the per-test table. Evaluate in this order (first match wins):
   - Any `OTHER_FILES` row is Fail (source bug) → go to (b), regardless of verdict.
   - Verdict `SCAFFOLD_DEFECT` → go to (c).
   - Verdict `CONFIRMED_RED` → proceed to (d).
   - Verdict `n/a` should not occur on this path — if seen, treat as `SCAFFOLD_DEFECT` (go to (c)).

   b. If any result is Fail (source bug) against a file in `OTHER_FILES` (already fully implemented by Phase 2, not a `MATCHED_FILES` stub) → this is a genuine bug, unrelated to RED-confirmation. Route it exactly as the `TEST_FIRST_ACTIVE = false` flow's source-bug path: `SendMessage` to the developer to fix, then repeat (a) with a fresh test-writer. This consumes one iteration of the same Phase-3 dev↔test loop counter used at step (e) — max 2 total, combined across (b) and (e). If this shared counter is exhausted during the RED round (two `OTHER_FILES` fix cycles before RED is confirmed), (e)'s GREEN verification is skipped and the `AskUserQuestion` fallback fires immediately on the first GREEN attempt — an accepted safety valve, since a change needing two or more `OTHER_FILES` fixes before RED is confirmed is already unhealthy.
   c. **Any scaffold-defect** → `SendMessage` the same developer agent to correct the stub signatures only (no behaviour change), then repeat (a) with a fresh test-writer agent. Cap this scaffold-fix sub-loop at **2 attempts**, tracked separately from and never counted against the GREEN loop's max-2 cap. On exhaustion, present via `AskUserQuestion`:
      - `Continue adjusting the stub signatures`
      - `Skip test-first for this change and implement directly`
      - `Stop here — I'll fix manually`
   d. `SendMessage` the same developer agent instance with the RED report and the Test Strategy, instructing it to implement `MATCHED_FILES` to GREEN.
   e. Spawn a fresh test-writer agent to verify GREEN. Evaluate using the exact same rules as the `TEST_FIRST_ACTIVE = false` bullet above:
      - **All pass** → proceed to Phase 4.
      - **Failures due to source bugs** → `SendMessage` to the developer to fix, then repeat (e) with a fresh test-writer.
      - **Maximum 2 iterations total** of this Phase-3 dev↔test loop — counting this spawn plus any (b) bug-fix cycle already consumed during the RED round. On exhaustion, present the same `AskUserQuestion` fallback: `Continue iterating` / `Skip failing tests and proceed to review` / `Stop here — I'll fix manually`.

### Phase 4 — Review (Quality, then Design + Perf)

7. **Pipeline checkpoint** — retaken on every entry into Phase 4, including loop-back re-entries from the correction path (step 11). Build an out-of-band recovery point that covers tracked AND untracked files without touching the real index or working tree, and without creating any ref, stash entry, or commit on the branch:

    ```bash
    CKPT_INDEX="$(mktemp)"
    rm -f "$CKPT_INDEX"
    GIT_INDEX_FILE="$CKPT_INDEX" git add -A
    TREE_SHA=$(GIT_INDEX_FILE="$CKPT_INDEX" git write-tree)
    CHECKPOINT_SHA=$(git commit-tree "$TREE_SHA" -p HEAD -m "project-implement internal checkpoint (never for user history)")
    rm -f "$CKPT_INDEX"
    ```

    `CHECKPOINT_SHA` is held only in the pipeline's own state for this run — never printed to the user, never written to `refs/stash` or any branch. If there is nothing to checkpoint (clean tree), skip and proceed. This step is unchanged in isolated mode: it already operates against HEAD/the working tree, and `EnterWorktree` has moved the session's CWD, so HEAD resolves to the worktree branch; the checkpoint is not redundant here, since isolated edits stay uncommitted and are equally exposed to destructive auto-fix.

8. **Relevance check** — decide whether the performance reviewer is needed:
    - If the change touches **executable code** (back-end logic, data access, or front-end logic) → **perf review applies**, spawn all three reviewers.
    - If the change is **docs/config-only** with no runtime code → **perf review skipped**, spawn quality + design only.

    (The performance reviewer is stack-aware — it reads the project's convention bundles to apply the relevant perf lens — so it self-limits when little applies.)

9. **Spawn reviewers** — quality first and alone, then the read-only reviewers in parallel, never overlapping:
    - 9a. Spawn the **code-quality reviewer** (`${CLAUDE_PLUGIN_ROOT}/agents/reviewer-quality.md` — linting, style, rule compliance) alone. Wait for it to fully complete, including its Phase 3 auto-fixes, before spawning anything else.
    - 9b. Once the quality reviewer has returned, spawn the remaining reviewers in parallel per the relevance check:
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
      - `Stop here — I'll review and roll back myself`

      Selecting the last option ends the skill here and leaves the working tree intact for the user to review — the user may discard their own uncommitted work if they choose, but agents and the skill itself never run destructive git.

12. **Checkpoint unwind** — verify the working tree still reflects the expected changes (developer's, test-writer's, and reviewer auto-fixes — cross-check against the file lists those agents reported).
    - If intact, `CHECKPOINT_SHA` is simply discarded — it was never attached to a ref, so there is nothing further to clean up and it cannot leak into the user's history even if this step is skipped by an earlier abort.
    - If the tree was destructively reverted, recover immediately with `git checkout "$CHECKPOINT_SHA" -- .` (the one sanctioned exception to the destructive-git ban — it restores lost work from the internal checkpoint rather than discarding anything), then report the recovery to the user before continuing.

### Phase 5 — Done

13. Present a final summary to the user:
    - What was implemented (files created/modified)
    - Test results (pass/fail counts)
    - Review outcome (clean / accepted with notes)
14. If `ISOLATED = true`, skip the question entirely — there is no in-skill "Commit these changes" option in isolated mode. Append the worktree handback note (see `## Isolated mode`) to the summary and end.
    Otherwise, ask via `AskUserQuestion`:
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
   - If `ISOLATED = true`, also append the worktree handback note (see `## Isolated mode`)
6. Ask via `AskUserQuestion`:
   - `Promote to full — run tests and review now (Recommended)`
   - `Leave as draft — I'll review manually`

> Selecting "Promote to full" re-enters this skill at Full mode Phase 3 (testing), carrying forward both the developer agent's output and the architect's plan from Draft Phase 1 — the test-writer needs the architect's Test Strategy section to derive test scenarios. `TEST_FIRST_ACTIVE` is not computed on this path (Draft mode has no Testing Policy Detection step) and defaults to `false`: Draft already implemented the behaviour directly, with no stubs, so RED→GREEN cannot be retrofitted. Phase 3 runs its `TEST_FIRST_ACTIVE = false` flow — test-writer runs once, as today.

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
   - If `ISOLATED = true`, also append the worktree handback note (see `## Isolated mode`)

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
   - If `ISOLATED = true`, also append the worktree handback note (see `## Isolated mode`)
7. Ask via `AskUserQuestion`:
   - `Promote to full — add review now (run the review phase)`
   - `Leave as-is — I'll review the diff manually`

> Selecting "Promote to full — add review now" re-enters this skill at Full mode Phase 4 (Review), carrying forward the developer agent's output and the test results. The test-writer does **not** re-run — the tests from Phase 2 stand. (`TEST_FIRST_ACTIVE` is never referenced on this path — it re-enters at Phase 4/Review, after Phase 2/3 have already run.)

**Never commit.** Always end here and leave the user to review and commit.

---

## Orchestration Rules

- **Always use `SendMessage`** to continue an existing agent rather than spawning a new one (except for the test-writer, which should always be spawned fresh each iteration since it re-analyses changes from scratch).
- **Never apply fixes yourself** — always delegate to the appropriate agent.
- **Track iteration counts** and enforce the maximum of **2 per loop** to avoid infinite cycles.
- Track the RED-confirmation sub-loop (scaffold-defect retries, max 2) separately from the GREEN dev↔test loop (max 2) — the initial expected RED never counts as a failed iteration of either. `OTHER_FILES` source-bug fixes during the RED round (step (b)) draw from the GREEN loop's shared max-2 budget.
- **Only re-run reviewers that flagged issues** in iteration 2 — do not re-spawn reviewers that already passed.
- The quality reviewer's auto-fix always runs to completion, alone, before any read-only reviewer starts — never parallelise a mutating reviewer with a read-only one.
- The Phase 4 pipeline checkpoint (`CHECKPOINT_SHA`) is internal only — never mention it or its underlying git commands in user-facing output; only a recovery outcome, if triggered, is reported.
- When routing errors back to agents, include the **specific findings** and **file/line references** so the agent has full context.
- **Isolated mode**: never set `isolation:` on an individual agent spawn — see `## Isolated mode` → During the run.
- Use British English throughout.

## Conversation Style

- Be a **project manager** — coordinate, summarise progress, and keep things moving.
- After each phase, give the user a brief status update before proceeding.
- In Quick mode, be brief and direct — this is a quick-fix flow, not a project.
- In Increment mode, be concise — this is a targeted, tested change, not a full project pipeline.
- If an agent produces unexpected output, flag it to the user rather than guessing.
