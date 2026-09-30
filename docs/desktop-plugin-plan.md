# RemCTL desktop plugin

Approved scope: the entire September 30 plan, desktop only. Worktree: `remctl-desktop-plugin`.

## Delivery checklist

Checked items are implemented and installed. The validation report separates automated coverage, live checks, and remaining platform limits.

- [x] Portable manifest, marketplace, bundled skills, onboarding, generated four-circle translucent icon, monochrome navigation icon.
- [x] Global workspace, per-thread Selected Reminders, inline cards, direct links.
- [x] Today, Scheduled, Flagged, All, Completed, Recently Deleted, Assigned to Me, lists/groups and custom smart lists.
- [x] List, columns and calendar layouts; sections, subtasks, colors, counts, manual order, quick entry.
- [x] Complete inspector: title, notes, list, dates, recurrence, priority, flags, tags, sections, assignment, Early Reminder, location, links and images.
- [x] Bulk actions, keyboard navigation, command palette, safe undo, stale edit detection, mutation deduplication, partial/uncertain outcomes.
- [x] Composer mentions, readable resources, selected model context, explicit conversation actions, context removal and restored UI state.
- [x] Typed advanced operations: groups, sections, subtasks, ordering, Groceries, templates, smart lists and attachments.
- [x] Native structured settings and native rich forms, including list/assignee/tag/image selection with previews.
- [x] RemCTL file viewer/editor, host file reads/subscriptions/writes, reviewed import, export/open file.
- [x] Efficient paginated reads, foreground refresh and after-write refresh, errors and missing capability states.
- [x] Install into Codex with one effective MCP connection; keep ordinary CLI/other clients working.
- [x] Focused automated checks; live disposable-data verification; Computer testing in installed Codex, demo conversations, screenshots, iteration.

## Product direction

A refined Mac productivity workspace. Quiet neutral chrome, six-color accents, confident typography, compact rows, contextual controls. A sidebar and optional inspector frame lists, columns and calendar. No explanatory dashboard prose. Apple Reminders is authoritative; selections and drafts are presentation state.

See [desktop validation](desktop-plugin-validation.md) for the installed acceptance results.

## Evidence

Planning reviewed `openai/mcp-extensions` commit `e314720a0daac326217d1f123fcf51647868fa9f`. Source and installed MCP/widget matched before implementation. Live doctor: effective Capability Host ready, all three permissions authorized, private protocol 3, zero failures. Existing untracked `.papercuts.jsonl` and `BUG_REPORT_flagging.md` in the original checkout are untouched.

Desktop testing must exercise real UI through Computer, not substitute a browser-only mock. No remote tunnel or public service is in scope. No push or public publication is authorized.

## Expanded inspector and Events pass

- [x] Attachment lightbox/downloads, tag chips, visual exclusions and relative smart filters, Groceries conversion/language, JSON/CSV export, Urgent/Overdue, statistics and links.
- [x] Durable signed webhook Events server, Activity UI and scoped monitoring requests.
- [x] Failed reads remain unavailable, rather than being shown as empty lists; a worker retains its matching UI across installs.
- [ ] Native ChatGPT webhook subscription and resulting chat invocation: the tested local host exposes no Events interface or callback credentials.

See [capability coverage](desktop-capabilities.md) and [Events](desktop-events.md).
