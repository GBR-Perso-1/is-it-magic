# 0005. Inject an explicit failure-modes list into the AI's context

**Status**: Accepted
**Date**: 2026-08-07 (records a practice established earlier)
**Amended by**: [ADR-0014](0014-raise-correction-loop-budgets-to-three-passes.md) (correction-loop budget: two iterations to three)

## Context

AI coding assistants fail in characteristic, repeatable ways: retrying a failing fix instead of
questioning the framing, inventing abstractions for single-use code, adding error handling for
impossible scenarios, widening scope beyond what was asked. Experienced engineers learn to watch for
these, and in the source article one engineer describes holding exactly such a list in his head.

A model cannot watch for a bias it has not been told about.

## Decision

Write the failure modes down and inject them into the AI's own context, rather than relying on the
human to catch each one after the fact.

The list exists as the "catch yourself" section of the engineering handbook and as the "Reason Before
You Act" doctrine in `rules/general.md`, which auto-loads into every session. The same discipline is
restated as constraint blocks inside every pipeline agent, so an agent carries it even when spawned
without the ambient rules.

One consequence is encoded as a hard cap rather than advice: if a fix fails twice, stop and reassess,
because the framing is usually wrong. Every correction loop in `project-implement` is capped at two
iterations and then escalates to the user.

## Consequences

- The bias list is available at the moment of generation rather than only at review time.
- Because it is written, it can be improved when a new failure mode is observed, and the improvement
  reaches every session at once.
- Retries and redundancy get conflated by the cap. An independent fresh-context second opinion is not
  a retry, and the current caps suppress both equally. This is tracked as backlog item A4.
- Triple encoding across rules, handbook and agent constraint blocks is a maintenance burden and is
  already drifting. Tracked as backlog item B5.

## Relates to

[ADR-0001](0001-manufacture-judgment-through-codified-doctrine.md),
[ADR-0008](0008-gate-every-mutating-phase-on-a-human.md)
