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

from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import os
import argparse
import fs_uploader as fs
from ftplib import all_errors
import traceback
from threading import Thread, Event
from time import sleep

def update_loop(ftp, filetable_current:pd.DataFrame, config:fs.Configuration, replacements:pd.DataFrame, segments:pd.DataFrame, manual_time:datetime, sleep_interval:int, stop_event:Event, done_signal:Event):
    last_updated = datetime.now()
    filetable_for_disk = filetable_current
    while not stop_event.is_set():
        try:
            filetable_for_disk, last_updated = fs.return_from_generator_cli(
                fs.update_ftp_server,
                [ftp,filetable_for_disk,config,replacements,segments, last_updated, manual_time]
            )
            sleep(sleep_interval)
        except all_errors:
            ftp = fs.return_from_generator_cli(
                fs.ftp_connect,
                [config.host, config.user, config.password, config.remote_dir, config.port]
            )
        except Exception as e:
            print('Encountered unexpected exception during update with the following error message:')
            traceback.print_exception(e)
            break
    
    ftp.quit()
    print('Connection closed.')
    if config.save_file is not None:
        filetable_for_disk.to_csv(os.path.abspath(os.path.normpath(config.save_file)), index=False)
        print(f'Wrote current filetable status to "{os.path.abspath(os.path.normpath(config.save_file))}".')
    done_signal.set()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('CONFIG',help='Configuration file following template example.')
    parser.add_argument('--dry-run','-d',action='store_true',help='Print config and exit without connecting.')
    parser.add_argument('--sleep-interval','-s',help='Time in seconds to wait between update cycles. Defaults to 5.',default=5)
    parser.add_argument('--time','-t',help='Set a manual time to check segments against. Must be set in "YYYY-mm-dd HH:MM:SS" format.')
    args = parser.parse_args()

    if args.time is not None:
        manual_time = datetime.strptime(args.time,'%Y-%m-%d %H:%M:%S')
    else:
        manual_time = None

    sleep_interval = int(args.sleep_interval)

    config = fs.Configuration()
    config.from_ini(os.path.normpath(os.path.abspath(args.CONFIG)))

    if args.dry_run is True:
        print(config)
        exit(0)

    os.chdir(config.local_dir)

    try:
        with open(os.path.join(config.local_dir,'index.htm'),'r') as f:
            html_content = f.read()
    except Exception as e:
        print('Could not open index file with the following error:')
        print(e)
        exit(1)

    # Scrape web content
    if fs.verify_file_status(html_content) is False:
        print('ISU copyright notice could not be found in index.htm! Either this is the wrong folder or you have been modifying the templates extensively.\nRestore the default copyright notice to the generated site to continue.')
        exit(1)

    soup = BeautifulSoup(html_content,'lxml')

    try:
        results_table = fs.find_results_table(soup)
    except Exception as e:
        print('Failed to find timetable with following error:')
        print(e)
        exit(1)

    segments = fs.build_segment_table(results_table)

    try:
        ftp = fs.return_from_generator_cli(fs.ftp_connect, [config.host, config.user, config.password, config.remote_dir, config.port])
    except ConnectionError as e:
        exit(1)

    if config.replace is not None:
        try:
            replacements = pd.read_csv(config.replace, dtype=str)
        except Exception as e:
            print('Could not open replacements file with following error:')
            print(e)
            print('Exiting...')
            exit(1)

    # Load filetable if applicable
    if config.save_file is None:
        filetable_current = pd.DataFrame({'filepaths':'',
                                          'hashes':''}, index = [0])
    else:
        try:
            filetable_current = pd.read_csv(os.path.abspath(os.path.normpath(config.save_file)))
        except FileNotFoundError:
            print(f'No save file found at {config.save_file}. Uploading all files and continuing.')
            filetable_current = pd.DataFrame({'filepaths':'',
                                              'hashes':''}, index = [0])
    
    ## Main ftp update logic
    stop_event = Event()
    done_signal = Event()
    thread = Thread(target=update_loop, args=(ftp, filetable_current, config, replacements, segments, manual_time, sleep_interval, stop_event, done_signal))
    thread.start()

    try:
        while thread.is_alive():
            thread.join(1)
    except KeyboardInterrupt:
        print('Interrupt received - stopping transfer after this iteration completes...')
        stop_event.set()
        while not done_signal.is_set():
            sleep(sleep_interval)
        thread.join()

        print('Upload done. Exiting...')

if __name__ == "__main__":
    main()