# Lead Magnet Spec — output template

Fill this and save as the deliverable (e.g. `lead-magnet-<company>.md`). Tag claims `[data]` / `[owner]` / `[assumption]`.

```markdown
# Lead Magnet Spec — <Company name>

_Date: <YYYY-MM-DD> · Prepared by: <you>_

## 0. Inputs
- **Core offer:** <what they sell + the dream outcome it delivers>
- **ICP (who it's for):** <pull from the ICP brief — company + persona>
- **Persona's pains:** <the candidate problems to solve>

## 1. The narrow problem
The one problem this magnet solves, completely: …
- Why it's urgent for the ICP: … [data|owner]
- Why solving it reveals the next problem: … (this is the bridge)

## 2. Candidates considered (scored, /45)
Score each 1–5: **personalized** · **zero-effort** · reveals next problem · ICP-aligned · quick win · worth paying for · scalable to deliver · (× "pulls toward offer"). Hard-fail on *personalized*, *reveals next problem*, or *ICP-aligned* disqualifies regardless of total.
| Candidate | Type | Personalized? | Zero-effort? | Reveals next? | ICP-aligned? | Quick win? | Worth $? | Scalable? | Score |
|---|---|---|---|---|---|---|---|---|---|
| … | personalized-engine / reveal / sample / one-step | | | | | | | | /45 |
**Winner:** … — because …
**Fallback:** …

## 3. The winning magnet — full design
- **Type:** personalized done-for-you engine / reveal / sample / one-step
- **Format:** software · information · service · physical
- **What the prospect receives (complete solution, already done):** …
- **The quick win / payoff:** … (how fast, how tangible)
- **Why it's worth paying for:** …

### 3a. The personalization engine (if personalized — usually is)
- **Public-data inputs gathered per prospect** (exact sources + tools): … (LinkedIn/company data · website/pricing/careers · using their public product · reviews/G2/Reddit · job posts · computed benchmark — see PERSONALIZED-MAGNETS.md)
- **Transformation:** how inputs become the artifact (what's extracted, computed, generated): …
- **Accuracy guardrails:** how each finding is verified true before it ships: …
- **Cost / time to generate one (must be automatable):** …

## 4. The bridge to the core offer
narrow problem solved → **win** → next problem revealed (`<what>`) → core offer solves it → **CTA**: `<the exact next step>`
- **Reason-why it's free:** …

## 5. Name + worked example
Names: 1) … 2) … 3) — **Recommended:** "<name>".
**Worked example** — the artifact generated for one real sample prospect (`<prospect>`), end to end, so everyone sees exactly what lands: …

## 6. Production plan
- What it takes to build the engine: … (data pipeline, generation, who, tools)
- Cost per prospect: … (must stay low — automated)
- MVP first: the thinnest version that still produces a real personalized win: …

## 7. Distribution (how it's deployed)
- **Outreach:** the artifact *is* the opener — tied to which **timing signal** (from the ICP brief). "Saw <signal> — I made you <artifact>."
- **Positioning/content:** how the win (or anonymized aggregate) is shown publicly to pull inbound.
- **Tribe angle:** which tribe makes the give land warmer (from the ICP brief).

## 8. Open questions / assumptions
- [ ] …
```

Close by reading §1 (the narrow problem), §3a (the personalization engine), and §4 (the bridge) back to the owner — if those don't click, nothing downstream will.
