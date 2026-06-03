# is-it-magic — Claude Code Plugin

General-purpose Claude Code plugin providing an AI-assisted development workflow — orchestration skills, specialised agents, project bootstrapping, and language rules.

## What's included

| Component  | Count | Items                                                                                                                                                                                                                                                                                                                              |
| ---------- | ----- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Skills** | 18    | `devbox-init`, `project-session`, `project-investigate`, `project-decide`, `project-requirements`, `project-implement`, `project-sync`, `repo-commit`, `repo-ef-sql`, `repo-git-env`, `repo-git-trigger-workflow`, `repo-security-scan`, `plugin-commit`, `plugin-implement`, `devbox-scan-secrets`, `devbox-set-context`, `az-query`, `session-to-skill` |
| **Agents** | 16    | `architect`, `developer`, `test-writer`, `reviewer-quality`, `reviewer-design`, `reviewer-perf`, `codebase-explorer`, `repo-archaeologist`, `project-locator`, `azure-investigator`, `scanner-secrets`, `scanner-injection`, `scanner-exposure`, `scanner-devbox`, `plugin-architect`, `plugin-reviewer`                            |
| **Rules**  | 6     | `general`, `api-lang`, `app-lang`, `infra-lang`, `infra-naming`, `python-lang` — synced to `~/.claude/rules/` by `/devbox-init`                                                                                                                                                                                                     |

---

## Installation

### Prerequisites

- [Claude Code](https://code.claude.com) installed

### Step 1 — Register the marketplace

Add the following to your **user-level** settings file at `~/.claude/settings.json`:

```json
{
  "extraKnownMarketplaces": {
    "ekla-internal": {
      "source": {
        "source": "settings",
        "name": "ekla-internal",
        "owner": {
          "name": "Ekla"
        },
        "plugins": [
          {
            "name": "is-it-magic",
            "source": {
              "source": "url",
              "url": "https://github.com/GBR-Perso-1/is-it-magic.git"
            },
            "description": "AI-assisted development workflow — agents, skills, project init, and language rules."
          }
        ]
      }
    }
  }
}
```

### Step 2 — Install the plugin

```powershell
claude plugin install is-it-magic@ekla-internal --scope user
```

### Step 3 — Reload plugins

```
/reload-plugins
```

### Step 4 — Initialise this machine

Run once after install (and again after any plugin update to pick up refreshed rules):

```
/devbox-init
```

This syncs all bundled plugin rules into `~/.claude/rules/` so they load globally in every Claude Code session, and ensures the favoured language LSP plugins are present in `~/.claude/settings.json`.

---

## Skills

### Project workflow

| Skill                   | Purpose                                                                                                                                                                          |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/devbox-init`          | Set up this machine for the is-it-magic plugin — sync all plugin rules into `~/.claude/rules/` and enable favoured language LSPs in user settings. Idempotent; re-run to refresh. |
| `/project-session`      | Load architecture docs and current session context (branch, working tree, stack commands) at the start of a conversation for full project awareness.                           |
| `/project-investigate`  | Investigate a codebase or system — bug hunt, analytical question, or full repository archaeology. Always read-only.                                                             |
| `/project-decide`       | Decision layer between investigation and implementation. Infers debt trajectory, generates 2–4 solution options with pros/cons and effort, and commits to a recommendation. Read-only. |
| `/project-requirements` | Produce a formal, versioned requirements document for app evolution — never proposes implementation details.                                                                   |
| `/project-implement`    | Implement a requirement. `full` (default): architect → dev → test → review. `draft`: architect + dev only. `quick`: dev only. Never commits.                                   |
| `/project-sync`         | Sync files between sibling projects in a `<Scope>.Applications/` folder — merges or copies intelligently. Never stages or commits.                                              |

### Repository operations

| Skill                       | Purpose                                                                                                                  |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `/repo-commit`              | Run the test suite, then stage, commit, and push to the current branch with a conventional-commit message. Tests gate the push. |
| `/repo-ef-sql`              | Generate a SQL upgrade script from a given EF Core migration to the latest.                                              |
| `/repo-git-env`             | Manage GitHub environment variables and secrets from a JSON config — validates, confirms, and applies via `gh`.          |
| `/repo-git-trigger-workflow`| Trigger GitHub Actions workflows via `workflow_dispatch`. Resolves shortnames (app, api, mcp, infra, all), gated by confirmation. |
| `/repo-security-scan`       | Scan a repo for secrets, injection vulnerabilities, and exposure risks via three parallel scanner agents. Read-only report. |

### Plugin development

| Skill                | Purpose                                                                                              |
| -------------------- | ---------------------------------------------------------------------------------------------------- |
| `/plugin-commit`     | Bump the plugin version based on the changes, commit with a meaningful message, and push to main.    |
| `/plugin-implement`  | Implement new or updated plugin artefacts (skills, agents, hooks, rules) with ecosystem awareness.   |

### Dev machine & context

| Skill                  | Purpose                                                                                                              |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `/devbox-scan-secrets` | Audit the local dev machine for exposed secrets — writes a CSV report to `.claude/secret-audit-<date>.csv`.         |
| `/devbox-set-context`  | Manage the user-level `contexts.json` manifest describing your GitHub/Azure accounts.                               |
| `/az-query`            | Read-only Azure lookups (app registrations, groups, Key Vault, resources) using natural language.                  |

### Meta

| Skill               | Purpose                                                                                                  |
| ------------------- | -------------------------------------------------------------------------------------------------------- |
| `/session-to-skill` | Retroactively distil a completed piece of session work into a reusable `fix-` or `migrate-` skill.       |

---

## Agents

Agents are spawned by skills (and can be invoked directly). Grouped by role:

| Group                     | Agents                                                                       |
| ------------------------- | ---------------------------------------------------------------------------- |
| **Implementation pipeline** | `architect`, `developer`, `test-writer`, `reviewer-quality`, `reviewer-design`, `reviewer-perf` |
| **Investigation**         | `codebase-explorer`, `repo-archaeologist`, `project-locator`, `azure-investigator` |
| **Security scanners**     | `scanner-secrets`, `scanner-injection`, `scanner-exposure`, `scanner-devbox` |
| **Plugin development**    | `plugin-architect`, `plugin-reviewer`                                        |

---

## Updating the plugin

```powershell
claude plugin update is-it-magic@ekla-internal
```

---

## Local development

```powershell
claude --plugin-dir "C:/Workspace/Dev/Perso.Applications/is-it-magic"
```
