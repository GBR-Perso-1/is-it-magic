#!/usr/bin/env python3
"""Read-only scan of local Claude Code transcripts into token-usage tables.

Usage:
    python docs/investigations/token-usage-scan.py [--days 30] [--top 3] [--sessions 40] [--root PATH]

Reads ~/.claude/projects/**/*.jsonl and ~/.claude/stats-cache.json. Writes nothing.
Output is plain text; redirect it to keep it:
    python docs/investigations/token-usage-scan.py > docs/investigations/token-usage-results-main.txt

Requires Python 3.8+ and nothing else. Runtime is a few seconds per 100 MB of transcripts.

Definitions used throughout
    turn      one API request. Streaming writes one JSONL record per content block, each carrying the
              same usage object, so assistant records are de-duplicated by requestId.
    context   cache_read + cache_creation + input tokens of a turn (what the model re-read that turn)
    tokens    input + cache_read + cache_creation + output (the /usage panel's "total tokens")
    cold      context of an agent's first turn (its spawn payload plus system prompt)

Sections (letters are referenced from token-usage-brief.md)
    A  panel reconciliation: stats-cache per-day totals vs raw record sum vs de-duplicated sum
    B  sessions in the window, largest first
    C  window totals: orchestrator (main) sessions vs subagents
    D  subagents by attributionAgent
    E  is-it-magic spawn counts per session; full runs that never spawned a test-writer
    F  profile of the largest developer runs (tool mix, repeated reads/edits, repeated commands)
    G  profile of the largest orchestrator sessions (what fills their context)
    H  counterfactual: cost if every turn's context had been capped at 200k
    I  orchestrator text that skipped the test-writer because the smoke run was clean
"""
import argparse
import collections
import datetime as dt
import glob
import json
import os
import platform
import re

SKIP_PHRASES = (
    "no test-writer",
    "inline smoke check was clean",
    "inline tests were clean",
    "skip directly to phase",
)
CAP = 200_000
SUITE_PREFIX = "is-it-magic:"


def parse_ts(s):
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception:
        return None


def fmt(n):
    n = n or 0
    if n >= 1e9:
        return f"{n / 1e9:.2f}b"
    if n >= 1e6:
        return f"{n / 1e6:.1f}m"
    if n >= 1e3:
        return f"{n / 1e3:.0f}k"
    return str(int(n))


def dur(a, b):
    if not a or not b:
        return "-"
    s = int((b - a).total_seconds())
    return f"{s // 3600}h{(s % 3600) // 60:02d}"


def bash_pattern(cmd):
    return re.sub(r"[0-9a-f]{7,}|\d+", "#", cmd.split("&&")[-1].strip())[:60]


class Rec:
    """Everything the sections need from one transcript file, collected in a single pass."""

    def __init__(self, path, kind, proj, sid, aid=None):
        self.path, self.kind, self.proj, self.sid, self.aid = path, kind, proj, sid, aid
        self.ctx = []
        self.cr = self.cc = self.inp = self.out = 0
        self.t0 = self.t1 = None
        self.models = collections.Counter()
        self.attr_agent = collections.Counter()
        self.attr_skill = collections.Counter()
        self.tools = collections.Counter()
        self.res_bytes = collections.Counter()
        self.res_n = collections.Counter()
        self.tool_errors = 0
        self.edits = collections.Counter()
        self.reads = collections.Counter()
        self.bash = []
        self.user_msgs = self.user_bytes = 0
        self.invocations = collections.Counter()
        self.compactions = 0
        self.agent_results = []
        self.skip_hits = 0
        self.spawns = collections.Counter()
        self.sendmsg = 0
        self.agents = []  # main sessions only

    tokens = property(lambda self: self.inp + self.cr + self.cc + self.out)
    turns = property(lambda self: len(self.ctx))
    peak = property(lambda self: max(self.ctx) if self.ctx else 0)
    cold = property(lambda self: self.ctx[0] if self.ctx else 0)
    name = property(lambda self: self.attr_agent.most_common(1)[0][0] if self.attr_agent else "(none)")
    short = property(lambda self: self.name.split(":", 1)[1] if self.name.startswith(SUITE_PREFIX) else self.name)
    model = property(lambda self: self.models.most_common(1)[0][0] if self.models else "?")


def note_command(rec, text):
    if "<command-name>" in text:
        rec.invocations[text.split("<command-name>")[1].split("</command-name>")[0].strip()] += 1


def scan(rec, raw_day, dedup_day):
    seen = set()
    tid2name = {}
    with open(rec.path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            try:
                o = json.loads(line)
            except Exception:
                continue
            ts = parse_ts(o["timestamp"]) if o.get("timestamp") else None
            if ts:
                rec.t0 = ts if rec.t0 is None or ts < rec.t0 else rec.t0
                rec.t1 = ts if rec.t1 is None or ts > rec.t1 else rec.t1
            if o.get("attributionAgent"):
                rec.attr_agent[o["attributionAgent"]] += 1
            if o.get("attributionSkill"):
                rec.attr_skill[o["attributionSkill"]] += 1
            if o.get("type") == "summary" or o.get("subtype") == "compact_boundary" or o.get("isCompactSummary"):
                rec.compactions += 1
            m = o.get("message") or {}
            typ = o.get("type")
            if typ == "assistant":
                u = m.get("usage")
                if u:
                    day = (o.get("timestamp") or "")[:10]
                    tot = sum((u.get(k) or 0) for k in (
                        "input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens", "output_tokens"))
                    raw_day[day] += tot
                    rid = o.get("requestId")
                    if not (rid and rid in seen):
                        if rid:
                            seen.add(rid)
                        dedup_day[day] += tot
                        cr = u.get("cache_read_input_tokens") or 0
                        cc = u.get("cache_creation_input_tokens") or 0
                        inp = u.get("input_tokens") or 0
                        rec.cr += cr
                        rec.cc += cc
                        rec.inp += inp
                        rec.out += u.get("output_tokens") or 0
                        rec.ctx.append(cr + cc + inp)
                        rec.models[m.get("model", "?")] += 1
                for b in m.get("content") or []:
                    if not isinstance(b, dict):
                        continue
                    if b.get("type") == "tool_use":
                        n = b.get("name", "?")
                        rec.tools[n] += 1
                        tid2name[b.get("id")] = n
                        i = b.get("input") or {}
                        if n == "Bash" and len(rec.bash) < 5000:
                            rec.bash.append((i.get("command") or "")[:120].replace("\n", " "))
                        elif n in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
                            rec.edits[(i.get("file_path") or "")[-60:]] += 1
                        elif n == "Read":
                            rec.reads[(i.get("file_path") or "")[-60:]] += 1
                        elif n == "Agent":
                            rec.spawns[i.get("subagent_type") or "?"] += 1
                        elif n == "SendMessage":
                            rec.sendmsg += 1
                    elif b.get("type") == "text" and rec.kind == "main":
                        t = (b.get("text") or "").lower()
                        if any(p in t for p in SKIP_PHRASES):
                            rec.skip_hits += 1
            elif typ == "user":
                c = m.get("content")
                if isinstance(c, str):
                    rec.user_msgs += 1
                    rec.user_bytes += len(c)
                    note_command(rec, c)
                elif isinstance(c, list):
                    for b in c:
                        if not isinstance(b, dict):
                            continue
                        if b.get("type") == "tool_result":
                            n = tid2name.get(b.get("tool_use_id"), "?")
                            s = len(json.dumps(b.get("content")))
                            rec.res_bytes[n] += s
                            rec.res_n[n] += 1
                            if b.get("is_error"):
                                rec.tool_errors += 1
                            if n == "Agent":
                                rec.agent_results.append(s)
                        elif b.get("type") == "text":
                            rec.user_msgs += 1
                            rec.user_bytes += len(b.get("text") or "")
                            note_command(rec, b.get("text") or "")


def load_all(root, raw_day, dedup_day):
    mains, agents = [], []
    projects = os.path.join(root, "projects")
    for proj in sorted(os.listdir(projects)):
        pdir = os.path.join(projects, proj)
        if not os.path.isdir(pdir):
            continue
        for f in sorted(glob.glob(os.path.join(pdir, "*.jsonl"))):
            sid = os.path.basename(f)[:-6]
            r = Rec(f, "main", proj, sid)
            scan(r, raw_day, dedup_day)
            mains.append(r)
            for af in sorted(glob.glob(os.path.join(pdir, sid, "subagents", "agent-*.jsonl"))):
                ar = Rec(af, "agent", proj, sid, os.path.basename(af)[6:-6])
                scan(ar, raw_day, dedup_day)
                r.agents.append(ar)
                agents.append(ar)
    return mains, agents


def head(title):
    print(f"\n\n== {title} ==")


def section_a(root, raw_day, dedup_day, cutoff_day):
    head("A. Panel reconciliation (stats-cache.json vs transcripts)")
    path = os.path.join(root, "stats-cache.json")
    if not os.path.exists(path):
        print("stats-cache.json not found; skipping.")
        return
    sc = json.load(open(path, encoding="utf-8"))
    cache_day = {d["date"]: sum(d["tokensByModel"].values()) for d in sc.get("dailyModelTokens", [])}
    print(f"{'day':12}{'stats-cache':>13}{'raw records':>13}{'de-duplicated':>15}{'cache/dedup':>12}")
    for day in sorted(set(cache_day) | set(dedup_day)):
        if day < cutoff_day:
            continue
        s, r, d = cache_day.get(day, 0), raw_day.get(day, 0), dedup_day.get(day, 0)
        print(f"{day:12}{fmt(s):>13}{fmt(r):>13}{fmt(d):>15}{(s / d if d else 0):>12.2f}")
    print("cache == raw on fully preserved days proves the cache sums one usage record per streamed block.")
    for days, label in ((7, "last 7 days"), (30, "last 30 days")):
        lo = (dt.date.today() - dt.timedelta(days=days)).isoformat()
        sess = sum(d["sessionCount"] for d in sc.get("dailyActivity", []) if d["date"] >= lo)
        tok = sum(v for k, v in cache_day.items() if k >= lo)
        print(f"stats-cache {label:13}: sessions={sess:>4}  tokens={fmt(tok)}")
    mu = sc.get("modelUsage", {})
    print(f"stats-cache all-time: sessions={sc.get('totalSessions')}  cache_read={fmt(sum(m['cacheReadInputTokens'] for m in mu.values()))}"
          f"  output={fmt(sum(m['outputTokens'] for m in mu.values()))}  first session={sc.get('firstSessionDate', '')[:10]}")


def section_b(W, limit):
    head(f"B. Sessions in window, largest first (top {limit})")
    print(f"{'start':16} {'dur':>6} {'project':36} {'turns':>5} {'tokens':>7} {'cache_rd':>8} {'out':>6} {'peak':>6} {'#ag':>3}  skills")
    for s in sorted(W, key=lambda r: -r.tokens)[:limit]:
        skills = ",".join(k.split(":")[-1][:14] for k, _ in s.attr_skill.most_common(3))
        print(f"{s.t0.strftime('%Y-%m-%d %H:%M'):16} {dur(s.t0, s.t1):>6} {s.proj[-36:]:36} {s.turns:>5} {fmt(s.tokens):>7} "
              f"{fmt(s.cr):>8} {fmt(s.out):>6} {fmt(s.peak):>6} {len(s.agents):>3}  {skills}")


def section_c(W, WA):
    head("C. Window totals: orchestrator sessions vs subagents")
    mt, at = sum(r.tokens for r in W), sum(r.tokens for r in WA)
    tot = mt + at or 1
    print(f"main sessions : {len(W):>4} sessions {sum(r.turns for r in W):>6} turns  tokens {fmt(mt):>7} ({100 * mt / tot:.0f}%)  cache_rd {fmt(sum(r.cr for r in W))}  output {fmt(sum(r.out for r in W))}")
    print(f"subagents     : {len(WA):>4} spawns   {sum(r.turns for r in WA):>6} turns  tokens {fmt(at):>7} ({100 * at / tot:.0f}%)  cache_rd {fmt(sum(r.cr for r in WA))}  output {fmt(sum(r.out for r in WA))}")
    print(f"TOTAL tokens {fmt(tot)}")
    return tot


def section_d(WA, tot):
    head("D. Subagents by attributionAgent (window)")
    by = collections.defaultdict(list)
    for a in WA:
        by[a.name].append(a)
    print(f"{'agent':30}{'spawns':>7}{'turns':>7}{'t/spawn':>8}{'max_t':>6}{'tokens':>8}{'share':>6}{'out':>7}{'cold':>6}{'avgpeak':>8}{'peak':>7}{'avgmin':>7}  models")
    for name, rs in sorted(by.items(), key=lambda kv: -sum(r.tokens for r in kv[1])):
        n, T, tk = len(rs), sum(r.turns for r in rs), sum(r.tokens for r in rs)
        mins = [(r.t1 - r.t0).total_seconds() / 60 for r in rs if r.t0 and r.t1]
        models = collections.Counter()
        for r in rs:
            models += r.models
        print(f"{name[:30]:30}{n:>7}{T:>7}{T / n:>8.1f}{max(r.turns for r in rs):>6}{fmt(tk):>8}{100 * tk / tot:>5.0f}%{fmt(sum(r.out for r in rs)):>7}"
              f"{fmt(sum(r.cold for r in rs) / n):>6}{fmt(sum(r.peak for r in rs) / n):>8}{fmt(max(r.peak for r in rs)):>7}{(sum(mins) / len(mins) if mins else 0):>7.0f}  {dict(models.most_common(2))}")


def section_e(WA):
    head("E. is-it-magic spawn counts per session (loop-iteration evidence)")
    per = collections.defaultdict(collections.Counter)
    for a in WA:
        if a.name.startswith(SUITE_PREFIX):
            per[(a.t0.strftime("%m-%d"), a.proj[-28:], a.sid[:8])][a.short] += 1
    no_tw = []
    for k, c in sorted(per.items()):
        full = "architect" in c and "developer" in c and any(x.startswith("reviewer-") for x in c)
        flag = ""
        if full and "test-writer" not in c:
            flag = "   <-- full-run shape, no test-writer"
            no_tw.append(k)
        print(f"  {k[0]} {k[1]:28} {k[2]} {dict(c)}{flag}")
    print(f"\nsessions with full-run shape and no test-writer: {len(no_tw)} of {sum(1 for c in per.values() if 'architect' in c and 'developer' in c)}"
          " (approximate: counted per session, not per run)")


def profile(r):
    print(f"tools: {dict(r.tools.most_common())}   tool_errors={r.tool_errors}")
    print("tool_result KB by tool: " + str({k: f"{v // 1024}KB/{r.res_n[k]}" for k, v in sorted(r.res_bytes.items(), key=lambda kv: -kv[1])[:8]}))
    print(f"edited files (top): {r.edits.most_common(5)}")
    print(f"files read more than once: {[(k, v) for k, v in r.reads.most_common(6) if v > 1]}")
    pat = collections.Counter(bash_pattern(c) for c in r.bash)
    print(f"repeated bash patterns: {[(k, v) for k, v in pat.most_common(10) if v > 1]}")
    step = max(1, r.turns // 12)
    print(f"context growth (every {step} turns): {[fmt(c) for c in r.ctx[::step]]}")


def section_f(WA, top):
    head(f"F. Largest developer runs (top {top})")
    devs = sorted((a for a in WA if a.short == "developer"), key=lambda r: -r.tokens)
    if not devs:
        print("no developer runs in window")
        return
    print(f"{'date':6}{'turns':>6}{'tokens':>8}{'peak':>7}{'ctx/turn':>9}{'min':>5}{'msgs':>5}  project")
    for a in devs[:12]:
        print(f"{a.t0.strftime('%m-%d'):6}{a.turns:>6}{fmt(a.tokens):>8}{fmt(a.peak):>7}{fmt(a.tokens / max(a.turns, 1)):>9}{dur(a.t0, a.t1):>6}{a.user_msgs:>5}  {a.proj[-30:]}")
    print(f"\ndeveloper runs with any compaction marker: {sum(1 for a in devs if a.compactions)} of {len(devs)};"
          f" peaking >200k: {sum(1 for a in devs if a.peak > 200_000)}; >400k: {sum(1 for a in devs if a.peak > 400_000)}")
    for a in devs[:top]:
        print(f"\n--- {a.proj[-30:]} / agent-{a.aid}  turns={a.turns} tokens={fmt(a.tokens)} peak={fmt(a.peak)} orchestrator_messages={a.user_msgs} model={a.model}")
        profile(a)


def section_g(W, top):
    head(f"G. Largest orchestrator sessions (top {top}): what fills the context")
    for s in sorted(W, key=lambda r: -r.tokens)[:top]:
        over = sum(1 for c in s.ctx if c > 500_000)
        print(f"\n--- {s.proj[-36:]} / {s.sid[:8]}  {s.t0.strftime('%Y-%m-%d')} {dur(s.t0, s.t1)}  turns={s.turns} peak={fmt(s.peak)} turns>500k={over} tokens={fmt(s.tokens)} compactions={s.compactions}")
        print(f"user messages: {s.user_msgs} ({s.user_bytes // 1024}KB)   skill invocations: {dict(s.invocations.most_common(6))}")
        print(f"agents spawned: {len(s.agents)} ({dict(s.spawns.most_common(6))})  Agent results {sum(s.agent_results) // 1024}KB  SendMessage calls {s.sendmsg}")
        print(f"skill attribution: {dict(s.attr_skill.most_common(6))}")
        profile(s)


def section_h(W, WA):
    head(f"H. Counterfactual: cost if every turn's context were capped at {fmt(CAP)}")
    rows = []
    for r in W + WA:
        act = sum(r.ctx)
        if act:
            rows.append((act, sum(min(c, CAP) for c in r.ctx), r))
    rows.sort(key=lambda x: -x[0])
    print(f"{'kind':6}{'turns':>6}{'peak':>7}{'actual':>9}{'capped':>9}{'saving':>8}  who")
    for act, capd, r in rows[:8]:
        who = f"{r.proj[-24:]}/{'agent-' + r.aid + ' ' + r.short if r.kind == 'agent' else r.sid[:8]}"
        print(f"{r.kind:6}{r.turns:>6}{fmt(r.peak):>7}{fmt(act):>9}{fmt(capd):>9}{100 * (1 - capd / act):>7.0f}%  {who}")
    for kind in ("main", "agent"):
        a = sum(x[0] for x in rows if x[2].kind == kind)
        c = sum(x[1] for x in rows if x[2].kind == kind)
        if a:
            print(f"{kind:6} context-tokens {fmt(a)} -> {fmt(c)} if capped  (saving {100 * (1 - c / a):.0f}%)")


def section_i(W):
    head("I. Orchestrator text that skipped the test-writer after a clean smoke run")
    hits = [(s, s.skip_hits) for s in W if s.skip_hits]
    for s, n in sorted(hits, key=lambda x: -x[1]):
        print(f"  {s.t0.strftime('%Y-%m-%d')} {s.proj[-36:]:36} {s.sid[:8]}  hits={n}")
    print(f"sessions with skip phrases: {len(hits)} of {len(W)}   (phrases: {', '.join(SKIP_PHRASES)})")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--days", type=int, default=30, help="window in days (default 30)")
    ap.add_argument("--top", type=int, default=3, help="runs/sessions to profile in F and G (default 3)")
    ap.add_argument("--sessions", type=int, default=40, help="rows in section B (default 40)")
    ap.add_argument("--root", default=os.path.expanduser("~/.claude"), help="Claude Code home (default ~/.claude)")
    a = ap.parse_args()

    raw_day, dedup_day = collections.Counter(), collections.Counter()
    mains, agents = load_all(a.root, raw_day, dedup_day)
    cutoff = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=a.days)
    W = [r for r in mains if r.t0 and r.t0 >= cutoff]
    WA = [r for r in agents if r.t0 and r.t0 >= cutoff]

    print(f"token-usage-scan  machine={platform.node()}  run={dt.date.today()}  root={a.root}")
    print(f"window: last {a.days} days (from {cutoff.date()})   transcripts on disk: {len(mains)} sessions, {len(agents)} subagents   in window: {len(W)} sessions, {len(WA)} subagents")

    section_a(a.root, raw_day, dedup_day, cutoff.date().isoformat())
    section_b(W, a.sessions)
    tot = section_c(W, WA)
    section_d(WA, tot)
    section_e(WA)
    section_f(WA, a.top)
    section_g(W, a.top)
    section_h(W, WA)
    section_i(W)


if __name__ == "__main__":
    main()
