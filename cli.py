from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import os
import argparse
import fs_uploader as fs

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('CONFIG',help='Configuration file following template example.')
    parser.add_argument('--dry-run','-d',action='store_true',help='Print config and exit without connecting.')
    parser.add_argument('--keepalive','-k',help='Time in seconds to wait between sending keepalive signals to the FTP server. Defaults to 780 (13 minutes).',default=780)
    parser.add_argument('--sleep-interval','-s',help='Time in seconds to wait between update cycles. Defaults to 5.',default=5)
    parser.add_argument('--time','-t',help='Set a manual time to check segments against. Must be set in "YYYY-MM-DD HH:MM:SS" format.')
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

    keepalive_interval = int(args.keepalive)
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

    ftp = fs.ftp_connect(config.host, config.user, config.password, config.remote_dir, config.port)

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
            print('No save file found at specified address. Uploading all files and continuing.')
            filetable_current = pd.DataFrame({'filepaths':'',
                                              'hashes':''}, index = [0])
    
    ## Main loop
    filetable_for_disk = fs.update_ftp_server(ftp, filetable_current, config,
                                           replacements, segments,
                                           manual_time, keepalive_interval, sleep_interval)
    
    ftp.quit()
    print('Connection closed.')
    if config.save_file is not None:
        filetable_for_disk.to_csv(os.path.abspath(os.path.normpath(config.save_file)), index=False)
        print(f'Wrote current filetable status to "{os.path.abspath(os.path.normpath(config.save_file))}".')
    exit(0)

if __name__ == "__main__":
    main()