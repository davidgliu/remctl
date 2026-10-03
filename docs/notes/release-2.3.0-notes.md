RemCTL 2.3.0 adds saved sidebar ordering in the Codex workspace and fixes Smart List folders and Codex onboarding.

- Arrange ordinary lists, folders, custom Smart Lists, and pinned tiles with Move Up and Move Down. Order survives refreshing and reopening the workspace. Reset Order restores the default for that section. These preferences apply to RemCTL's workspace on this Mac.
- Custom Smart Lists now appear inside their Reminders folders, alongside ordinary lists. Collapsing the folder hides both.
- Onboarding recognizes an active Codex plugin when the `codex` command is absent from PATH, and guides desktop-only installations through plugin setup.
- Both plugins track the full shared build. A repeatable audit checks installed CLI code, sealed host code, UI assets, packaged plugins, and installed plugin caches against the source.

Thanks to @john-catalano for reporting [#57](https://github.com/viticci/remctl/issues/57), [#58](https://github.com/viticci/remctl/issues/58), and [#59](https://github.com/viticci/remctl/issues/59).

The Apple silicon download is signed and notarized. [Installation instructions](https://github.com/viticci/remctl#install) and the [desktop workspace guide](https://github.com/viticci/remctl/blob/main/docs/desktop-plugin.md) cover setup and updating plugins.
