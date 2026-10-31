# UI patterns: the tactical rulebook (one element, one way)

How each recurring UI element is built. `SKILL.md` says *use the design system*. This file says *exactly how each recurring element behaves*.

Build to this list. Audit against this list. Use the same rulebook on both sides, so a review never flags something the builder was never told.

Adapt it: swap the component names for your own, and keep the rules. Add a rule only when a lint cannot express it. If a rule can be grepped, make it a lint or a test instead.

> **Rule of one.** Every recurring element has exactly one implementation. If you are about to build a second copy, reuse the shared component. If you copy a `className` a third time, extract it. Drift between two screens is never "both fine". It is one pattern with two spellings.

## Buttons and actions

1. **Icon-only button: aria-label and tooltip, always.** The label and the tooltip show the same string. An icon with no label is a guess. An icon with a label but no tooltip makes sighted users guess.
2. **One-shot async action: one shared action button.** It owns the loading state, the success toast and the error toast. Do not re-wire that trio by hand.
3. **Form or dialog submit: a button with a `loading` prop.** Use it when the error must show inline. It gives a spinner, `aria-busy` and auto-disable. Never gate a primary action with bare `disabled={isPending}`. Never wire a mutation to a button with no loading feedback.
4. **Destructive action: an alert dialog, never `window.confirm`.** Use a specific title that names the object ("Delete list "Q3 prospects"?"), a destructive confirm, and a Cancel. The confirm is the only red button on screen.
5. **One primary action per surface.** Exactly one solid button per screen, dialog or sheet. Everything else is outline, ghost or link. Two solid buttons side by side means no primary.
6. **Success is one toast. Failure is one report.** Confirm a completed action with one shared success helper. Server and offline errors are reported once, globally. Do not double-report. Toast copy is verb plus object ("Invitation sent to alex@acme.com"), not "Success!".

## Tables and lists

7. **All tabular data uses the shared table.** No hand-rolled `<table>`.
8. **The action column is identical on every table.** Trailing actions sit in a right-aligned `⋯` menu. It is quiet until row hover or focus on desktop, and always visible on mobile. One shared component owns this. Do not paste its classes.
9. **Lists are infinite and sortable, never paginated.** Load incrementally. Give columns a sensible default sort. Feed it with cursor paging.
10. **Same row actions at every altitude.** A row's actions use the same words as the actions on that object's own page.
11. **A table fits its own columns at 1280px.** Give every column but the identity column a fixed width. If the widths add up to more than the box, narrow a column, drop one, or move it behind a columns menu. A deliberately wide table says so in a comment.
12. **Use one component for the count above a table and one for an empty cell.** Do not let five copies drift into three glyphs for "no value".

## States: every surface has four

13. **Empty: an empty-state component that names the next action.** Never a bare "No results" on a first-run surface.
14. **Loading: a skeleton shaped like the content.** The layout does not jump on arrival. Spinners are for in-button pending only.
15. **Error: inline and recoverable.** A failed load shows a message in place with a retry. Not a toast that vanishes. Not a blank screen.
16. **Account for all four.** Loading, empty, error, populated. If you built only the populated state, the screen is not done.

## Forms and inputs

17. **Native controls are banned. Use the primitive.** A control built by hand fills with the same field token as the primitives.
18. **Every input has a visible, associated label.** A placeholder is not a label. Show errors next to the field, in the destructive color, and set `aria-invalid`.
19. **Disable submit only while submitting.** Do not disable it "until the form is valid". That hides why. Let the user submit and show the errors.
20. **Real forms use one scaffold.** Use a form library, a schema resolver, one shared field wrapper, and a sticky footer with a primary `loading` button and a ghost Cancel. Trivial one- or two-field forms may stay simple.
21. **Where the message goes decides what it is.** A message about one control goes under that control. A message about the whole submit is one `role="alert"` line at the top. Never report a field's problem at form level. A line that names no field is a dead end.
22. **A validation message is a sentence about the mistake, not about the schema.** Library defaults like "Too small: expected string to have >=1 characters" are neither. Map error keys to your own translated sentences.

## Affordance and polish

23. **Badges carry status, not actions.** A badge is a read-only pill. If it does something, it is a button.
24. **Icons beside text are decorative.** Mark them `aria-hidden` at one standard size. The accessible name comes from the text.
25. **All user-facing strings go through your i18n layer.**

## Page chrome and navigation

26. **Every route renders through one page header, fixed height, one row.** The header has the same height on every route, so content never shifts on navigation. It carries identity (title or breadcrumb) and the sidebar toggle. It does not carry the page's main action or object metadata.
27. **Top-level pages have a title. Deeper pages have a breadcrumb. Never both.** The last crumb is the current page and is not a link.
28. **Each page sets its own document title**, from the same string as its visible identity. Never hardcode it per route.

## Detail surfaces: sheet, dialog or route

29. **Inspect or lightly edit an object: a side sheet.** The list stays mounted behind it. This is the default for "open a row".
30. **Short, single-step or confirm: a centered dialog.** A flow with more than one section, or one that needs its own URL, is not a dialog.
31. **Complex, multi-section editing: a full route.** Do not grow a sheet or dialog into a mini-app.

## Layout and rhythm

32. **One content width per intent.** Reading and form pages cap at a comfortable measure and align left. Data surfaces run full width. Section spacing uses the standard gap scale, never ad hoc margins.
33. **Filters, search, sort and the table's actions live in one toolbar directly above the list.** Search on the left, then filters and sort, then every action on the right. Do not scatter a sort control into the table header on one page and above it on another.
34. **Align to shared edges.** Labels and values share a baseline. Rows share edges. Dividers that meet across a split sit on one axis; give adjacent bars a shared height instead of eyeballing it.
35. **Footer action buttons are right-aligned.** Primary rightmost, Cancel to its left.

## Copy and formatting

36. **Create verbs.** "New x" makes a brand-new object. "Add x" attaches existing ones. Use sentence case for buttons and labels.
37. **One formatter for numbers, dates, currency and relative time**, bound to the active locale. Show relative time for recent activity and the absolute time on hover.

## Motion

Pick calm and fast by default. Delight only where it is earned.

38. **One motion vocabulary.** Easing and durations come from tokens in your theme file. Never hand-roll a curve or an arbitrary duration.
39. **Decide whether to animate by frequency.** Keyboard-driven and hundred-times-a-day actions get no animation. Occasional surfaces (dialogs, sheets, toasts) get the standard entrance. Rare moments (first run) may add a little delight. Every animation answers "why?".
40. **Animate `transform` and `opacity` only, and name the properties.** Never `transition-all`. Entrances start from a small scale (about 95%), never from zero.
41. **Gate hover motion to real pointers.** Movement on hover must not fire on touch taps. Honor `prefers-reduced-motion` once, globally.
