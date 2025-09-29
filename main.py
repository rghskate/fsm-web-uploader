# FSM Web Uploader - an FTP program for uploading FS Manager websites via FTP
# Copyright (C) 2025  Robert Hayes

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

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QDialog,
    QFileDialog,
    QLineEdit,
    QMessageBox,
    QDialogButtonBox,
    QWidget,
)
from PySide6.QtCore import Signal, Slot, QDateTime, Qt, QThread, QTimer
from PySide6.QtGui import QIcon

from internals import FilesystemQueue, Configuration
import workers
import editor

import sys
import os
import json
import logging

from mainWindow import Ui_MainWindow
from timeWindow import Ui_Dialog
from helpWindow import Ui_Form as Ui_Help
from licenseWindow import Ui_Form as Ui_License


class HelpWindow(QWidget, Ui_Help):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButtonClose.clicked.connect(self.close)


class LicenseWindow(QWidget, Ui_License):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButtonClose.clicked.connect(self.close)


class TimeDialog(QDialog, Ui_Dialog):
    """
    Dialog for setting a custom upload time.
    """

    custom_time = Signal(QDateTime)
    unset_custom_time = Signal()

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.previously_chosen_time: QDateTime = QDateTime.currentDateTime()
        self.dateTimeEditCustom.setDateTime(QDateTime.currentDateTime())
        self.setModal(True)

    def init_ui(self):
        self.setupUi(self)
        self.checkBoxUseCustom.checkStateChanged.connect(
            self.use_custom_checkbox_what_do
        )
        self.checkBoxUploadAll.checkStateChanged.connect(
            self.upload_all_checkbox_what_do
        )
        self.buttonBox.button(QDialogButtonBox.StandardButton.Save).clicked.connect(
            self.save_what_do
        )

    def save_what_do(self):
        """Determine what to do when clicking save."""
        if self.checkBoxUseCustom.isChecked():
            self.custom_time.emit(self.dateTimeEditCustom.dateTime())
        else:
            self.unset_custom_time.emit()

    def use_custom_checkbox_what_do(self):
        """Determine what to do when the Use Custom Time checkbox is toggled."""
        if self.checkBoxUseCustom.isChecked():
            self.enable_custom_time()
        else:
            self.disable_custom_time()

    def upload_all_checkbox_what_do(self):
        """Determine what to do when the Upload All checkbox is toggled."""
        if self.checkBoxUploadAll.isChecked():
            self.set_upload_all()
        else:
            self.unset_upload_all()

    def enable_custom_time(self):
        """Enable the use of a custom time."""
        self.labelSetTime.setEnabled(True)
        self.dateTimeEditCustom.setEnabled(True)
        self.checkBoxUploadAll.setEnabled(True)

    def disable_custom_time(self):
        """Disable the use of a custom time."""
        self.checkBoxUploadAll.setChecked(False)
        self.labelSetTime.setEnabled(False)
        self.dateTimeEditCustom.setEnabled(False)
        self.checkBoxUploadAll.setEnabled(False)

    def set_upload_all(self):
        """Set the date to 1st Jan 3000 to ensure all segments are uploaded."""
        self.labelSetTime.setEnabled(False)
        self.dateTimeEditCustom.setEnabled(False)
        self.previously_chosen_time = self.dateTimeEditCustom.dateTime()
        self.dateTimeEditCustom.setDateTime(
            QDateTime(3000, 1, 1, 0, 0, 0)
        )  # Needs attention around 1st Jan 2998

    def unset_upload_all(self):
        """Revert date to previous selection and unlock UI."""
        self.labelSetTime.setEnabled(True)
        self.dateTimeEditCustom.setEnabled(True)
        self.dateTimeEditCustom.setDateTime(self.previously_chosen_time)


class MainWindow(QMainWindow, Ui_MainWindow):
    signal_copy_pdf = Signal(str)
    signal_upload_file = Signal(str, int)
    signal_ftp_connect = Signal()
    signal_ftp_keepalive = Signal()
    signal_write_save = Signal(QDateTime)
    signal_create_panel_dict = Signal()
    signal_initial_folder_read = Signal()

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.config_object = Configuration()
        self.transfers_completed = 0
        self.time_window = None
        self.license_window = LicenseWindow()
        self.help_window = HelpWindow()

        self.custom_upload_time: QDateTime | None = None
        self.current_dialog = None

        self.differencer_object = None
        self.differencer_thread = None
        self.ftp_watcher_object = None
        self.ftp_watcher_thread = None
        self.pdf_watcher_object = None
        self.pdf_watcher_thread = None
        self.pdf_copier_thread = None
        self.pdf_copier_object = None
        self.copy_timer = None
        self.upload_timer = None
        self.ftp_uploader_object = None
        self.ftp_uploader_thread = None
        self.stop_timer = None
        self.emergency_stop_timer = None
        self.graceful_stop = False
        self.panel_dict = None

        self.accepting_signals = False

        self.time_last_update = None
        self.time_since_last_update = None

        self.upload_queue = FilesystemQueue()
        self.copy_queue = FilesystemQueue()

        self.copy_frequency = 1000
        self.upload_frequency = 1000
        self.cool_off_period = 1000

        self.target_pdfs = editor.TARGET_PDFS

        self.init_ui()
        self.setWindowTitle("FSM Web Uploader")

    def init_ui(self):
        self.setupUi(self)

        self.pushButtonBrowseEditsFile.clicked.connect(
            lambda: self.open_file_chooser(
                self.lineEditEditsFile,
                "JSON Files (*.json)",
                dialog_text="Choose an edits file",
                filemode=QFileDialog.FileMode.ExistingFile,
            )
        )
        self.pushButtonBrowseSaveFile.clicked.connect(
            lambda: self.open_file_chooser(
                self.lineEditSaveFile,
                "JSON Files (*.json)",
                dialog_text="Choose an existing save file or enter a name",
                filemode=QFileDialog.FileMode.AnyFile,
            )
        )
        self.pushButtonBrowseFSMDir.clicked.connect(
            lambda: self.open_file_chooser(
                self.lineEditFSMDir,
                dialog_text="Select the FS Manager root directory",
                filemode=QFileDialog.FileMode.Directory,
            )
        )
        self.pushButtonBrowseLocalFolder.clicked.connect(
            lambda: self.open_file_chooser(
                self.lineEditLocalFolder,
                dialog_text="Choose the export directory for your competition site",
                filemode=QFileDialog.FileMode.Directory,
            )
        )

        self.pushButtonRun.clicked.connect(self.run_button_what_do)
        self.actionLoad_configuration.triggered.connect(self.config_read)
        self.actionSave_configuration.triggered.connect(self.config_write)
        self.actionExit.triggered.connect(self.close)
        self.actionManual_upload_time.triggered.connect(self.open_time_window)
        self.actionHelp.triggered.connect(self.help_window.show)
        self.actionLicenses.triggered.connect(self.license_window.show)
        self.listViewUploadQueue.setModel(self.upload_queue.item_model)
        self.checkBoxCopyPDFs.stateChanged.connect(self.copy_pdf_checkbox_what_do)
        self.upload_queue.item_model.rowsInserted.connect(
            self.update_upload_queue_length
        )
        self.upload_queue.item_model.rowsRemoved.connect(
            self.update_upload_queue_length
        )

    def display_time_since_last_update(self):
        if self.time_last_update is None:
            self.labelLastUpdateDeltaDisplay.setText("...")
            self.labelLastUpdateDisplay.setText("...")
        elif self.time_since_last_update == 0:
            self.labelLastUpdateDisplay.setText(
                QDateTime.fromSecsSinceEpoch(self.time_last_update).toString(
                    "hh:mm:ss dd-MM-yyyy"
                )
            )
            self.labelLastUpdateDeltaDisplay.setText("00:00")
        else:
            self.labelLastUpdateDisplay.setText(
                QDateTime.fromSecsSinceEpoch(self.time_last_update).toString(
                    "hh:mm:ss dd-MM-yyyy"
                )
            )
            time_delta_secs = QDateTime.currentSecsSinceEpoch() - self.time_last_update
            mins_component = time_delta_secs // 60
            secs_component = time_delta_secs % 60
            self.labelLastUpdateDeltaDisplay.setText(
                f"{mins_component:02d}:{secs_component:02d}"
            )
            if mins_component >= (self.config_object.timeout_mins - 1):
                self.signal_ftp_keepalive.emit()

    @Slot()
    def copy_pdf_checkbox_what_do(self):
        if self.checkBoxCopyPDFs.isChecked():
            self.labelFSMDir.setEnabled(True)
            self.lineEditFSMDir.setEnabled(True)
            self.pushButtonBrowseFSMDir.setEnabled(True)
        else:
            self.labelFSMDir.setEnabled(False)
            self.lineEditFSMDir.setEnabled(False)
            self.pushButtonBrowseFSMDir.setEnabled(False)

    @Slot(QDateTime)
    def set_custom_time(self, datetime: QDateTime):
        self.custom_upload_time = datetime
        self.labelCustomTimeDisplay.setText(datetime.toString(Qt.DateFormat.TextDate))

    @Slot()
    def unset_custom_time(self):
        self.custom_upload_time = None
        self.labelCustomTimeDisplay.setText("Not set (using current time)")

    def open_time_window(self):
        if self.time_window is None:
            self.time_window = TimeDialog()
            self.time_window.custom_time.connect(self.set_custom_time)
            self.time_window.unset_custom_time.connect(self.unset_custom_time)
            self.time_window.exec()
        else:
            self.time_window.destroy(True, True)
            self.time_window = None
            self.open_time_window()

    def config_read(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Load configuration file", "", "Config files (*.json);;All files (*)"
        )
        if file_path:
            try:
                self.config_object.from_json(file_path)
                self.set_configuration()
            except Exception as e:
                self.logger.error(f"Failed to save state with following error:{e}")
                self.create_error_dialog(e, "Error encountered when saving state")

    def config_write(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save configuration file", "", "Config files (*.json);;All files (*)"
        )
        if file_path:
            try:
                if not file_path.endswith(".json"):
                    file_path = file_path + ".json"
                self.collect_configuration()
                with open(file_path, "w") as f:
                    json.dump(self.config_object.to_dict(), f, indent=1)
            except Exception as e:
                self.logger.error(f"Error when loading state: {e}")
                self.create_error_dialog(e, "Error encountered when loading state")

    def create_error_dialog(
        self,
        error_message: Exception,
        error_preamble: str,
    ):
        if not self.current_dialog:
            self.current_dialog = QMessageBox(self)
        if not self.current_dialog.isVisible():
            self.current_dialog.setWindowTitle("Error")
            self.current_dialog.setText(f"{error_preamble}:\n{error_message}")
            self.current_dialog.setStandardButtons(QMessageBox.StandardButton.Ok)
            self.current_dialog.setIcon(QMessageBox.Icon.Critical)
            self.current_dialog.setModal(True)
            self.current_dialog.exec()

    def run_button_what_do(self):
        if self.pushButtonRun.text() == "Run!":
            self.run_uploader_phase_one()
        elif self.pushButtonRun.text() == "Stop":
            self.stop_uploader_phase_one()

    @Slot()
    def update_upload_queue_length(self):
        current_uploads, future_uploads = self.upload_queue.get_queue_size()
        if current_uploads == 0 and future_uploads == 0:
            self.groupBoxUploadQueue.setTitle(f"Upload Queue")
        else:
            self.groupBoxUploadQueue.setTitle(
                f"Upload Queue ({current_uploads},{future_uploads})"
            )

    # Business Logic
    def get_check_time(self):
        if self.custom_upload_time is not None:
            return self.custom_upload_time
        else:
            return QDateTime.currentDateTime()

    def start_differencer(self):
        if self.differencer_object is None:
            self.differencer_thread = QThread()
            if self.config_object.copy_pdfs is True:
                pdf_dir = os.path.join(
                    self.config_object.fsm_dir,
                    "Export",
                    os.path.basename(self.config_object.local_website_dir),
                    "PDF",
                )
            else:
                pdf_dir = None
            self.differencer_object = workers.Differencer(
                self.config_object.local_website_dir,
                self.config_object.save_filepath,
                pdf_dir,
            )
            self.differencer_object.pdf_to_copy.connect(self.receive_copy_signal)
            self.differencer_object.file_to_upload.connect(self.receive_upload_signal)
            self.differencer_object.save_written.connect(self.reenable_run)
            self.differencer_object.fail_signal.connect(self.emergency_stop_uploader)
            self.differencer_object.send_panel_dictionary.connect(
                self.receive_panel_dict
            )
            self.differencer_object.moveToThread(self.differencer_thread)

            self.signal_create_panel_dict.connect(
                self.differencer_object.create_panel_dict
            )
            self.signal_write_save.connect(self.differencer_object.create_save_file)
            self.signal_initial_folder_read.connect(self.differencer_object.run_checks)

            self.differencer_thread.start()

    @Slot(dict)
    def receive_panel_dict(self, panels: dict[str, QDateTime]):
        self.panel_dict = panels
        self.run_uploader_phase_two()

    def stop_differencer(self):
        if self.differencer_thread:
            self.differencer_thread.quit()
            self.differencer_thread.wait()
            self.differencer_thread.deleteLater()
            self.differencer_object.deleteLater()
            self.differencer_object = None
            self.differencer_thread = None

    def start_ftp_filesystem_watcher(self):
        if self.ftp_watcher_object is None:
            self.ftp_watcher_thread = QThread()
            self.ftp_watcher_object = workers.WatcherObject(
                self.config_object.local_website_dir, recursive=False
            )
            self.ftp_watcher_object.file_created.connect(self.receive_upload_signal)
            self.ftp_watcher_object.file_modified.connect(self.receive_upload_signal)

            self.ftp_watcher_object.moveToThread(self.ftp_watcher_thread)
            self.ftp_watcher_thread.start()
        else:
            self.ftp_watcher_thread.quit()
            self.ftp_watcher_thread.wait()
            self.ftp_watcher_object.deleteLater()
            self.ftp_watcher_thread.deleteLater()
            self.ftp_watcher_object = None
            self.start_ftp_filesystem_watcher()

    def stop_ftp_filesystem_watcher(self):
        if self.ftp_watcher_object and self.ftp_watcher_thread:
            self.ftp_watcher_thread.quit()
            self.ftp_watcher_thread.wait()
            self.ftp_watcher_object.deleteLater()
            self.ftp_watcher_thread.deleteLater()
            self.ftp_watcher_object = None
            self.ftp_watcher_thread = None

    def start_pdf_filesystem_watcher(self):
        if self.pdf_watcher_object is None and self.pdf_watcher_thread is None:
            self.pdf_watcher_thread = QThread()
            self.pdf_watcher_object = workers.WatcherObject(
                os.path.join(
                    self.config_object.fsm_dir,
                    "Export",
                    os.path.basename(self.config_object.local_website_dir),
                ),
                recursive=True,
                signal_mask=self.target_pdfs,
            )
            self.pdf_watcher_object.file_created.connect(self.receive_copy_signal)
            self.pdf_watcher_object.file_modified.connect(self.receive_copy_signal)

            self.pdf_watcher_object.moveToThread(self.pdf_watcher_thread)
            self.pdf_watcher_thread.start()
        else:
            self.stop_pdf_filesystem_watcher()
            self.start_pdf_filesystem_watcher()

    def stop_pdf_filesystem_watcher(self):
        if self.pdf_watcher_object and self.pdf_watcher_thread:
            self.pdf_watcher_thread.quit()
            self.pdf_watcher_thread.wait()
            self.pdf_watcher_object.deleteLater()
            self.pdf_watcher_thread.deleteLater()
            self.pdf_watcher_object = None
            self.pdf_watcher_thread = None

    def start_pdf_copier(self):
        if not self.pdf_copier_thread and not self.pdf_copier_object:
            self.pdf_copier_thread = QThread()
            self.pdf_copier_object = workers.PdfCopier(
                self.config_object.local_website_dir
            )

            self.signal_copy_pdf.connect(self.pdf_copier_object.copy_pdf)
            self.pdf_copier_object.copy_successful.connect(self.remove_copy_queue_entry)

            self.pdf_copier_object.moveToThread(self.pdf_copier_thread)
            self.pdf_copier_thread.start()

            self.copy_timer = QTimer(self)
            self.copy_timer.timeout.connect(self.dispatch_copy_signals)
            self.copy_timer.start(self.copy_frequency)

    def stop_pdf_copier(self):
        if self.pdf_copier_thread:
            self.copy_timer.stop()
            self.pdf_copier_thread.quit()
            self.pdf_copier_thread.wait()
            self.copy_timer.deleteLater()
            self.pdf_copier_object.deleteLater()
            self.pdf_copier_thread.deleteLater()
            self.copy_timer = None
            self.pdf_copier_thread = None
            self.pdf_copier_object = None

    def append_filesystem_signal(
        self,
        item_model: FilesystemQueue,
        filepath: str,
        signal_time: QDateTime,
        operation: str,
    ):
        signal_time_ms = signal_time.currentMSecsSinceEpoch()
        item_model.add_entry(filepath, signal_time_ms, operation)

    @Slot(str, QDateTime, str)
    def receive_copy_signal(
        self, filepath: str, signal_time: QDateTime, operation: str
    ):
        if self.accepting_signals is True:
            self.append_filesystem_signal(
                self.copy_queue, filepath, signal_time, operation
            )

    @Slot()
    def dispatch_copy_signals(self):
        for value in self.copy_queue.event_queue.values():
            time_now = QDateTime.currentMSecsSinceEpoch()
            if ((time_now - value.time_added) >= self.cool_off_period) and (
                value.in_progress is False
            ):
                value.set_in_progress()
                self.signal_copy_pdf.emit(value.full_path)

    @Slot(str)
    def remove_copy_queue_entry(self, filepath: str):
        self.copy_queue.remove_entry(filepath)

    def start_ftp_uploader(self):
        self.ftp_uploader_object = workers.FtpUploader(
            self.config_object.hostname,
            self.config_object.port,
            self.config_object.username,
            self.config_object.password,
            self.config_object.remote_dir,
            self.config_object.edits_dict,
            False,
        )
        self.signal_ftp_connect.connect(
            self.ftp_uploader_object.initiate_ftp_connection
        )
        self.ftp_uploader_object.connection_successful_signal.connect(
            self.enable_stop_uploader
        )
        self.ftp_uploader_object.give_up_signal.connect(self.emergency_stop_uploader)
        self.ftp_uploader_object.upload_successful.connect(
            self.remove_upload_queue_entry
        )
        self.signal_ftp_keepalive.connect(
            self.ftp_uploader_object.send_keepalive_signal
        )
        self.ftp_uploader_object.keepalive_successful.connect(
            self.receive_successful_keepalive
        )
        self.signal_upload_file.connect(self.ftp_uploader_object.upload_file)

        self.ftp_uploader_thread = QThread()
        self.ftp_uploader_thread.finished.connect(self.ftp_uploader_object.stop)
        self.ftp_uploader_object.moveToThread(self.ftp_uploader_thread)
        self.ftp_uploader_thread.start()
        self.signal_ftp_connect.emit()

        self.upload_timer = QTimer(self)
        self.upload_timer.timeout.connect(self.dispatch_upload_signals)
        self.upload_timer.start(self.upload_frequency)

    def stop_ftp_uploader(self):
        if self.ftp_uploader_thread:
            self.upload_timer.stop()
            self.ftp_uploader_thread.quit()
            self.ftp_uploader_thread.wait()

            self.ftp_uploader_thread.deleteLater()
            self.ftp_uploader_object.deleteLater()
            self.upload_timer.deleteLater()

            self.upload_timer = None
            self.ftp_uploader_object = None
            self.ftp_uploader_thread = None

    @Slot(str, QDateTime, str)
    def receive_upload_signal(
        self, filepath: str, signal_time: QDateTime, operation: str
    ):
        if self.accepting_signals is True:
            self.append_filesystem_signal(
                self.upload_queue, filepath, signal_time, operation
            )

    @Slot()
    def receive_successful_keepalive(self):
        self.time_last_update = QDateTime.currentSecsSinceEpoch()
        self.display_time_since_last_update()
        self.labelConnectionStatusDisplay.setText("Connected")

    @Slot()
    def dispatch_upload_signals(self):
        for value in self.upload_queue.event_queue.values():
            if value.check_time is True:
                item_upload_time = self.panel_dict.get(
                    value.basename, QDateTime.currentDateTime()
                ).toMSecsSinceEpoch()
                check_time = self.get_check_time().toMSecsSinceEpoch()
            else:
                check_time = QDateTime.currentMSecsSinceEpoch()
                item_upload_time = value.time_added
            if value.in_progress is False:
                if (check_time - item_upload_time) >= self.cool_off_period:
                    value.set_in_progress()
                    value.standard_item.setText(f"📨{value.standard_item.text()}")
                    self.signal_upload_file.emit(value.full_path, 0)
                elif (check_time - item_upload_time) < 0:
                    value.set_in_progress()
                    value.standard_item.setText(f"⏳{value.standard_item.text()}")
                    value.set_future()

    @Slot(str)
    def remove_upload_queue_entry(self, filepath: str):
        self.upload_queue.remove_entry(filepath)
        self.time_last_update = QDateTime.currentSecsSinceEpoch()
        self.display_time_since_last_update()

    def test_filepaths(self):
        filepaths_to_test = {self.config_object.local_website_dir: "folder"}

        if self.config_object.edits_filepath is not None:
            filepaths_to_test[self.config_object.edits_filepath] = "file"

        if self.config_object.copy_pdfs is True:
            pdf_dir = os.path.join(
                self.config_object.fsm_dir,
                "Export",
                os.path.basename(self.config_object.local_website_dir),
                "PDF",
            )
            filepaths_to_test[pdf_dir] = "folder"

        for path, path_type in filepaths_to_test.items():
            if not os.path.exists(path):
                raise FileNotFoundError(f"Could not verify {path_type}: {path}")

    def run_uploader_phase_one(self):
        try:
            self.accepting_signals = True
            self.pushButtonRun.setEnabled(False)
            self.textBrowserServerMessages.clear()
            self.pushButtonRun.setText("Initialising...")
            self.collect_configuration()
            self.test_filepaths()

            self.upload_queue.clear()
            self.copy_queue.clear()

            self.start_differencer()
            self.signal_create_panel_dict.emit()

            self.set_action_state(False)
            self.set_config_ui_state(False)
            self.timer_display_update = QTimer(self)
            self.timer_display_update.timeout.connect(
                self.display_time_since_last_update
            )
            self.timer_display_update.start(1000)
        except FileNotFoundError as e:
            self.logger.error(
                f"Error finding specified file/directory: {e}", exc_info=False
            )
            self.pushButtonRun.setEnabled(True)
            self.pushButtonRun.setText("Run!")
            self.create_error_dialog(e, "Error finding specified file/directory")
        except Exception as e:
            self.logger.error(f"Error collecting configuration: {e}", exc_info=False)
            self.pushButtonRun.setEnabled(True)
            self.pushButtonRun.setText("Run!")
            self.create_error_dialog(
                e, "Error encountered when collecting configuration"
            )

    def run_uploader_phase_two(self):
        self.start_ftp_filesystem_watcher()
        self.pushButtonRun.setText("Connecting...")
        self.start_ftp_uploader()

        if self.config_object.copy_pdfs is True:
            self.start_pdf_copier()
            self.start_pdf_filesystem_watcher()

    @Slot(str)
    def enable_stop_uploader(self, message: str):
        self.textBrowserServerMessages.setText(message)
        self.labelConnectionStatusDisplay.setText("Connected")
        self.signal_initial_folder_read.emit()
        self.pushButtonRun.setText("Stop")
        self.pushButtonRun.setEnabled(True)

    @Slot(str)
    def emergency_stop_uploader(self, error_message: str):
        self.accepting_signals = False
        self.graceful_stop = False
        self.stop_uploader_phase_two()
        self.create_error_dialog(
            error_message,
            f"FTP upload encountered an error",
        )

    @Slot()
    def check_upload_queue(self):
        if len(self.upload_queue) == 0:
            self.stop_timer.stop()
            self.stop_timer.deleteLater()
            self.stop_timer = None

            self.emergency_stop_timer.stop()
            self.emergency_stop_timer.deleteLater()
            self.emergency_stop_timer = None

            self.stop_uploader_phase_two()
            self.graceful_stop = True

    def stop_uploader_phase_one(self):
        self.accepting_signals = False
        self.graceful_stop = True
        self.pushButtonRun.setEnabled(False)
        self.pushButtonRun.setText("Stopping...")
        self.stop_timer = QTimer(self)
        self.stop_timer.timeout.connect(self.check_upload_queue)
        self.stop_timer.start(1000)
        self.emergency_stop_timer = QTimer(self)
        self.emergency_stop_timer.timeout.connect(self.stop_uploader_phase_two)
        self.emergency_stop_timer.start(60_000)

    def stop_uploader_phase_two(self):
        if self.stop_timer:
            self.stop_timer.stop()
            self.stop_timer.deleteLater()
            self.stop_timer = None
        if self.emergency_stop_timer:
            self.emergency_stop_timer.stop()
            self.emergency_stop_timer.deleteLater()
            self.emergency_stop_timer = None

        self.pushButtonRun.setEnabled(False)
        self.pushButtonRun.setText("Stopping...")
        self.stop_ftp_filesystem_watcher()
        self.stop_ftp_uploader()

        if self.config_object.copy_pdfs is True:
            self.stop_pdf_filesystem_watcher()
            self.stop_pdf_copier()

        self.copy_queue.clear()
        self.upload_queue.clear()

        if self.timer_display_update:
            self.timer_display_update.stop()
            self.timer_display_update.deleteLater()
            self.timer_display_update = None
        self.display_time_since_last_update()

        if (self.graceful_stop == True) and (
            self.config_object.save_filepath is not None
        ):
            self.signal_write_save.emit(self.get_check_time())
        else:
            self.reenable_run()

    @Slot()
    def reenable_run(self):
        self.set_action_state(True)
        self.set_config_ui_state(True)
        self.labelConnectionStatusDisplay.setText("Disconnected")
        self.textBrowserServerMessages.clear()
        self.stop_differencer()
        self.graceful_stop = False
        self.pushButtonRun.setText("Run!")
        self.pushButtonRun.setEnabled(True)

    def set_action_state(self, enabled: bool):
        self.actionManual_upload_time.setEnabled(enabled)
        self.actionSave_configuration.setEnabled(enabled)
        self.actionLoad_configuration.setEnabled(enabled)

    def set_config_ui_state(self, enabled: bool):
        self.groupBoxDirectories.setEnabled(enabled)
        self.groupBoxEdits.setEnabled(enabled)
        self.groupBoxFtpConfig.setEnabled(enabled)

    def set_configuration(self):
        self.lineEditHostname.setText(self.config_object.hostname)
        self.spinBoxPort.setValue(self.config_object.port)
        self.lineEditUsername.setText(self.config_object.username)
        self.lineEditPassword.setText(self.config_object.password)
        self.spinBoxTimeout.setValue(self.config_object.timeout_mins)
        self.lineEditLocalFolder.setText(self.config_object.local_website_dir)
        self.lineEditRemoteDir.setText(self.config_object.remote_dir)
        self.lineEditFSMDir.setText(self.config_object.fsm_dir)
        self.lineEditEditsFile.setText(self.config_object.edits_filepath)
        self.lineEditSaveFile.setText(self.config_object.save_filepath)
        self.checkBoxCopyPDFs.setChecked(self.config_object.copy_pdfs)

    def collect_configuration(self):
        self.config_object = Configuration()
        self.config_object.from_vars(
            self.lineEditHostname.text(),
            self.spinBoxPort.value(),
            self.lineEditUsername.text(),
            self.lineEditPassword.text(),
            self.spinBoxTimeout.value(),
            self.lineEditLocalFolder.text().replace('"', ""),
            self.lineEditRemoteDir.text().replace('"', ""),
            self.lineEditFSMDir.text().replace('"', ""),
            self.lineEditEditsFile.text().replace('"', ""),
            self.lineEditSaveFile.text().replace('"', ""),
            self.checkBoxCopyPDFs.isChecked(),
        )

    def open_file_chooser(
        self,
        target_text_box: QLineEdit,
        file_filters: list[str] | None = None,
        options: list[QFileDialog.Option] | None = None,
        dialog_text: str = "Select a file",
        filemode: QFileDialog.FileMode = QFileDialog.FileMode.AnyFile,
    ):
        dialog = QFileDialog(caption=dialog_text)

        if file_filters is None:
            file_filters = []
        elif not isinstance(file_filters, list):
            file_filters = [file_filters]
        file_filters.extend(["All Files (*)"])
        file_filters = ";;".join(file_filters)
        dialog.setNameFilter(file_filters)

        if options is None:
            options = []
        options.extend([QFileDialog.Option.DontUseCustomDirectoryIcons])
        options = list(set(options))

        dialog.setFileMode(filemode)
        if len(options) > 0:
            for option in options:
                dialog.setOption(option, True)

        if dialog.exec():
            file_path = dialog.selectedFiles()
        else:
            file_path = None

        if file_path is not None:
            target_text_box.setText(os.path.normpath(file_path[0]))

    def closeEvent(self, event):
        try:
            self.stop_ftp_filesystem_watcher()
        except RuntimeError:
            self.logger.warning(
                f"Error encountered when terminating FTP filesystem watcher:",
                exc_info=True,
            )
        try:
            self.stop_pdf_filesystem_watcher()
        except RuntimeError:
            self.logger.warning(
                f"Error encountered when terminating PDF filesystem watcher:",
                exc_info=True,
            )
        try:
            self.stop_pdf_copier()
        except RuntimeError:
            self.logger.warning(
                f"Error encountered when terminating PDF copier thread:", exc_info=True
            )
        try:
            self.stop_ftp_uploader()
        except RuntimeError:
            self.logger.warning(
                f"Error encountered when terminating FTP upload thread:", exc_info=True
            )
        try:
            self.stop_differencer()
        except RuntimeError:
            self.logger.warning(
                f"Error encountered when terminating differencer thread:", exc_info=True
            )
        return super().closeEvent(event)


def main():
    log_format = "%(asctime)s:%(levelname)s:%(module)s - %(message)s"
    logging.basicConfig(
        filename=os.path.join(
            "logs",
            f"fsmwebuploader_{QDateTime.currentDateTime().toString('yyyy-MM-dd_hhmmss')}.log",
        ),
        level=logging.WARNING,
        format=log_format,
    )
    app = QApplication(sys.argv)
    if sys.platform.startswith("win32"):
        icon = QIcon(
            os.path.abspath(os.path.join(os.path.dirname(__file__), "win_icon.ico"))
        )
    else:
        icon = QIcon(
            os.path.abspath(os.path.join(os.path.dirname(__file__), "icon.svg"))
        )
    app.setWindowIcon(icon)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
