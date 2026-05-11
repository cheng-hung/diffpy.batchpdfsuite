from pyface.api import ImageResource
from traits.api import Any, HasTraits, Instance
from traitsui.api import Action, HGroup, InstanceEditor, Item, VGroup, View
from traitsui.menu import ToolBar

from diffpy.batchpdfsuite.help import IMAGE_DIR
from diffpy.batchpdfsuite.refinement_config import RefinementConfig
from diffpy.batchpdfsuite.refinement_editor import LogDialog
from diffpy.batchpdfsuite.refinement_io import (
    SimpleSelectFiles,
    SimpleSelectFolder,
)

toolbar_settings = Action(
    name="settings",
    action="_settings",
    tooltip="Configure the settings for PDF refinement",
    image=ImageResource(str(IMAGE_DIR / "settings.png")),
)
toolbar_refinement_log = Action(
    name="log",
    action="_refinement_log",
    tooltip="Display the runtime output for PDF refinement",
    image=ImageResource(str(IMAGE_DIR / "log.png")),
)

toolbar_help = Action(
    name="help",
    action="_help",
    tooltip="Quick start",
    image=ImageResource(str(IMAGE_DIR / "help.png")),
)

toolbar = ToolBar(
    toolbar_settings,
    toolbar_refinement_log,
    toolbar_help,
)


class BatchPDFsuiteGUI(HasTraits):
    splash = Any
    exp_files = Instance(SimpleSelectFolder, ())
    phase_files = Instance(SimpleSelectFiles, ())
    refinement_configuration = Instance(RefinementConfig)
    log_dialog = Instance(LogDialog, ())

    def __init__(self, *args, **kargs):
        super().__init__(*args, **kargs)
        self.refinement_configuration = RefinementConfig(
            structure_files_selector=self.phase_files,
            profile_folder_selector=self.exp_files,
            log_dialog=self.log_dialog,
        )
        if self.splash is not None:
            self.splash.close()

    def _refinement_log(self):
        self.log_dialog.edit_traits("log_view")
        return

    def _settings(self):
        pass

    def _help(self):
        pass

    traits_view = View(
        HGroup(
            VGroup(
                Item(
                    "exp_files",
                    style="custom",
                    editor=InstanceEditor(view="traits_view"),
                    show_label=False,
                ),
                Item(
                    "phase_files",
                    style="custom",
                    editor=InstanceEditor(view="traits_view"),
                    show_label=False,
                ),
            ),
            Item(
                "refinement_configuration",
                style="custom",
                editor=InstanceEditor(view="traits_view"),
                show_label=False,
            ),
        ),
        toolbar=toolbar,
        resizable=True,
        title="Batch PDF Refinement Suite",
        width=800,
        height=600,
    )
