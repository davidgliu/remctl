# Distribution implementation and validation

September 30, 2026. Local branch: `codex/remctl-distribution`. No push, main update or public release.

## Implemented paths

- `./install.sh`: download the native-architecture DMG, verify the MacStories Developer ID and Gatekeeper acceptance, then install the immutable app and matching CLI.
- `./install.sh --from-source`: fetch checksum-pinned Python, compile the host/helpers, create or reuse an owner-only local signing key, verify the resulting app, and run the same installer.
- `--prebuilt APP`: install a reviewed existing build. Local certificate builds require `--allow-local-build`; ad-hoc signatures fail.
- Runtime installation uses an administrator-authorized native host command. It copies only the manifest-verified Python tree into a root-owned content-addressed directory. It never edits an existing system Python.
- Staged update, rollback and uninstall retain the existing ownership-manifest checks. Switching signing identities requires explicit `--migrate-signing`.

## Current evidence

| Check | Result |
| --- | --- |
| Complete arm64 local app build | Passed, including Python 3.13.15 and shared icon |
| One-command source build and dry run | Passed |
| Strict nested code signature verification | Passed |
| Persistent local key, changed binary under same identity, other-key rejection | Passed |
| Keychain search list preservation and private-file checks | Passed |
| Pinned archive extraction, traversal and symlink rejection | Passed |
| Isolated prebuilt install, update, injected publication failure, rollback, uninstall | Passed |
| Tampered bundle rejection and non-admin runtime-install rejection | Passed |
| Existing installer suite | 24 tests passed |
| Capability transport/archive/planner/diagnostics | 99 tests passed |
| CLI/MCP/desktop/events | 563 tests passed |
| Native host original identity, post-start resign rejection, sealed invocation/broker | 4 tests passed |
| Distribution-focused tests | 9 tests passed, including explicit signing migration and protected runtime reuse |
| Default download with no published artifact | Reports HTTP 404 and exits with failure; no silent fallback |
| Notarization of a local certificate build | Rejected before submission |
| Packaged license notices | Project, Python and locked UI dependency notices included |
| Protected free-build Python installation | Passed: manifest bytes, root ownership and non-writable modes verified |
| Actual packaged shell launcher | Passed: protected Python starts the CLI and reports 2.0.0 |
| Free-build persistent sealed broker | Passed: repeated live status requests, with missing permissions reported correctly |
| Free-build Reminders permission across an app update | Passed: changed code hash, identical local certificate, authorized state and real sealed EventKit read without another prompt |
| Signed-release protected runtime and broker | Passed: manifest bytes/root ownership, packaged CLI and live sealed broker |
| Developer ID app and DMG notarization | Accepted; both tickets stapled and validated |
| Gatekeeper execution and disk-image opening | Both accepted as Notarized Developer ID |
| Notarized payload installation | Default signature policy passed; isolated install/update/rollback/uninstall passed |
| Free source build with only Apple tools on PATH | Passed with Apple Python 3.9.6 and no Homebrew or separately installed Python |
| Existing runtime reused without elevation | Passed for local and Developer ID builds; missing runtime returns 77, damaged runtime returns 65 |

Simulation uses temporary prefixes and does not install a live LaunchAgent or grant permissions. The protected runtime and broker rows above are separate live checks. The free-build permission continuity row is backed by live checks before and after a changed signed app was installed; signature continuity alone is not treated as proof.

Final source build: `dist/source-system-python/RemCTL Capability Host.app`. Built by the actual `--from-source` command with only `/usr/bin:/bin:/usr/sbin:/sbin` on PATH and the normal persistent key directory, whose directory/files were verified as owner-only. This was a dry run; that newly built runtime generation has not been installed. Earlier free-build protected runtime and live broker checks are listed separately above. Packaged UI, plugin configuration, icon, installers and license notices match the checked-in inputs. `--bootstrap` starts guided onboarding after installation when run in an interactive Terminal; redirected and test runs remain noninteractive.

## Remaining release gates

- Free-build Full Disk Access, Reminders and Automation persistence passed across an installed update with a changed code hash. A protected-store read passed before and after the update without a new prompt.
- Signed release live permission checks passed: all three grants, a protected-store read, and the visible ChatGPT workspace refresh. Both protected runtimes are installed and verified.
- Validate the Intel artifact and the advertised minimum macOS version on appropriate systems. Cross compilation alone is insufficient.
- Final local app matches the coordinated desktop UI: HTML SHA-256 `06e2d56c86bc7fa750579b5ebafdc799cf1e444f2de103cebd95900f37b0b50f`, imported from the desktop plugin thread and fingerprint recomputed for this branch. That thread independently verified the live UI. Packaged HTML, plugin fingerprint, icon and installer byte parity passed in this branch.

## Build a release locally

```bash
python3 scripts/build_distribution.py --release \
  --identity 'Developer ID Application: …' --output dist/release-arm64
scripts/notarize_distribution.sh dist/release-arm64 --asc
```

`--asc` uses the existing App Store Connect CLI credential. Alternatively pass a `notarytool` keychain profile as the second argument. The script submits the app, requires Accepted, staples and verifies it, creates a DMG with the installer, submits and staples that DMG, checks Gatekeeper, and writes a SHA-256 receipt. Rejected submissions retain result/log files. Notarization uploads to Apple; it does not publish a GitHub release.

Build on each supported architecture. Artifacts are `RemCTL-arm64.dmg` and `RemCTL-x86_64.dmg`. Do not publish an architecture before its runtime and permission checks pass.

## Signing credential check

The initial M5 and M3 Ultra checks found the same Apple Development identity and no usable Developer ID identity. The M3 was checked through its saved Screen Sharing connection because SSH authentication was unavailable. After Federico approved creation, Xcode on the M5 created Developer ID Application for team `4W35M4UN6R`, certificate SHA-1 `4F0E9E16BE3065B93E959199C1A4EFA21041C80A`. The existing MacStories App Store Connect credential submitted both artifacts without exporting its key.

## Notarized local artifact

Final artifact: `dist/release-final/RemCTL-arm64.dmg` (43 MB).

- App submission: `2d2cd545-5870-433a-83c7-640a74d11470`, Accepted.
- DMG submission: `2406fdad-ce63-4235-986c-3352d3d01788`, Accepted.
- SHA-256: `80a80bc333de36162b845ba1cf1b0ff8ef8ddf276e3d8952ef2ffd1ef0040a15`.
- `stapler validate` passes for both app and DMG.
- `spctl --assess --type execute` accepts the app.
- `spctl --assess --type open --context context:primary-signature` accepts the DMG.

The first notarized DMG was unsigned: Apple accepted it, but Gatekeeper's disk-image opening check rejected it. The packaging script now signs the DMG with the app's exact Developer ID certificate before submitting it, verifies the publisher, and requires the disk-image opening assessment before reporting success. Use the final `dist/release-final` artifact; earlier images are superseded.

For permission acceptance, launch the host through its LaunchAgent. A host directly spawned by the development client can make macOS attribute a new Reminders request to that client. No ChatGPT permission was granted during that discovery. Temporary test LaunchAgents run the free build and signed release, separate from the existing installed host. A changed app at `dist/local-update-check` has code hash `f5c4110421bfeb6f4c2afe6bb037d174fa5d96e7`, different from the original `de141726b1d7e110a66e82e3aeeb0bd16122b5f7`, with the identical persistent signing requirement. Reminders remained authorized after this update, and a real `today --via-eventkit --json` read through the sealed host passed without another prompt.

The signed release's separately signed Python is installed and verified under `/Library/RemCTL/Python/a85b3a52b0d60214bfba8a3847ddded0ba077989138eda6152c41a43c6de1592`. Its packaged shell CLI and sealed broker run successfully. Full Disk Access remains blocked by the old Apple Development permission entry: macOS's TCC log explicitly reports that the saved code requirement does not match the new certificate. Adding the source app to the existing entry did not replace that requirement. This is permission migration, not a reason to grant disk access to Python or the AI client.

During permission refresh, turning off the old grant caused the existing workspace to report a database-access error. The original grant was restored and the old installed host restarted: all three permissions were authorized, `fullReady` was true, and the visible ChatGPT workspace completed Refresh without an error. Both temporary test LaunchAgents were stopped. Further identity tests must run sequentially and finish with a verified working installation.

Federico subsequently approved live replacement. The previous app, client directory and LaunchAgent were saved in `dist/pre-release-install-backup`. The notarized build was installed successfully, then updated under the same Developer ID to the final `release-final` artifact. Both transactions restarted the existing MCP HTTP endpoint and passed its health check; both reused verified protected Python without elevation. The installed app passes strict signature and Gatekeeper checks, reports version 2.0.0, and matches the checked-in installer, UI and icon bytes. The final host distinguishes invalid runtime data from missing-runtime authorization (exit 65 versus 77). After this change, all 19 installer lifecycle tests, 5 installer diagnostics tests and 9 distribution tests passed.

The installed Developer ID host now has all three permissions. After Federico unlocked System Settings, the obsolete Full Disk Access entry was removed and the exact installed app was added. Restarting its LaunchAgent produced `doctor --for-agent` with `ok: true`, zero failures and effective access ready. A real protected-store `today --json` read succeeded. The visible ChatGPT workspace completed Refresh with the button enabled again and the database-access error absent. This verifies the final notarized installation, not just the earlier recovery of the old host. No other test host remains running. Intel/minimum-macOS acceptance remains unverified as listed above; the subsequent free-build check below completed its permission-continuity gate.

## Free-build permission continuity completed

The free build was installed at the normal app path with the existing protected runtime. After its initial macOS grants, `doctor --for-agent` reported all three permissions authorized and a real protected-store `today --json` read returned 12 items. The app was then updated with the transactional installer, using the same local certificate and a changed build number/code hash. All three permissions remained authorized and another protected-store read returned 12 items, without requesting any new permission.

- Local signing certificate: `CA5B3C8F2DDA499D8DFD35B004266CF94720C368`.
- Original code hash: `8f543c49bd0adcd7eb237b3fe75cb5c50b104366`.
- Updated code hash: `96a5e2b290fa049cd9233c867b8379418b558205`.
- Evidence: `docs/distribution-permission-continuity.json`.

This verifies ordinary updates within the free-build identity. Switching between that certificate and Developer ID is a deliberate identity migration and needs new grants. The installer refuses an unrequested identity change. Following this test, the original final notarized app was restored; its Full Disk Access grant was restored, and its Reminders grant was restored. The installed notarized host again passed `doctor --for-agent` with all three permissions, a protected-store read, and the visible ChatGPT workspace Refresh without an error.
