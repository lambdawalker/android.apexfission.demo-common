package com.apexfission.android.democommon

import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.ui.test.assertIsDisplayed
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test

internal class DemoInteractionTest {
    @get:Rule
    val compose = createComposeRule()

    @Test
    fun emptyScreenOffersSettingsAndHidesWelcomeInstruction() {
        var settingsClicks = 0
        val welcome = "Choose an example"
        compose.setContent {
            MaterialTheme {
                DemoScreen(
                    title = "Demo catalog",
                    welcomeNote = welcome,
                    showEmptyState = true,
                    onOpenSettings = { settingsClicks++ },
                )
            }
        }

        compose.onNodeWithText("No demos available").assertIsDisplayed()
        compose.onNodeWithText(welcome).assertDoesNotExist()
        compose.onNodeWithText("App settings").assertIsDisplayed().performClick()
        compose.runOnIdle { assertEquals(1, settingsClicks) }
    }

    @Test
    fun populatedCatalogShowsSettingsAboveCardsWithoutScrolling() {
        var settingsClicks = 0
        compose.setContent {
            MaterialTheme {
                DemoScreen(
                    title = "Demo catalog",
                    welcomeNote = "Choose an example",
                    onOpenSettings = { settingsClicks++ },
                ) {
                    repeat(20) { index ->
                        item(key = "demo_$index") {
                            DemoCard { Text("Demo $index") }
                        }
                    }
                }
            }
        }

        val settings = compose.onNodeWithText("App settings").assertIsDisplayed()
        val firstCard = compose.onNodeWithText("Demo 0").assertIsDisplayed()
        assertTrue("Settings must appear above the first demo card",
            settings.fetchSemanticsNode().boundsInRoot.bottom <=
                firstCard.fetchSemanticsNode().boundsInRoot.top)
        settings.performClick()
        compose.runOnIdle { assertEquals(1, settingsClicks) }
    }

    @Test
    fun tappingSecondCardInvokesOnlyItsCallback() {
        val opened = mutableListOf<String>()
        compose.setContent {
            MaterialTheme {
                DemoScreen(title = "Demo catalog", welcomeNote = "Choose an example") {
                    item {
                        DemoCard("First demo", "First description", "Open first", { opened.add("first") })
                    }
                    item {
                        DemoCard("Second demo", "Second description", "Open second", { opened.add("second") })
                    }
                }
            }
        }

        compose.onNodeWithText("Open second").assertIsDisplayed().performClick()
        compose.runOnIdle { assertEquals(listOf("second"), opened) }
    }

    @Test
    fun customCardContentRendersAndHandlesInput() {
        var clicks = 0
        compose.setContent {
            MaterialTheme {
                DemoCard {
                    Button(onClick = { clicks++ }) { Text("Custom action") }
                }
            }
        }

        compose.onNodeWithText("Custom action").assertIsDisplayed().performClick()
        compose.runOnIdle { assertEquals(1, clicks) }
    }
}
