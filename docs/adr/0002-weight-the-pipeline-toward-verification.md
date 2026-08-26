# 0002. Weight the pipeline toward verification

**Status**: Accepted
**Date**: 2026-08-07 (records a practice established earlier)
**Amended by**: [ADR-0014](0014-raise-correction-loop-budgets-to-three-passes.md) (the correction cycles this record counts as verification now run up to three times)

## Context

When code generation becomes cheap, the scarce resource stops being implementation and becomes
confidence that the implementation is correct. The source article puts the split at roughly 85 per
cent implementation effort to 15 per cent verification effort in terms of where engineers' attention
now goes, with verification default-on and repeated.

A specific failure mode threatens AI-assisted testing: tests written by reading the implementation
merely restate what the code does, so they pass by construction and prove nothing. The article never
names this risk.

## Decision

Spend the majority of the `project-implement` full-mode pipeline on verification rather than
production. Of the agent slots in a full run, roughly six of eight verify: `test-writer`,
`reviewer-quality`, `reviewer-design`, `reviewer-perf`, and the correction cycles they trigger.

Bind the test author to the requirements, never to the implementation. The `test-writer` agent
receives the original requirements and the architect's Test Strategy section, and in Increment mode
receives an explicit instruction that the requirement brief is the sole authoritative specification
and scenarios must not be invented from the implementation.

## Consequences

- Tests assert what was asked for, so they can fail on a wrong implementation. Tests derived from the
  implementation cannot.
- Verification dominates the token cost of a full run. `test-writer` in particular is spawned fresh on
  every iteration with no context reuse, which makes it the pipeline's largest cost multiplier and is
  why it stays pinned to a cheaper model under
  [ADR-0012](0012-inherit-the-session-model-on-reasoning-agents.md).
- Full mode is correspondingly slow and expensive, which is the reason cheaper modes exist at all. See
  [ADR-0004](0004-scale-planning-rigour-to-complexity.md).

## Alternatives considered

**Fuzzing.** High value for a runtime or parser, where the input space is adversarial and an oracle is
cheap. Rejected here: the portfolio is line-of-business applications whose failure modes are
requirement mismatches rather than malformed input handling. Revisit only if a parser-like component
appears.

## Relates to

[ADR-0003](0003-enforce-red-green-on-governed-layers.md),
[ADR-0012](0012-inherit-the-session-model-on-reasoning-agents.md),
[ADR-0013](0013-scan-for-security-on-cadence-not-per-change.md)
