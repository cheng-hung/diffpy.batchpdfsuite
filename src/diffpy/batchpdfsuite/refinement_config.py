import json
import re
import subprocess
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path

import jinja2
from diffpy.apps.app_runmacro import MacroParser
from pyface.api import OK, DirectoryDialog
from traits.api import (
    Any,
    Bool,
    Button,
    DelegatesTo,
    Dict,
    Directory,
    Enum,
    File,
    HasTraits,
    Instance,
    Int,
    List,
    Property,
    Str,
    observe,
)
from traitsui.api import (
    FileEditor,
    Handler,
    HGroup,
    Item,
    ObjectColumn,
    TableEditor,
    View,
    spring,
)

from diffpy.batchpdfsuite.refinement_editor import (
    LogDialog,
    TextFileEditorDialog,
)
from diffpy.batchpdfsuite.refinement_io import (
    SimpleSelectFiles,
    SimpleSelectFolder,
)


class Task(HasTraits):
    profile_file = Str()
    result_dict = Dict()
    status = Enum("completed", "working", "waiting")


class _TaskColumn(ObjectColumn):
    def get_value(self, obj):
        return Path(obj.profile_file).name

    def get_text_color(self, obj):
        return "black" if obj.status == "completed" else "gray"


_task_table_editor = TableEditor(
    columns=[
        _TaskColumn(
            name="profile_file",
            label="Task",
            editable=False,
        ),
    ],
    editable=False,
    sortable=False,
    selected="selected_task",
    dclick="task_dclick",
)


class _RefinementConfigHandler(Handler):
    def object_task_dclick_changed(self, info):
        task = info.object.selected_task
        if task and task.status == "completed":
            dialog = TextFileEditorDialog(
                file_content=json.dumps(task.result_dict, indent=4)
            )
            dialog.edit_traits()


class RefinementTasks(HasTraits):
    tasks = List(Task)
    progress_text = Property(Str, depends_on="tasks.status")
    reload_button = Button("Reload")
    save_button = Button("Save to...")
    profile_files = List(Str)
    sorting_number = List(Int)

    def _tasks_default(self):
        return []

    def _get_progress_text(self):
        total = len(self.tasks)
        done = sum(1 for task in self.tasks if task.status == "completed")
        return f"{done} / {total} tasks completed"

    def _reload_button_fired(self):
        self._reload_tasks()

    def _save_button_fired(self):
        self._save_tasks()

    def add_log(self, new_logs=""):
        # virtual method
        pass

    @observe("profile_files, profile_files.items")
    def _update_tasks(self, event):
        existing_files = [task.profile_file for task in self.tasks]
        for file in self.profile_files:
            if file not in existing_files:
                self.tasks.append(Task(profile_file=file, status="waiting"))
        if self.always_sort and self.sorting_regex:
            self._sort_tasks(self.sorting_regex)
            return

    def _reload_tasks(self):
        self.tasks = [
            Task(profile_file=file, status="waiting")
            for file in self.profile_files
        ]
        if self.always_sort and self.sorting_regex:
            self._sort_tasks(self.sorting_regex)

    def _save_tasks(self):
        # FIXME: save to a SQLite database in the future
        dialog = DirectoryDialog()
        if dialog.open() == OK:
            dest_folder = dialog.path
            for task in self.tasks:
                if task.status == "completed":
                    dest_path = (
                        Path(dest_folder) / Path(task.profile_file).name
                    )
                    with open(dest_path.with_suffix(".json"), "w") as f:
                        json.dump(task.result_dict, f, indent=4)

    sorting_regex = Str("")
    apply_regex_button = Button("Apply")
    ascending_sort = Bool(True)
    always_sort = Bool(False)

    def _apply_regex_button_fired(self):
        self._sort_tasks(self.sorting_regex)

    def _sort_tasks(self, regex):
        # handle wrong regex
        if not self.sorting_regex:
            return
        try:
            pattern = re.compile(regex)

            def sort_key(f):
                m = pattern.search(Path(f).name)
                if m is None:
                    raise re.error(
                        f"Regex did not match filename: {Path(f).name}"
                    )
                return float(m.group(0))

            self.profile_files = sorted(
                self.profile_files,
                key=sort_key,
                reverse=not self.ascending_sort,
            )
        except (re.error, ValueError) as e:
            self.log_dialog.add(f"Error applying sorting regex: {e}")
        # handle conflict with existing completed tasks
        completed_files = [
            task.profile_file
            for task in self.tasks
            if task.status == "completed"
        ]
        if completed_files != self.profile_files[: len(completed_files)]:
            self.log_dialog.add(
                "Error applying sorting regex: "
                "The order of the updated tasks conflict "
                "with the existing completed tasks. This results in "
                "ambiguous chaining configuration.\n"
                "Please check the regular expression to extract order "
                "number for the sorting, or run tasks again with the "
                "updated profiles."
            )
        # reorder tasks
        for i in range(len(completed_files), len(self.tasks)):
            self.tasks[i].profile_file = self.profile_files[i]


class RefinementConfig(RefinementTasks):
    # run configuration
    instruction_file = File()
    instruction_text = Str("")
    instruction_type = Enum("macro", "code")
    run_event = Instance(threading.Event)
    is_running = Property(Bool)
    result_folder = Directory()

    # log
    log_dialog = Instance(LogDialog)

    # profiles and structures
    structure_files_selector = Instance(SimpleSelectFiles)
    profile_folder_selector = Instance(SimpleSelectFolder)

    structure_files = DelegatesTo(
        "structure_files_selector", prefix="named_path"
    )  # [(name, path), ...]
    profile_files = DelegatesTo(
        "profile_folder_selector", prefix="files_path"
    )  # [path1, path2, ...]

    def _run_event_default(self):
        event = threading.Event()
        event.clear()
        return event

    def _get_is_running(self):
        return self.run_event.is_set()

    @observe("profile_folder_selector.folder_path")
    def _update_profile_files(self, event):
        self._reload_tasks()
        if not self.profile_files:
            return
        # FIXME: determine the result folder once profile folder is set
        #   so that results can be saved automatically.
        result_folder_path = (
            Path(self.profile_folder_selector.folder_path) / "fit_results"
        )
        if result_folder_path.exists() and not result_folder_path.is_dir():
            raise NotADirectoryError(
                f"Error creating result folder: {result_folder_path} "
                "already exists and is not a directory."
            )
        if not result_folder_path.exists():
            result_folder_path.mkdir(parents=True, exist_ok=True)
        self.result_folder = str(result_folder_path)

    # refine tasks
    start_button = Button("Start")
    stop_button = Button("Stop")
    sequential_flag = Bool(False)
    run_thread = Instance(threading.Thread)
    # self.tasks defined in the parent class
    selected_task = Instance(Task)
    dclicked_task = Instance(Task)
    task_dclick = Any()

    def _selected_task_default(self):
        return None

    def _start_button_fired(self):
        if not self.tasks:
            return
        if not self.selected_task:
            self.selected_task = self.tasks[0]
        if not self.instruction_file:
            raise ValueError("Instruction file is not specified.")
        if not self.structure_files:
            raise ValueError("Structure files are not specified.")
        start_ind = self.tasks.index(self.selected_task)
        for i in range(start_ind, len(self.tasks)):
            self.tasks[i].status = "waiting"
        self.run_event.set()
        self.run_thread = threading.Thread(
            target=self._run_job, args=(start_ind,), daemon=True
        )
        self.run_thread.start()

    def _run_job(self, start_ind):
        ind = start_ind
        while self.run_event.is_set():
            if ind >= len(self.tasks):
                time.sleep(1)  # wait for new tasks
                continue
            task = self.tasks[ind]
            if (
                self.sequential_flag
                and ind > 0
                and self.tasks[ind - 1].status == "completed"
            ):
                previous_task = self.tasks[ind - 1]
            else:
                previous_task = None
            task.status = "working"
            self._submit_a_task(task, previous_task)
            ind += 1

    def _stop_button_fired(self):
        self.run_event.clear()
        if self.run_thread:
            self.run_thread.join(timeout=5)

    def _submit_a_task(self, task, previous_task=None):
        previous_result = previous_task.result_dict if previous_task else {}
        task.status = "working"
        self.log_dialog.add(f"Starting task: {Path(task.profile_file).name}")
        result_path = tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        )
        result_path.close()
        result_path = str(result_path.name)
        script_path = str(self.instruction_file)
        if self.instruction_type == "code":
            args = {"profile": task.profile_file}
            args["structures"] = {}
            for name, path in self.structure_files:
                args["structures"][name] = path
            args["result_path"] = result_path
            args["previous_result"] = previous_result
            argument_path = tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            )
            argument_path.write(json.dumps(args))
            argument_path.close()
            argument_path = str(argument_path.name)
            proc = subprocess.Popen(
                ["python", script_path, argument_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )
            for line in proc.stdout:
                self.log_dialog.add("STDOUT: " + line.strip())
            proc.wait()
            Path(argument_path).unlink(missing_ok=True)
            if proc.returncode != 0:
                task.status = "waiting"
                self.log_dialog.add(
                    f"Task failed with exit code {proc.returncode}"
                )
                self.run_event.clear()
                return
        else:
            script_template = jinja2.Template(Path(script_path).read_text())
            context = {
                "diffpy": {
                    "profile_path": task.profile_file,
                    "result_path": result_path,
                    "structure_path": self.structure_files[0][1],
                }
            }
            script_content = script_template.render(**context)
            self.log_dialog.add(
                f"Running macro script for task:\n{script_content}"
            )
            try:
                # FIXME: Support multiple phases refinement in the future
                parser = MacroParser()
                parser.parse(script_content)
                # FIXME: `diffpy.app.runmacro` save and read variables values
                #   into results_dict['variables'][var_name]['value'] by
                #   default
                for var_name, var_pack in previous_result.get(
                    "variables", {}
                ).items():
                    parser.inputs[
                        "set_initial_variable_values.variable_name_to_value"
                    ][var_name] = var_pack["value"]
                parser.preprocess()
                parser.run()
            except Exception as e:
                self.log_dialog.add(f"Error parsing macro script: {e}")
                task.status = "waiting"
                self.run_event.clear()
                return
        task.status = "completed"
        task.result_dict = json.loads(Path(result_path).read_text())
        self.log_dialog.add(f"Task completed: {Path(task.profile_file).name}")
        Path(result_path).unlink(missing_ok=True)
        save_path = Path(self.result_folder) / (
            Path(task.profile_file).stem + ".json"
        )
        # FIXME: when result file already exists, save with a timestamp.
        if save_path.exists():
            save_path = Path(self.result_folder) / (
                Path(task.profile_file).stem
                + datetime.now().strftime("_%Y%m%d_%H%M%S")
                + ".json"
            )
        Path(save_path).write_text(json.dumps(task.result_dict))

    traits_view = View(
        # run config
        HGroup(
            Item(
                "instruction_type",
                label="Type",
                enabled_when="not is_running",
            ),
            Item(
                "instruction_file",
                label="File",
                editor=FileEditor(dialog_style="open"),
                visible_when="input_mode == 'from_file'",
                enabled_when="not is_running",
            ),
            label="Run configuration",
            show_border=True,
        ),
        # run control
        HGroup(
            Item(
                "start_button",
                show_label=False,
                enabled_when="not is_running",
            ),
            Item(
                "stop_button",
                show_label=False,
                enabled_when="is_running",
            ),
            Item(
                "sequential_flag",
                label="Sequential",
                tooltip="Whether to run tasks sequentially.",
                enabled_when="not is_running",
            ),
        ),
        # sorting config
        HGroup(
            Item(
                "sorting_regex",
                label="Sorting regex",
                tooltip="Regex to sort profile files before task generation",
                width=150,
            ),
            Item("apply_regex_button", show_label=False),
            Item("ascending_sort", label="Ascending", show_label=True),
            Item("always_sort", label="Always", show_label=True),
        ),
        # task column
        Item(
            "tasks",
            editor=_task_table_editor,
            show_label=False,
            springy=True,
        ),
        HGroup(
            Item("progress_text", style="readonly", show_label=False),
            spring,
            Item("reload_button", show_label=False),
            Item("save_button", show_label=False),
        ),
        resizable=True,
        handler=_RefinementConfigHandler(),
    )


if __name__ == "__main__":
    pass
