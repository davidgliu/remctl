# Installation and Onboarding

RemCTL installs a CLI and a signed **Capability Host** app. The host holds the macOS permissions and starts automatically at login. Both installation routes include the same CLI, Python runtime, helpers and desktop workspace.

## Requirements

- macOS 14 or later and iCloud Reminders enabled.
- A Mac administrator password for the protected runtime installation.
- For source builds only: free Xcode Command Line Tools (`xcode-select --install`). No Apple account, signing subscription, Homebrew or separate Python installation is needed.

The current distribution is being validated locally. No downloadable release has been published from this work. Apple silicon source builds have been exercised on macOS 27; Intel and older macOS versions need separate runtime acceptance before release.

## Install the default download

Open the release disk image for your Mac and double-click **Install RemCTL.command**. Or, from this checkout:

```bash
./install.sh --bootstrap
~/bin/remctl onboard
```

The command downloads the matching disk image. Before installing, it checks the app's complete signature, the MacStories Developer ID and macOS Gatekeeper acceptance. It never silently falls back to an unsigned build.

To install a previously downloaded app explicitly:

```bash
./install.sh --prebuilt '/path/to/RemCTL Capability Host.app' --bootstrap
```

## Build it yourself for free

```bash
xcode-select --install      # once, if the Command Line Tools are missing
./install.sh --from-source --bootstrap
~/bin/remctl onboard
```

This one command downloads a pinned, checksum-verified Python runtime, compiles the native helpers and host, and signs them with a local certificate. No Apple account is contacted to create that certificate. Build output goes under `.build/`; `--build-output DIRECTORY` selects a new output directory.

The key lives in `~/Library/Application Support/RemCTL Signing`, in a dedicated keychain with owner-only files. It is not added to your normal keychain search list. Preserve this directory: using the same key keeps the app's signing identity stable across rebuilds. Losing or replacing the key can require granting macOS permissions again. Uninstalling RemCTL preserves it.

Rebuild and update with the same command. Existing installations retain their certificate unless you explicitly choose `--migrate-signing`. `REMCTL_CODESIGN_IDENTITY` selects an existing certificate; `REMCTL_SIGNING_DIRECTORY` selects the local key directory. A separately built local app can be installed with `--prebuilt APP --allow-local-build`; this explicit option still requires a valid certificate signature and rejects ad-hoc signatures.

## Protected Python permissions

The app carries its matching Python version, so it never runs a random Python from your PATH. The installer asks `sudo` for administrator authorization to copy this runtime into `/Library/RemCTL/Python/<content-id>`. The host validates the signed manifest, every file and internal symlink, and root ownership before using it. Ordinary user processes cannot change the installed runtime.

The password is handled by macOS/`sudo`, never stored by RemCTL. The installer does not change permissions on a system or Homebrew Python. Different runtime generations can coexist. Uninstall leaves these shared copies in place.

Maintainers can still select an existing protected Python 3.13+ with `REMCTL_CAPABILITY_PYTHON` for the legacy developer installer. That route requires a stable signing identity. The interpreter and import paths must be root-owned, not group- or world-writable, and have no ACLs. This override is not needed for either normal route.

## Installation paths and rollback

The default CLI is `~/bin/remctl`; the app is `~/Applications/RemCTL Capability Host.app`. The service file is `~/Library/LaunchAgents/net.macstories.remctl.capability-host.plist` and the user-only socket is `~/Library/Application Support/RemCTL/capability-host.sock`. `--bootstrap` also creates first-run configuration. The installer creates `rctl` and `reminders` aliases and installs shell completion.

To use `~/.local/bin`, keep this prefix on every install and upgrade:

```bash
PREFIX="$HOME/.local" ./install.sh --from-source --bootstrap
```

A custom prefix also moves the app and socket. The LaunchAgent stays in `~/Library/LaunchAgents` so macOS starts it at login. `REMCTL_LAUNCH_AGENT_DIR` overrides that directory but other locations do not start automatically.

The installer stages and verifies a complete generation before replacing the previous one. It records owned files in `.remctl-install-manifest.json` and restores the previous generation if publication or service startup fails. `--dry-run` builds/verifies without installing the protected runtime, replacing files or starting the service. It does not prove permission readiness.

If the installer prints `PATH action required`, add its line to your shell profile and open a new terminal. `remctl doctor` reports the effective paths and permission state.

## Onboarding

```bash
remctl onboard
```

Onboarding is a guided flow. Each step explains what it does, asks before changing anything, and can be repeated. Running it again shows what is already set up and only asks about what is missing.

**Step 1: macOS permissions.** RemCTL reads and writes Reminders through the Capability Host, so the host needs three grants:

- Reminders. The host shows the standard macOS prompt.
- Automation for the Reminders app. Used for flags, which have no public API. The host shows the standard prompt.
- Full Disk Access, for the Reminders database. macOS has no prompt for this. If it is missing, RemCTL opens a helper that shows the exact app to add. See [Permissions](#permissions) for the manual steps.

The step lists each grant with a check mark or a fix.

**Step 2: Health check.** RemCTL confirms the host is ready and reads today's reminders.

**Step 3: Connect your AI apps.** RemCTL looks for Claude Code, Codex, and Claude Desktop on the Mac. For each one it finds, it asks whether to connect it, then registers the MCP server in that app's configuration. Apps that are already connected show a check mark. See [mcp.md](mcp.md).

**Step 4: Your other devices (optional).** This step appears only when Tailscale is installed. RemCTL offers to serve the MCP tools to your other tailnet devices over HTTPS with a private token, and prints the command to run on those devices. The default answer is no.

Flags: `--no-mcp` skips steps 3 and 4. `--no-tailscale` skips step 4. `--json` runs the permission checks and reports everything, including detected apps, without asking questions or opening the helper.

On a first run, the first data command you type (for example `remctl today`) also runs onboarding automatically when no onboarding state exists yet. That automatic run only does step 1 and prints a hint for the rest. `REMCTL_SKIP_ONBOARD=1` disables it.

After onboarding:

```bash
remctl doctor
remctl today
```

## Permissions

The Capability Host is the single macOS privacy target. Terminal, scripts, AI apps, and the MCP server use its grants through the owner-only socket. Do not grant Reminders, Automation, or Full Disk Access to Terminal, Python, Hermes, Codex, or Claude; they do not need it.

`remctl doctor --for-agent --json` reports two things: `access.direct` (what the current process could do on its own) and `access.effective` (what RemCTL can do through the host). Use `access.effective` to check readiness. A blocked direct result is normal.

### Full Disk Access by hand

If the helper does not open, or you closed it:

```bash
remctl permissions full-disk-access
```

The helper opens System Settings and shows the exact host app path. In the Full Disk Access list:

1. Click `+`.
2. Drag the host row from the helper into the file picker, or press Command-Shift-G, paste the path (`~/Applications/RemCTL Capability Host.app` for a default install), press Return, and click Open.
3. Restart the host so it picks up the grant:

   ```bash
   launchctl kickstart -k "gui/$(id -u)/net.macstories.remctl.capability-host"
   ```

4. Run `remctl doctor`.

Restart the host only after changing Full Disk Access. Reminders and Automation grants take effect immediately.

### Automation state

The host caches the Automation result after it has seen a definitive answer (`authorized`, `denied`, or `notDetermined`). A freshly started host that cannot reach the Reminders app may report `targetNotRunning` or `unknown` until it verifies the state; `fullReady` stays false until then. Reminders does not need to stay open between commands. `doctor` waits up to three seconds for a starting host to finish verifying, then reports a permission it still cannot read as a warning rather than a failure, because the host clears that state on its own and reads and writes work meanwhile. A refused or restricted grant is still a failure.

### Limited reads without Full Disk Access

`show`, `search`, `today`, and `upcoming` accept `--via-eventkit`, a read-only path through EventKit that does not need Full Disk Access. It is never selected automatically. It returns `eventKitId` values, not RemCTL numeric ids, and omits sections, tags, private metadata, and table output. Use it for recovery, not as a setup.

## Connect AI apps

Onboarding offers this. The direct commands:

```bash
remctl mcp install                          # every app found on this Mac
remctl mcp install --client claude-desktop  # Claude Desktop and Cowork; restart Claude afterwards
remctl mcp install --client tailscale       # serve to your other devices over Tailscale
remctl mcp bundle --open                    # one-click .mcpb extension for Claude Desktop
remctl mcp status
```

The server needs no extra permissions because every tool runs the installed `remctl` through the host. [mcp.md](mcp.md) has the tool list, the Tailscale setup, and troubleshooting.

## Upgrading

`git pull` updates the checkout only. The installed copy is separate.

```bash
git pull
./install.sh
hash -r
remctl --version
remctl doctor
```

For source builds use `./install.sh --from-source`. Updates retain the existing certificate. Switching between a source build and a public release requires `--migrate-signing`; macOS may require new grants for the new identity. Run `remctl onboard` again only if `doctor` reports a permission problem. If the HTTP endpoint is loaded, the installer restarts it and verifies its new process and health response. If this step fails, the installer reports the failure; inspect `remctl mcp status` and repair the endpoint with `remctl mcp install --client tailscale`. Existing stdio connections keep their imported code until the client reconnects or starts a new session.

For an install under `~/.local/bin`, keep the same prefix: `PREFIX="$HOME/.local" ./install.sh`.

### Upgrading from 1.7.1

Release 1.7.1 had no Capability Host and no ownership manifest. The first 2.0 install over it works like a first install:

1. Run `./install.sh` with the same prefix as the old install.
2. If it refuses because of unmanifested files, inspect every RemCTL path in that bin directory. Confirm they are the official 1.7.1 files, the `rctl` and `reminders` aliases, and the compiled helpers. Move anything else out of the way.
3. Run `./install.sh --adopt-existing-install` once.
4. Run `remctl onboard`, complete Full Disk Access if asked, restart the host, and run `remctl doctor`.

`--adopt-existing-install` accepts exactly the official 1.7.1 files or a reviewed prerelease host. It is not a general migration path and should not be used for routine upgrades.

## PATH

```bash
which remctl rctl reminders
remctl --version
```

If `which remctl` finds nothing, add the installer's PATH line to your shell profile and open a new terminal. If it finds `~/.local/bin/remctl`, keep using `PREFIX="$HOME/.local"` for upgrades.

## Shell completion

```bash
remctl setup --shell auto
```

For zsh, setup installs `_remctl` under `~/.zsh/completions` and prints the two lines to add to `~/.zshrc`:

```zsh
fpath=(~/.zsh/completions $fpath)
autoload -Uz compinit && compinit
```

`remctl doctor` warns (`completion_fpath`) when that directory is not on `fpath`. Manual alternatives:

```bash
eval "$(remctl completion zsh)"
eval "$(remctl completion bash)"
remctl completion fish | source
```

## Custom installation

Do not copy the script and helpers by hand. That skips the sealed runtime, the signed host identity, the LaunchAgent, and the socket. Use the installer overrides instead:

```bash
PREFIX="$HOME" \
REMCTL_BIN_DIR="$HOME/bin" \
REMCTL_APP_DIR="$HOME/Applications" \
REMCTL_LAUNCH_AGENT_DIR="$HOME/Library/LaunchAgents" \
./install.sh --bootstrap
```

Use the same overrides for every later upgrade.

## Uninstall

```bash
remctl mcp remove            # disconnect AI apps and the tailnet endpoint first
./uninstall.sh
```

The uninstaller checks that every file it removes belongs to RemCTL. It stops the host LaunchAgent, removes the app, the socket, the installed files, and empty completion directories. `--dry-run` shows the plan; `--keep-config` keeps `~/.config/remctl`. It does not edit your shell profile or revoke macOS permissions.

Protected Python copies under `/Library/RemCTL/Python` and the source-signing key under `~/Library/Application Support/RemCTL Signing` are retained. Do not remove shared runtimes while another installation references them.
