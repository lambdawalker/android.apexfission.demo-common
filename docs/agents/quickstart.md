# Apexfission Demo Common

Reusable Material 3 Compose components extracted from the
[Card Detector welcome screen](https://github.com/lambdawalker/android.apexfission.carddetector/blob/main/app/src/main/java/com/apexfission/android/carddetector/demo/WelcomeActivity.kt).

## Requirements and installation

The library targets Compose Material 3 and Android API 28 or later. Building this
repository requires Android SDK 37 and JDK 17 for compilation. CI runs Gradle
with JDK 21. The library has no permissions, navigation, or lifecycle setup.

Use the confirmed **0.1.2** release from Maven Central or JitPack. See the
[installation instructions](../../IMPORT.md) for repository setup and the exact
coordinates for the selected publication destination. Both destinations contain
identical library binaries and sources; their release commits differ only in
publication metadata. See [release provenance](../releases.md).

Maven Central:

```kotlin
implementation("com.apexfission.android:demo-common:0.1.2")
```

JitPack:

```kotlin
implementation("com.github.lambdawalker:android.apexfission.demo-common:demo-common~v0.1.2-jitpack")
```

Only the library's release variant is published. In version 0.1.2, the optional
App settings button follows custom catalog content. Its placement above the
cards belongs to later development changes and is not part of this release.

## Declare a demo catalog

Call from an existing Material 3 theme. Pass localized strings from the
consuming app. Supply your own navigation callbacks and actions.

```kotlin
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import com.apexfission.android.democommon.CardTitle
import com.apexfission.android.democommon.DemoCard
import com.apexfission.android.democommon.DemoScreen

@Composable
fun ExampleCatalog(onOpenExample: () -> Unit) {
    DemoScreen(
        title = "Demo catalog",
        welcomeNote = "Choose an example to get started.",
        eyebrow = "EXAMPLES",
    ) {
        item(key = "example") {
            DemoCard {
                CardTitle(title = "Interactive example")
                Text("Try the example with your own input.")
                FilledTonalButton(
                    onClick = onOpenExample,
                    modifier = Modifier.fillMaxWidth(),
                    shape = MaterialTheme.shapes.small,
                ) {
                    Text("Open example")
                }
            }
        }
    }
}
```

`DemoScreen` uses the standard `LazyListScope` DSL, so callers can declare
individual items, keyed lists, and footers. `DemoCard` takes a `ColumnScope`
slot for any Compose content. Use `CardTitle` inside or outside a card with an
optional decorative icon. The screen and card accept padding and
spacing overrides, and the screen accepts a maximum content width.

## Preview and screenshot coverage

The populated catalog exercises `DemoScreen`, `DemoCard`, and `CardTitle` with
an icon in the first card and a title-only second card. The empty catalog exercises
`DemoScreen` with its themed empty panel and App settings button. The
populated catalog also shows the settings button after the custom demo cards. Both scenarios cover light and dark
mode under a fixture host theme with custom colors, type, and shapes. A narrow
320 dp preview at 1.6× font scale exercises wrapping with a long Spanish card title, description, and action.

```shell
./gradlew :demo-common:assembleRelease :demo-common:lintDebug
./gradlew :demo-common:updateDebugScreenshotTest
./gradlew :demo-common:validateDebugScreenshotTest
```

Use the update task to generate candidates. Review the five PNGs in
`demo-common/src/screenshotTestDebug/reference/` before committing them as
baselines. Once committed, CI uses the validation task and uploads reports
and an image checksum manifest. Until then, CI renders candidates and checks
that all five images were generated.

## Run the sample

Check out one of the published 0.1.2 source commits linked in
[release provenance](../releases.md). With an API 28+ emulator or connected device, run `./gradlew :sample:installDebug`
and open **Demo Common sample**. Tap **Toggle details** to show or hide text
inside the demo card. Change the device theme or language to exercise the
light/dark colors and English/Spanish strings. The
[sample Activity](https://github.com/lambdawalker/android.apexfission.demo-common/blob/86b43bd7ee858ceb09642ec755f0dc99e7eb5a2f/sample/src/main/kotlin/com/apexfission/android/democommon/sample/SampleActivity.kt)
contains the complete integration.
