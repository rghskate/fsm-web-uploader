# FSM Web Uploader: a simple program for uploading the web files produced by FS Manager software used in figure skating judging.
#     Copyright (C) 2025  Robert Hayes

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import sys
from bs4 import BeautifulSoup
import pandas as pd
from time import sleep
from datetime import datetime

import fs_uploader as fs

from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QThread, pyqtSignal, QObject, Qt, QUrl

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
    QPlainTextEdit,
    QMainWindow,
    QMessageBox,
    QDateTimeEdit,
    QTextBrowser,
    )

class Uploader(QObject):
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.config = None
        self.sleep = None

    def set_arguments(self, configuration: fs.Configuration, sleep_interval:int=5, manual_time:datetime = None):
        self.config = configuration
        self.sleep = sleep_interval
        self.manual_time = manual_time
    
    def set_continue_state(self, state:bool=True):
        self.continue_signal = state

    def upload(self, sleep_interval:int = 5):
        configuration = self.config
        try:
            os.chdir(configuration.local_dir)
        except OSError as e:
            self.output_signal.emit('Encountered OSError when changing working directory:\n')
            self.output_signal.emit(f'{e}\n')
            self.output_signal.emit('Is this definitely the correct directory?')
            self.finished_signal.emit()
            return

        try:
            with open(os.path.join(configuration.local_dir,'index.htm'),'r') as f:
                html_content = f.read()
        except Exception as e:
            self.output_signal.emit('Could not open index file with the following error:\n')
            self.output_signal.emit(f'{e}')
            self.finished_signal.emit()
            return
        
        if fs.verify_file_status(html_content) is False:
            self.output_signal.emit('ISU copyright notice could not be found in index.htm! Either this is the wrong folder or you have been modifying the templates extensively.\nRestore the default copyright notice to the generated site to continue.')
            self.finished_signal.emit()
            return

        soup = BeautifulSoup(html_content,'lxml')

        try:
            results_table = fs.find_results_table(soup)
        except Exception as e:
            self.output_signal.emit('Failed to find timetable with following error:')
            self.output_signal.emit(e)
            self.finished_signal.emit()
            return

        segments = fs.build_segment_table(results_table)

        try:
            ftp = fs.return_from_generator_gui(fs.ftp_connect, self,
                                            [configuration.host,
                                            configuration.user,
                                            configuration.password,
                                            configuration.remote_dir,
                                            configuration.port,
                                            '"Stop"'])
        except ConnectionError as e:
            self.finished_signal.emit()
            return
        except Exception as e:
            self.output_signal.emit(f'{e}')
            self.finished_signal.emit()
            return
        
        if configuration.replace is not None:
            try:
                replacements = pd.read_csv(configuration.replace, dtype=str)
            except Exception as e:
                self.output_signal.emit('Could not open replacements file with following error:')
                self.output_signal.emit(e)
                self.finished_signal.emit()
                return
        
        if configuration.save_file is None:
            filetable_current = pd.DataFrame({'filepaths':'',
                                        'hashes':''}, index = [0])
        else:
            try:
                filetable_current = pd.read_csv(os.path.abspath(os.path.normpath(configuration.save_file)))
            except FileNotFoundError:
                self.output_signal.emit('No save file found at specified address. Uploading all files and continuing.')
                filetable_current = pd.DataFrame({'filepaths':'',
                                                'hashes':''}, index = [0])
        
        time_last_update = datetime.now()
        filetable_for_disk = filetable_current
        while self.continue_signal is True:
            filetable_for_disk, time_last_update = fs.return_from_generator_gui(
                fs.update_ftp_server, self,
                (ftp, filetable_for_disk, configuration, replacements, segments, time_last_update, self.manual_time, False, self)
            )
            sleep(sleep_interval)
        
        ftp.quit()
        self.output_signal.emit('Connection closed.')
        if (configuration.save_file is not None) and (filetable_for_disk is not None):
            filetable_for_disk.to_csv(os.path.abspath(os.path.normpath(configuration.save_file)), index=False)
            self.output_signal.emit(f'Wrote current filetable status to "{os.path.abspath(os.path.normpath(configuration.save_file))}".')
        
        self.finished_signal.emit()
        return

class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('About')
        self.setGeometry(150,150,800,800)
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        self.gnu = QTextBrowser()
        self.gnu.setSource(QUrl(f"file:{os.path.abspath(os.path.join(os.path.dirname(__file__),'LICENSE.md'))}"))
        self.bsd = QTextBrowser()
        self.bsd.setSource(QUrl(f"file:{os.path.abspath(os.path.join(os.path.dirname(__file__),'LICENSES.md'))}"))
        self.heading = QLabel('FSM Web Uploader is a simple program intended to make the upload of websites produced by FS Manager easier.\n'
                              'The main motivation behind the software was to automate a process of withholding the upload of panel makeup\n'
                              'until the start of a segment, so as to avoid sending out conflicting information ahead of the event.\n\n'
                              'This program will also scrape the directories of FSM to find the results PDFs for upload to the site.\n\n'
                              'This software is licensed under the GPL 3.0 License, the text of which can be found below or bundled with this program.\n'
                              'The author can be reached at robert.hayes@iceskating.org.uk.')
        self.subheading = QLabel('The following third party licenses are also included to ensure compliance for the use of their modules:')
        layout.addWidget(self.heading, 0, 0, 1, 1)
        layout.addWidget(self.gnu, 1, 0, 1, 1)
        layout.addWidget(self.subheading, 2, 0, 1, 1)
        layout.addWidget(self.bsd, 3, 0, 1, 1)
        self.setLayout(layout)

class HelpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Help')
        self.setGeometry(150,150,800,800)
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        self.readme = QTextBrowser()
        self.readme.setSource(QUrl(f"file:{os.path.abspath(os.path.join(os.path.dirname(__file__),'README.md'))}"))
        layout.addWidget(self.readme, 0, 0, 1, 1)
        self.setLayout(layout)

class TimeWindow(QWidget):
    '''
    Window for setting a manual override time.
    '''
    chosen_time = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Manual time entry')
        self.setGeometry(150, 150, 300, 100)
        self.initUI()

    def initUI(self):
        layout = QGridLayout()
        
        self.checkbox_label = QLabel('Use manual upload time?')
        self.checkbox = QCheckBox()
        self.checkbox.clicked.connect(self.enable_time_chooser)

        layout.addWidget(self.checkbox_label, 0, 0, 1, 1)
        layout.addWidget(self.checkbox, 0, 1, 1, 1)
        
        self.timechooser = QDateTimeEdit()
        self.timechooser.setCalendarPopup(True)
        self.timechooser.setDateTime(datetime.now())
        self.timechooser.setEnabled(self.checkbox.isChecked())
        layout.addWidget(self.timechooser, 1, 0, 1, 2)

        self.setLayout(layout)
    
    def enable_time_chooser(self):
        self.timechooser.setEnabled(self.checkbox.isChecked())
    
    def closeEvent(self, event):
        if self.checkbox.isChecked():
            value = self.timechooser.dateTime().toPyDateTime()
        else:
            value = None
        self.chosen_time.emit(value)
        event.accept()
        

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def create_text_entry(self, section_title:str, placeholder_text:str, stylesheet:str|None=None, echomode=QLineEdit.EchoMode.Normal):
        '''
        Helper function for creating labelled text entry fields.
        '''
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
        '''
        Helper function for positioning text entry fields and labels next to one another on a QGridLayout
        '''
        grid_layout.addWidget(title, top_left_row, top_left_col, 1, 1)
        grid_layout.addWidget(text_box, top_left_row, top_left_col+1, 1, (columns-1))

        return top_left_row + 2
    
    def create_file_chooser(self, section_title:str, target_file_name:str, stylesheet:str|None=None):
        '''
        Helper function for creating file chooser buttons and textboxes.
        '''
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
        '''
        Helper function for positioning file choosers on a QGridLayout
        '''
        grid_layout.addWidget(title, top_left_row, top_left_col, 1, 1)
        grid_layout.addWidget(text_box, top_left_row, top_left_col+1, 1, columns-2)
        grid_layout.addWidget(button, top_left_row, top_left_col+(columns-1), 1, 1)

        return top_left_row + 2

    def init_ui(self):
        self.manual_time = None
        self.ui_state = True

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
        config_open = QAction('Load configuration...',self)
        config_open.triggered.connect(self.config_read)
        config_save = QAction('Save configuration...',self)
        config_save.triggered.connect(self.config_write)
        close_action = QAction('Exit', self)
        close_action.triggered.connect(self.close)
        file_menu.addAction(config_open)
        file_menu.addAction(config_save)
        file_menu.addSeparator()
        file_menu.addAction(close_action)
        ## Create options menu
        options_menu = menu_bar.addMenu('Options')
        set_time = QAction('Set manual time', self)
        set_time.triggered.connect(self.set_manual_time)
        about_window = QAction('About', self)
        about_window.triggered.connect(self.show_about)
        help_window = QAction('Help', self)
        help_window.triggered.connect(self.show_help)
        options_menu.addAction(set_time)
        options_menu.addSeparator()
        options_menu.addAction(help_window)
        options_menu.addAction(about_window)

        self.setWindowTitle("FS Manager Web Uploader")
        self.setGeometry(100, 100, 800, 100)

        # Position UI Elements
        ## FTP Parameters
        self.ti_hostname, self.tb_hostname = self.create_text_entry('Hostname','e.g., 192.168.0.1, https://example.com', stylesheet=default_stylesheet)
        target_row_ftp = self.position_text_entry(grid_ftp, target_row_ftp, 0, self.ti_hostname, self.tb_hostname)
        self.ti_port, self.tb_port = self.create_text_entry('Port','e.g., 21', stylesheet=default_stylesheet)
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
        self.cb_movepdf.setChecked(True)
        grid_management.addWidget(self.cb_movepdf, target_row_management, 1, 1, 1)
        target_row_management += 1
        self.ti_save_file, self.tb_save_file, self.bb_save_file = self.create_file_chooser('Save File','save state file',stylesheet=default_stylesheet)
        target_row_management = self.position_file_chooser(grid_management, target_row_management, 0, self.ti_save_file, self.tb_save_file, self.bb_save_file)

        ## Output
        self.output_feed = QPlainTextEdit()
        self.output_feed.setReadOnly(True)
        grid_output.addWidget(self.output_feed)

        ## Run button
        self.run_button = QPushButton()
        self.run_button.setText('Run!')
        master_grid_layout.addWidget(self.run_button,master_grid_layout.rowCount()-1,0,
                                     1, master_grid_layout.columnCount()-1)

        # Connect buttons
        self.bb_local_dir.clicked.connect(lambda: self.open_file_chooser(self.tb_local_dir, filemode=QFileDialog.FileMode.Directory, options=[QFileDialog.Option.ShowDirsOnly], dialog_text='Select a directory'))
        self.bb_swiss_timing.clicked.connect(lambda: self.open_file_chooser(self.tb_swiss_timing, filemode=QFileDialog.FileMode.Directory, options=[QFileDialog.Option.ShowDirsOnly], dialog_text='Select FSM directory'))
        self.bb_edits.clicked.connect(lambda: self.open_file_chooser(self.tb_edits, filemode=QFileDialog.FileMode.ExistingFile, dialog_text='Select a file', file_filters=['Edit list files (*.csv)']))
        self.bb_save_file.clicked.connect(lambda: self.open_file_chooser(self.tb_save_file, filemode=QFileDialog.FileMode.AnyFile, dialog_text='Select a file or enter a path', file_filters=['Save states (*.csv)']))
        
        # Connect run button
        self.run_button.clicked.connect(self.run_button_what_do)

    def receive_manual_time(self, value):
        '''
        Function to receive manual time from TimeWindow.
        '''
        self.manual_time = value
        if self.manual_time is None:
            self.output_feed.appendPlainText('No manual time chosen. Current time will be used when determining panels to upload.')
        else:
            self.output_feed.appendPlainText(f'Manual time of {self.manual_time.strftime("%Y-%m-%d %H:%M:%S")} will be used when determining panels to upload.')

    def set_manual_time(self):
        self.manual_time_window = TimeWindow()
        self.manual_time_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.manual_time_window.chosen_time.connect(self.receive_manual_time)
        self.manual_time_window.show()

    def show_about(self):
        self.about_window = AboutWindow()
        self.about_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.about_window.show()
    
    def show_help(self):
        self.about_window = HelpWindow()
        self.about_window.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.about_window.show()
    
    def run_button_what_do(self):
        if self.run_button.text() == 'Run!':
            self.run_button.setText('Stop')
            self.start_upload()
        else:
            self.worker.set_continue_state(False)
            self.run_button.setText('Stopping...')
    
    def set_ui_state(self, state:bool):
        '''
        Set the state of the main window's UI elements to either enabled (True) or disabled (False).
        '''
        self.tb_hostname.setEnabled(state)
        self.tb_port.setEnabled(state)
        self.tb_username.setEnabled(state)
        self.tb_password.setEnabled(state)
        self.tb_remote_dir.setEnabled(state)
        self.tb_local_dir.setEnabled(state)
        self.bb_local_dir.setEnabled(state)
        self.tb_swiss_timing.setEnabled(state)
        self.bb_swiss_timing.setEnabled(state)
        self.tb_edits.setEnabled(state)
        self.bb_edits.setEnabled(state)
        self.cb_movepdf.setEnabled(state)
        self.tb_save_file.setEnabled(state)
        self.bb_save_file.setEnabled(state)

    def start_upload(self):
        '''
        Start the upload loop by spawning a worker thread.
        '''
        self.output_feed.clear()
        self.set_ui_state(False)
        try:
            config_object = self.get_field_values(self.tb_hostname,
                                                self.tb_port,
                                                self.tb_username,
                                                self.tb_password,
                                                self.tb_local_dir,
                                                self.tb_remote_dir,
                                                self.tb_swiss_timing,
                                                self.tb_edits,
                                                self.cb_movepdf,
                                                self.tb_save_file)
            self.worker = Uploader()
            self.worker.set_arguments(config_object, manual_time=self.manual_time)
            self.worker.set_continue_state(True)

            self.worker_thread = QThread()
            self.worker.moveToThread(self.worker_thread)

            self.worker.output_signal.connect(self.update_output_feed)
            self.worker.finished_signal.connect(self.worker_thread.quit)
            self.worker.finished_signal.connect(lambda: self.run_button.setText('Run!'))
            self.worker.finished_signal.connect(self.worker.deleteLater)
            self.worker_thread.finished.connect(self.worker_thread.deleteLater)
            self.worker_thread.finished.connect(lambda: self.set_ui_state(True))

            self.worker_thread.started.connect(self.worker.upload)
            self.worker_thread.start()
        except Exception as e:
            self.output_feed.appendPlainText('Encountered exception when starting upload:\n')
            self.output_feed.appendPlainText(f'{e}')
            self.set_ui_state(True)

    def update_output_feed(self, message):
        self.output_feed.appendPlainText(message)

    def open_file_chooser(self, target_text_box: QLineEdit, file_filters:list[str]|None=None, options:list[QFileDialog.Option]|None=None,
                            dialog_text:str='Select a file', filemode:QFileDialog.FileMode=QFileDialog.FileMode.AnyFile):
        dialog = QFileDialog(caption=dialog_text)
        
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

    def closeEvent(self, a0):
        reply = QMessageBox.question(
            self,
            "Save config",
            "Do you want to save your configuration?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.config_write()
            a0.accept()
        else:
            a0.accept()

    def set_field_values(self,
                         field_hostname:QLineEdit, field_port:QLineEdit, field_username:QLineEdit, field_password:QLineEdit,
                         field_local_dir:QLineEdit, field_remote_dir:QLineEdit, field_swiss_timing_dir:QLineEdit,
                         field_edits:QLineEdit,
                         field_move_pdf:QCheckBox, field_save_file:QLineEdit,
                         config:fs.Configuration):
        field_hostname.setText(config.host)
        field_port.setText(config.port)
        field_username.setText(config.user)
        field_password.setText(config.password)
        field_local_dir.setText(config.local_dir)
        field_remote_dir.setText(config.remote_dir)
        field_swiss_timing_dir.setText(config.swiss_timing)
        field_edits.setText(config.replace)
        field_move_pdf.setChecked(config.move_pdf)
        field_save_file.setText(config.save_file)
    
    def get_field_values(self,
                         field_hostname:QLineEdit, field_port:QLineEdit, field_username:QLineEdit, field_password:QLineEdit,
                         field_local_dir:QLineEdit, field_remote_dir:QLineEdit, field_swiss_timing_dir:QLineEdit,
                         field_edits:QLineEdit,
                         field_move_pdf:QCheckBox, field_save_file:QLineEdit):
        config = fs.Configuration()
        config.host = field_hostname.text()
        config.port = field_port.text()
        config.user = field_username.text()
        config.password = field_password.text()
        config.local_dir = field_local_dir.text()
        config.remote_dir = field_remote_dir.text()
        config.swiss_timing = field_swiss_timing_dir.text()
        config.replace = field_edits.text()
        config.move_pdf = field_move_pdf.isChecked()
        config.save_file = field_save_file.text()

        return config
        
    def config_read(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, 'Load configuration file', '', 'Config files (*.ini);;All files (*)'
        )
        if file_path:
            config = fs.Configuration()
            try:
                config.from_ini(file_path)
                self.set_field_values(self.tb_hostname, self.tb_port, self.tb_username, self.tb_password,
                                    self.tb_local_dir, self.tb_remote_dir, self.tb_swiss_timing,
                                    self.tb_edits,
                                    self.cb_movepdf, self.tb_save_file,
                                    config)
            except Exception as e:
                message = QMessageBox()
                message.setText(f'Error encountered when loading:\n---\n{e}\n---')
                message.exec()
    
    def config_write(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, 'Load configuration file', '', 'Config files (*.ini);;All files (*)'
        )
        if file_path:
            try:
                config = self.get_field_values(self.tb_hostname, self.tb_port, self.tb_username, self.tb_password,
                                    self.tb_local_dir, self.tb_remote_dir, self.tb_swiss_timing,
                                    self.tb_edits,
                                    self.cb_movepdf, self.tb_save_file)
                config.to_ini(file_path)
            except Exception as e:
                message = QMessageBox()
                message.setText(f'Error encountered when saving:\n---\n{e}\n---')
                message.exec()

def main():
    app = QApplication(sys.argv)
    svg_icon = QIcon(os.path.abspath(os.path.join(os.path.dirname(__file__),'icon.svg')))
    app.setWindowIcon(svg_icon)
    app.setStyle('Fusion')
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()