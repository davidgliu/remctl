# RemCTL

![RemCTL's splash screen and today's reminders in Terminal](https://cdn.macstories.net/images/uploads/2026/09/30/15-cli-today-1790776847710-fed98e698d.png)

RemCTL gives you full control of Apple Reminders from the terminal, from AI apps, and from a Reminders workspace inside Codex. It covers the basics (reminders, lists, due dates, flags, and search) as well as features Apple doesn't expose to other apps, such as sections, tags, subtasks, smart lists, and templates.

Everything goes through **RemCTL Capability Host**, a small signed app that holds the macOS permissions. You grant access to that one app, and the terminal, scripts, and AI apps use it. None of them need their own permissions.

## Install

You need macOS 14 or later with iCloud Reminders turned on. You don't need an Apple developer account, Xcode, or your own copy of Python.

**Download (recommended).** On a Mac with Apple silicon, download `RemCTL-arm64.dmg` from [Releases](https://github.com/viticci/remctl/releases), open it, and double-click 'Install RemCTL.command'. Terminal opens, checks that the app is signed by MacStories and notarized by Apple, installs it, and walks you through permissions.

**Build it yourself (free).** This is also the route for Intel Macs. Install Apple's Command Line Tools once, then build from this repo:

```bash
xcode-select --install
git clone https://github.com/viticci/remctl.git
cd remctl
./install.sh --from-source --bootstrap
```

This builds everything on your Mac and signs it with a certificate RemCTL creates for you. It never signs in to Apple. The certificate lives in `~/Library/Application Support/RemCTL Signing`: keep it, because future updates need the same certificate to keep your permissions.

Both routes ask for your Mac password once. RemCTL installs its own Python under `/Library/RemCTL`, owned by root, so other apps can't tamper with it.

### Permissions

Setup asks for three permissions, all for 'RemCTL Capability Host': Reminders, Automation for the Reminders app, and Full Disk Access. The first two are standard macOS prompts. Full Disk Access has no prompt, so RemCTL opens a helper that shows you exactly which app to add. When it's done, check everything with:

```bash
remctl doctor
```

If you quit setup early, pick it up again with `remctl onboard`. If `remctl` isn't found, the installer tells you which folder to add to your PATH (usually `~/bin`). [Installation](docs/installation.md) covers custom paths, permissions by hand, and troubleshooting.

## Upgrade

Find your current setup below. `remctl --version` tells you which version you have.

| You have | Do this |
| --- | --- |
| RemCTL 2.0 from the download | Download the new release and run 'Install RemCTL.command' again. |
| RemCTL 2.0 you built yourself | `git pull`, then `./install.sh --from-source`. |
| A 2.0 prerelease installed from `main` with your own Apple Development certificate | `git pull`, then `./install.sh --from-source`. It reuses your certificate, so permissions carry over. |
| RemCTL 1.7.1 | `git pull`, then `./install.sh --from-source --adopt-existing-install --bootstrap`. |
| RemCTL 1.7.0 or older | From your old checkout, run `./uninstall.sh --keep-config`. Then `git pull` and install as new. |

Updates that keep the same signature keep your permissions. RemCTL 1.x had no Capability Host, so coming from 1.x means granting permissions once to the new app. (You can remove the old grants for Terminal afterwards; RemCTL doesn't need them anymore.)

Switching between the download and your own build changes the app's signature. The installer refuses unless you add `--migrate-signing`, and you'll need to grant Full Disk Access again. [Switching signatures](docs/installation.md#switching-between-the-download-and-your-own-build) explains how.

## Use it from the terminal

```bash
remctl today                      # due today and overdue
remctl upcoming 7                 # the next week
remctl show Work --format table   # one list, in Reminders' order
remctl search "invoice" --json    # titles, notes, and saved links
remctl add "Review PR" -l Work -d "tomorrow 10:00" -p high
remctl add "Pay rent" -d 2026-06-01 --recurrence monthly
remctl done 23880 23881           # one id or a batch of up to 50
remctl info 23880 --json          # everything RemCTL knows about one reminder
```

Every reminder has a stable numeric `id`, and every read command has `--json`. `rctl` and `reminders` work as aliases. The [command guide](docs/commands.md) covers due dates, recurrence, output formats, inline images, and every command.

## Use it from AI apps

RemCTL includes an MCP server (MCP, or Model Context Protocol, is the standard AI apps use to call tools). Setup offers to connect the AI apps it finds on your Mac. You can also do it yourself:

```bash
remctl mcp install                          # every supported app on this Mac
remctl mcp install --client claude-desktop  # Claude Desktop and Cowork; restart Claude afterwards
remctl mcp bundle --open                    # or install it as a one-click Claude Desktop extension
remctl mcp status
```

AI apps can read, create, edit, complete, and delete reminders and lists, search with paging, and restore reminders from Recently Deleted. Apps that support MCP Apps also get an interactive reminders widget. To use RemCTL from Claude Code, Codex, or Claude Desktop on another computer, `remctl mcp install --client tailscale` serves the same tools over your private Tailscale network.

The [MCP guide](docs/mcp.md) has the full tool list and troubleshooting. There's also a guide for [Hermes Agent](docs/hermes.md).

## Use it in Codex

The RemCTL plugin for Codex on the Mac adds a full Reminders workspace, with a sidebar that works like the Reminders app: list, column, and calendar layouts, an inspector for every reminder field, drag and drop, a command palette, quick add, and your real list icons and colors. It follows your Mac's light and dark appearance, remembers the layout you pick for each list, and keeps your reminders in Apple Reminders. You can attach specific reminders to a conversation.

Install RemCTL first, then add the plugin from the installed app:

```bash
codex plugin marketplace add "$HOME/Applications/RemCTL Capability Host.app/Contents/Resources"
codex plugin add remctl@remctl-local
```

Open 'Reminders' in the Codex sidebar, or ask Codex to open your Reminders workspace. The [Codex plugin guide](docs/desktop-plugin.md) covers updates, settings, keyboard shortcuts, and removal.

![A RemCTL list in Codex with a reminder open in the inspector](https://cdn.macstories.net/images/uploads/2026/09/30/07-inspector-light-1790776780368-d6ee34a75e.png)

![The calendar layout in dark mode](https://cdn.macstories.net/images/uploads/2026/09/30/12-calendar-dark-1790776812431-03166da0b7.png)

![The columns layout, with one column per section](https://cdn.macstories.net/images/uploads/2026/09/30/05-kanban-demo-light-1790776758217-8b3e480458.png)

![The command palette](https://cdn.macstories.net/images/uploads/2026/09/30/13-command-palette-light-1790776824784-63935204c2.png)

## Private metadata

Some Reminders features have no public API: sections, synced tags, rich links, image attachments, subtasks, shared-list assignment, urgent reminders, Early Reminders, manual ordering, list icons, Groceries lists, list groups, custom smart lists, and templates. RemCTL writes them only when you pass `--private`:

```bash
remctl add "Research" -l Projects --private --url https://example.com -t remctl --section Research
remctl smart-list-create "Priority or Today" --private --match any --priority high,medium --date today
```

These writes use Apple's private ReminderKit framework, never the database directly. Apple can change these APIs in any macOS release. [Private metadata](docs/private-metadata.md) lists what works and how to verify it.

## For agents

Read [SKILL.md](SKILL.md). In short: use the RemCTL MCP tools when they're connected, use deterministic dates (`YYYY-MM-DD` or `YYYY-MM-DD HH:MM`), and verify writes with `info <id> --json`. `remctl doctor --for-agent --json` reports readiness; `access.effective` is the field that matters.

## Uninstall

Disconnect AI apps and remove the Codex plugin first, then run the uninstaller that came with the app (or `./uninstall.sh` from a checkout):

```bash
remctl mcp remove
codex plugin remove remctl@remctl-local && codex plugin marketplace remove remctl-local
~/Applications/"RemCTL Capability Host.app"/Contents/Resources/Distribution/uninstall.sh
```

It stops the Capability Host and removes the app, the CLI, its background service, and your RemCTL settings (add `--keep-config` to keep them). It leaves the shared Python under `/Library/RemCTL` and your signing certificate in place, and it doesn't revoke macOS permissions. `--dry-run` shows what it would remove.

## Documentation

- [Installation](docs/installation.md)
- [Command guide](docs/commands.md)
- [MCP server](docs/mcp.md)
- [Codex plugin](docs/desktop-plugin.md)
- [Hermes Agent](docs/hermes.md)
- [Private metadata](docs/private-metadata.md)
- [Architecture](docs/architecture.md)
- [Agent manual](SKILL.md)
- [Changelog](CHANGELOG.md)

## Project layout

| Path | Purpose |
| --- | --- |
| `remctl` | The CLI |
| `remctl_mcp.py`, `remctl_mcp_widget.html` | MCP server and its reminders widget |
| `remctl_plugin.py`, `remctl_workspace.py`, `remctl_workspace.html` | Codex plugin tools and the built workspace |
| `remctl_events.py` | MCP Events (not enabled in the plugin yet) |
| `remctl_broker.py`, `remctl_capability_policy.py`, `remctl_capabilities.py` | Socket protocol and host command policy |
| `remctl_runtime.py`, `remctl_serialization.py`, `remctl_images.py`, `remctl_smart_lists.py` | Shared helpers, JSON, images, and smart-list filters |
| `remctl-capability-host.swift` | The signed host app |
| `remctl-bridge.swift`, `remctl-private.m`, `remctl-permissions.swift` | EventKit, private ReminderKit, and Full Disk Access helpers |
| `plugins/`, `.agents/plugins/` | Codex plugin manifest, skills, and marketplace |
| `ui/` | Workspace source (only needed to change the interface) |
| `scripts/` | Release builds, notarization, signing, and live test matrices |
| `install.sh`, `uninstall.sh` | Installer and uninstaller |

## License

MIT. See [LICENSE](LICENSE).
