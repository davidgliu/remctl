# Desktop capability coverage

This maps every user-facing RemCTL command family to its desktop surface. A typed action is a validated form in the command palette; it is available even when the common operation also has a direct control. CLI formatting flags are represented by the interface or export formats rather than separate switches.

| RemCTL commands | Desktop surface |
| --- | --- |
| `today`, `upcoming`, `overdue`, `flagged`, `urgent`, `show`, `search` | Sidebar, search, calendar and command palette. Urgent and Overdue have dedicated palette destinations. |
| `info`, `add`, `edit`, `done`, `undone`, `flag`, `unflag`, `delete` | Click-to-open inspector, quick entry, row controls, menus and bulk selection. |
| `subtasks`, `reminder-move` | Expandable hierarchy, inspector subtask creation, parent/section/list moves and typed ordering controls. |
| `tags` | Inspector chips, suggestions, clickable row tags, search and smart filters. |
| `lists`, `list-info`, `list-create`, `list-edit`, `list-rename`, `list-delete`, `list-pin`, `list-unpin` | Sidebar, appearance/type editor, list context menus and typed actions. |
| `list-symbols` | Actual local Reminders symbols, emoji and colors; 71 symbols in the appearance picker. |
| `groups`, `group-info`, `group-create`, `group-edit`, `group-delete` | Grouped sidebar, list drag into groups, group menus and typed actions. |
| `sections`, `section-create`, `section-rename`, `section-delete` | List section headings, columns, section menus, drag moves and typed actions. |
| `sharees` | Inspector assignment picker and native rich form, populated from actual list members. |
| `location-lookup` | Typed location search; location address/coordinate/radius/proximity editing in the inspector. |
| `smart-lists`, `smart-list-create`, `smart-list-edit`, `smart-list-delete` | Sidebar and visual all/any editor with preview: flags, priorities, tag include/exclude/untagged, absolute/relative/no-date, time/no-time, multiple list include/exclude, location and car rules. JSON remains available for exact filter editing. |
| `templates`, `template-info`, `template-create`, `template-apply`, `template-delete` | Template browser, review/apply controls, list menus and typed actions. |
| Groceries fields on `add`, `edit`, `list-create`, `list-edit` | List type/language controls, item categorization and typed forms. |
| Images and rich links on `add` / `edit` | Drop images/links, native file picker, inspector gallery/lightbox, open existing links, add another link. Save existing attachments to Downloads, up to 50 MiB. Image writes support PNG/JPEG/WebP/HEIC up to 8 MiB each. |
| `deleted`, `restore` | Recently Deleted with identity-preserving restore and destination-list selection. |
| `link`, `open` | Copy plugin link, Open in Reminders and typed Reminder Links. |
| `stats` | Reminder Statistics in the command palette. |
| `export`, `import` | `.remctl`, JSON and CSV export; rich `.remctl` file viewer/editor and reviewed import. |
| `doctor`, `onboard`, `setup`, `permissions` | Settings diagnostics and plugin onboarding; OS permission steps remain in the signed host's existing onboarding flow. |
| `completion`, `mcp`, `workspace` | Shell/client installation and internal transport operations; intentionally not presented as task-management controls. |

Recurrence, Early Reminders, alarms, urgency, locations, assignment and clear/reset operations remain available in the complete typed Reminder Fields form as well as their direct inspector controls. The command palette, right-click menus, keyboard navigation, multiple selection, drag moves, selected-context chips, native rich forms, file subscriptions and conversation handoff are desktop additions.

## Runtime boundaries

- Car rules can be written, but local previews/reads explicitly reject unavailable car-alarm metadata. They do not pretend to match.
- Assignment needs real members of a shared list. No existing shared list was modified during acceptance.
- Existing general attachments can be downloaded; RemCTL's write support is for images and rich links. Arbitrary file attachment creation/removal is not claimed.
- Smart-list renaming is not offered because the underlying CLI does not support it. Identity, filter, color, emoji and symbol editing follow the CLI contract.
- `.remctl` import copies supported fields into new reminders. It is not a lossless backup restore; omitted fields are shown before import.
- Private ReminderKit features depend on the installed macOS implementation and require the existing Advanced Reminders setting.
- [MCP Events](desktop-events.md) is implemented; native ChatGPT subscription acceptance remains limited by the tested desktop host.

