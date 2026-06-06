# Owning the metric

A builder owns the merge. A product owner owns the outcome. This skill is for the second kind. Two touchpoints bookend the build: define + instrument before you write code (step 4), measure the lift after you ship (step 15).

## Define the success metric (before building)

1. **Name one metric.** The single number that, if it moves, means this feature worked. Pick the closest to user value you can measure: activation, weekly active users, acceptance/reply rate, conversion, time-to-first-value. Avoid vanity counts (page views, clicks) unless they're a real proxy.
2. **State the target and the window.** "WAU on this surface from X% to Y% within N weeks." A direction without a number isn't a target.
3. **Confirm it's instrumented.** Either the event/field is already tracked (verify the query returns sane data), or **add the instrumentation as a plan item** so it ships with the feature. If you can't query it, you can't claim it.
4. **Capture the baseline now.** Run the query before launch and write the number down in the plan doc. Without a baseline there is no lift, only an anecdote.

## Measure the lift (after shipping)

1. Re-run the baseline query over a comparable window (same length, same segment, no holiday/launch-week skew).
2. Compare against the baseline from step 4. Report the delta as a number, not "feels better".
3. If it moved: that's the headline. If it didn't: say so plainly and state the hypothesis for why and what's next. A flat metric you understood beats a green metric you didn't measure.

## Anti-patterns

- Shipping with no metric, then reverse-engineering a flattering one afterward.
- "Engagement is up" with no baseline, window, or query.
- Comparing incomparable windows (7 days post-launch vs a 30-day pre-period).
- Treating the merged PR as the finish line. The number moving is the finish line.
