# 0004. Scale planning rigour to change complexity

**Status**: Accepted
**Date**: 2026-08-07 (records a practice established earlier)

## Context

A single pipeline shape is wrong at both ends. Applied to a one-line fix, a full architect-to-review
pipeline is ceremony that costs more than the change. Applied to a subtle platform change, a bare
implement-and-commit flow skips the thinking that would have caught the problem.

The source article describes the same split observed at a team level: platform work still warrants
real planning, while product work increasingly does not.

## Decision

Offer four named rigour modes in `project-implement`, and separate the decision of *what to do* from
the act of doing it.

| Mode | Pipeline |
|---|---|
| `full` | architect, developer, test loop, review loop |
| `draft` | architect, developer. No tests, no review |
| `quick` | developer only |
| `increment` | developer, test loop. No architect, no review |

Draft and increment both end by offering promotion to full, so a cheap start can escalate without
being restarted.

Precede implementation with `/project-decide` where the question is which option to take rather than
how to build it. That skill is strictly read-only, weighs up to four distinct options including
retaining the status quo, infers debt trajectory from investigation evidence, and commits to a
recommendation.

## Consequences

- Cost tracks the work. The expensive path is chosen deliberately rather than by default.
- Escalation is cheap and demotion is impossible, which is the correct asymmetry: a run that turns out
  to be harder than expected can gain rigour, while a run cannot silently lose it.
- Treating "retain the status quo" as a first-class option makes not building something a recordable
  outcome rather than an absence of one. The source article has no equivalent to this at all.
- Four modes plus promotion paths is a real share of the state machine's complexity.

## Relates to

[ADR-0002](0002-weight-the-pipeline-toward-verification.md),
[ADR-0003](0003-enforce-red-green-on-governed-layers.md),
[ADR-0010](0010-keep-skills-deterministic-state-machines.md)
