---
name: gtm-roadmap
description: Turn an ICP brief + lead magnet into a sequenced GTM implementation roadmap — the order in which outreach campaigns get switched on, laddered by lead warmth (existing network → schedule/event-relational → ICP × tribes → always-on ICP signals), each with its own Hormozi-grounded message strategy and autonomy level. Grounded in Alex Hormozi's $100M Leads "Core Four". Use after the ICP and lead magnet exist, or when asked for "the GTM plan", "the roadmap", "rollout plan", "what campaigns do we run", "where do we start outreach", "what's the sequence", or "how do we get to first replies fastest".
---

# GTM Roadmap

Third skill of the GTM set (`icp-definition` → `lead-magnet` → `gtm-roadmap`). The ICP says *who*; the lead magnet says *what we give*; this says **in what order we turn campaigns on, and what each one says.** It's the plan you put in front of the founder (or client) so they can see — and approve — the path from zero to first replies.

Principle to honor throughout: the win is *"thank god you reached out"*, not reach volume — and the ordering here is what protects that. Frameworks come from Hormozi's *$100M Leads* — see [HORMOZI-OUTREACH.md](HORMOZI-OUTREACH.md).

## The core idea: the warmth ladder

Sequence campaigns by **relationship temperature, warmest first** — the warmer the lead, the faster the time-to-value and the higher the reply rate. The fastest value any startup can get is **contacting the people it already knows.** So start there and ladder outward:

1. **Existing network** — people who already know you. Warmest, fastest, highest reply.
2. **Schedule / event-relational** — tied to where you'll physically be (a trip, a conference). A real-world reason lands far better than a cold message.
3. **ICP × tribes** — strangers who share a tribe (alma mater, ex-employer, community). The shared identity warms a cold lead; run **one campaign per tribe in parallel and let them compete.**
4. **Always-on ICP signals** — strangers with a live timing signal. No tribe needed, because the signal *is* the honest reason to reach out. Runs forever in the background.

The ladder doubles as **graduated autonomy**: the warm top rungs are *your real relationships* — co-drafted, human-approved, never auto-sent. The cold bottom rungs are templated, tested, and eventually automated. Trust is earned going down the ladder, not assumed.

**The lead magnet is the value payload on every rung** — but it matters most on 3 and 4, where there's no relationship to carry the message. (See [`lead-magnet`](../lead-magnet/).)

The detailed per-wave spec — audience, how the list is built, message strategy, channel, cadence, autonomy level, metric — is in [WAVES.md](WAVES.md).

## Workflow

1. **Load the inputs.** Read the **ICP brief** (`icp-definition` output — fit + timing signals, tribes) and the **lead magnet spec** (`lead-magnet` output). The roadmap is a remix of these two; if either is missing, build it first. Note what you'll still need (network access, calendar, which channels are connected).

2. **Confirm the warmth assets.** How big/relevant is the network? Does the founder travel / attend events? Which tribes from the ICP brief are real and reachable? This decides how much weight each wave carries — a founder with a huge warm network front-loads Wave 1; a first-time founder with none leans on Waves 3–4 sooner.

3. **Design each wave** against [WAVES.md](WAVES.md): audience (from the ICP brief), how the list gets built (source + tool), the **message strategy** (warm A-C-A vs. cold value-first; see [HORMOZI-OUTREACH.md](HORMOZI-OUTREACH.md)), the lead magnet's role, channel(s), cadence/volume, autonomy level, and the success metric. **Each wave's message is different** — that's the point; don't reuse one template across rungs.

4. **Sequence + set the experiment.** Lay the waves on a timeline (one-time burst vs. always-on, what overlaps). Make **Wave 3 the learning engine** — parallel per-tribe variants whose winner becomes the default message that scales into Wave 4. Say explicitly what gets turned on *first* (usually Wave 1, this week).

5. **Write the roadmap.** Produce the markdown deliverable using [TEMPLATE.md](TEMPLATE.md). If you're in a code repo, save it *outside* the repo (or ask). Tag every claim `[data]` / `[owner]` / `[assumption]`.

## Quality bar

- **Warmth-ordered, not channel-ordered.** The sequence is justified by reply rate and time-to-value, not "LinkedIn then email". Earlier waves must be genuinely warmer than later ones.
- **Every wave traces to the ICP brief + lead magnet.** Audiences come from defined signals/tribes; the give is the defined magnet. No new targeting invented here.
- **A distinct, honest message per wave.** Each opener earns the reply on its own terms (relationship / real-world context / shared tribe / live signal) — never fabricated commonality, never a pitch where a give belongs.
- **Autonomy matches warmth.** Warm = human-approved. Cold/always-on = templated with guardrails + reply escalation. Never auto-blast real relationships.
- **Starts this week.** The roadmap names a concrete first move that produces replies fast — not a quarter of setup.
