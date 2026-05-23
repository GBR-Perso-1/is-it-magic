# project-decide — Option 3 Reference: Rebuilt Evaluation Model

> Status: **Deferred** — preserved for future implementation.
> This document records Option 3 from the project-decide skill evolution design session. Option 2 (Maturity-aware stance calibration) was implemented first. Option 3 builds on Option 2 and should be considered when the team is ready for a deeper structural rework of the evaluation phase.

---

## The Problem It Solves

Option 2 introduces a recommendation stance that shifts the framing of option generation and evaluation based on project maturity and debt tolerance. However, the stance is a single upstream signal — it biases the evaluation but does not change the evaluation rubric itself. The underlying model still evaluates each option independently on pros/cons and effort. It does not model:

- How debt trajectory evolves over time under each option (i.e., which option makes future decisions easier or harder)
- Whether the current project context makes architectural investment recoverable in a reasonable timeframe
- The distinction between "architecturally correct against sound principles" and "architecturally correct for this project at this stage"

Option 3 replaces the informal evaluation narrative with a structured three-part rubric that makes these dimensions explicit and auditable.

---

## The Design

### Three-Part Evaluation Rubric

Each solution option is evaluated against three named lenses, scored qualitatively (Favourable / Neutral / Unfavourable), with a one-sentence evidence statement for each:

**Lens 1 — Debt Trajectory**
Does this option reduce, hold steady, or increase the codebase's debt load? Consider not just the change itself but the precedent it sets for future decisions in the same area. A shortcut that is isolated and reversible scores differently from one that embeds a pattern others will follow.

**Lens 2 — Project Maturity Fit**
Given where this project is in its lifecycle, is the cost of this option recoverable? A high-effort structural refactor in a pre-production codebase is low-risk to schedule; the same refactor in a production system with active users carries a different risk profile. Score this option against the maturity and debt-tolerance context captured in Phase 0.5.

**Lens 3 — Architectural Correctness**
Does this option move toward or away from sound design principles (separation of concerns, appropriate abstraction boundaries, cohesion, coupling)? Assess against principles — not against what the existing codebase does today. The existing codebase's conventions are evidence of the current state, not the target state.

### Scoring and Recommendation

After scoring all options on all three lenses:
1. The option with the most Favourable scores across all three lenses is the default recommendation.
2. If scores are split, the Recommendation Stance (from Phase 0.5) acts as the tiebreaker: Structural correctness first weights Lenses 1 and 3; Minimal disruption first weights Lens 2.
3. The recommendation rationale must cite the lens scores explicitly — not replace them with prose.

### Report Format Change

The Decision Report's **Recommended Option** section gains a structured rubric block:

```markdown
### Recommended Option

**Option {N}: <title>**

| Lens | Score | Evidence |
|------|-------|----------|
| Debt Trajectory | Favourable / Neutral / Unfavourable | <one sentence> |
| Project Maturity Fit | Favourable / Neutral / Unfavourable | <one sentence> |
| Architectural Correctness | Favourable / Neutral / Unfavourable | <one sentence> |

<rationale — 2–4 sentences explaining the recommendation given the scores and Recommendation Stance>
```

---

## Why Phases 2 and 3 Must Be Redesigned Together

Option 3 cannot be applied only to Phase 3. Option generation in Phase 2 must also be aware of the rubric, because:

- The "debt trajectory" lens requires that at least one option explicitly model the long-term debt trajectory — not just the immediate change. This may produce an option type that does not currently exist in the mandatory option set (e.g. "incremental structural migration" as distinct from "full structural overhaul").
- The "project maturity fit" lens requires Phase 2 to generate options at granularities appropriate to the project stage. In a pre-production project, a full structural rewrite and a targeted refactor may both be viable; in a production system with users, intermediate options (feature flags, parallel implementations, strangler fig patterns) deserve explicit generation.
- If Phase 3's rubric evaluates options that Phase 2 never generated, the rubric has no surface to act on.

The practical implication: Option 3 requires updating the **Mandatory option types** rules in Phase 2 to mandate at least one option that models the debt trajectory explicitly, alongside the existing smallest-safe-change and structurally-correct mandates.

---

## Dependencies

- **Option 2 must be in place first.** Option 3 extends the Recommendation Stance signal introduced by Option 2 — it does not stand alone.
- **Phase 0.5 remains unchanged.** The two user questions and the stance derivation table from Option 2 carry over directly.
- **The Constraints section must remain untouched.** The read-only, no-agents, no-file-I/O constraints are non-negotiable regardless of how deeply the evaluation model is rebuilt.

---

## Risks and Open Questions

- **Rubric fatigue**: A three-lens scored table per option in every Decision Report may feel bureaucratic for simple decisions. Consider whether the rubric should be omitted (or collapsed to prose) when the problem is low-complexity and all options score identically on two of three lenses.
- **Subjectivity of "Architectural Correctness"**: Without an explicit set of principles the model applies consistently, two runs of the same skill on the same findings could produce different scores. A future iteration might reference a shared principles document (e.g. `skills/shared/_architecture-principles.md`) as the scoring standard.
- **Backwards compatibility**: The Decision Report format change (adding a rubric table) may look unfamiliar to users accustomed to the prose-only format. Consider a transitional format where the rubric table is presented as an appendix rather than inline in the recommendation block.
- **Option 3 scope boundary**: Does Option 3 also change how the skill handles conflicts between the Recommendation Stance and the rubric scores? This is not specified here and should be resolved before implementation begins.
