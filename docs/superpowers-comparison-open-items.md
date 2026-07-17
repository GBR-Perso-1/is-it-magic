# is-it-magic vs superpowers — open items to investigate later

> **Purpose**: park the findings from the `is-it-magic` ↔ `superpowers` comparison so they can be
> picked up cold. Focuses on the three methodology areas where a real (or partial) gap exists.
> **Date captured**: 2026-07-16. **Status**: read-only investigation output — nothing implemented, nothing committed.

## TL;DR (so this doc stands alone)

- **`is-it-magic` is not a cheap clone of `superpowers`.** They are different categories of tool.
  Superpowers is a *methodology/discipline layer* (14 auto-activating ritual skills: TDD, debugging,
  brainstorming, worktrees, code review). is-it-magic is a *personal toolkit + deterministic orchestrator*
  (18 skills, 16 agents) with a large operational surface superpowers has **nothing** for — Azure, GitHub
  ops, security scanning, dependency upgrades, machine setup, plugin authoring, cross-project porting.
- **Verdict: keep is-it-magic.** ~two-thirds of it has no superpowers equivalent.
- **Methodology is not "thin" — it's *ambient* rather than *ritual*.** is-it-magic delivers discipline as
  always-on standing rules (`rules/general.md` + `paths:`-scoped per-language rules) plus constraints baked
  into agents. Superpowers delivers the same discipline as invokable step-by-step rituals. Different
  mechanism, not different depth.
- **Only one genuine *new capability* gap: test-first TDD.** Brainstorming and verification are already at
  parity (`project-requirements`, `general.md` "Understand & Verify"). Debugging is near-parity.
- Author of superpowers: **Jesse Vincent (obra) + Prime Radiant** — a community plugin distributed *through*
  Anthropic's marketplace, **not** an official Anthropic product.

The three items below are the only ones left worth a decision.

---

## 1. Test-driven development — the one real capability gap

**Gap severity: real, but a philosophical choice — not a deficiency.**

- **What superpowers does**: `test-driven-development` enforces RED-GREEN-REFACTOR. A failing test must exist
  *before* any production code, enforced hard ("delete the code and start over" if you skip it). ~2,000 words,
  13 rationalisation-counters, checklists. The most opinionated, heaviest part of superpowers.
- **What is-it-magic has today**: test-*after*. In `project-implement`, the developer writes code (Phase 2),
  then `test-writer` writes tests (Phase 3) deriving scenarios **from the requirements/test-strategy, not from
  the implementation**. Good discipline — but the code exists first. No skill drives writing a failing test
  before implementation.
- **The actual gap**: test-first vs test-after are *different practices*, not different packaging. This is the
  one net-new thing superpowers offers.

**Open questions to resolve when picking this up:**
- Do I actually *want* test-first as a default discipline, or is spec-derived test-after the right call for my
  work (which includes plugin authoring, infra, exploratory changes where hard TDD is often too rigid)?
- If yes: import as a *new standalone skill* (e.g. `project-tdd` / a discipline skill) or fold a "test-first"
  mode into `project-implement`? Note the current pipeline is architect→dev→test→review; a RED-first loop
  inverts dev↔test ordering.
- How hard to enforce? Superpowers' "delete your code" is dogmatic; my house style (`_ux-rules.md`,
  gated pipelines) is interactive. A softer "write the failing test first, confirm RED, then implement" gate
  may fit better than deletion threats.

---

## 2. Systematic debugging — minor gap, mostly mechanism

**Gap severity: minor. I already have the principles and an investigation skill; I lack a single always-available ritual.**

- **What superpowers does**: `systematic-debugging` — a dedicated 4-phase protocol (reproduce → isolate/trace →
  understand root cause → fix + verify) with a hard gate: **"do not fix what you have not understood."**
- **What is-it-magic has today** (two places):
  - `rules/general.md:38-44` "Reason Before You Act" — codebase is source of truth; **"if a fix fails twice,
    stop and re-frame instead of retrying variations"**; don't add the Nth patch to a wrong structure.
  - `project-investigate` **bug-hunt mode** — quick-scan → evidence-grounded root-cause report, read-only.
- **The actual gap**: I have the *principles* (rule) and a *structured investigation* (skill), but not a
  single "when stuck mid-task, drop into this 4-phase protocol" ritual that fires during implementation.
  Superpowers is also more prescriptive about the exact sequence.

**Open questions to resolve when picking this up:**
- Is `project-investigate` bug-hunt mode + the `general.md` rule already enough in practice, or do I hit cases
  mid-implementation where a dedicated debug ritual would have helped?
- If worth building: a lightweight standalone `debug` skill (reproduce → isolate → root-cause gate → fix →
  verify), or just make the existing `general.md` debugging principles more prescriptive?
- Lowest-effort option: none — this may already be adequately covered. Decide whether the gap is worth any work at all.

---

## 3. Git worktrees — low value for a solo developer

**Gap severity: mechanism gap; genuinely low priority solo.**

- **What superpowers does**: `using-git-worktrees` — isolates each unit of work (and each parallel subagent)
  on its own branch/working directory, with a verified test baseline before work starts.
- **What is-it-magic has today**: nothing. `project-port`/`project-locator`/`session-to-skill` do directory-based
  sibling discovery, but that is not branch/worktree isolation.
- **Honest solo assessment**:
  - The headline rationale (stop parallel subagents colliding) mostly *doesn't apply* one-task-at-a-time.
  - Real solo value is narrow: (a) an agent churns on a branch in an isolated dir while my main tree stays
    untouched; (b) run a long build/test in one worktree while editing in another; (c) hotfix without stashing
    a half-done feature.
  - Pairs naturally with how I already work **only if** I run background/parallel agents — my plugin *is*
    agent-heavy, and the environment already supports agent worktree isolation (Agent tool `isolation:"worktree"`,
    Claude Code EnterWorktree/ExitWorktree).

**Open questions to resolve when picking this up:**
- Do I actually run background/parallel agents often enough to benefit? If I mostly drive one task
  interactively → **skip this entirely.**
- If yes: do I need a *skill* at all, or just lean on the built-in Agent `isolation:"worktree"` option when
  spawning agents from my orchestration skills (`project-implement`, `repo-security-scan`)?

---

## What's NOT a gap (settled — don't re-litigate)

- **Brainstorming**: `project-requirements` is a full brainstorming skill and arguably *better* separated —
  it stays at the *what* (requirements) and pushes *how* (design) to the `architect` step, whereas superpowers'
  `brainstorming` blends clarify + design into one gate. **Parity or better.**
- **Verification before completion**: covered by `general.md:46-49` "Understand & Verify" —
  *"'It should work' is not done — build it, run it, and observe the behaviour you changed."* **Parity.**
- **Everything operational** (Azure, GitHub, security, upgrades, devbox, plugin authoring, porting): superpowers
  has no equivalent. **is-it-magic only.**

## How to resume

Pick one item above, then run `/project-decide` (it reads findings from conversation) or
`/project-requirements` to spec it — then `/project-implement` to build. Decide TDD first: it's the only item that changes a real capability.
