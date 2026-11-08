# Compose API

Import these declarations from `com.apexfission.android.democommon`. Call
them from an existing Material 3 composition. Each accepts the caller's
`Modifier` and returns `Unit`.

```kotlin
@Composable
public fun DemoScreen(
    title: String,
    welcomeNote: String,
    modifier: Modifier = Modifier,
    eyebrow: String? = null,
    maxContentWidth: Dp = 640.dp,
    contentPadding: PaddingValues = PaddingValues(24.dp),
    contentWindowInsets: WindowInsets = ScaffoldDefaults.contentWindowInsets,
    itemSpacing: Dp = 16.dp,
    content: LazyListScope.() -> Unit,
)
```

Provide localized text and declare cards with `item` or `items`. Use stable
keys for changing lists. The screen fills available bounds, combines Scaffold
`contentWindowInsets` with `contentPadding` without clipping edge-to-edge
scrolling, and centers its lazy column within the configured maximum width.
An empty slot displays the header. Give this screen bounded height and avoid
nesting it in a vertically scrolling parent.

```kotlin
@Composable
public fun DemoCard(
    modifier: Modifier = Modifier,
    contentPadding: PaddingValues = PaddingValues(20.dp),
    itemSpacing: Dp = 12.dp,
    content: @Composable ColumnScope.() -> Unit,
)
```

The card fills the available width and uses the host's medium shape.
Content owns interaction state, accessibility labels, and callbacks.
Use a Material button in the content slot to open the selected demo.

```kotlin
@Composable
public fun CardTitle(
    title: String,
    modifier: Modifier = Modifier,
    subtitle: String? = null,
    icon: ImageVector? = null,
)
```

The title has heading semantics and merges descendants with the optional
subtitle for TalkBack without forcing unnecessary width expansion. The icon
is decorative. Put essential status information in the text. The theme
provides typography and colors. There are no callbacks, background tasks,
Android permissions, or resources to close.
