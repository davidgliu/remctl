# Install the desktop plugin from the repo

RemCTL can be installed into Codex for Mac from a local checkout. OpenAI gallery submission is not required. The repository contains a local plugin marketplace, the plugin manifest and skills, artwork, and the built workspace HTML.

There are two installed parts: the RemCTL CLI and signed Capability Host provide access to Apple Reminders; the Codex plugin supplies the workspace and conversation integration. Installing the plugin alone does not install the host or grant macOS permissions.

## Requirements

- A Mac with iCloud Reminders enabled and the [RemCTL installation requirements](installation.md#requirements): macOS 14+ and administrator authorization for its bundled Python. Free source builds also need Xcode Command Line Tools. No paid developer account is required.
- Codex for Mac with local plugin and MCP app support, plus its `codex` command on your PATH. Check `codex plugin --help`. These instructions were verified with Codex CLI 0.159.0 on September 30, 2026; the CLI version alone does not establish desktop feature support.
- The checkout containing `.agents/plugins/marketplace.json` and `plugins/remctl/plugin.json`. Keep this checkout in a stable location because Codex registers its path as the marketplace source.

Node and npm are only required when changing the interface. Users install the checked-in `remctl_workspace.html` without a frontend build.

Choose the notarized download or `./install.sh --from-source` for a free local build. Source builds create their own persistent certificate. The download is not yet published from this local work. The host remains the only permission target.

## First installation

Open Terminal in this checkout. Add `--from-source` to the installation command to build for free; omit it when a notarized release is available.

```sh
./install.sh --bootstrap --shell-completions none
~/bin/remctl onboard --no-mcp
~/bin/remctl doctor
```

Onboarding guides Reminders, Automation and Full Disk Access permissions for **RemCTL Capability Host**. The `--no-mcp` option leaves the Codex connection to the plugin registration below. Complete the reported permission steps and confirm effective host access is ready before continuing.

```sh
codex plugin marketplace add .
codex plugin add remctl@remctl-local
```

Open Codex for Mac, start a fresh conversation, and ask “Open my Reminders workspace.” The global Reminders entry also appears in the app sidebar. In RemCTL Settings, enable **Advanced Reminders features** to use sections, tags, attachments, templates and other private ReminderKit operations.

The current plugin launcher expects the default `~/bin/remctl` installation. For an existing custom-prefix installation, change the executable path in `plugins/remctl/mcp.json` to that installation before registering the plugin, and keep that local configuration through updates. The CLI's custom-prefix support does not automatically reconfigure the plugin launcher.

## If RemCTL is already installed

Update its installed runtime from this checkout, then register the marketplace and plugin:

```sh
./install.sh --doctor --shell-completions none
codex plugin marketplace add .
codex plugin add remctl@remctl-local
```

Use `--from-source` for source-build updates and keep the same path overrides. Switching to the public signature requires explicit `--migrate-signing` and may require permission setup again. Onboarding is only needed again if doctor reports missing permissions.

If Codex already has a plain RemCTL MCP connection, remove that duplicate after the plugin is installed:

```sh
~/bin/remctl mcp remove --client codex
```

This removes the old direct registration, not the plugin. Connections in other AI apps remain independent. Start a new conversation after changing connections.

## Updating

Obtain the next revision of this checkout, then run:

```sh
./install.sh --doctor --shell-completions none
codex plugin add remctl@remctl-local
```

The installer updates the CLI, signed host and built workspace together. Reinstalling the plugin refreshes its cached manifest, skills and connection fingerprint. A running conversation or open app tab can still retain the previous MCP process: close and reopen the workspace and start a fresh conversation. Restart Codex if its global entry still shows the old build. Do not kill a server process beneath an open workspace; that closes its transport.

If the checkout moved, register its new location again with `codex plugin marketplace add .` from the new root.

## Verify the installation

1. Confirm `~/bin/remctl doctor` reports effective host access ready. A blocked direct caller is expected when the signed host has the grants.
2. Open Today and a regular list. Check the counts and the lists' real symbols or emoji.
3. Create a disposable reminder, open its inspector, edit it, and check the result in Apple Reminders.
4. Press ⌘K and try a list, columns and calendar layout. See [the practical walkthrough](desktop-try-it.md) for more.

The workspace operates locally. MCP Events additionally needs a host that can create subscriptions and provide an HTTPS callback and signing secret. The tested Codex installation did not expose that interface: installing this plugin does not make a ChatGPT automation active. See [Events status and repeatable demos](desktop-events.md).

## Remove the plugin

```sh
codex plugin remove remctl@remctl-local
codex plugin marketplace remove remctl-local
```

This removes the Codex integration; it leaves the RemCTL CLI, Capability Host and your Apple Reminders in place. To remove the runtime too, follow [RemCTL uninstall](installation.md#uninstall).

## What maintainers ship

Keep these together in the same repo revision:

| Part | Location |
| --- | --- |
| Local marketplace | `.agents/plugins/marketplace.json` |
| Plugin manifest, connection, skills and icons | `plugins/remctl/` |
| CLI, host and desktop/Event modules | Root sources and `install.sh` |
| Built workspace | `remctl_workspace.html` |
| Editable workspace sources and dependency lock | `ui/` |

For interface or runtime changes, regenerate the bundle and connection fingerprint before installing or packaging:

```sh
npm ci --prefix ui
npm run check --prefix ui
npm test --prefix ui
npm run build --prefix ui
```

Increment the plugin version in `plugins/remctl/plugin.json` for a distributed update, and include the generated HTML and updated `plugins/remctl/mcp.json` in the same change. Validate the installation from that exact checkout; [desktop acceptance](desktop-plugin-validation.md) records the current evidence.

The local marketplace is the initial distribution route. Codex also accepts Git marketplace sources, so a published repo revision can later supply the same manifest without a gallery submission. That does not replace RemCTL's local host installation. No remote release or gallery listing is created by these instructions.
