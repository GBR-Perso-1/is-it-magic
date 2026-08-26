# 0008. Gate every mutating phase on a human

**Status**: Accepted
**Date**: 2026-08-07 (records a practice established earlier)
**Amended by**: [ADR-0014](0014-raise-correction-loop-budgets-to-three-passes.md) (correction-loop budget: two iterations to three)

## Context

Accountability for shipped code rests with a person, not with a pipeline. The mechanism by which the
lead's judgment enters an otherwise automated flow has to be an explicit point where the flow stops
and asks.

The same gates also serve a second purpose that was not originally designed in: because the lead runs
five to ten sessions in parallel, each gate is a multiplexing point where attention moves to another
session. The lead's attention is the scheduler.

## Decision

Separate read-only phases from mutating ones, and gate the transitions.

- Investigation and decision skills (`project-investigate`, `project-decide`) are strictly read-only
  and never modify code or infrastructure.
- `project-implement` never commits. It always ends by leaving the diff for the user.
- Correction loops escalate to an explicit choice after two iterations rather than continuing.
- Pushing to a remote is never done without confirmation.

## Consequences

- A person decides every irreversible step, which is what makes accountability real rather than
  nominal.
- Gates do not block throughput as once assumed. They are where the operator switches sessions, so
  they function as scheduling points in the parallel-session practice.
- Gated lanes are currently the only lanes. Nothing can run from an issue, overnight, or while the
  operator is away. That gap is tracked as backlog item A5, deliberately scoped as an experiment in
  one repo rather than a change to this decision.
- The context-switching cost of many gates across many sessions is real and is acknowledged in the
  source article as remaining hard even when it gets easier.

## Relates to

[ADR-0005](0005-inject-an-explicit-failure-modes-list.md),
[ADR-0009](0009-commit-direct-to-main.md)
