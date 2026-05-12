import sys

from pyface.api import ImageResource, SplashScreen
from traits.etsconfig.api import ETSConfig

from diffpy.batchpdfsuite.batchpdfsuite_gui import BatchPDFsuiteGUI
from diffpy.batchpdfsuite.help import IMAGE_DIR

# break if help passed to the args
sysargv = sys.argv[1:]
# if ('--help' in sysargv) or('-h' in sysargv):
#     from dpx.srxplanargui.srxconfig import SrXconfig
#     SrXconfig(args=sysargv)

ETSConfig.toolkit = "qt"


# open splash screen
def maybe_show_splash(argv):
    if any(aa in ("-h", "--help") for aa in argv):
        return None

    try:
        splash = SplashScreen(
            image=ImageResource(str(IMAGE_DIR / "splash.png")),
            show_log_messages=False,
        )
        if splash is not None:
            splash.open()
        return splash
    except Exception:
        return None


def running_under_pytest():
    return "pytest" in sys.modules


splash = None
if not running_under_pytest():
    splash = maybe_show_splash(sysargv)


def main():
    gui = BatchPDFsuiteGUI(splash=splash)
    gui.configure_traits(view="traits_view")
    return


if __name__ == "__main__":
    sys.exit(main())
    # main()
