# Failure modes checklist

Scan this list when you plan tests. For each mode, ask:

1. **Can it be triggered** in this code path?
2. **Do we own it?** Or is it library or framework behavior?
3. **Can I name the code hook?** That is the specific branch, constraint or query.

If you cannot answer all three, skip it.

---

## Inputs and validation

| Mode | Look for |
| --- | --- |
| Missing required fields | Schema checks, `null` and empty-string checks |
| Empty collections | `length === 0` branches, empty lists, a parent with no children |
| Malformed formats | Id parsing, URLs and slugs, dates, emails |
| Invalid field combinations | Cross-field rules, one value sent to both sides of an edit |
| Boundary values | Limits and caps, off-by-one on windows |
| Unknown or misspelled fields | Strict schemas at the door. A typo must be refused, not ignored |

## Data and invariants

| Mode | Look for |
| --- | --- |
| Duplicate keys | Upsert versus insert, unique constraints, importing the same record twice |
| Idempotency | Retry-safe writes, the same request sent twice, a webhook delivered twice |
| Missing related rows | Soft-deleted parents, a child whose parent is gone |
| Partial writes on error | Multi-step changes, transaction boundaries. Check that "nothing landed" |
| Broken invariants | Business rules that must hold after the operation (one active run per user, version numbers) |
| Tenancy | Another tenant's id must read as not-found and change nothing |

## External dependencies

| Mode | Look for |
| --- | --- |
| Timeout | Abort signals, deadline handling |
| Error responses | Each vendor error branch, rate limits |
| Unexpected response shape | Parsing vendor JSON, `null` fields, empty pages |
| Partial success | Batches, multi-call sequences, a page that fails mid-walk |
| Money or quota spent | Anything that charges: a usage meter, a paid order, a metered API |

## Concurrency and ordering

| Mode | Look for |
| --- | --- |
| Double processing | At-least-once delivery (queues, durable workflows), re-entry locks |
| Lost updates | Read-modify-write without a compare-and-set |
| Stale reads | Caches, client-side query invalidation |
| Ordering assumptions | Event sequences, cursor paging across pages |

## Error handling and safety

| Mode | Look for |
| --- | --- |
| Wrong error surfaced | Error code and params, HTTP status, the message the user reads |
| Error swallowed | Empty `catch`, an ignored promise, a fallback that hides a failure |
| Sensitive data leaked | Logs, error details, credentials, another tenant's data in a response |

---

## Mapping to tests

Each failure mode you select needs a row in your plan table:

| Test | Kind | What it catches | Why realistic | Code hook |
| --- | --- | --- | --- | --- |
| Setting tags with a deleted tag refuses the whole call | 2 | Partial write | A tag deleted in another tab | `setTags` lookup before insert |
| Adding the same block twice keeps one row | 1 | Duplicate key | The client retries after a timeout | unique index on `block_list` |
| (none) | n/a | Database connection drops mid-write | n/a | Skip: needs fault injection |
