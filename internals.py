from PySide6.QtGui import QStandardItemModel, QStandardItem
import os
import json


class QueueEntry:
    check_time_entries = ("OF.htm",)

    def __init__(self, filepath: str, add_time: int, action: str):
        self.full_path = filepath
        self.basename = os.path.basename(filepath)
        self.action = action
        self.time_added = add_time
        self.standard_item = QStandardItem(self.basename)
        self.in_progress = False
        self.future = False
        if self.full_path.endswith(self.check_time_entries):
            self.check_time = True
        else:
            self.check_time = False

    def set_in_progress(self):
        self.in_progress = True

    def set_stalled(self):
        self.in_progress = False

    def set_future(self):
        self.future = True

    def get_is_future(self):
        return self.future


class FilesystemQueue:
    def __init__(self):
        self.event_queue: dict[str, QueueEntry] = dict()
        self.item_model = QStandardItemModel()

    def __len__(self) -> tuple[int, int]:
        """
        Returns a tuple of lengths: (non-future events, future events).
        """
        return self.get_queue_size()[0]

    def get_queue_size(self):
        non_future_events = 0
        future_events = 0
        for queue_entry in self.event_queue.values():
            if queue_entry.get_is_future() is False:
                non_future_events += 1
            else:
                future_events += 1

        return (non_future_events, future_events)

    def add_entry(self, filepath: str, add_time: int, action: str):
        if self.event_queue.get(filepath) is None:
            model_entry = QueueEntry(filepath, add_time, action)
            self.event_queue[filepath] = model_entry
            self.item_model.insertRow(0, self.event_queue[filepath].standard_item)
        else:
            self.event_queue[filepath].time_added = add_time

    def remove_entry(self, filepath: str):
        if filepath in self.event_queue.keys():
            entry_to_remove = self.event_queue.pop(filepath)
            if entry_to_remove.standard_item.index().isValid():
                self.item_model.removeRow(entry_to_remove.standard_item.row())

    def clear(self):
        keys = list(self.event_queue.keys())
        for key in keys:
            self.event_queue.pop(key)
        self.item_model.clear()


class Configuration:
    """
    Class for managing the configuration state of FSM Web Uploader.
    """

    def __init__(self):
        self.hostname: str | None = None
        self.port: int | None = None
        self.username: str | None = None
        self.password: str | None = None
        self.timeout_mins: int | None = None
        self.local_website_dir: str | None = None
        self.remote_dir: str | None = None
        self.fsm_dir: str | None = None
        self.edits_filepath: str | None = None
        self.save_filepath: str | None = None
        self.copy_pdfs: bool | None = None

        self.edits_dict: dict[str, str] = dict()

        self.key_hostname: str = "hostname"
        self.key_port: str = "port"
        self.key_username: str = "username"
        self.key_password: str = "password"
        self.key_timeout_mins: str = "timeout"
        self.key_local_website_dir: str = "local_website_directory"
        self.key_remote_dir: str = "remote_directory"
        self.key_fsm_dir: str = "fsm_directory"
        self.key_edits_filepath: str = "edits_file"
        self.key_save_filepath: str = "save_file"
        self.key_copy_pdfs: str = "copy_pdfs"

    def __str__(self):
        return "\n".join(
            [
                f"Hostname: {self.hostname}"
                f"Port: {self.port}"
                f"Username: {self.username}"
                f"Password: {self.password}"
                f"Timeout: {self.timeout_mins} minutes"
                f"Local website folder: {self.local_website_dir}"
                f"FTP remote directory: {self.remote_dir}"
                f"FS Manager root directory: {self.fsm_dir}"
                f"Edits file: {self.edits_filepath}"
                f"Save state file: {self.save_filepath}"
                f"Copy PDFs? {self.copy_pdfs}"
            ]
        )

    def from_vars(
        self,
        hostname: str,
        port: int,
        username: str,
        password: str,
        timeout_mins: int,
        local_website_dir: str,
        remote_dir: str,
        fsm_dir: str,
        edits_filepath: str,
        save_filepath: str,
        copy_pdfs: bool,
    ):
        """
        Set properties of a `Configuration` object from in memory variables.
        """
        if "" in [hostname, local_website_dir, remote_dir]:
            raise ValueError(
                "You must explicitly define the following:\n"
                "local website directory, remote directory, hostname"
            )
        self.hostname = str(hostname)
        self.port = int(port)
        self.username = str(username)
        self.password = str(password)
        self.timeout_mins = int(timeout_mins)
        self.local_website_dir = os.path.abspath(str(local_website_dir))
        self.remote_dir = str(remote_dir)

        if fsm_dir in ["", None]:
            self.fsm_dir = None
        else:
            self.fsm_dir = os.path.abspath(str(fsm_dir))

        if edits_filepath in ["", None]:
            self.edits_filepath = None
            self.edits_dict = dict()
        else:
            self.edits_filepath = os.path.abspath(str(edits_filepath))
            with open(self.edits_filepath, "r") as f:
                self.edits_dict = json.load(f)

        if save_filepath in ["", None]:
            self.save_filepath = None
        else:
            self.save_filepath = os.path.abspath(str(save_filepath))

        self.copy_pdfs = bool(copy_pdfs)

    def from_json(self, json_filepath: str):
        """
        Set properties of `Configuration` object from a JSON file.

        Wrapper for `from_vars` method that loads a JSON file containing a saved config object and passes the
        values to the `from_vars` call.
        """
        with open(json_filepath, "r") as f:
            config_file = json.load(f)
        self.from_vars(
            config_file[self.key_hostname],
            config_file[self.key_port],
            config_file[self.key_username],
            config_file[self.key_password],
            config_file[self.key_timeout_mins],
            config_file[self.key_local_website_dir],
            config_file[self.key_remote_dir],
            config_file[self.key_fsm_dir],
            config_file[self.key_edits_filepath],
            config_file[self.key_save_filepath],
            config_file[self.key_copy_pdfs],
        )

    def to_dict(self):
        """
        Translates the `Configuration` object to a dictionary. Used for exporting to a JSON.
        """
        return {
            self.key_hostname: self.hostname,
            self.key_port: self.port,
            self.key_username: self.username,
            self.key_password: self.password,
            self.key_timeout_mins: self.timeout_mins,
            self.key_local_website_dir: self.local_website_dir,
            self.key_remote_dir: self.remote_dir,
            self.key_fsm_dir: self.fsm_dir,
            self.key_edits_filepath: self.edits_filepath,
            self.key_save_filepath: self.save_filepath,
            self.key_copy_pdfs: self.copy_pdfs,
        }
