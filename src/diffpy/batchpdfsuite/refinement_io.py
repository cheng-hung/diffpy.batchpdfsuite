from pathlib import Path

from pyface.api import OK, FileDialog
from pyface.ui.qt.directory_dialog import DirectoryDialog
from traits.api import (
    Bool,
    Button,
    Event,
    HasTraits,
    Instance,
    List,
    Str,
    Tuple,
    observe,
)
from traitsui.api import (
    HGroup,
    Item,
    TableEditor,
    View,
    message,
)
from traitsui.table_column import ObjectColumn
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from diffpy.batchpdfsuite.refinement_editor import show_file_editor_dialog


def _display_file_path_format_func(path_string, len_limit=10):
    if len(path_string) > len_limit:
        path_parts = Path(path_string).parts[1:]
        index = 1
        while len(str(Path(*path_parts[-index:]))) < len_limit:
            index += 1
        index = index - 1 if index != 1 else 1
        parts = ["...", *path_parts[-index:]]
        return str(Path(*parts))
    else:
        return path_string


class FileEntry(HasTraits):
    file_name = Str()
    file_path = Str()


class SimpleSelectFiles(HasTraits):
    current_file_path = Str()
    current_file_name = Str()
    named_path = List(Tuple)
    displayed_named_paths = List(Instance(FileEntry))
    select_file = Button("Select File")
    add_file = Button("Add File")
    clear_file = Button("Clear")
    selected_entry = Instance(FileEntry)
    dclick = Event()

    def _select_file_fired(self):
        dialog = FileDialog(action="open")

        if dialog.open() == OK:
            self.current_file_path = dialog.path

    @observe("current_file_path")
    def _update_current_file_name(self, event):
        if Path(self.current_file_path).is_file():
            self.current_file_name = Path(event.new).stem

    def _clear_file_fired(self):
        self.named_path.clear()
        self.displayed_named_paths.clear()

    def _add_file_fired(self):
        if self.named_path:
            all_names, all_files = list(zip(*self.named_path))
            if self.current_file_name in all_names:
                message(
                    f"Duplicated name: {self.current_file_name}",
                    title="Warning",
                )
                return
            if self.current_file_path in all_files:
                message(
                    f"Duplicated path: {self.current_file_path}",
                    title="Warning",
                )
                return
            if not self.current_file_name.isidentifier():
                message(
                    f"{self.current_file_name} is not a valid identifier",
                    title="Warning",
                )
                return
        if self.current_file_path != "":
            self.named_path.append(
                (self.current_file_name, self.current_file_path)
            )
        self.current_file_path = ""
        self.current_file_name = ""
        return

    @observe("dclick")
    def _open_selected_file_in_editor(self, event):
        if self.selected_entry:
            show_file_editor_dialog(self.selected_entry.file_path)

    @observe("named_path.items")
    def _update_displayed_named_paths(self, event):
        self.displayed_named_paths = [
            FileEntry(file_name=item[0], file_path=item[1])
            for item in self.named_path
        ]

    table_editor = TableEditor(
        columns=[
            ObjectColumn(name="file_name", label="Name"),
            ObjectColumn(name="file_path", label="Path"),
        ],
        editable=False,
        sortable=False,
        selection_mode="row",
        selected="selected_entry",
        dclick="dclick",
    )

    traits_view = View(
        Item(
            "displayed_named_paths",
            editor=table_editor,
            show_label=False,
        ),
        HGroup(
            Item("select_file", show_label=False),
            Item(
                "current_file_path",
                show_label=False,
                style="readonly",
                format_func=_display_file_path_format_func,
                width=80,
            ),
            Item("current_file_name", show_label=False),
            Item("add_file", show_label=False),
            Item("clear_file", show_label=False),
        ),
    )


class FolderWatcher(FileSystemEventHandler):
    def __init__(self, app):
        self.app = app

    def on_created(self, event):
        self.app.refresh = True

    def on_deleted(self, event):
        self.app.refresh = True

    def on_modified(self, event):
        self.app.refresh = True


class SimpleSelectFolder(HasTraits):
    folder_path = Str
    files_path = List(Str)
    displayed_files_path = List(Instance(FileEntry))
    select_folder = Button("Select Folder")
    refresh = Button("Refresh")
    watch = Bool(False)
    observer = None
    # NOTE: add supported file types here
    experiment_file_types = [".gr"]
    selected_entry = Instance(FileEntry)
    dclick = Event()

    def _select_folder_fired(self):
        dialog = DirectoryDialog(action="open")
        if dialog.open() == OK:
            self.folder_path = dialog.path

    @observe("folder_path, refresh")
    def _update_files_path(self, event):
        self.files_path = [
            str(f)
            for f in Path(self.folder_path).iterdir()
            if f.suffix in self.experiment_file_types
        ]
        self.displayed_files_path = [
            FileEntry(file_name=Path(f).name, file_path=f)
            for f in self.files_path
        ]

    def _watch_changed(self, event):
        if not self.folder_path:
            return
        if not event:  # turn-off watching
            if self.observer:
                self.observer.stop()
                self.observer.join()
        else:
            self.observer = Observer()
            self.observer.schedule(FolderWatcher(self), self.folder_path)
            self.observer.start()

    @observe("dclick")
    def _open_selected_file_in_editor(self, event):
        if self.selected_entry:
            show_file_editor_dialog(self.selected_entry.file_path)

    table_editor = TableEditor(
        columns=[
            ObjectColumn(name="file_name", label="Name"),
        ],
        editable=False,
        sortable=False,
        selection_mode="row",
        selected="selected_entry",
        dclick="dclick",
    )
    traits_view = View(
        Item(
            "displayed_files_path",
            show_label=False,
            editor=table_editor,
        ),
        HGroup(
            Item("select_folder", show_label=False, enabled_when="not watch"),
            Item("refresh", show_label=False),
            Item("watch"),
        ),
    )
