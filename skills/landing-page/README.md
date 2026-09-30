# landing-page

A [Claude Code](https://claude.com/claude-code) skill for building or relaunching a startup's home page, the way [Kairon](https://heykairon.com)'s home was built in September 2026.

It stops the two usual failures: pretty pages that say nothing you can check, and honest pages that look like every AI template.

## What it does

1. Picks **one reader** and writes their pain in their own words.
2. Writes the **copy as a document before any code**: a "what it's for" line per section, option A and B for the hero and the pain, the owner picks.
3. **Checks every claim**: a claims table with a source and a date for each number, an adversarial pass as a skeptical buyer, and an anti-slop checklist line by line.
4. Lets **search volume** pick the H1, the title and the description.
5. Puts **the product working in the fold**: the real UI rebuilt as a component, playing a real story in about ten seconds.
6. Adds an optional **mascot with one job**: an interactive bust built on page-mascot that peeks over the product and reacts to each step, plus a brief for scene renders (16:9, one empty third for text, measured luminance, no text, same lens).
7. Brings in **Juan**, a strict AI design judge. He shapes the plan, then scores mocks and the live page from screenshots, round after round, until 8/10.
8. Verifies every locale in the browser.

## Files

- [`SKILL.md`](SKILL.md) — the order, the rules and the checklist.
- [`COPY.md`](COPY.md) — how to write and fact-check the copy document.
- [`MASCOT.md`](MASCOT.md) — sprite sheets, the interactive component, the peeking-bust pattern, the render brief, where a mascot does not go.
- [`JUAN.md`](JUAN.md) — how to run the design judge: plan mode, mock and live rounds, hard states, the review panel.
- [`JUAN-PROMPT.md`](JUAN-PROMPT.md) — the prompt template for each Juan round.

## Install

```bash
npx skills add maleonro/startup-product-skills --skill landing-page
```

## Credits

The interactive mascot is adapted from [page-mascot](https://github.com/nilbuild/page-mascot) by Kamran Ahmed (MIT). Juan's bar in the Kairon build was the designer-founder of [Ato](https://heyato.ai/launch).
