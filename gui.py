#!/usr/bin/env python3

import sys
import os

from PyQt6.QtGui import QIcon
from PyQt6.QtCore import pyqtSlot

from PyQt6.QtWidgets import (
    QApplication,
    # QLabel,
    # QMainWindow,
    # QStatusBar,
    # QToolBar,
    QWidget,
    # QGroupBox,
    QGridLayout,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QLineEdit
    )

class Application(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        grid_layout = QGridLayout()

        self.text_box = QLineEdit(self)
        self.text_box.setPlaceholderText("Enter file path...")
        self.browse_button = QPushButton("Browse", self)

        grid_layout.addWidget(self.text_box, 0,0,1,2)
        grid_layout.addWidget(self.browse_button,0,0,1,1)

        main_layout.addLayout(file_layout)

        self.setLayout(main_layout)

        self.browse_button.clicked.connect(self.open_file_chooser)
        self.setWindowTitle("FS Manager Web Uploader")
        self.setGeometry(100, 100, 400, 100)
    
    def open_file_chooser(self):
        # Open file dialog and get the selected file path
        options = QFileDialog.Option.DontUseCustomDirectoryIcons
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select a file", "", "Config Files (*.ini);;All Files (*)", options=options
        )
        if file_path:
            self.text_box.setText(file_path)

def main():
    app = QApplication(sys.argv)
    window = Application()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()