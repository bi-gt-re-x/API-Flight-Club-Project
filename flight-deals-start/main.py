from __future__ import annotations

import sys
from PyQt6.QtWidgets import QApplication
from ui_styles import setup_dark_theme
from main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    setup_dark_theme(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
