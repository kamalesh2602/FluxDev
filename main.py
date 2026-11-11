"""
FluxDev — Where ideas flow into code.
Main entry point launching the frameless, minimal code studio.
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

from editor.main_window import MainWindow


def main():
    """Initializes and runs the FluxDev PyQt6 application."""
    if os.name == "nt":
        try:
            import ctypes
            app_id = "FluxDev.Studio.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setApplicationName("FluxDev")
    app.setOrganizationName("FluxDevStudio")
    app.setApplicationVersion("1.0.0")

    window = MainWindow()

    # Open file/folder arguments if passed
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if os.path.isfile(arg):
                window.tab_manager.open_file(arg)
            elif os.path.isdir(arg):
                window.sidebar.set_root_path(arg)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
