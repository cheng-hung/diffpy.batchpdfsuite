from pathlib import Path

from traits.api import Bool, Button, HasTraits, Str
from traitsui.api import (
    Action,
    CancelButton,
    Handler,
    Item,
    TextEditor,
    View,
    message,
)


class TextFileEditorDialog(HasTraits):
    file_content = Str()
    saved = Bool(False)

    class _Handler(Handler):
        def save(self, info):
            info.object.saved = True
            info.ui.dispose()

    traits_view = View(
        Item(
            "file_content",
            show_label=False,
            style="custom",
            editor=TextEditor(multi_line=True),
        ),
        title="Edit File",
        buttons=[Action(name="Save", action="save"), CancelButton],
        kind="modal",
        width=700,
        height=500,
        resizable=True,
        handler=_Handler(),
    )


def show_file_editor_dialog(file_path):
    """Open a modal dialog for editing plain text files."""
    if not file_path or not Path(file_path).exists():
        message(f"File does not exist: {file_path}", title="Warning")
        return

    try:
        content = Path(file_path).read_text(encoding="utf-8")
    except Exception as exc:
        message(f"Unable to read file:\n{exc}", title="Warning")
        return

    dialog = TextFileEditorDialog(file_content=content)
    dialog.edit_traits()
    if not dialog.saved:
        return

    try:
        Path(file_path).write_text(dialog.file_content, encoding="utf-8")
    except Exception as exc:
        message(f"Unable to save file:\n{exc}", title="Warning")


class LogDialog(HasTraits):
    logs = Str("")
    clear_button = Button("Clear")

    log_view = View(
        Item(
            "logs",
            style="custom",
            editor=TextEditor(read_only=True, multi_line=True),
            show_label=False,
        ),
        Item("clear_button", show_label=False),
        title="Logs",
        width=600,
        height=400,
        resizable=True,
    )

    def add(self, new_logs):
        self.logs += new_logs + "\n"

    def _clear_button_fired(self):
        self.logs = ""


logdialog = LogDialog()
