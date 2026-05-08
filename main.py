"""Backwards-compatible entry point. Use 'python -m xampp_tray' or 'xampp-tray' instead."""
import os
import sys

# Support the installed .deb layout: /usr/share/xampp-tray/main.py
_lib = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")
if os.path.exists(_lib):
    sys.path.insert(0, _lib)

_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if os.path.exists(_src):
    sys.path.insert(0, _src)

from xampp_tray.__main__ import main  # noqa: E402

if __name__ == "__main__":
    main()
