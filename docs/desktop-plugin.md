# RemCTL for Codex on Mac

The desktop plugin turns the installed RemCTL server into an interactive Reminders workspace. Apple Reminders remains the source of truth. Everything runs on this Mac through the signed Capability Host.

## Install from this checkout

Use the [repo installation guide](desktop-install.md) for first setup, upgrades, duplicate connection cleanup and removal. The built UI is included; users do not need Node or an OpenAI gallery listing. RemCTL's signed Capability Host remains a prerequisite.

Open Reminders from the app sidebar or ask to open the RemCTL workspace. Start with the [practical walkthrough](desktop-try-it.md). After an update, reopen the workspace and start a fresh conversation so both use the new server code.

## Workspace

Today, Scheduled, Flagged, All, Completed, Assigned to Me and Recently Deleted sit alongside regular lists, groups and custom smart lists. The list's real color, emoji or Reminders symbol appears in navigation. Appearance offers the Mac's own 71 list symbols; Apple artwork is rendered locally during installation.

Use the toolbar to switch between list, columns and calendar. Lists show sections and nested subtasks. Columns accept reminders dropped into sections. The calendar accepts drops on a date and preserves an existing time. Its No date strip keeps unscheduled reminders accessible. Double-click a day to create a dated reminder.

The inspector edits title, notes, list, date and time, repeat rules, priority, flag, URL, tags, section, assignment, Early Reminder and location. It shows subtasks and an attachment gallery. Click an image for a full preview, or save an attachment to Downloads. Tag chips support suggestions, additions and removal. Inspector drafts survive external refreshes; stale drafts cannot overwrite newer changes. Drop image files onto a reminder or its inspector, or drop a web link onto a reminder. Image uploads accept PNG, JPEG, WebP and HEIC up to 8 MB each.

Right-click a reminder for completion, flags, scheduling, priority, list/section moves, subtasks, context, conversation actions and deletion. Lists and section headings have their own menus. Drag rows to reorder them, drag to another list to move them, or drag a list onto a group. Multi-selection applies to bulk actions and dragging.

Enable **Advanced Reminders features** in Settings for operations requiring RemCTL's private ReminderKit helper. The command palette exposes typed operations for groups, sections, subtasks, manual ordering, Groceries, templates, smart lists and attachments. Forms show common fields first, with less-used fields under More options.

The visual smart-list editor covers all/any matching, tag exclusions, priorities, absolute and relative date ranges, time, multiple lists and locations. Preview matches before saving. The exact filter JSON remains editable. See the [complete capability map](desktop-capabilities.md).

Open **New Reminder** or press **N** for floating Quick Add. The panel stays above the host's conversation composer. Choose a list, date and optional time, priority, flag or notes. Return in the title adds the reminder; ⌘Return adds it and keeps the panel ready for another. Escape or clicking outside keeps an unfinished draft for the next time you open it.

Rows show notes, saved link cards and image attachments inline. Saved Apple link artwork takes precedence; **Load missing link previews** can fetch artwork from public linked websites when no saved image exists. Today separates overdue, all-day, morning, afternoon and evening reminders. App Radar notes show their changelog without changing the original stored notes.

Hover over a sidebar list to reveal its pin button. Click to pin or unpin; pinned regular and custom smart lists become colored tiles at the top, in the same pin order as Apple Reminders. Pinning a list removes its duplicate row below; unpinning restores it to its list or group. The tile keeps its icon, count, right-click menu and reminder drop target. Built-in smart tiles respect Reminders’ hidden state, while the other views remain reachable below. Pins sync with Apple Reminders. The button also works from the keyboard and for custom smart lists.

## Keyboard

| Shortcut | Action |
| --- | --- |
| ⌘K | Search actions, lists and loaded reminders |
| ⌘F | Search reminders |
| N or ⌘N | Floating Quick Add |
| ⌘Return in Quick Add | Add and keep capturing |
| ⌘⇧N | New list |
| ↑ / ↓ | Move selection |
| ⇧↑ / ⇧↓ or Shift-click | Extend selection |
| ⌘-click | Toggle individual selection |
| ⌘A | Select loaded reminders |
| Return | Open the selected reminder |
| Space | Toggle completion |
| ⇧F10 | Selected reminder's context menu |
| Delete | Review reminder deletion |
| ⌘Z | Undo the last reversible flag or non-recurring completion change |
| Escape | Close the frontmost menu, dialog or inspector |

Text fields retain normal editing shortcuts. The app handles shortcuts while it has keyboard focus.

## Conversations and files

Attach deliberately selected reminders as individually removable composer chips. **Selected Reminders** restores that app instance's context after a remount. Use its Choose reminders button to browse and attach items. Context belongs to the app instance; unrelated workspace instances do not silently share it.

Ask ChatGPT opens a reviewable prompt and a choice of the current or a new conversation. Sending requires an explicit click. Composer mentions resolve reminder/list resources. Copy link creates a plugin link to the reminder; Open in Reminders uses Apple's native link.

Choose details opens the host's rich form with native list thumbnails, tag choices, available list members and an image picker. A cancelled form changes nothing. Accepted fields become an inspector draft; uploaded images are attached immediately and shown after refresh.

Export writes a `.remctl` snapshot, JSON array or spreadsheet-safe CSV to Downloads. If Codex initially shows its text editor, choose **Open options → RemCTL File** to use the rich file entrypoint. Preview shows readable reminders. Edit document changes the JSON file, with host file subscriptions and revision checks preventing stale saves. Review import validates the full document before offering to create new reminders. Imports support up to 1,000 reminders and explicitly report omitted fields; they do not restore original identity, completion state, private metadata or attachments. Use Recently Deleted to restore original reminders and their hierarchy instead.

## Reliability and boundaries

Reads are paginated. Foreground refresh, explicit refresh and refresh after changes keep the workspace current. Edits include a reminder revision so a stale inspector cannot overwrite a newer edit. A durable operation identifier prevents a retry from duplicating a write. Partial or uncertain results stay visible and require checking current state before retrying.

The plugin implements the OpenAI MCP extensions for app entrypoints, settings, rich forms, mentions, model context, messages, deep links and host files. It also implements the webhook MCP Events profile, with subscription and delivery status in Activity. Host support is required to create a native subscription; see [Events behavior and acceptance limits](desktop-events.md). The ordinary CLI and MCP remain independent of the desktop mode. No Mac Remote adapter, public server or mobile UI is involved.

Location smart lists work when their alarm metadata is available. Car-trigger smart lists currently report an unsupported metadata error instead of returning an incorrect result. Shared-list assignment depends on members returned by Reminders. Private capabilities remain subject to the installed macOS ReminderKit implementation.

## Development checks

```sh
npm ci --prefix ui
npm run check --prefix ui
npm test --prefix ui
npm run build --prefix ui
python3 -m unittest discover -s tests -p test_desktop_plugin.py
python3 -m unittest discover -s tests -p test_mcp_server.py
python3 -m unittest discover -s tests -p test_events.py
python3 -m unittest discover -s tests -p test_cli.py
```

The JavaScript checks include actual extension SDK validation of the generated native forms, settings and app entrypoints. The backend checks cover stale writes, durable replay, invalid-request rejection, private opt-in and native form round trips. Live desktop testing uses a disposable RemCTL Studio · Demo list.

The four-circle translucent icon is shared by the plugin, MCP server and Capability Host. See [icon provenance](icon-provenance.md) for the ImageGen edit prompt and assets.

Installed acceptance results and known verification limits are recorded in [desktop validation](desktop-plugin-validation.md).
