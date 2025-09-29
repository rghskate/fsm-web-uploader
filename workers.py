# FSM Web Uploader - an FTP program for uploading FS Manager websites via FTP
# Copyright (C) 2025  Robert Hayes

from PySide6.QtCore import Slot, Signal, QObject, QDateTime

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

import io
import shutil
import os
import logging
import json

import ftp
import editor

LOGGER = logging.getLogger(__name__)
EDITABLE_TEXT_EXTENSIONS = ("htm", "html", "txt")
RETRIES = 3
MEMORY_LIMIT_BYTES = 500_000_000


def replace_strings(html_string: str, replacements: dict[str, str]) -> str:
    for original, replacement in replacements.items():
        html_string = html_string.replace(original, replacement)
    return html_string


class Differencer(QObject):
    pdf_to_copy = Signal(str, QDateTime, str)
    file_to_upload = Signal(str, QDateTime, str)
    send_panel_dictionary = Signal(dict)
    save_written = Signal()
    fail_signal = Signal(str)

    def __init__(
        self,
        local_website_folder: str,
        save_filepath: str | None,
        pdf_root_folder: str | None,
    ):
        super().__init__()
        self.panel_dict = None
        self.local_website_folder = local_website_folder
        self.save_filepath = save_filepath
        if self.save_filepath is not None:
            if os.path.exists(self.save_filepath):
                with open(self.save_filepath, "r") as f:
                    self.save_state = json.load(f)
            else:
                with open(self.save_filepath, "w") as f:
                    self.save_state = dict()
                    json.dump(self.save_state, f)
        else:
            self.save_state = dict()
        self.pdf_root_folder = pdf_root_folder

    @Slot()
    def create_panel_dict(self):
        if os.path.exists(os.path.join(self.local_website_folder, "index.htm")):
            try:
                with open(
                    os.path.join(self.local_website_folder, "index.htm"), "r"
                ) as f:
                    html = f.read()
                self.panel_dict = editor.create_panel_dict(html)
                self.send_panel_dictionary.emit(self.panel_dict)
            except Exception:
                self.panel_dict = dict()
                self.send_panel_dictionary.emit(self.panel_dict)
        else:
            self.fail_signal.emit(
                "index.htm not found! Index page must be present before running uploader."
            )

    @Slot()
    def run_checks(self):
        if self.pdf_root_folder is not None:
            pdfs_to_copy = editor.list_pdfs_to_copy(
                self.pdf_root_folder, self.local_website_folder, editor.TARGET_PDFS
            )
            for pdf in pdfs_to_copy:
                self.pdf_to_copy.emit(pdf, QDateTime.currentDateTime(), "create")

        files_to_upload = editor.list_files_to_upload(
            self.local_website_folder, self.save_state
        )
        for file in files_to_upload:
            self.file_to_upload.emit(file, QDateTime.currentDateTime(), "create")

    @Slot(QDateTime)
    def create_save_file(self, check_time: QDateTime):
        if self.save_filepath is not None:
            save_file = editor.create_hash_dict(self.local_website_folder)
            save_file = editor.trim_hash_dict(save_file, self.panel_dict, check_time)
            with open(self.save_filepath, "w") as f:
                json.dump(save_file, f)
            self.save_written.emit()


class PdfCopier(QObject):
    copy_successful = Signal(str)

    def __init__(self, destination: str):
        super().__init__()
        self.destination_filepath = destination

    @Slot(str, str)
    def copy_pdf(self, source_filepath: str):
        try:
            shutil.copyfile(
                source_filepath,
                os.path.join(
                    self.destination_filepath, os.path.basename(source_filepath)
                ),
            )
            self.copy_successful.emit(source_filepath)
        except PermissionError as e:
            LOGGER.error(f"Error copying file: {e}")


class FtpUploader(QObject):
    upload_successful = Signal(str)
    upload_retry_signal = Signal(str, int)
    give_up_signal = Signal(str)
    connection_successful_signal = Signal(str)
    keepalive_successful = Signal()

    def __init__(
        self,
        host: str,
        port: str,
        username: str,
        password: str,
        remote_directory: str,
        replacement_dict: dict[str, str],
        allow_insecure: bool,
    ):
        super().__init__()
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.remote_directory = remote_directory
        self.replacement_dict = replacement_dict
        self.allow_insecure = allow_insecure
        self.upload_retry_signal.connect(self.upload_file)

    @Slot()
    def initiate_ftp_connection(self):
        try:
            self.ftp_connection = ftp.FtpConnection(
                self.host, self.port, self.username, self.password, self.allow_insecure
            )
            self.ftp_connection.set_working_directory(self.remote_directory)
            self.connection_successful_signal.emit(self.ftp_connection.get_welcome())
        except Exception as e:
            self.error_stop(e)

    @Slot()
    def send_keepalive_signal(self):
        try:
            self.ftp_connection.keepalive()
            self.keepalive_successful.emit()
        except Exception as e:
            self.error_stop(e)

    @Slot(str, int)
    def upload_file(self, source_filepath: str, retry_count: int):
        if retry_count < RETRIES:
            try:
                file_object = io.BytesIO()
                if source_filepath.endswith(EDITABLE_TEXT_EXTENSIONS):
                    with open(source_filepath, "r") as f:
                        html_string = f.read()

                    html_string = replace_strings(html_string, self.replacement_dict)

                    n_bytes = file_object.write(html_string.encode("utf-8"))
                else:
                    with open(source_filepath, "rb") as f:
                        n_bytes = file_object.write(f.read())
                LOGGER.info(
                    f"Read {os.path.basename(source_filepath)}, size {n_bytes / 1000:.1f} kb"
                )
                file_object.seek(0)
                self.ftp_connection.upload(
                    os.path.basename(source_filepath), file_object
                )
                file_object.close()
                self.upload_successful.emit(source_filepath)
            except Exception:
                self.upload_retry_signal.emit(source_filepath, retry_count + 1)
        else:
            self.error_stop(ConnectionError("Upload retry limit exceeded."))

    def error_stop(self, error_message: Exception):
        self.give_up_signal.emit(f"{error_message}")

    @Slot()
    def stop(self):
        try:
            self.ftp_connection.close()
        except Exception:
            pass


class WatcherObject(QObject):
    file_created = Signal(str, QDateTime, str)
    file_deleted = Signal(str, QDateTime, str)
    file_modified = Signal(str, QDateTime, str)
    file_moved = Signal(str, QDateTime, str)

    def __init__(
        self,
        path: str,
        recursive: bool = False,
        signal_mask: tuple = tuple(),
        parent=None,
    ):
        super().__init__(parent)
        self.target_pdfs = editor.TARGET_PDFS
        self._observer = Observer()
        self._event_handler = QWatchdog(self, signal_mask=signal_mask)
        self._observer.schedule(self._event_handler, path, recursive=recursive)
        self._observer.start()
        LOGGER.info(f"Started filesystem watcher observing {path}")

    def stop(self):
        self._observer.stop()
        self._observer.join()


class QWatchdog(FileSystemEventHandler):
    def __init__(self, watcher_object: WatcherObject, signal_mask: tuple):
        super().__init__()
        self.watcher_object = watcher_object
        self.signal_mask = signal_mask

    def test_filepath(self, filepath: str):
        is_file = os.path.isfile(filepath)
        if len(self.signal_mask) > 0:
            has_ending = filepath.endswith(self.signal_mask)
        else:
            has_ending = True

        if all([is_file, has_ending]):
            return filepath
        else:
            return None

    def on_created(self, event: FileSystemEvent):
        if self.test_filepath(event.src_path) is not None:
            self.watcher_object.file_created.emit(
                event.src_path, QDateTime.currentDateTime(), "create"
            )

    def on_deleted(self, event: FileSystemEvent):
        if self.test_filepath(event.src_path) is not None:
            self.watcher_object.file_deleted.emit(
                event.src_path, QDateTime.currentDateTime(), "delete"
            )

    def on_modified(self, event: FileSystemEvent):
        if self.test_filepath(event.src_path) is not None:
            self.watcher_object.file_modified.emit(
                event.src_path, QDateTime.currentDateTime(), "modify"
            )

    def on_moved(self, event: FileSystemEvent):
        if self.test_filepath(event.dest_path) is not None:
            self.watcher_object.file_moved.emit(
                event.dest_path, QDateTime.currentDateTime(), "move"
            )
