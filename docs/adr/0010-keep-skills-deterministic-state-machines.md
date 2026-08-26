# 0010. Keep skills deterministic state machines

**Status**: Accepted (conditional on the prompt-debt ritual)
**Date**: 2026-08-07 (records a practice established earlier)

## Context

There is direct tension here with the source article. Claude Code's own system prompt had roughly 80
per cent of it deleted, on the reasoning that the model had become capable enough that most of the
instruction was no longer earning its place, and that assumptions must be revisited with each model
generation.

`project-implement` runs the other way: a roughly 300-line state machine with nested loop counters, a
shared iteration budget across two sub-loops, five distinct RED and GREEN verdict cases, and explicit
git plumbing. Four months of steadily accumulating determinism.

## Decision

Keep the determinism. The artefact is a transmission mechanism, not a prompt.

A junior invoking `/project-implement` must get the lead's workflow, reproducibly, rather than the
model's interpretation of it on that particular day. Consistency is a feature when the thing being
transmitted is a way of working. Deleting the scaffolding would return variance to exactly the place
[ADR-0001](0001-manufacture-judgment-through-codified-doctrine.md) is trying to remove it from.

This decision is explicitly **conditional**. Determinism must be re-earned per model generation, not
assumed permanent.

## Consequences

- Behaviour is reproducible across operators and sessions, which is what makes the skill teachable.
- The skills are long and their control flow has to be maintained by hand. Complexity concentrates in
  `project-implement`.
- Without a countervailing ritual, the state machine only ever grows, and instruction that has stopped
  earning its place is indistinguishable from instruction that still does.
- The countervailing ritual is therefore part of this decision, tracked as backlog item C1: on each
  model generation, halve the largest skill, run both versions against the same requirement, compare,
  and keep the cut if it holds. If C1 is never run, this decision should be revisited rather than
  silently retained.

## Relates to

[ADR-0004](0004-scale-planning-rigour-to-complexity.md),
[ADR-0006](0006-compound-solved-problems-into-skills.md)
