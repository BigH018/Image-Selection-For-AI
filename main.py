import sys

from PyQt5.QtWidgets import QApplication, QDialog

from ui import AnnotationWindow, SetupDialog, apply_dark_theme


def main():
    app = QApplication(sys.argv)
    apply_dark_theme(app)

    setup = SetupDialog()
    if setup.exec() == QDialog.Accepted:
        screenshot_dir, enemy_dir, no_enemy_dir = setup.get_directories()
        window = AnnotationWindow(screenshot_dir, enemy_dir, no_enemy_dir)
        window.show()
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
