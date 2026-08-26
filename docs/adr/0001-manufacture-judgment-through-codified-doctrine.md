# 0001. Manufacture judgment through codified doctrine

**Status**: Accepted
**Date**: 2026-08-07 (records a practice established earlier)

## Context

Engineering judgment is normally acquired, not taught: an organisation hires for it and transmits it
as oral culture. The source article closes on exactly this worry, asking whether the practices it
describes only work if you can hire standout engineers, and warning that copying them without the
same hiring bar "could well result in disappointment".

This operating model cannot rely on hiring. It serves one lead engineer plus juniors who are meant to
inherit the lead's way of working across a portfolio of line-of-business applications.

## Decision

Codify judgment rather than assume it. Every element of the way of working is written down,
versioned, and installable:

- Six ambient rules auto-loaded into every AI session.
- An engineering handbook, in a human variant and an AI variant.
- A Socratic coach skill for juniors.
- Constraint blocks embedded in every pipeline agent.
- "Not yet justified" treated as a first-class review finding.

The handbook's lifecycle steps map one-to-one onto the skill suite, so doctrine and automation are the
same shape rather than two parallel systems that can drift apart in intent.

## Consequences

- Judgment becomes transmissible without the lead being present, which is what makes juniors able to
  inherit the practice at all.
- The doctrine is versioned and diffable, so a change to how the team works is reviewable like code.
- Cost: the same principles now live in several places (rules, two handbook variants, agent constraint
  blocks) synchronised by memory. Drift is already observable and is tracked as backlog item B5.
- Cost: written doctrine must be re-earned as models improve, or it ossifies. See
  [ADR-0010](0010-keep-skills-deterministic-state-machines.md).

## Relates to

[ADR-0005](0005-inject-an-explicit-failure-modes-list.md),
[ADR-0006](0006-compound-solved-problems-into-skills.md),
[ADR-0007](0007-line-level-defensibility-as-the-default.md)
