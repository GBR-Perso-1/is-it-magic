# 0003. Enforce RED to GREEN test-first on governed layers

**Status**: Accepted
**Date**: 2026-08-07 (records a practice established earlier)
**Amended by**: [ADR-0014](0014-raise-correction-loop-budgets-to-three-passes.md) (correction-loop budget: two iterations to three)

## Context

A test that has never been observed to fail proves nothing about the code it covers. It may be
asserting something trivially true, or exercising a path that does not reach the change at all. The
sharpest verification practice in the source article is one engineer's personal habit: require that a
test fails on the unpatched build and passes on the patched one.

Held as a habit, this depends on the engineer remembering to do it under time pressure.

## Decision

Encode the fail-first proof as policy rather than habit, and scope it to the layers a project declares
as governed.

`project-implement` resolves `TEST_FIRST_ACTIVE` in Phase 1 by reading the project's convention
bundles for a `## Testing Policy` heading and its `**Governed layers**` list, then intersecting that
list against the architect's planned change surface. When the change touches a governed layer:

1. The developer scaffolds the matched files as compiling signatures and stubs, with no behaviour,
   while implementing everything else fully.
2. A test-writer runs and must return a `CONFIRMED_RED` verdict, proving the tests fail against the
   stub.
3. Only then is the developer instructed to implement to GREEN.
4. A fresh test-writer verifies GREEN.

The policy applies automatically with no user gate, because it is a policy rather than a decision
point. It defaults to inactive and is only ever switched on by that resolution step.

## Consequences

- Every test on a governed layer has been observed failing for the right reason before it was trusted.
- Projects opt in by declaring governed layers in their convention bundles, so the policy travels with
  the project rather than being imposed uniformly.
- The flow needs distinct loop budgets: a scaffold-defect sub-loop capped at two attempts, tracked
  separately from the GREEN dev-to-test loop capped at two. This is a meaningful share of the
  complexity that [ADR-0010](0010-keep-skills-deterministic-state-machines.md) commits to carrying.
- Draft mode cannot retrofit RED to GREEN, because it implements behaviour directly with no stub
  phase. Promoting a draft to full therefore runs the non-test-first path.

## Relates to

[ADR-0002](0002-weight-the-pipeline-toward-verification.md),
[ADR-0004](0004-scale-planning-rigour-to-complexity.md)
