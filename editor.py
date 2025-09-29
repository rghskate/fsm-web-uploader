# FSM Web Uploader - an FTP program for uploading FS Manager websites via FTP
# Copyright (C) 2025  Robert Hayes

from bs4 import BeautifulSoup
from PySide6.QtCore import QDateTime
import os
import hashlib


TARGET_PDFS = ("JudgesDetailsperSkater.pdf",)


def hash_sha256(filepath: str):
    """
    Return the sha256 checksum of a given binary.
    """
    try:
        with open(filepath, "rb") as f:
            file_hash = hashlib.sha256()
            while chunk := f.read(8192):
                file_hash.update(chunk)
        return file_hash.hexdigest()
    except FileNotFoundError:
        return None


def list_pdfs_to_copy(
    pdf_root_dir: str, local_website_dir: str, target_pdfs: list[str]
) -> list[str]:
    """
    Scans the FS Manager directory for PDFs of the target type, comparing them against PDFs already in the
    local website directory, listing only missing or updated PDFs.
    """
    file_paths = []
    for root, _, files in os.walk(pdf_root_dir):
        for file in files:
            abs_path = os.path.abspath(os.path.join(root, file))
            file_paths.append(abs_path)

    fsm_pdf_dict = dict()
    pdfs_in_fsm_dir = [
        pdf
        for pdf in file_paths
        if any(target_file in pdf for target_file in target_pdfs)
    ]
    for pdf in pdfs_in_fsm_dir:
        fsm_pdf_dict[os.path.basename(pdf)] = pdf

    web_pdf_dict = dict()
    pdfs_in_web_dir = [
        pdf
        for pdf in os.listdir(local_website_dir)
        if any(target_file in pdf for target_file in target_pdfs)
    ]
    for pdf in pdfs_in_web_dir:
        web_pdf_dict[pdf] = os.path.join(local_website_dir, pdf)

    pdfs_to_copy = []

    for basename, full_path in fsm_pdf_dict.items():
        if web_pdf_dict.get(basename) is None:
            pdfs_to_copy.append(full_path)
        else:
            web_dir_pdf_hash = hash_sha256(web_pdf_dict[basename])
            fsm_dir_pdf_hash = hash_sha256(full_path)
            if web_dir_pdf_hash != fsm_dir_pdf_hash:
                pdfs_to_copy.append(full_path)

    return pdfs_to_copy


def create_hash_dict(folder_path: str) -> dict[str, str]:
    """
    Documents the state of the folder, creating a dictionary of filepaths and sha256 checksums.
    """
    hash_dict = dict()
    for path in os.listdir(folder_path):
        abs_path = os.path.join(folder_path, path)
        hash_dict[abs_path] = hash_sha256(abs_path)

    return hash_dict


def trim_hash_dict(
    hash_dict: dict[str, str],
    segment_table: dict[str, QDateTime],
    check_time: QDateTime,
):
    """
    Takes a current folder snapshot and removes judges segments that have not yet been uploaded.
    """
    segments_in_the_future = []
    dirname = os.path.dirname(list(hash_dict.keys())[0])

    for panel, start_time in segment_table.items():
        if check_time.toSecsSinceEpoch() < start_time.toSecsSinceEpoch():
            segments_in_the_future.append(panel)

    for panel in segments_in_the_future:
        hash_dict.pop(os.path.join(dirname, panel), None)

    return hash_dict


def list_files_to_upload(folder: str, last_folder_state: dict[str, str]) -> list[str]:
    """
    Lists the files to be uploaded in a given folder, based on the previous state of the folder.
    """
    current_folder_state = create_hash_dict(folder)

    files_to_upload = []
    for path, hash in current_folder_state.items():
        if last_folder_state.get(path) is None:
            files_to_upload.append(path)
        else:
            if last_folder_state.get(path) != hash:
                files_to_upload.append(path)

    return files_to_upload


def create_panel_dict(
    index_page_html: str,
    parser: str = "lxml",
    tag_name: str = "table",
    attributes: dict = {"width": "70%"},
    target_table_index: int = 0,
) -> dict[str, QDateTime]:
    """
    Constructs a dictionary of panel pages (those ending OF.htm) and the corresponding start times of their segments.
    """
    soup = BeautifulSoup(index_page_html, features=parser)
    category_table = soup.find_all(tag_name, attributes)[target_table_index]
    rows: list = category_table.find_all("tr")
    rows.pop(0)

    segments = []
    date = None
    for row in rows:
        cells = row.find_all("td")
        if "TabHeadWhite" in f"{row}" and "<th>" not in f"{row}":
            date = cells[0].text.strip()
        elif len(cells) > 0:
            time = cells[1].text.strip()
            link = cells[3].find_all("a", href=True)[0].get("href")
            date_obj = QDateTime.fromString(f"{date} {time}", "dd.MM.yyyy h:mm:ss")
            segments.append((date_obj, link))

    seg_dict = dict()
    for datetime_obj, filename in segments:
        judges_filename = filename.replace(".htm", "OF.htm")
        seg_dict[judges_filename] = datetime_obj

    return seg_dict
