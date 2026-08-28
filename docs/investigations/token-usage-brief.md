# Token-usage investigation (28 August 2026)

**Status**: measured on the **secondary** machine only. The `/usage` panel screenshot that started this
(38 sessions, 5.6b tokens, labelled "last 7 days") never matched that machine's transcripts (8 sessions,
75m true tokens in 7 days), so it was taken elsewhere, almost certainly the main machine. The ranking of
causes in section 4 is therefore provisional until re-measured there. The plugin-source findings in
section 2 do not depend on the machine and are settled.

Plugin source at commit `a57af59`, installed plugin 6.3.0. Written by a Claude Code session on the
secondary machine.

## How to use this file (next session, on the main machine)

1. `git pull` so this folder is present.
2. Run the scan (Python 3, no dependencies, writes nothing):
   `python docs/investigations/token-usage-scan.py > docs/investigations/token-usage-results-main.txt`
   Add `--days 60` if the heavy period is older than a month.
3. Start `/project-investigate` with:
   *"Re-measure token usage on the main machine per `docs/investigations/token-usage-brief.md` and the scan
   output in `token-usage-results-main.txt`. Treat section 2 as established (do not re-read the plugin source
   for it), test the hypotheses in section 3, fill section 6. Compare with section 4."*
4. Then `/project-decide`; it should re-weight the options in section 7 rather than invent new ones.

## 1. Question

Which structural choices in `is-it-magic` drive the limit consumption reported by the panel (developer 40%,
test-writer 10%, reviewers ~11%, 97% subagent-heavy, 69% of usage at >150k context, 42% with 4+ parallel
sessions), and is any of it a mistake rather than a deliberate trade?

## 2. Machine-independent findings (established from the plugin source)

| # | Finding | Evidence |
|---|---|---|
| S1 | Full and increment modes **skip the test-writer** when the developer's inline smoke run is clean. The sentence contradicts the bullet that follows it, and in increment mode it jumps straight to Done, defeating that mode's purpose. Observed in transcripts (section 4). | `skills/project-implement/SKILL.md:98` ("Skip directly to Phase 4 if the inline run was clean"), `:257` (same, Phase 3) |
| S2 | The developer agent has **no turn budget**, no "do not re-read what you already hold", no batching guidance. Its only brake is the agent-scale heuristic "if a fix fails twice, re-frame". | `agents/developer.md`; `rules/general.md:43` |
| S3 | All four verifiers scope themselves from the **git working tree**, not from the plan's file list, and read matched files in full (design reviewer adds the dependency closure). The skill never commits, so scope is the session's cumulative dirt. | `agents/test-writer.md:45`, `reviewer-design.md:24-25`, `reviewer-perf.md:23`, `reviewer-quality.md:26-30`; `SKILL.md:10, 239, 282` |
| S4 | The review loop re-enters the full test loop; both were raised from 2 to 3 on 26 Aug (`9214a09`). Worst case is 9 fresh test-writer spawns (was 4), a 2.25x increase where ADR-0014 recorded "roughly half". | `SKILL.md:103, 159, 161`; `docs/adr/0014` |
| S5 | ADR-0012 unpinned `reviewer-design` and `reviewer-perf` to the session model on a "diff-scoped" premise that S3 shows is not implemented. | `docs/adr/0012` |
| S6 | Suite **state lives in the conversation**: `project-decide` forbids file I/O and reads the report from context; `project-implement` re-enters phases "carrying forward" earlier output. `/clear` between handoffs loses the chain. The orchestrator also runs heavy Bash itself (`project-port` copies, `repo-commit` test runs), whose output lands in its own context. | `skills/project-decide/SKILL.md` constraints; `project-implement` Draft and Increment "Promote" notes |
| S7 | `repo-archaeologist`'s system prompt is exhaustive (all data models, all routes, all docs). `project-investigate`'s "targeted investigation" instruction cannot switch that off. | `agents/repo-archaeologist.md` Phase 2 |
| S8 | `~/.claude/stats-cache.json` sums **one usage record per streamed content block** (thinking, text, each tool_use all carry the same usage object). The panel over-counts by ~2.2x on every fully preserved day. Claude Code issue, not the plugin's; feedback drafted. | scan section A (cache total equals the raw record sum to the decimal; de-duplicated total is ~45% of it) |

## 3. Hypotheses to test on the main machine (ranked by the secondary-machine result)

| # | Hypothesis | Scan sections |
|---|---|---|
| H1 | Orchestrator (main) sessions are the largest bucket because context sits at 500k to 1M for days with 0 to 2 compactions; capping at 200k would save most of it. | C, G, H |
| H2 | `developer` is the largest agent and its cost is **turns x ~160k**, not peak context: runs average ~95 turns in a one-edit, one-test, one-re-read loop. Capping its context saves little; halving turns halves its share. | D, F, H |
| H3 | Full-mode runs skip the test-writer (S1) on the main machine too. | E, I |
| H4 | Verifiers plus architect are second-order (~14% here); model pinning is negligible because architect and design reviewer ran on Sonnet for most of their turns anyway. | D |
| H5 | Panel inflation of ~2.2x holds there too. | A |
| H6 | *(only testable there)* Which projects and skills drive the main-machine sessions, and whether the shape differs (e.g. `project-port` or `repo-commit` heavy, more parallel sessions, longer autonomous runs). | B, G |

## 4. Secondary-machine results (28 Aug 2026), for comparison

Machine: Windows profile `gbrourhant_ekla.co.u`. Transcripts on disk from 27 Jul (earlier ones partially
cleaned up, so the 30-day figure is a floor). "True" means de-duplicated by requestId.

| Window | Panel-style count | True tokens | Sessions |
|---|---|---|---|
| Last 7 days (21 to 28 Aug) | 161m | 75m | 8 |
| Last 30 days | 3.0b | 1.29b | ~47 |

The spike is one sprint: 27 Jul to 6 Aug consumed 1.1b true tokens in 11 days (one-fleet session 94h with
53 agents; justi-fi 55h with 16 agents). Quiet days are 5 to 20m true.

Ranking, last 30 days, true tokens:

| Consumer | Share | Runs | Turns/run | Avg peak ctx |
|---|---|---|---|---|
| Orchestrator sessions | 49% | 47 | 52 | up to 996k |
| `developer` | 28% | 23 | 95 (max 275) | 193k (max 546k) |
| `test-writer` | 6% | 24 | 37 | 118k |
| `reviewer-quality` | 4% | 20 | 34 | 105k |
| `architect` | 3% | 16 | 29 | 132k |
| `reviewer-design` | 3% | 20 | 26 | 104k |
| `reviewer-perf` | 1% | 16 | 15 | 58k |
| other | 3% | | | |

Orchestrator profile: justi-fi session 382 turns, 246 above 500k context, peak 869k, 0 compactions, 209m
(74m if capped at 200k); one-fleet 230 turns, 124 above 500k, peak 996k, 2 compactions, 118m (44m capped).
Orchestrator ran 201 Bash calls itself in the justi-fi session. Capping all main sessions at 200k: 41% saving.

Developer profile: the 275-turn run (79m, 6% of the month alone) made 300 tool calls (Bash 104, Read 98,
Edit 84), edited `http-server.ts` 26 times and read it 26 times, ran `npm test` 9 times. 0 of 23 developer
runs ever compacted; 9 peaked above 200k. Capping agents at 200k saves only 11%; the lever is turn count.

Test-writer skip: 4 sessions with the full-run shape (architect, developer, reviewers) and zero test-writer
spawns; orchestrator text on 26 Aug: *"The inline smoke check was clean, so no test-writer iteration is
needed; moving to review."*

## 5. Reading the scan output

Section letters map to hypotheses in section 3. `tokens` is the panel's definition (input + cache read +
cache write + output). Shares in C and D are of true tokens in the window. Section E is per session, not per
run, so a session with several runs can hide a skipped test-writer; use I as the direct check.

## 6. Results: main machine (to fill)

| Window | Panel-style count | True tokens | Sessions |
|---|---|---|---|
| Last 7 days | | | |
| Last 30 days | | | |

| Consumer | Share | Runs | Turns/run | Avg peak ctx |
|---|---|---|---|---|
| Orchestrator sessions | | | | |
| `developer` | | | | |
| `test-writer` | | | | |
| reviewers + architect | | | | |

- H1 (orchestrator context):
- H2 (developer turns):
- H3 (test-writer skip):
- H4 (verifiers second-order, model pinning negligible):
- H5 (panel inflation):
- H6 (main-machine shape):

## 7. Draft options for `/project-decide` (re-weight, do not re-invent)

Written against the secondary-machine ranking. The re-weighting rule is at the end.

- **O1. Operational, no plugin change**: one feature per session, `/clear` after commit, `/compact` at phase
  boundaries, keep pasted documents out of the orchestrator. Attacks H1 immediately but only at feature
  boundaries (S6 makes `/clear` unsafe between handoffs); relies on discipline across parallel sessions;
  does nothing for H2 or S1.
- **O2. Bound the developer and fix the skip**: `developer.md` gains a working discipline (batch a plan
  step's edits before running the gate, never re-read a file already held, cap the fix-verify cycle and
  return with Deviations instead of grinding); correct `SKILL.md:98` and `:257` so full mode always spawns
  the test-writer and increment mode always runs its loop. Surgical; targets H2's actual lever; restores
  ADR-0002's contract (adds back the test-writer's ~6%).
- **O3. File-backed handoffs so sessions can be short, plus O2**: persist suite artefacts (investigation,
  decision, requirements, plan, developer report) and let each skill read its input from file when it is not
  in the conversation, so `/clear` is safe at every handoff; move the orchestrator's heavy file work behind
  agents. Structurally correct for H1; aligned with ADR-0011 and the archaeologist's existing
  `.claude/reports/` write; reverses `project-decide`'s "no file I/O" constraint; needs a freshness rule;
  touches every suite skill.
- **Lost weight after measurement** (still valid, second-order): scope verifiers to the plan's file list
  (S3, S5); roll the loop budgets back to two (S4, contradicts ADR-0014's evidence); repin `inherit` agents
  to Sonnet (negligible here: architect and design reviewer ran 93% of turns on Sonnet anyway).

Recommendation on secondary data: **O3 with O2 landing first**, O1 habits adopted meanwhile.

Re-weighting rule for the main machine: if H1 does not hold (orchestrator sessions well under a third of
true tokens), O2 plus the S3 scoping fix becomes the recommendation and O3 drops to optional. If H2 does not
hold (developer runs short and cheap), the developer budget drops out of O2 and S1 stays as a pure
correctness fix. If H4 fails (verifiers a large share), the first-pass options (plan-scoped verifiers,
de-nested loops) return to the table.

## 8. Open uncertainties

- The panel's window and data source: 38 sessions / 5.6b matches neither the 7-day nor the 30-day figure of
  the secondary machine's cache, which is why the main machine must be measured.
- Server-side credit accounting is invisible locally; "100% used, resets 1 Sep" cannot be attributed from
  transcripts.
- Absence of compaction in subagents is inferred from missing markers and a 546k peak, not from Claude Code
  internals.
- Whether main-machine transcripts are complete (cleanup may have removed older sessions; section A shows
  cache > raw on days where files are missing).
