import io
import os

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import (
    QDialog,
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from PIL import Image

from logic import get_image_files, move_image


# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------

DARK_THEME = """
    QWidget {
        background-color: #121212;
        color: #e0e0e0;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 13px;
    }

    QDialog, QMainWindow {
        background-color: #121212;
    }

    QLabel {
        color: #e0e0e0;
        background-color: transparent;
    }

    QLineEdit {
        background-color: #1e1e1e;
        border: 1px solid #3a3a3a;
        border-radius: 5px;
        padding: 6px 10px;
        color: #e0e0e0;
        selection-background-color: #0078d4;
    }

    QLineEdit:focus {
        border-color: #0078d4;
    }

    QPushButton {
        background-color: #1e1e1e;
        color: #e0e0e0;
        border: 1px solid #3a3a3a;
        border-radius: 5px;
        padding: 6px 16px;
    }

    QPushButton:hover {
        background-color: #2a2a2a;
        border-color: #0078d4;
        color: #ffffff;
    }

    QPushButton:pressed {
        background-color: #0078d4;
        border-color: #0078d4;
    }

    QMessageBox {
        background-color: #1a1a1a;
    }

    QMessageBox QLabel {
        color: #e0e0e0;
    }

    QMessageBox QPushButton {
        min-width: 80px;
    }
"""

BRAND = "By BigH"


def apply_dark_theme(app):
    app.setStyleSheet(DARK_THEME)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_divider():
    """Return a thin horizontal rule QLabel."""
    line = QLabel()
    line.setFixedHeight(1)
    line.setStyleSheet("background-color: #2a2a2a;")
    return line


def _header_label(text):
    label = QLabel(text)
    label.setFont(QFont("Segoe UI", 18, QFont.Bold))
    label.setStyleSheet("color: #ffffff; letter-spacing: 1px;")
    label.setAlignment(Qt.AlignCenter)
    return label


def _sub_label(text):
    label = QLabel(text)
    label.setFont(QFont("Segoe UI", 9))
    label.setStyleSheet("color: #555555;")
    label.setAlignment(Qt.AlignCenter)
    return label


# ---------------------------------------------------------------------------
# Explanation dialog
# ---------------------------------------------------------------------------

EXPLANATION_PAGES = [
    (
        "Page 1 of 3 — Introduction\n\n"
        "Welcome to the Screenshot Annotation Tool!\n\n"
        'This tool lets you categorize screenshots into "Enemy Present" and '
        '"No Enemy Present" folders for AI training.\n\n'
        "Before starting, create two output folders:\n"
        "  •  One for images that contain an enemy\n"
        "  •  One for images that do not contain an enemy\n\n"
        "Click Next to continue."
    ),
    (
        "Page 2 of 3 — Select Directories\n\n"
        "You need to provide three folder paths:\n\n"
        "  1.  Screenshot Directory — where your source images live\n"
        "  2.  Enemy Present — destination for images with enemies\n"
        "  3.  No Enemy Present — destination for images without enemies\n\n"
        "Use the Browse buttons to pick each folder. "
        "Clicking Browse again replaces the current selection.\n\n"
        "Click Next to continue."
    ),
    (
        "Page 3 of 3 — Annotating\n\n"
        "Once directories are set, click Start Annotation.\n\n"
        "For each image:\n"
        "  •  Click  Enemy Present  if an enemy is visible\n"
        "  •  Click  No Enemy Present  if there is no enemy\n\n"
        "The image is moved to the correct folder automatically. "
        "Keep going until all images are processed.\n\n"
        "Click Next to close this guide."
    ),
]


class ExplanationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"How to Use — {BRAND}")
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.setMinimumWidth(540)
        self.page_number = 0
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)

        layout.addWidget(_header_label("How to Use"))
        layout.addWidget(_sub_label(BRAND))
        layout.addWidget(_make_divider())

        self.text_label = QLabel(EXPLANATION_PAGES[self.page_number])
        self.text_label.setWordWrap(True)
        self.text_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.text_label.setStyleSheet(
            "color: #cccccc; line-height: 160%; padding: 10px 0;"
        )
        layout.addWidget(self.text_label)

        layout.addWidget(_make_divider())

        self.next_btn = QPushButton("Next  →")
        self.next_btn.setFixedHeight(38)
        self.next_btn.setStyleSheet(
            "QPushButton { background-color: #0078d4; color: #ffffff; border: none;"
            "  border-radius: 5px; font-weight: bold; }"
            "QPushButton:hover { background-color: #1a8fe3; }"
            "QPushButton:pressed { background-color: #005fa3; }"
        )
        self.next_btn.clicked.connect(self._next_page)
        layout.addWidget(self.next_btn, alignment=Qt.AlignRight)

    def _next_page(self):
        self.page_number += 1
        if self.page_number < len(EXPLANATION_PAGES):
            self.text_label.setText(EXPLANATION_PAGES[self.page_number])
        else:
            self.accept()


# ---------------------------------------------------------------------------
# Setup dialog
# ---------------------------------------------------------------------------

class SetupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"AI Image Selection Tool — {BRAND}")
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.setMinimumWidth(620)
        self._build_ui()

    def _build_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(30, 25, 30, 25)
        root_layout.setSpacing(0)

        # Header
        root_layout.addWidget(_header_label("Enemy or Not"))
        root_layout.addSpacing(4)
        root_layout.addWidget(_sub_label(BRAND))
        root_layout.addSpacing(18)
        root_layout.addWidget(_make_divider())
        root_layout.addSpacing(20)

        # Directory grid
        grid = QGridLayout()
        grid.setSpacing(10)
        grid.setColumnStretch(1, 1)

        def add_dir_row(row, label_text, entry_attr):
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: #aaaaaa;")
            entry = QLineEdit()
            entry.setPlaceholderText("Click Browse to select a folder...")
            entry.setFixedHeight(34)
            browse_btn = QPushButton("Browse")
            browse_btn.setFixedSize(80, 34)
            browse_btn.clicked.connect(lambda _, e=entry: self._browse(e))
            grid.addWidget(lbl, row, 0)
            grid.addWidget(entry, row, 1)
            grid.addWidget(browse_btn, row, 2)
            setattr(self, entry_attr, entry)

        add_dir_row(0, "Screenshot Directory", "screenshot_entry")
        add_dir_row(1, "Enemy Present Folder", "enemy_entry")
        add_dir_row(2, "No Enemy Folder", "no_enemy_entry")

        root_layout.addLayout(grid)
        root_layout.addSpacing(24)
        root_layout.addWidget(_make_divider())
        root_layout.addSpacing(18)

        # Bottom row: explanation + start
        btn_row = QHBoxLayout()

        explain_btn = QPushButton("? How to Use")
        explain_btn.setFixedHeight(38)
        explain_btn.clicked.connect(self._show_explanation)
        btn_row.addWidget(explain_btn)

        btn_row.addStretch()

        start_btn = QPushButton("Start Annotation  ▶")
        start_btn.setFixedHeight(38)
        start_btn.setMinimumWidth(180)
        start_btn.setStyleSheet(
            "QPushButton { background-color: #1a7f37; color: #ffffff; border: none;"
            "  border-radius: 5px; font-weight: bold; font-size: 14px; }"
            "QPushButton:hover { background-color: #22a045; }"
            "QPushButton:pressed { background-color: #145c28; }"
        )
        start_btn.clicked.connect(self._on_start)
        btn_row.addWidget(start_btn)

        root_layout.addLayout(btn_row)

    def _browse(self, entry):
        directory = QFileDialog.getExistingDirectory(self, "Select Folder")
        if directory:
            entry.setText(directory)

    def _show_explanation(self):
        ExplanationDialog(self).exec()

    def _on_start(self):
        if (
            self.screenshot_entry.text()
            and self.enemy_entry.text()
            and self.no_enemy_entry.text()
        ):
            self.accept()
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("Missing Directories")
            msg.setText("Please select all three directories before starting.")
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()

    def get_directories(self):
        return (
            self.screenshot_entry.text(),
            self.enemy_entry.text(),
            self.no_enemy_entry.text(),
        )


# ---------------------------------------------------------------------------
# Annotation window
# ---------------------------------------------------------------------------

class AnnotationWindow(QMainWindow):
    def __init__(self, screenshot_dir, enemy_present_dir, no_enemy_present_dir):
        super().__init__()
        self.screenshot_dir = screenshot_dir
        self.enemy_present_dir = enemy_present_dir
        self.no_enemy_present_dir = no_enemy_present_dir
        self.files = get_image_files(screenshot_dir)
        self.idx = 0

        self.setWindowTitle(f"Annotation Tool — {BRAND}")
        self.setFixedSize(580, 700)
        self._build_ui()
        self._display_image()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(0)

        # Top bar: title + counter
        top_bar = QHBoxLayout()
        title = QLabel("Screenshot Annotation")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet("color: #ffffff;")
        top_bar.addWidget(title)

        top_bar.addStretch()

        self.counter_label = QLabel()
        self.counter_label.setStyleSheet("color: #555555; font-size: 12px;")
        top_bar.addWidget(self.counter_label)

        layout.addLayout(top_bar)
        layout.addSpacing(4)
        layout.addWidget(_sub_label(BRAND))
        layout.addSpacing(14)
        layout.addWidget(_make_divider())
        layout.addSpacing(14)

        # Image display
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setFixedSize(530, 530)
        self.image_label.setStyleSheet(
            "border: 1px solid #2a2a2a;"
            "border-radius: 6px;"
            "background-color: #0a0a0a;"
        )
        layout.addWidget(self.image_label, alignment=Qt.AlignCenter)

        layout.addSpacing(16)
        layout.addWidget(_make_divider())
        layout.addSpacing(14)

        # Annotation buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(16)

        self.enemy_btn = QPushButton("Enemy Present")
        self.enemy_btn.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.enemy_btn.setFixedHeight(54)
        self.enemy_btn.setStyleSheet(
            "QPushButton {"
            "  background-color: #1a7f37; color: #ffffff;"
            "  border: none; border-radius: 6px;"
            "}"
            "QPushButton:hover { background-color: #22a045; }"
            "QPushButton:pressed { background-color: #145c28; }"
        )
        self.enemy_btn.clicked.connect(lambda: self._annotate("enemy_present"))
        btn_layout.addWidget(self.enemy_btn)

        self.no_enemy_btn = QPushButton("No Enemy Present")
        self.no_enemy_btn.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.no_enemy_btn.setFixedHeight(54)
        self.no_enemy_btn.setStyleSheet(
            "QPushButton {"
            "  background-color: #b91c1c; color: #ffffff;"
            "  border: none; border-radius: 6px;"
            "}"
            "QPushButton:hover { background-color: #dc2626; }"
            "QPushButton:pressed { background-color: #7f1d1d; }"
        )
        self.no_enemy_btn.clicked.connect(lambda: self._annotate("no_enemy_present"))
        btn_layout.addWidget(self.no_enemy_btn)

        layout.addLayout(btn_layout)

    def _update_counter(self):
        total = len(self.files)
        self.counter_label.setText(f"Image {self.idx + 1} of {total}")

    def _display_image(self):
        self._update_counter()
        image_path = os.path.join(self.screenshot_dir, self.files[self.idx])
        image = Image.open(image_path).resize((530, 530))

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")

        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())
        self.image_label.setPixmap(pixmap)

    def _annotate(self, annotation):
        dest_dir = (
            self.enemy_present_dir
            if annotation == "enemy_present"
            else self.no_enemy_present_dir
        )
        move_image(self.screenshot_dir, self.files[self.idx], dest_dir)
        self.idx += 1

        if self.idx < len(self.files):
            self._display_image()
        else:
            msg = QMessageBox(self)
            msg.setWindowTitle("Done")
            msg.setText("All images have been annotated.")
            msg.setIcon(QMessageBox.Information)
            msg.exec_()
            self.close()
