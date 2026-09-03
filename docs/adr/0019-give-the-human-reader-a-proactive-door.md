# 0019. Give the human-reader path its own proactive door

**Status**: Accepted
**Date**: 2026-09-03
**Scopes**: [ADR-0011](0011-author-reports-in-markdown.md)

## Context

The investigation surface has two consumers today, and they have never been told apart in the
tooling:

| | Path A — pipeline | Path B — human reader |
|---|---|---|
| Consumer | `/project-decide` (a machine, reading conversation text) | a person orienting on an app |
| Output shape | prose report, unbounded | diagram-led, bounded |
| Current door | `/project-investigate` | none — reactive only, via `dumb-down` |

Four facts, each independently verified against this repository before this decision was taken:

1. **Zero hits** for `mermaid|diagram|flowchart|graph TD|sequenceDiagram` across `skills/`,
   `agents/`, `rules/`. Nothing in the plugin today produces or expects a diagram.
2. **Exactly one length bound in the whole plugin**: `agents/codebase-explorer.md:54` — "the whole
   summary should fit in roughly 200-400 words". No other skill or agent states a size cap on its
   output.
3. **Zero hits** for a data-ownership frame (system of record vs borrowed/read vs copy vs writes
   back) anywhere in `skills/` or `agents/`. No existing output distinguishes what a system owns
   from what it merely reads or mirrors.
4. **The report text printed in the terminal *is* the machine handoff.** `skills/project-decide/SKILL.md`
   Phase 0 step 1 locates its input by scanning conversation text for an Investigation Report or a
   Debug Report heading — there is no separate machine channel. `skills/shared/_ux-rules.md`'s
   "never re-validate suite-produced input" rule depends on that same report body being the thing
   the user already approved; a change to that body's shape is a change to what the rule protects.

Path A cannot be made diagram-led or bounded without weakening it as a machine handoff: a mermaid
block is not conversation text `/project-decide` can scan headings out of, and a 200-400 word cap on
an Investigation Report would drop exactly the detail `/project-decide` reasons over. Path B has no
door of its own at all — a person wanting a first-pass orientation to an unfamiliar app has to either
force `/project-investigate`'s unbounded prose report to double as an orientation, or wait until an
earlier explanation has already landed badly and use `dumb-down` reactively.

## Decision

Path B gets its own proactive door: a new skill, `explain-visually`, that produces a four-section,
diagram-led, bounded orientation (data model, users and roles, workflow, data ownership) grounded in
the existing 200-400 word bound and the existing altitude cap already precedented in
`agents/codebase-explorer.md`.

Path A is left alone. `project-investigate`'s three user-facing report templates (the no-argument
archaeology summary, the Debug Report, the Investigation Report) gain a strictly additive ASCII
digest header — `## At a glance` — above the existing heading in each. The report bodies below that
heading are byte-identical to before this decision.

`dumb-down` — renamed to match the user's own vocabulary for what it does — is kept, not
folded into the new skill or replaced by it. It receives three narrow edits: its
`description` gains a hand-off clause pointing a first-pass-orientation request at
`explain-visually`, plus a set of jargon-facing trigger phrases; Rule 4 is qualified so that a
diagram is an admissible explanation where the confusion is structural, rather than prose being the
only sanctioned form; and a new Rule 6 requires plain word choice across every line of the rewrite,
not just its worked example.

This scopes [ADR-0011](0011-author-reports-in-markdown.md) rather than amending it — load-bearing,
so recorded here explicitly. ADR-0011 keeps Markdown as the authoring format for all reports and
working documents, rejecting HTML as an alternative authoring format. This decision does not
revisit that: Markdown remains the source of truth for `explain-visually`'s output — the persisted
orientation file in `.claude/reports/` is Markdown with fenced mermaid blocks, exactly as ADR-0011
already permits for any report. A rendered Artifact, where the surface supports one, is a *render*
of that Markdown file — not a second authoring format competing with it, and not something authored
independently of the Markdown. ADR-0011 stands unamended.

## Consequences

- Agent count is unchanged at 14 — no new agent file, and `agents/codebase-explorer.md` is not
  edited.
- Skill count moves 19 → 21 in `README.md` and `.claude/CLAUDE.md`. This also fixes a pre-existing
  drift: commit `f81ded2` added the skill then named `explain-plainly` (now `dumb-down`)
  without updating either document's count or skill list, so the true count was already 20
  (undercounted by one) before this decision added the 21st.
- Within the two skills this decision touches — `explain-visually` and `dumb-down` — mermaid
  is now permitted inside written `.md` files and rendered Artifacts, and is **forbidden** in
  terminal output; printing unrendered mermaid source at a terminal user is a failure there, not a
  degraded fallback, and the fallback is an ASCII substitute. This is scoped to those two skills, not
  an ambient rule, and no rule file is added by this decision — a consumer-scoped ambient rule was
  considered and rejected below.
- The diagram legibility caps introduced here (at most one diagram per section, at most ~12 nodes
  each) and the digest bound introduced in `project-investigate` (at most 8 lines, at most ~60
  words) are new conventions, not inherited from any existing file, and are therefore in scope for
  the prompt-debt ritual proposed in the open backlog
  (`docs/anthropic-practices-gap-open-items.md`, "Prompt-debt ritual per model generation") the
  next time it runs.
- This is a released skill, so its rename is a breaking change for the slash command surface:
  `/explain-plainly` no longer resolves, `/dumb-down` replaces it. Accepted, because anyone with the
  old name in muscle memory or in a written reference has no automatic fallback — the cost of a
  clearer name paid once, now, rather than compounding it by keeping a name the user has already
  said does not fit.

## Alternatives considered

1. **Route `project-investigate` into a bounded, diagram-led agent.** Rejected: this compresses the
   machine handoff. `/project-decide` reasons over the full Investigation/Debug Report body; a
   200-400 word cap and mermaid-only diagrams would drop exactly the evidence it needs, for the sake
   of a consumer (a human skimming) that Path A does not serve today and should not be made to serve
   at Path B's expense.

2. **A consumer-scoped ambient rule** (e.g. "if the reader is human, render diagrams"). Rejected: a
   rule cannot carry a four-section outline, a diagram-count bound, or a data-ownership inference
   rubric — that is a skill's job, not a rule's. It would also require judging "is this an agent or a
   human reader" per invocation, and a wrong judgement degrades Path A for the times it guesses
   wrong.

3. **Upgrade `agents/codebase-explorer.md` in place** to the four-section, diagram-led shape.
   Rejected: `skills/project-requirements/SKILL.md:56` depends on the agent's current output shape
   (Business Purpose / Key Business Domains / Core Features / Users & Context) for its "State of the
   App" summary. Changing the agent's default shape breaks that consumer; `explain-visually`
   overrides the shape per spawn instead, leaving the agent file — and its existing contract with
   `project-requirements` — untouched.

4. **Fold the capability into `dumb-down`.** Rejected: `dumb-down` is reactive by
   construction — its Rule 1 re-derives a claim from source because a *previous* explanation already
   missed — and it is prose-first (Rule 2, Rule 3). A first-pass orientation has no previous
   explanation to re-derive from, and needs diagrams as the primary carrier, not prose with an
   occasional diagram. Two distinct jobs stay two distinct skills.

5. **A hand-authored HTML companion**, following the precedent of
   `docs/lecture-contre-lecture-anthropic.html`. Rejected: that file is bespoke per document — written
   once, for one piece of source material — and, checked directly, contains zero diagrams. It is not
   a repeatable mechanism and does not answer the diagram-led requirement at all.

6. **A dedicated new agent for the scan**, rather than reusing `codebase-explorer` with an override.
   Rejected *for now*: the four-section shape can be carried entirely as an override prompt on the
   existing agent, exactly as `project-investigate` already does against `repo-archaeologist` for its
   Bug Location and Code Investigation Report shapes. Promotion trigger: if a second skill needs the
   same diagram-led shape from a *different* base agent, or if the override prompt itself grows past
   what a single spawn instruction can carry cleanly, that is the point to extract a dedicated agent.

## Relates to

[ADR-0010](0010-keep-skills-deterministic-state-machines.md),
[ADR-0011](0011-author-reports-in-markdown.md)
