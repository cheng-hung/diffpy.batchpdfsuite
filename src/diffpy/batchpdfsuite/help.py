from pathlib import Path

from traits.api import HasTraits

# FIXME: add image dir including splash image, log icon, and help icon
PACKAGE_DIR = Path(__file__).resolve().parent
IMAGE_DIR = PACKAGE_DIR / "images"


# FIXME: add quick start guide for the help button
class SuiteHelp(HasTraits):
    pass
