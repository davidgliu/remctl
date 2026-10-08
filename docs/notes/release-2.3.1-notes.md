# RemCTL 2.3.1

Making a timed reminder all-day now removes the alarms that matched its due time, instead of moving them to midnight ([#60](https://github.com/viticci/remctl/issues/60)). Custom alarms stay as they are, and an explicit `--alarm` still takes precedence. The fix applies to the CLI, MCP tools, and both plugins. Thanks to @elmgate for the report.

Download `RemCTL-arm64.dmg`, open it, and run **Install RemCTL**. Existing installs keep their macOS permission grants.
