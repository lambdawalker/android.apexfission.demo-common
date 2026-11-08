package com.apexfission.android.democommon

import android.content.res.Configuration
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Shapes
import androidx.compose.material3.Text
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.graphics.vector.path
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp

@Preview(name = "Populated light", widthDp = 393, heightDp = 740)
@Preview(name = "Populated dark", widthDp = 393, heightDp = 740, uiMode = Configuration.UI_MODE_NIGHT_YES)
@Preview(name = "Narrow large text", widthDp = 320, heightDp = 640, locale = "es", fontScale = 1.6f)
@Composable
private fun PopulatedPreview() {
    DemoCatalogFixture(populated = true)
}

@Preview(name = "Empty light", widthDp = 393, heightDp = 740)
@Preview(name = "Empty dark", widthDp = 393, heightDp = 740, uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
private fun EmptyPreview() {
    DemoCatalogFixture(populated = false)
}

@Preview(name = "Card light", widthDp = 360, showBackground = true)
@Preview(name = "Card dark", widthDp = 360, showBackground = true, uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
private fun DemoCardPreview() {
    CatalogPreviewTheme {
        Surface {
            Column(Modifier.padding(16.dp)) {
                ExampleDemoCard()
            }
        }
    }
}

@Preview(name = "Title light", widthDp = 360, showBackground = true)
@Preview(name = "Title dark", widthDp = 360, showBackground = true, uiMode = Configuration.UI_MODE_NIGHT_YES)
@Composable
private fun CardTitlePreview() {
    CatalogPreviewTheme {
        Surface {
            CardTitle(
                title = "Interactive example",
                modifier = Modifier.padding(16.dp),
                subtitle = "ExampleComponent",
                icon = playIcon,
            )
        }
    }
}

/** Debug-only fixture shared with the screenshot test source set. */
@Composable
internal fun DemoCatalogFixture(populated: Boolean) {
    CatalogPreviewTheme {
        DemoScreen(
            title = "Demo catalog",
            welcomeNote = "Choose an example to explore what this library can do.",
            eyebrow = if (populated) "EXAMPLES" else null,
        ) {
            if (populated) {
                item {
                    ExampleDemoCard()
                }
                item {
                    DemoCard {
                        CardTitle("Read the setup guide")
                        Text("A card can contain any Compose content.")
                    }
                }
            }
        }
    }
}

@Composable
private fun CatalogPreviewTheme(content: @Composable () -> Unit) {
    val typography = Typography()
    MaterialTheme(
        colorScheme = if (isSystemInDarkTheme()) {
            darkColorScheme(primary = Color(0xFF83DBCB))
        } else {
            lightColorScheme(primary = Color(0xFF006B5D))
        },
        typography = typography.copy(
            headlineLarge = typography.headlineLarge.copy(fontFamily = FontFamily.Serif),
            titleLarge = typography.titleLarge.copy(fontFamily = FontFamily.Serif),
        ),
        shapes = Shapes(small = RoundedCornerShape(6.dp), medium = RoundedCornerShape(10.dp)),
        content = content,
    )
}

@Composable
private fun ExampleDemoCard() {
    DemoCard(
        title = "Interactive example",
        subtitle = "ExampleComponent",
        icon = playIcon,
        description = "Try the interactive example and see how it responds to your input.",
        actionLabel = "Open example",
        onClick = {},
    )
}

private val playIcon = ImageVector.Builder("Play", 24.dp, 24.dp, 24f, 24f).apply {
    path(fill = SolidColor(Color.Black)) {
        moveTo(8f, 5f)
        lineTo(19f, 12f)
        lineTo(8f, 19f)
        close()
    }
}.build()
