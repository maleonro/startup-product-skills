# Compliance for AI-generated video ads

Not legal advice. Summarises platform rules as of September 2026; platforms change them often, so check
the current policy before a large launch. Validator rule R20 covers the checks below.

## Disclosure

| Platform | When | How |
|---|---|---|
| Meta (FB/IG) | Photorealistic AI people or events in political/social-issue ads: mandatory. Other ads: Meta auto-labels "AI info" when it detects AI content | Self-disclosure at upload for regulated categories |
| TikTok | Any realistic-looking AI scene or person | Turn on the AI-generated content label |
| YouTube / Google Ads | Realistic altered or synthetic people, places or events; Google Ads "How this ad was made" panel (EU, India, New York) | Creator/advertiser attestation for third-party tools |
| EU AI Act Art. 50 (from Aug 2, 2026) | Deepfakes and synthetic media | Machine-readable marking (Omni's SynthID) plus visible disclosure for deepfakes |

Default in this skill: when the plan has realistic people (`characters[].realistic`, default true) or
dialogue, set `disclosure.ai_label: true`. The end card then carries the disclosure text, and you tell
the user to tick the platform's AI label on upload. Omni's SynthID watermark survives in every clip.

## Hard stops (the skill does not build these)

- Political, electoral or social-issue ads (R20 error): need platform authorization and special rules.
- A real, identifiable person's likeness or voice without written consent. Flag them
  (`source_contains_people`, `contains_people`, `first_frame_contains_people` or
  `brief.real_person_likeness`); the validator blocks the plan until `brief.likeness_consent: true`,
  which you set only after the user confirms a signed release exists.
- Fake testimonials: a generated person presented as a real customer quoting results. Use real reviews
  (quoted exactly, with permission) as supers, or present the person as a dramatization.
- Imitating another brand's logo, pack or characters.

## Claims

Every claim in `brief.claims` needs a `substantiation` (R20 warns without one). Health, finance, weight
loss, "clinically proven", "#1" and before/after results draw ad-review rejections and legal exposure.
Keep regulated claims out of supers unless the user provides the proof.

## Regional generation limits

Separate from ad rules: Omni itself blocks some uploads in the EEA, Switzerland and the UK
(see omni-api.md section 7, validator R8).
