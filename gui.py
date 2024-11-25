#!/usr/bin/env python3

import os
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import pyqtSlot

import sys

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QGridLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QLineEdit,
    QCheckBox,
    QGroupBox,
    QTextBrowser,
    QMainWindow
    )

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def create_text_entry(self, section_title:str, placeholder_text:str, stylesheet:str|None=None, echomode=QLineEdit.EchoMode.Normal):
        title_label = QLabel(section_title)
        if stylesheet is None:
            stylesheet = 'font-weight: normal; font-size: 11px'
        title_label.setStyleSheet(stylesheet)
        text_box = QLineEdit(self)
        text_box.setEchoMode(echomode)
        text_box.setPlaceholderText(placeholder_text)

        return title_label, text_box
    
    def position_text_entry(self, grid_layout:QGridLayout, top_left_row:int, top_left_col:int,
                              title:QLabel, text_box:QLineEdit,
                              columns:int = 5):
        grid_layout.addWidget(title, top_left_row, top_left_col, 1, 1)
        grid_layout.addWidget(text_box, top_left_row, top_left_col+1, 1, (columns-1))

        return top_left_row + 2
    
    def create_file_chooser(self, section_title:str, target_file_name:str, stylesheet:str|None=None):
        title_label = QLabel(section_title)
        if stylesheet is None:
            stylesheet = 'font-weight: normal; font-size: 11px'
        title_label.setStyleSheet(stylesheet)
        text_box = QLineEdit(self)
        text_box.setPlaceholderText(f"Enter path to {target_file_name}...")
        browse_button = QPushButton('Browse', self)

        return title_label, text_box, browse_button
    
    def position_file_chooser(self, grid_layout:QGridLayout, top_left_row:int, top_left_col:int,
                              title:QLabel, text_box:QLineEdit, button:QPushButton,
                              columns:int = 5):
        grid_layout.addWidget(title, top_left_row, top_left_col, 1, 1)
        grid_layout.addWidget(text_box, top_left_row, top_left_col+1, 1, columns-2)
        grid_layout.addWidget(button, top_left_row, top_left_col+(columns-1), 1, 1)

        return top_left_row + 2
    
    def init_ui(self):
        default_stylesheet = 'font-weight: normal; font-size: 11px'
        master_grid_layout = QGridLayout()
        
        target_row_ftp = 0
        target_row_directories = 0
        target_row_edits = 0
        target_row_management = 0

        box_ftp = QGroupBox()
        box_directories = QGroupBox()
        box_edits = QGroupBox()
        box_management = QGroupBox()
        box_output = QGroupBox()

        grid_ftp = QGridLayout()
        grid_directories = QGridLayout()
        grid_edits = QGridLayout()
        grid_management = QGridLayout()
        grid_output = QGridLayout()
        
        box_ftp.setTitle('FTP Configuration')
        box_directories.setTitle('Directories')
        box_edits.setTitle('Edits')
        box_management.setTitle('File Management')
        box_output.setTitle('Output')

        box_ftp.setLayout(grid_ftp)
        box_directories.setLayout(grid_directories)
        box_edits.setLayout(grid_edits)
        box_management.setLayout(grid_management)
        box_output.setLayout(grid_output)

        # Main layout
        master_grid_layout.addWidget(box_ftp, 0, 0, 1, 1)
        master_grid_layout.addWidget(box_directories, 1, 0, 1, 1)
        master_grid_layout.addWidget(box_edits, 2, 0, 1, 1)
        master_grid_layout.addWidget(box_management, 3, 0, 1, 1)
        master_grid_layout.addWidget(box_output, 0,1,5,1)
        master_grid_layout.setColumnMinimumWidth(0,400)

        self.uploader = QWidget()
        self.uploader.setLayout(master_grid_layout)

        # Main window configuration
        ## Locate uploader widget
        self.setCentralWidget(self.uploader)
        menu_bar = self.menuBar()
        ## Create file menu
        file_menu = menu_bar.addMenu('File')
        config_open = QAction('Open',self)
        config_open.triggered.connect(self.config_read)
        config_save = QAction('Save',self)
        config_save.triggered.connect(self.config_write)
        close_action = QAction('Exit', self)
        close_action.triggered.connect(self.close)
        file_menu.addAction(config_open)
        file_menu.addAction(config_save)
        file_menu.addSeparator()
        file_menu.addAction(close_action)

        # Position UI Elements
        ## FTP Parameters
        self.ti_hostname, self.tb_hostname = self.create_text_entry('Hostname','e.g., 192.168.0.1, https://example.com', stylesheet=default_stylesheet)
        target_row_ftp = self.position_text_entry(grid_ftp, target_row_ftp, 0, self.ti_hostname, self.tb_hostname)
        self.ti_port, self.tb_port = self.create_text_entry('Port','e.g., 22', stylesheet=default_stylesheet)
        target_row_ftp = self.position_text_entry(grid_ftp, target_row_ftp, 0, self.ti_port, self.tb_port)
        self.ti_username, self.tb_username = self.create_text_entry('Username','Enter your FTP username...', stylesheet=default_stylesheet)
        target_row_ftp = self.position_text_entry(grid_ftp, target_row_ftp, 0, self.ti_username, self.tb_username)
        self.ti_password, self.tb_password = self.create_text_entry('Password','Enter your FTP password...', echomode=QLineEdit.EchoMode.Password, stylesheet=default_stylesheet)
        target_row_ftp = self.position_text_entry(grid_ftp, target_row_ftp, 0, self.ti_password, self.tb_password)

        ## Directories
        self.ti_remote_dir, self.tb_remote_dir = self.create_text_entry('Remote directory','Directory on FTP host', stylesheet=default_stylesheet)
        target_row_directories = self.position_text_entry(grid_directories, target_row_directories, 0, self.ti_remote_dir, self.tb_remote_dir)
        self.ti_local_dir, self.tb_local_dir, self.bb_local_dir = self.create_file_chooser('Local website folder','Folder containing the FS Manager generated site', stylesheet=default_stylesheet)
        target_row_directories = self.position_file_chooser(grid_directories, target_row_directories, 0, self.ti_local_dir, self.tb_local_dir, self.bb_local_dir)
        self.ti_swiss_timing, self.tb_swiss_timing, self.bb_swiss_timing = self.create_file_chooser('FS Manager Folder','FS Manager root folder', stylesheet=default_stylesheet)
        self.tb_swiss_timing.setText(r'C:\SwissTiming\OVR\FSManager')
        target_row_directories = self.position_file_chooser(grid_directories, target_row_directories, 0, self.ti_swiss_timing, self.tb_swiss_timing, self.bb_swiss_timing)

        ## Edits
        self.ti_edits, self.tb_edits, self.bb_edits = self.create_file_chooser('Edits file','CSV file containing replacements to make', stylesheet=default_stylesheet)
        target_row_edits = self.position_file_chooser(grid_edits, target_row_edits, 0, self.ti_edits, self.tb_edits, self.bb_edits)

        ## Management
        self.ti_movepdf = QLabel('Move PDFs?')
        self.ti_movepdf.setStyleSheet(default_stylesheet)
        grid_management.addWidget(self.ti_movepdf, target_row_management, 0, 1, 1)
        self.cb_movepdf = QCheckBox()
        grid_management.addWidget(self.cb_movepdf, target_row_management, 1, 1, 1)
        target_row_management += 1
        self.ti_save_file, self.tb_save_file, self.bb_save_file = self.create_file_chooser('Save File','save state file',stylesheet=default_stylesheet)
        target_row_management = self.position_file_chooser(grid_management, target_row_management, 0, self.ti_save_file, self.tb_save_file, self.bb_save_file)

        ## Output
        self.output_feed = QTextBrowser()
        grid_output.addWidget(self.output_feed)

        ## Run button
        self.run_button = QPushButton()
        self.run_button.setText('Run!')
        master_grid_layout.addWidget(self.run_button,master_grid_layout.rowCount()-1,0,
                                     1, master_grid_layout.columnCount()-1)

        # Connect buttons
        self.bb_local_dir.clicked.connect(lambda: self.open_file_chooser(self.tb_local_dir, filemode=QFileDialog.FileMode.Directory, options=[QFileDialog.Option.ShowDirsOnly], dialog_text='Select a directory'))
        self.bb_edits.clicked.connect(lambda: self.open_file_chooser(self.tb_edits, filemode=QFileDialog.FileMode.ExistingFile, dialog_text='Select a file', file_filters=['Edit list files (*.csv)']))
        self.bb_save_file.clicked.connect(lambda: self.open_file_chooser(self.tb_save_file, filemode=QFileDialog.FileMode.AnyFile, dialog_text='Select a file or enter a path', file_filters=['Save states (*.csv)']))
        self.bb_swiss_timing.clicked.connect(lambda: self.open_file_chooser(self.tb_swiss_timing, filemode=QFileDialog.FileMode.Directory, options=[QFileDialog.Option.ShowDirsOnly], dialog_text='Select a file or enter a path', file_filters=['Save states (*.csv)']))
        self.setWindowTitle("FS Manager Web Uploader")
        self.setGeometry(100, 100, 800, 100)
    
    def open_file_chooser(self, target_text_box: QLineEdit, file_filters:list[str]|None=None, options:list[QFileDialog.Option]|None=None,
                            dialog_text:str='Select a file', filemode:QFileDialog.FileMode=QFileDialog.FileMode.AnyFile):
        dialog = QFileDialog()
        
        if file_filters is None:
            file_filters = []
        file_filters.extend(['All Files (*)'])
        file_filters = ';;'.join(file_filters)
        dialog.setNameFilter(file_filters)
        
        if options is None:
            options = []
        options.extend([QFileDialog.Option.DontUseCustomDirectoryIcons])
        options = list(set(options))

        dialog.setFileMode(filemode)
        if len(options)>0:
            for option in options:
                dialog.setOption(option, True)

        if dialog.exec():
            file_path = dialog.selectedFiles()
        else:
            file_path = None
            
        if file_path is not None:
            target_text_box.setText(os.path.normpath(file_path[0]))
        
    def config_read(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Load configuration file', '', 'Config files (*.ini);;All files (*)'
        )
        if file_path:
            print('Hooray!')
    
    def config_write(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, 'Load configuration file', '', 'Config files (*.ini);;All files (*)'
        )
        if file_path:
            print('Hooray!')

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()