from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import os
import shutil
from ftplib import FTP, all_errors
from time import sleep
import argparse
import hashlib
import configparser
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

    config = fs.Configuration(os.path.normpath(os.path.abspath(args.CONFIG)))

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


    copyright_notices = [r'&copy;',r'<a href="http://www.isu.org">International Skating Union</a>', r'All Rights Reserved.']

    if not all(substring in html_content for substring in copyright_notices):
        print('ISU copyright notice could not be found in index.htm! Either this is the wrong folder or you have been modifying the templates extensively.\nRestore the default copyright notice to the generated site to continue.')
        exit(1)

    soup = BeautifulSoup(html_content,'lxml')

    try:
        results_table = soup.find_all('table',{'width':'70%'})[0]
    except IndexError:
        results_table = soup.find_all('table',{'class':'MainTables'})[1]
    except Exception as e:
        print('Failed to find timetable with following error:')
        print(e)
        exit(1)

    rows:list = results_table.find_all('tr')
    rows.pop(0)

    segments = []
    date = None
    for row in rows:
        cells = row.find_all('td')
        if 'TabHeadWhite' in f'{row}' and '<th>' not in f'{row}':
            date = cells[0].text.strip()
        elif len(cells) > 0:
            time = cells[1].text.strip()
            name = cells[2].text.strip()
            link_name = cells[3].text.strip()
            link = cells[3].find_all('a',href=True)[0].get('href')

            date_obj = datetime.strptime(f'{date} {time}','%d.%m.%Y %H:%M:%S')

            segments.append([date_obj,name,link_name,link])
            
    segments = pd.DataFrame(segments,columns=['date_obj','category','segment','segment_link'])
    segments.loc[:,'segment_judges_link'] = segments.loc[:,'segment_link'].str.replace('.htm','OF.htm')

    # Remove references to ISU from judges pages
    if config.replace_isu is not None:
        for page in segments.loc[:,'segment_judges_link']:
            fs.remove_isu(page, replace=config.replace_isu)

    ftp = fs.ftp_connect(config.host, config.user, config.password, config.remote_dir, config.port)

    ## Main loop
    filetable_current = pd.DataFrame({'filepaths':'',
                                          'hashes':''}, index = [0])
    try:
        while True:
            try:
                overprint('Checking for changes...')
                filetable_previous = filetable_current
                copy_pdfs(config.swiss_timing, config.local_dir)
                local_filelist = pd.Series(os.listdir('.'))

                for file in local_filelist:
                    if os.path.splitext(file)[1] == '.htm':
                        edit_header_image(file, config.comp_start, config.comp_end, config.comp_name)

                if manual_time is not None:
                    test_time = manual_time
                else:
                    test_time = datetime.now()
                files_to_ignore = segments['segment_judges_link'][segments['date_obj'] > test_time]

                filetable_current = pd.DataFrame({'filepaths':local_filelist[~local_filelist.isin(files_to_ignore)],
                                                'hashes':local_filelist[~local_filelist.isin(files_to_ignore)].apply(hash_sha256)})

                update_counter = upload_updated_files(ftp, filetable_current, filetable_previous)

                if update_counter == 0:
                    if (datetime.now()-time_last_update).total_seconds() >= keepalive_interval:
                        overprint(f'Time since last update exceeds {int(keepalive_interval/60)} minutes. Sending keepalive signal...')
                        ftp.cwd(config.remote_dir)
                        time_last_update = datetime.now()
                    else:
                        overprint(f'Time since last update = {str(datetime.now()-time_last_update).split('.')[0]}')
                else:
                    overprint(f'Updated {update_counter} on last round.')
                    time_last_update = datetime.now()

                sleep(sleep_interval)
            except all_errors:
                ftp = ftp_connect(config.host, config.user, config.password, config.remote_dir, config.port)
    except KeyboardInterrupt:
        print("\n\nClosing...")
    
    ftp.quit()
    print('Connection closed.')
    exit(0)

if __name__ == "__main__":
    main()