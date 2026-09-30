---
name: landing-page
description: Build or relaunch a startup's home page the way Kairon's was built — copy written and fact-checked as a document before any code, the product itself working in the fold instead of a screenshot, an optional animated mascot with one job, restrained motion, and a strict AI design judge ("Juan") scoring mocks and the live page from screenshots, round after round, until 8/10. Use when the user wants a new landing or home page, a relaunch, a hero rewrite, to add a mascot or character to a site, or wants an AI design partner to raise the taste bar ("que lo vea Juan", "judge this page", "make it feel less generic").
---

# Landing Page

The home page is the one screen every buyer sees. This skill builds it in the order that stops the two common failures: pretty pages that say nothing checkable, and honest pages that look like every AI template.

Worked example throughout: the Kairon home relaunch (Sept 2026). Its decisions are quoted as examples, not rules.

**Read before building:** [COPY.md](COPY.md) (the copy document), [MASCOT.md](MASCOT.md) (only if the page gets a character), [JUAN.md](JUAN.md) + [JUAN-PROMPT.md](JUAN-PROMPT.md) (the design judge).

## The order (do not skip ahead)

1. **Pick one reader.** One page talks to one person. Write who they are and their pain in their own words. Kairon: "someone who already runs outbound with several tools (Clay, HeyReach, Apollo, Instantly)"; the pain: "it's expensive to have so many separate tools, and coordinating them is a lot of work." The other two profiles got their own landings later.

2. **Write the copy as a document, not in code.** One section per block of the page. Each has a "what it's for" line (a note for the reviewer, never on the page) and then the final text. Give the owner **option A and option B** for the hero and the pain, and let them pick. Details in [COPY.md](COPY.md).

3. **Check every claim before it ships.** Build a claims table: every number and promise, with its source (a pricing page read on a date, a line of code, a prod query checked by hand). Anything with no source is cut. Then run an **adversarial pass**: read the whole page as a skeptical buyer who pays for a competitor, and rewrite each line they could disprove in a minute. Then the **anti-slop checklist** line by line.

4. **Let search volume pick the words.** Look up monthly volume for the candidate phrases in each market before choosing the H1, the `<title>` and the description. Kairon's hero dropped "outbound", "LinkedIn" and "email" for "Claude MCP": 5,400 searches a month against 390 for "linkedin outreach". Words with volume that left the H1 go in the title and description.

5. **Shape the page with Juan while it is a plan.** Give Juan today's page (screenshots) and the copy document. Ask for structure, not pixels. See [JUAN.md](JUAN.md) (plan mode).

6. **Put the product working in the fold.** Not a screenshot, not an illustration: rebuild the product's real surface as a component and let it play a real story in about ten seconds. Kairon's fold is one dark band: the claim and the trial button on the left, a rebuilt Claude window on the right running a real request to a live campaign. Section order after the fold: the pain, the solutions, the proof, the price, the ask. Doubts go on their own FAQ page, linked from the nav.

7. **Proof is real numbers with their base.** "19 out of every 100 (146 of 767)" beats "18%". Kairon drew the base as a grid of squares, one per person, so the number reads as a count and needs no count-up animation. Testimonials are asked for with a specific question and written permission; never drafted and published as if said.

8. **Add a mascot only if it has one job.** See [MASCOT.md](MASCOT.md). Kairon's first draft had mascot renders in every section; an adversarial review found they decorated without explaining, and they were cut from everywhere except the fold, where the mascot guides the eye through the product story.

9. **Motion enhances what is already there.** The page is prerendered and fully visible at first paint; every animation only moves content that is already on screen, and `prefers-reduced-motion` gets none of it. One accent color per surface: on Kairon's fold it belongs to the trial button, so an arrow sticker that competed with it was redrawn in neutrals.

10. **Judge the mock, then the live page, with Juan until 8/10.** HTML mock with the real tokens, screenshots light and dark at every width, Juan writes a verdict with a score and exact fixes, you apply them, repeat. Then the same on the real built page. See [JUAN.md](JUAN.md).

11. **Verify in every language, in the browser.** Open the page in each locale. A string that lives in two dictionaries (a shared one and a page one that overrides it) type-checks perfectly while the two languages sell different things. Grep both whenever copy is renamed.

## Rules that do not bend

- **Every claim has a source,** written in the copy document's claims table. "Better results" with no measurement is cut, not softened.
- **Say what the product does today.** A promise the product can't back, or a feature that isn't part of the value proposition, comes out, even if it is true.
- **The product carries the page.** Real UI and real numbers first; illustration only where it explains something the UI can't.
- **No provenance captions on marketing** ("names changed", "this is an example"). If a sample needs a caption to be honest, pick a real, consented case instead.
- **One obvious action per screen.** Everything else is quiet.
- **8/10 from Juan means "would ship as is".** Don't call it done below that without telling the owner.

## Checklist

```
- [ ] One reader and their pain, in their words
- [ ] Copy document: sections with "what it's for", A/B for hero and pain, owner picked
- [ ] Claims table: every number with a source and a date
- [ ] Adversarial pass as a skeptical buyer + anti-slop checklist
- [ ] Search volume read; H1, <title>, description chosen from it
- [ ] Juan plan round on the structure
- [ ] Fold shows the product working (rebuilt UI, real story, ~10 s)
- [ ] Proof: real numbers with their base; testimonials with written permission
- [ ] Mascot (optional): one job, cut everywhere it only decorates
- [ ] Motion: only on visible content, reduced-motion respected, one accent per surface
- [ ] Juan mock rounds to 8/10, then live rounds to 8/10
- [ ] Every locale opened in the browser; both dictionaries grepped after renames
```
