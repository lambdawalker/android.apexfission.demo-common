"""Textual presentation for the APK signing setup wizard."""

import asyncio

from textual import on
from textual.app import App, ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Button, Footer, Header, Input, Select, Static


class SigningSetupApp(App):
    TITLE = "Demo Common"
    SUB_TITLE = "APK signing setup"
    BINDINGS = [("ctrl+q", "quit", "Exit")]
    CSS = """
    Screen { align: center middle; background: $surface; }
    #panel { width: 80; max-width: 100%; height: auto; max-height: 95%;
             border: round $accent; padding: 1 2; background: $panel; }
    #heading { text-style: bold; color: $accent; margin-bottom: 1; }
    #details, #passwords { height: auto; margin-bottom: 1; }
    #passwords { border: round $warning; padding: 0 1; }
    #next { margin-top: 1; }
    """

    def __init__(self, run_setup):
        super().__init__()
        self.run_setup = run_setup
        self.answer = None
        self.messages = []

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="panel"):
            yield Static("Signing setup", id="heading", markup=False)
            yield Static("", id="details", markup=False)
            yield Static("", id="prompt", markup=False)
            yield Static("", id="passwords", markup=False)
            yield Input(id="entry")
            yield Select([], id="operations")
            yield Button("Continue", id="next", variant="primary")
        yield Footer()

    def on_mount(self):
        for selector in ("#entry", "#operations", "#passwords", "#next"):
            self.query_one(selector).display = False
        self.run_worker(self.run_setup(self))

    def note(self, message):
        self.messages.append(message)
        self.query_one("#details", Static).update("\n".join(self.messages[-8:]))

    def show_passwords(self, generated):
        panel = self.query_one("#passwords", Static)
        panel.update("\n".join(f"{label}: {value}" for label, value in generated))
        panel.display = bool(generated)

    async def prompt(self, label, *, secret=False, options=None):
        entry = self.query_one("#entry", Input)
        choices = self.query_one("#operations", Select)
        button = self.query_one("#next", Button)
        self.query_one("#prompt", Static).update(label)
        self.answer = asyncio.get_running_loop().create_future()
        entry.value = ""
        entry.password = secret
        entry.display = options is None
        choices.display = options is not None
        if options:
            values, default = options
            choices.set_options(values)
            choices.value = default
            choices.focus()
        else:
            entry.focus()
        button.display = True
        try:
            return await self.answer
        finally:
            entry.value = ""
            entry.display = choices.display = button.display = False
            self.query_one("#prompt", Static).update("")
            self.answer = None

    @on(Input.Submitted, "#entry")
    @on(Button.Pressed, "#next")
    def submit(self):
        if self.answer is not None and not self.answer.done():
            choices = self.query_one("#operations", Select)
            value = choices.value if choices.display else self.query_one("#entry", Input).value
            if isinstance(value, str):
                self.answer.set_result(value)
