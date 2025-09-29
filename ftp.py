# FSM Web Uploader - an FTP program for uploading FS Manager websites via FTP
# Copyright (C) 2025  Robert Hayes

import ftplib
import socket
import logging
import io

LOGGER = logging.getLogger(__name__)


class FtpConnection:
    def __init__(
        self, host: str, port: int, username: str, password: str, allow_insecure: bool
    ):
        self.connection: ftplib.FTP | ftplib.FTP_TLS = None
        try:
            connection = ftplib.FTP_TLS(
                host=f"{host}:{port}", user=username, passwd=password
            )
            connection.prot_p()
            self.connection = connection
        except socket.gaierror:
            connection = ftplib.FTP_TLS(host=host, user=username, passwd=password)
            connection.prot_p()
            self.connection = connection
        except Exception as e:
            LOGGER.error(f"Secure connection failed with following error: {e}")
            if allow_insecure is True:
                try:
                    connection = ftplib.FTP(host=host, user=username, passwd=password)
                    self.connection = connection
                except Exception as e:
                    LOGGER.critical(
                        f"Failed to establish FTP connection with following error: {e}"
                    )
                    raise ConnectionError("FTP connection could not be established.")
            else:
                raise ConnectionError("Secure connection could not be established.")

    def get_welcome(self):
        return self.connection.getwelcome()

    def keepalive(self):
        try:
            new_file = io.BytesIO()
            new_file.write(b".")
            new_file.seek(0)
            self.connection.storbinary("STOR .keep", new_file)
            LOGGER.info(f"Sent keepalive signal")
            new_file.close()
        except ftplib.all_errors as e:
            LOGGER.critical(f"Keepalive signal failed with following error: {e}")
            raise ConnectionError("Keepalive failed.")

    def set_working_directory(self, remote_directory: str):
        try:
            self.connection.cwd(remote_directory)
            LOGGER.info(f"Set working directory to {remote_directory}")
        except ftplib.all_errors as e:
            LOGGER.critical(
                f"Failed to set working directory with following error: {e}",
                exc_info=False,
            )
            raise ConnectionError(f"Failed to set working directory.")

    def upload(self, filename: str, file_object: io.BytesIO):
        try:
            self.connection.storbinary(f"STOR {filename}", file_object)
            LOGGER.info(f"Uploaded {filename} to remote.")
        except ftplib.all_errors as e:
            LOGGER.error(
                f"Failed to upload {filename} to remote with following error: {e}",
                exc_info=False,
            )
            raise ConnectionError(f"Failed to upload {filename}.")

    def close(self):
        try:
            self.connection.quit()
        except Exception as e:
            LOGGER.error(
                f"Failed to terminate connection to remote with following error: {e}",
                exc_info=False,
            )
            raise Exception("Failed to terminate connection.")
