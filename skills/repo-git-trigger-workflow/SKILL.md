---
name: repo-git-trigger-workflow
description: Trigger one or more GitHub Actions workflows via workflow_dispatch on a target repo. Resolves workflow shortnames (app, api, mcp, infra, all), auto-detects required inputs, and gates firing behind explicit confirmation.
---

Trigger GitHub Actions workflows via `workflow_dispatch` on the current repo or a sibling project in the same org.

The skill resolves the target repo, looks up which workflows match the user's shortlist, discovers each workflow's required inputs, asks for any missing values, shows a confirmation gate, then fires all selected workflows in parallel and reports the queued run URLs.

## Arguments

`$ARGUMENTS` is **optional**. Free-text describing which workflows to trigger and on which project.

**Examples:**

- `/repo-trigger-workflow` → ask interactively
- `/repo-trigger-workflow app` → trigger app-deploy on the current repo
- `/repo-trigger-workflow app api mcp` → trigger app-deploy, api-deploy, and mcp-deploy on the current repo
- `/repo-trigger-workflow all` → trigger every workflow_dispatch-enabled workflow on the current repo
- `/repo-trigger-workflow app on justifi` → trigger app-deploy on the repo matching "justifi"
- `/repo-trigger-workflow api mcp on air-fare prod` → trigger api-deploy and mcp-deploy on air-fare with `environment=prod`

## Important rules

Read and follow all rules in [`../shared/_ux-rules.md`](../shared/_ux-rules.md).

## Guardrails

- **Never** fire any workflow without an explicit confirmation gate — even for `qa` environments.
- **Never** assume input values (especially `environment`) — read them from the user's arguments, or ask.
- **Always** verify the target repo exists (`gh repo view`) before firing.
- **Never** trigger on a branch other than the default branch unless the user explicitly named one.
- If a workflow is gated by `if: github.ref == 'refs/heads/main'` (or similar), confirm the ref matches before firing — otherwise the run will queue then no-op.

## Process

### 1. Parse arguments

Extract from `$ARGUMENTS`:

- **Workflow shortnames** — one or more of: `app`, `api`, `mcp`, `infra`, `infra-plan`, `infra-apply`, `ci-app`, `ci-api`, or `all`. Map to filenames in step 3.
- **Project hint** — text after `on`, `for`, or `in` (e.g. `on justifi`). If absent, target the current repo.
- **Environment / inputs** — bare tokens like `prod`, `qa`, `staging` are treated as candidate `environment` input values. Anything in `key=value` form is a direct input override.
- **Branch** — text after `from` or `on branch` (e.g. `from main`, `on branch release/v2`). Defaults to the repo's default branch.

If no workflow shortnames were given, ask via `AskUserQuestion` after step 2 (once the available workflows are known).

### 2. Resolve target repo

**If a project hint was given:**

1. Detect the current GitHub org from `gh repo view --json owner -q .owner.login` (current repo's owner).
2. List repos in that org:
   ```
   gh repo list <org> --limit 200 --json name,nameWithOwner
   ```
3. Filter by case-insensitive substring match against the project hint. The hint may be a partial name (e.g. `justifi` matches `fi--justi-fi`).
4. If exactly one match → use it.
5. If multiple matches → ask the user to pick via `AskUserQuestion`, listing each candidate with its full `nameWithOwner`.
6. If zero matches → print the hint, list the closest 5 names, and **stop**.

**If no project hint was given:**

Run `gh repo view --json nameWithOwner,defaultBranchRef -q '{repo: .nameWithOwner, branch: .defaultBranchRef.name}'`. If it fails (not in a git repo with a GitHub remote), print the error and **stop**.

Store as `TARGET_REPO` (e.g. `Rise-4/h4--estate-ops`) and `DEFAULT_BRANCH` (e.g. `main`). If a branch was named in the arguments, it overrides `DEFAULT_BRANCH`.

### 3. Discover workflows on the target repo

Run:

```
gh workflow list --repo <TARGET_REPO>
```

Build a map of workflow filenames available on the repo. Apply the shortname → filename heuristic:

| Shortname | Matches workflow whose filename equals... |
|---|---|
| `app` | `app-deploy.yml` |
| `api` | `api-deploy.yml` |
| `mcp` | `mcp-deploy.yml` |
| `infra-plan` | `infra-plan.yml` |
| `infra-apply` | `infra-apply.yml` |
| `infra` | both `infra-plan.yml` and `infra-apply.yml` (in that order, with a confirmation gate between them — see step 6) |
| `ci-app` | `ci-app-build.yml` |
| `ci-api` | `ci-api-build.yml` |
| `all` | every workflow on the repo that has a `workflow_dispatch` trigger |

If a shortname doesn't resolve (workflow file doesn't exist on this repo), list the available workflows on the repo and ask the user to pick via `AskUserQuestion`.

If no shortnames were given in arguments, ask now:

> "Which workflow(s) do you want to trigger on `<TARGET_REPO>`?"
>
> [multiSelect option list of workflows that have `workflow_dispatch`]

To detect `workflow_dispatch` support without inspecting every YAML up-front, check the `Run workflow` button presence is implicit — use `gh workflow view <file> --yaml` and look for `workflow_dispatch:` in the `on:` block.

Store the chosen workflow filenames as `SELECTED_WORKFLOWS`.

### 4. Discover each workflow's inputs

For each filename in `SELECTED_WORKFLOWS`, run:

```
gh workflow view <file> --repo <TARGET_REPO> --yaml
```

Parse the `on.workflow_dispatch.inputs` block. For each declared input, record:

- `name` (e.g. `environment`, `target_environment`)
- `required` (true / false)
- `type` (e.g. `choice`, `string`, `boolean`, `environment`)
- `options` (for `choice` type)
- `default` (if set)

Build `WORKFLOW_INPUTS[workflow] = [...inputs]`.

### 5. Resolve input values

For each workflow's required inputs:

1. **If the argument string contains a `key=value` override** matching the input name → use that value (validate it against `options` if `choice`).
2. **Else if the input name suggests environment** (`environment`, `target_environment`, `env`) and a bare environment token was given in arguments (`prod`, `qa`, `staging`) → use it (validate against `options`).
3. **Else if the input has a `default`** → use the default (but still surface it in the confirmation gate).
4. **Else** → ask the user via `AskUserQuestion`. For `choice` inputs, present the options. For boolean, present Yes/No. For free-text, present the most likely values plus "Other".

Group all questions for all selected workflows into a single `AskUserQuestion` call where possible — never one prompt per workflow if they share inputs.

Store as `RESOLVED_INPUTS[workflow] = { key: value, ... }`.

### 6. Confirmation gate

Show the user the full picture:

```
──────────────────────────────────────
  REPO:    <TARGET_REPO>
           https://github.com/<TARGET_REPO>
  BRANCH:  <DEFAULT_BRANCH or override>
──────────────────────────────────────

  Will trigger:
    • app-deploy.yml     environment=prod
    • api-deploy.yml     environment=prod
    • mcp-deploy.yml     environment=prod

  Total: 3 workflows
──────────────────────────────────────
```

Then ask via `AskUserQuestion`:

> "Trigger these workflows on `<TARGET_REPO>`?"

Options:

1. Yes — trigger all *(Recommended)*
2. Cancel

If the selection contained `infra` (both plan and apply), the gate must be split:

- First gate: confirm `infra-plan` only.
- After plan completes (poll `gh run list` until status is `completed`), show plan results and ask a **second** gate to confirm `infra-apply`.
- Never auto-chain plan → apply without the second gate.

If any workflow's resolved environment is `prod`, present it prominently in the gate text — but do not require a second prompt unless the user has configured one. The `AskUserQuestion` itself is the prod gate.

### 7. Fire workflows

After confirmation, fire all selected workflows in parallel (one `Bash` tool call per workflow, all in a single message). Each command:

```
gh workflow run <file> --repo <TARGET_REPO> --ref <branch> -f <input>=<value> [-f <input2>=<value2> ...]
```

Capture the URL returned by `gh workflow run` for each.

### 8. Verify and report

For each fired workflow, run:

```
gh run list --workflow=<file> --repo <TARGET_REPO> --limit 1
```

Confirm the run shows up with status `queued` or `in_progress` and a recent timestamp (within the last ~60 seconds — older means we matched a previous run).

Print:

```
Triggered <N> workflows on <TARGET_REPO>:

  • <file>  → <status>  <url>
  • <file>  → <status>  <url>
  ...

Watch them with:
  gh run watch --repo <TARGET_REPO>
```

If any `gh workflow run` returned an error, list it explicitly and do not pretend the run was queued.

## Verification

- Every selected workflow appears in `gh run list` with status `queued` or `in_progress` and a fresh timestamp.
- `gh run view <run-id> --repo <TARGET_REPO>` resolves for each printed URL.
- No workflow was fired without passing through the step 6 gate.
