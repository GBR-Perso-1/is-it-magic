# 0007. Require line-level defensibility as the default

**Status**: Accepted
**Date**: 2026-08-07 (records a practice established earlier)

## Context

There is a genuine philosophical fork in how to relate to AI-written code. The source article
describes one position directly: trusting the code without the ability to read all of it, on the
grounds that at sufficient volume reading everything is not possible and the tests are the real
oracle. One engineer's 500,000-line rewrite was verified this way.

The opposing position, and the one the handbook states, is that an engineer must be able to explain
and defend every line they ship.

Both are defensible. The choice depends on who is shipping.

## Decision

Keep line-level defensibility as the default: "I can explain and defend every line."

The reasoning is pedagogical rather than technical. Judgment is still being manufactured in juniors
(see [ADR-0001](0001-manufacture-judgment-through-codified-doctrine.md)), and reading code you did not
write is how that judgment forms. The source article's own caveat protects this choice: adopting its
practices without its hiring bar risks disappointment.

## Consequences

- Juniors build the reading habit that makes review possible later, rather than learning to defer to a
  green test suite from day one.
- The rule currently has no escape valve. As written it forbids work that is legitimately verified by
  an oracle rather than by reading: mechanical bulk changes, large mechanical migrations, anything
  where nobody reasonably reads the whole diff.
- The boundary is therefore missing rather than wrong. Adding a second tier of oracle-level
  defensibility, with qualifying gates, is tracked as backlog item B2. The hinge already exists in the
  handbook: "reviewability comes from legibility, not size."

## Relates to

[ADR-0001](0001-manufacture-judgment-through-codified-doctrine.md),
[ADR-0002](0002-weight-the-pipeline-toward-verification.md),
[ADR-0008](0008-gate-every-mutating-phase-on-a-human.md)
