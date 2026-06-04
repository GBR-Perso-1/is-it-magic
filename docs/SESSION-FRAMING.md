# Framing: split is-it-magic (generic) from rise-dev-plugin (company-specific)

> Paste the relevant parts of this file into a new session to frame the work. Everything
> except the "What I want to work on now" section stays constant across sessions.

## The two plugins
- **is-it-magic** — my GENERAL / personal plugin, installed at USER level, meant to be
  100% generic and stack-agnostic. Path: `C:\Workspace\Dev\Perso.Applications\is-it-magic`
- **rise-dev-plugin** (a.k.a. "the project/company plugin") — company-specific (Rise).
  Path: `C:\Workspace\Dev\Rise.Applications\it--claude-rise-plugin`

## Overall goal for this work
Trim **is-it-magic** down to a PURE generic user plugin, and MOVE / PORT every
company- or stack-specific thing out of it into **rise-dev-plugin**. After this,
is-it-magic should contain only universal, stack-agnostic content; anything tied to a
specific stack (.NET/Node/SQL Server), specific repo layout (`api/`, `app/`, `infra/`),
specific company workflow, or specific tooling belongs in rise-dev-plugin.

## How Claude Code rule loading works (established facts — don't re-investigate)
- Claude Code natively auto-loads rules from `~/.claude/rules/` (global, every project)
  and `<project>/.claude/rules/` (that repo only). Rules are NOT a first-class plugin
  component — a plugin cannot auto-ship rules; a skill/hook must COPY them into those dirs.
- Rule files with NO `paths:` frontmatter are ALWAYS-ON; with `paths:` globs they load only
  when a matching file is in context. There is NO repo-identity (git remote/name) conditional
  — scoping is by file location + path globs only.
- Design we settled on: generic rules live global (synced by is-it-magic); company rules live
  project-scoped (synced by rise-dev-plugin into the repo). They compose only inside company repos.

## What was done in the prior session
- Confirmed the rule-loading model above.
- Wrote requirements at:
  `C:\Workspace\Dev\Perso.Applications\is-it-magic\docs\requirements\evolution-plugin-rule-sync.md`
  (NOTE its "Superseded 2026-06-03" banner: the standalone rules-sync skills were merged into
   richer skills — `devbox-init` in is-it-magic [syncs rules to `~/.claude/rules/` + enables
   favoured LSPs in `~/.claude/settings.json`], and `project-init` in rise-dev-plugin [bootstraps
   a project's `.claude/`: rule sync + `CLAUDE.md` + `project-context.md` + per-stack LSP settings].
   The SB-1..SB-7 shared sync behaviours still apply.)
- is-it-magic was bumped to v4.2.0 during that work.
- Reviewed `C:\Workspace\Dev\Perso.Applications\is-it-magic\rules\general.md` and found it is
  NOT actually generic. Stack/OS/workflow-specific content to move or genericise:
    * "Dependencies — No Global Installs" section hardcodes .NET/Node/SQL Server, `api/.config/
      dotnet-tools.json`, `app/package.json`. (Principle is generic; examples are stack-specific.)
    * "Windows environment — use PowerShell for scripts" (OS assumption).
    * "## Company Context" heading + unconditional read of `.claude/project-context.md`.
    * Git rule "Main: no PR needed" (opinionated workflow; conflicts with company PR policy).
    * Genuinely-generic sections to KEEP: Code Quality, Simplicity First, Surgical Changes,
      British English.
  rise-dev-plugin currently has NO `rules/` directory — the ported company content will seed it.

## What I want to work on now (new session)
The **rules** phase is done (generic rules kept/genericised in base; company/stack bits moved to
rise or flagged). Now: **rewrite the skills and agents from `.backup-skills/` into the live plugin,
one by one**, applying the base-vs-specialized split — see "Mode of work" below and the plan of
record at `docs/skills-agents-triage.md`.

## Mode of work — rewriting skills & agents from a frozen backup (current phase)

A **backup-as-source** workflow:

- `.backup-skills/{agents,skills}/` holds a frozen copy of every original agent and skill (plus the
  full `skills/shared/` set, including the `_api-archi-extended.md` / `_app-archi-extended.md`
  holding files). **This is read-only reference — never modify anything under `.backup-skills/`.**
  It is the source of truth for what each artefact originally did.
- The live `agents/` and `skills/` trees were emptied (only `skills/shared/_ux-rules.md` kept).
  We **rewrite each artefact from its backup into the live tree, one by one**, applying the
  base-vs-specialized split: generic artefacts are rebuilt lean in the base; company/stack-specific
  ones are rebuilt into the rise/specialized plugin instead.
- **The user guides the process and decides each artefact's fate** (rewrite-in-base / split /
  move-to-specialized / drop). Claude reads the backup and proposes; the user decides. Never edit
  the backup.
- **Port the whole dependency closure, not just the named artefact.** When a skill/agent is rewritten
  into the live tree, also port what it references — spawned agents, shared `_*.md` fragments — or the
  live artefact will have dangling references. (e.g. `repo-security-scan` pulled in `scanner-secrets`,
  `scanner-injection`, `scanner-exposure`, and `_secret-redaction.md`.)
- Plan of record: `docs/skills-agents-triage.md` (full classification + the 3 decision clusters).
  Litmus: `docs/plugin-model.md`.

> Housekeeping: `.backup-skills/` is currently untracked and **not** gitignored — decide whether it
> should be gitignored (treat as scratch reference) or committed (kept in history) before the next commit.

## How to work
Use the is-it-magic workflow skills as appropriate:
`/project-investigate` (read-only) → `/project-decide` → `/project-requirements` → `/plugin-implement`.
British English. Read-only investigation never modifies files. Don't commit unless I ask.
