#!/usr/bin/env python3

import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

from PyQt5.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QStatusBar,
    QToolBar,
    QWidget,
    QGroupBox,
    QGridLayout,
    QPushButton,
    QVBoxLayout,
    QLineEdit
    )


class Window(QMainWindow):
    def __init__(self):
        super().__init__(parent=None)
        self.title = 'FSM Uploader'
        self.top_offset = 100
        self.left_offset = 100
        self.width = 640
        self.height = 480
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self._initUI()
        # self.setCentralWidget(QLabel("I'm the Central Widget"))

    def _initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left_offset, self.top_offset, self.width, self.height)

        self._createMenu()
        self._createStatusBar()
        self._createFileChooser()
        self._createMainGrid()

        windowLayout = QVBoxLayout()
        windowLayout.addWidget(self.horizontalGroupBox)
        self.centralWidget.setLayout(windowLayout)

        self.show()

    
    def _createMenu(self):
        menu = self.menuBar().addMenu("&Menu")
        menu.addAction("&Exit", self.close)

    def _createStatusBar(self):
        status = QStatusBar()
        status.showMessage("I'm the Status Bar")
        self.setStatusBar(status)


    def _createFileChooser(self):
        layout = QGridLayout()
        layout.setColumnStretch(2,4)
        layout.addWidget(QLineEdit(self),0,0)
        layout.addWidget(QPushButton('...'))
        
        self.filepathBoxContainer = QVBoxLayout().addWidget(self).setLayout(layout)


    def _createMainGrid(self):
        self.horizontalGroupBox = QGroupBox("Grid")
        layout = QGridLayout()
        layout.setColumnStretch(1, 4)
        layout.setColumnStretch(2, 4)
        
        layout.addWidget(self.filepathBoxContainer,0,0)
        layout.addWidget(QPushButton('2'),0,1)
        layout.addWidget(QPushButton('3'),0,2)
        layout.addWidget(QPushButton('4'),1,0)
        layout.addWidget(QPushButton('5'),1,1)
        layout.addWidget(QPushButton('6'),1,2)
        layout.addWidget(QPushButton('7'),2,0)
        layout.addWidget(QPushButton('8'),2,1)
        layout.addWidget(QPushButton('9'),2,2)
        
        self.horizontalGroupBox.setLayout(layout)

        

def main():
    app = QApplication([])
    execute = Window()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()