# Lessons from real runs

What made the loop converge on a production TypeScript monorepo. One UI rework took 13
review passes to get three clean ones in a row. Knowing these up front would have saved
about six.

## Most blockers are a deleted test

Almost every blocker had the same cause: a behavior whose test was deleted together with
the old code. Copy branches, thresholds ("warn at 80%"), calendar-day math, the fallback
when storage is blocked, "closing the panel resets the view".

**Before round 1**, list every file and test the PR deletes (`git show <base>:<path>`),
write down what each one guaranteed, and check a new test still anchors it.

## Do the cheap checks yourself

Orphaned translation keys, dead imports, a leftover old name: grep finds them in a
minute. Do not spend a reviewer on them.

## Scale the reviewers to the diff

The skill runs one reviewer per round. For a large diff, run several in parallel, each
with a different angle:

| The diff touches | Reviewers |
| --- | --- |
| One surface (only backend, or only UI) | 1 |
| Logic and UI | 2: one on structure, one on tests |
| A third surface you cannot hold in your head at once (shared contracts, design tokens, a migration) | 3 |

Reviewers with the same prompt find the same things. Different angles find the next gap.
Angles that worked:

- the whole diff, from scratch;
- verify the blockers from the last round are really fixed;
- inventory every behavior, then prove each new test by mutating a scratch copy of the
  code and checking the test goes red;
- types and test quality only.

**Say the cost before you launch.** Each reviewer cost about 200k tokens and 5 minutes
on the most capable model. Three in parallel is a real spend; a diff in one surface
does not earn it.

## Reviewers contradict each other on shape

One pass asked to keep a whole row object; three later passes asked to join by a `kind`
field instead. Without a record, the loop never ends.

- **Keep a declined list.** Every finding you skip, with its reason. Pass it to every new
  reviewer and ask it to judge "defensible or not", not to re-raise it.
- **A blocker names something concrete**: an input that fails, or a mutation no test
  catches. A preference of shape is a minor.

## Count clean passes on the same code

Any production change after an approval needs a fresh pass. Even a test-only or
comment-only change got one closing pass, to be honest about what was reviewed.
