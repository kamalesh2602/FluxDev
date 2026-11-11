"""
FluxDev path utilities — PyInstaller-safe resource and data-directory helpers.

Two helpers are provided:

* ``get_resource_path(relative_path)``
  Locates a *read-only* bundled resource.  When the app is frozen by
  PyInstaller the bundle root is ``sys._MEIPASS``; in a normal Python
  environment the bundle root is the directory that contains this file.

* ``get_appdata_path(*parts)``
  Returns a writable path inside ``%APPDATA%\\FluxDev`` (Windows) or
  ``~/.local/share/FluxDev`` (non-Windows), creating intermediate
  directories as needed.  Use this for every file the app generates at
  runtime (settings exports, caches, logs, etc.) so the app never tries
  to write inside the read-only PyInstaller bundle.
"""

import os
import sys


def get_resource_path(relative_path: str) -> str:
    """
    Return the absolute path to a bundled read-only resource.

    When running as a PyInstaller one-file/one-dir build, resources are
    extracted to ``sys._MEIPASS``.  In a normal dev environment they live
    next to this file's package directory.

    Parameters
    ----------
    relative_path:
        Path relative to the bundle / package root
        (e.g. ``"resources/icon.png"``).
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = sys._MEIPASS  # PyInstaller temp-extraction folder
    else:
        # Development: resolve relative to the *package* root (editor/)
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


def get_appdata_path(*parts: str) -> str:
    """
    Return a writable path inside the FluxDev application-data directory.

    On Windows  : ``%APPDATA%\\FluxDev\\<parts>``
    On other OS : ``~/.local/share/FluxDev/<parts>``

    Intermediate directories are created automatically.

    Parameters
    ----------
    *parts:
        Path components to append after the base directory
        (e.g. ``get_appdata_path("cache", "preview.html")``).
    """
    if os.name == "nt":
        base = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "FluxDev")
    else:
        base = os.path.join(os.path.expanduser("~"), ".local", "share", "FluxDev")

    path = os.path.join(base, *parts) if parts else base
    os.makedirs(os.path.dirname(path) if os.path.splitext(path)[1] else path, exist_ok=True)
    return path

