# Demo Common integration

This is the Development guide. See [confirmed installation](../../IMPORT.md)
for public release coordinates. Demo Common provides a Material 3 Compose
catalog for Android API 28 and higher.

| Task | API |
| --- | --- |
| Show a welcome message and scrollable list | `DemoScreen` |
| Lay out custom content in an elevated card | `DemoCard` |
| Show a heading with optional metadata and icon | `CardTitle` |

Start with the [quickstart](quickstart.md) and see the [API contract](api.md)
for defaults. Keep navigation, state, localized strings, and actions in the
host app. The components read the active Material 3 theme and perform no I/O.
