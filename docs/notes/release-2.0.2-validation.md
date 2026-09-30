# RemCTL 2.0.2 release validation

September 30, 2026. Apple silicon release built from `main` at `105d939`. Later commits before publication changed only docs and a test assertion.

## Why 2.0.2

Two problems with the 2.0.0 and 2.0.1 downloads, both found by installing on a MacBook Pro that still had RemCTL 1.7.1:

- Gatekeeper refused 'Install RemCTL.command' ("Apple could not verify…"). The script was unsigned. A test showed that signing it doesn't help: a disk image notarized with a Developer ID-signed script inside was accepted, but its ticket listed only the disk image, and Gatekeeper still rejected the script as "Unnotarized Developer ID".
- The installer stopped at the 1.7.1 files in `~/bin` and asked for `--adopt-existing-install`, which a double-clicked script can't pass.

2.0.2 replaces the script with 'Install RemCTL', a signed and notarized app, and the installer asks in Terminal before adopting an exact 1.7.1 or moving unverifiable old files to the Trash.

## Signed artifact

- Build directory: `dist/release-2.0.2-arm64`.
- App submission (both apps): `7d94181e-0a48-40aa-b7b0-92ee2ca232ac` (Accepted).
- DMG submission: `42cbd505-17f2-4cc0-9183-8affa1b39e6e` (Accepted).
- DMG SHA-256: `41b1c7ee91e3b36e7e44bc9dd46e7170d0124dc96d412cf8897d91d52090bd77`.
- Protected Python runtime: `05b09254669d453d01d2dbff37588b645696e429eb36d2c03a9a3214b58215aa`.

Both apps and the disk image have stapled tickets. From a quarantined copy of the disk image, Gatekeeper accepted 'Install RemCTL' and the Capability Host as "Notarized Developer ID". Opening 'Install RemCTL' from the mounted image opened Terminal, the one-time launcher verified the host's Developer ID and deleted itself, and the installer reached the administrator prompt for the new Python runtime; the test stopped there without installing.

The full Python suite ran 849 tests. The one failure was a lifecycle test that still expected the old ownership error text; after updating it, all 21 lifecycle tests passed. Two new lifecycle tests rebuild an exact 1.7.1 install from the `v1.7.1` tag: without a terminal the installer changes nothing, and answering yes on a pseudo-terminal adopts it.

## Installed acceptance

The disk image was sent to the MacBook Pro with Taildrop. Double-clicking 'Install RemCTL' ran the installer in Terminal and upgraded RemCTL 1.7.1. Onboarding then opened Full Disk Access for the new host, and macOS showed the expected background-activity notice for the host's LaunchAgent.
