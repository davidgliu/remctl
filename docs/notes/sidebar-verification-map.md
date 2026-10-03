# Sidebar verification map

This map covers issues #57–#59. It complements the full CLI documentation.

| Feature | Entry point and common implementation | Setup and expected result |
| --- | --- | --- |
| Existing AI client connection | `remctl onboard`; `offer_mcp_connections` in `remctl` and `detect_clients` / `registration_status` in `remctl_mcp.py` | With the Codex plugin enabled and its command absent from PATH, onboarding reports the plugin connection. A desktop-only installation without a connection gets plugin setup guidance. |
| Custom Smart List folder | CLI `smart-lists --json`, MCP `smart_lists`, and Codex My Lists; `q_smart_lists` / `smart_list_to_dict` in `remctl`, `sidebarLists` in `ui/src/reminder-helpers.ts` | A custom Smart List with a parent folder appears inside that folder alongside ordinary lists. Folding the folder hides all children. Opening the Smart List uses its Smart List query. A missing parent folder places it at top level. |
| Manual display order | Codex list/folder/pinned right-click menus; shared plugin preference tools in `remctl_plugin.py`, ordering helpers in `ui/src/reminder-helpers.ts` | Move Up/Down saves only the current top, folder, or pinned scope. Boundaries disable the unavailable move. Order survives a new server session. Reset Order clears only that scope. Apple Reminders' order stays unchanged. |
| Installed consistency | `python3 scripts/verify_installed_surfaces.py`; archive builder's `SOURCE_MANIFEST` | Compare the installed CLI, generated interfaces, packaged plugins, available caches, exact sealed archive, and strict signature. Exit 1 identifies drift. Missing caches are reported as unavailable rather than verified. |

Build the UI with `npm run build` in `ui` after changing shared Python modules or either interface; this refreshes both plugin launchers' build fingerprint. Run the focused UI checks and the relevant Python tests. Install from the same checkout, refresh the affected plugin connection, then run the installed parity check and fresh MCP launchers.

For actual Codex acceptance, use the Computer plugin to open Reminders and interact with visible list labels. The current account can verify ordinary and pinned ordering. Folder acceptance needs a named temporary test workflow with approval to create and clean up the exact live items. Fixture tests establish rendering behavior but do not prove that a live account has the required folder membership.

Full results and limitations are in [the validation record](issues-57-59-2026-10-03.md).
