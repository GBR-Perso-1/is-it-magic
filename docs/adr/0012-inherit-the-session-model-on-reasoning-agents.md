# 0012. Inherit the session model on the reasoning agents

**Status**: Superseded by [ADR-0015](0015-repin-the-reasoning-agents-to-sonnet.md)
**Date**: 2026-08-07
**Amended by**: [ADR-0014](0014-raise-correction-loop-budgets-to-three-passes.md) (the review loop that bounds reviewer cost now allows three runs)

## Context

All fourteen agents carried `model: sonnet`, so none inherited the session model. Running a stronger
model at the orchestrator bought nothing below it: every agent that actually reads code, plans, or
reviews ran on the pinned model regardless.

This put the lowest spend exactly where the source article locates the highest value, describing AI
review as catching bugs that would otherwise take an hour to find, with expense as the named caveat.
The point is sharper in this context than in the article's, because the reviewers are also teaching
artefacts: a junior promoting a draft run to full is being shown what good review looks like, and weak
reviewers teach weakly.

The constraint the article does not have is a token budget. Breaking it uniformly was not an option.

## Decision

Set `model: inherit` on `architect`, `reviewer-design` and `reviewer-perf`. Leave the other eleven
agents pinned to `sonnet`.

Use the explicit `inherit` value rather than omitting the field. Omission produces the same behaviour,
since `inherit` is the documented default, but the explicit form reads as a deliberate choice and
repins in one word.

Per-run cost across the pipeline ranks roughly: `developer` far above `test-writer`, above `architect`,
above the read-only reviewers.

**The two reviewers are the safe part.** They are diff-scoped, single-pass, capped at two runs by the
review loop, and spawn only in full mode or on explicit promotion to it. Unpinning them has no effect
outside the mode already chosen for rigour, and their cost tracks the size of the change.

**`architect` is the accepted risk.** It also runs in draft mode, which exists to be cheap, and its
cost scales with repository size rather than diff size.

**`test-writer` stays pinned**, resolving an open question. It is spawned fresh up to three times per
RED to GREEN run with no context reuse, making it the pipeline's worst cost multiplier, and deriving
assertions from requirements is its most mechanical duty.

## Consequences

- Planning and the two judgment-heavy reviewers run on the session model, so choosing a stronger model
  for a session now propagates to where it matters.
- Full-mode runs cost more. Draft-mode runs also cost more, via `architect`, which is the leak to
  watch.
- Five to ten parallel sessions multiply any per-run delta, so this should be trialled before it
  becomes the default posture.
- Reversal is one word: set `architect` back to `sonnet`. If draft-mode spend is the only problem, the
  tighter fix is a full-mode-only model override at the spawn site in `project-implement`, leaving the
  frontmatter pinned.

## Relates to

[ADR-0002](0002-weight-the-pipeline-toward-verification.md),
[ADR-0004](0004-scale-planning-rigour-to-complexity.md),
[ADR-0013](0013-scan-for-security-on-cadence-not-per-change.md)
