from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import os
from ftplib import FTP, error_perm
from dotenv import dotenv_values
from time import sleep
import argparse

def overprint(content):
    print(end='\x1b[2K')
    print(content,end='\r')

def get_mtime_remote(ftp:FTP, remote_file:str):
    response = ftp.sendcmd(f'MDTM {remote_file}')
    mtime = response[4:]
    return datetime.strptime(mtime,"%Y%m%d%H%M%S")

def get_mtime_local(local_file:str):
    return datetime.fromtimestamp(os.path.getmtime(local_file))

def upload_newer(ftp:FTP, filename:str):
    overprint(f'Checking {filename} on remote...')
    try:
        remote_mtime = get_mtime_remote(ftp, filename)
    except error_perm:
        remote_mtime = None
    
    local_mtime = get_mtime_local(filename)

    update_status = False

    if remote_mtime is None or local_mtime > remote_mtime:
        with open(filename,'rb') as file:
            ftp.storbinary(f'STOR {filename}', file)
            overprint(f'Updated {filename} on remote')
            update_status=True
    
    return update_status

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('DIR',help='Target directory containing an FS Manager generated site. Program will throw an error if the ISU copyright notice at the bottom of the index page has been removed.')
    parser.add_argument('ENV',help='Environment file containing the following parameters: USER, PASSWORD, HOSTNAME, PORT, REMOTE_DIR')
    parser.add_argument('--sleep-interval','-s',help='Time in seconds to wait between update cycles. Defaults to 5.',default=5)
    parser.add_argument('--time','-t',help='Set a manual time to check segments against. Must be set in "YYYY-MM-DD HH:MM:SS" format.')
    args = parser.parse_args()

    if args.time is not None:
        manual_time = datetime.strptime(args.time,'%Y-%m-%d %H:%M:%S')
    else:
        manual_time = None

    sleep_interval = int(args.sleep_interval)
    env = dotenv_values(os.path.normpath(os.path.abspath(args.ENV)))
    local_dir = os.path.normpath(os.path.abspath(args.DIR))
    os.chdir(local_dir)

    try:
        with open(os.path.join(local_dir,'index.htm'),'r') as f:
            html_content = f.read()
    except Exception as e:
        print('Could not open index file with the following error:')
        print(e)
        exit(1)

    copyright_notice = r'<tr class="LastLine"><td>&copy; 2024 <a href="http://www.isu.org">International Skating Union</a>. All Rights Reserved.</td></tr>'

    if copyright_notice not in html_content:
        print('ISU copyright notice could not be found in index.htm! Either this is the wrong folder or you have been modifying the templates extensively.\nRestore the default copyright notice to the generated site to continue.')
        exit(1)

    soup = BeautifulSoup(html_content,'lxml')

    tables = soup.find_all('table',{'width':'70%'})

    rows:list = tables[0].find_all('tr')
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

    

    print(f'Connecting to FTP site {env["HOSTNAME"]} as {env["USER"]}...')

    try:
        ftp = FTP(env['HOSTNAME'])
    except Exception as e:
        print('Connection to remote failed with the following error:\n')
        print(e)
        print('\nPlease review your connection settings in your environment file.')
        exit(1)
    
    try:
        ftp.login(user=env['USER'],passwd=env['PASSWORD'])
    except Exception as e:
        print('Authentication failed with the following error:\n')
        print(e)
        print('\nPlease review your connection settings in your environment file.')
        exit(1)
    
    print('Connection successful! Server returned following welcome message:\n')
    print(ftp.getwelcome())
    
    try:
        ftp.cwd(env['REMOTE_DIR'])
    except Exception as e:
        print('Could not find directory on remote. Server returned following error:\n')
        print(e)
        print('\nPlease review your connection settings in your environment file.')
        exit(1)
    
    print('\nChecking filelist against remote.')
    print('\nTo close connection, press Ctrl-C.\n')
    
    try:
        while True:
            local_filelist = pd.Series(os.listdir('.'))
            update_counter=0
            if manual_time is not None:
                test_time = manual_time
            else:
                test_time = datetime.now()

            files_to_ignore = segments['segment_judges_link'][segments['date_obj'] > test_time]

            filelist_to_check = local_filelist[~local_filelist.isin(files_to_ignore)]

            for file in filelist_to_check:
                update_status = upload_newer(ftp, file)
                if update_status is True:
                    update_counter+=1
            
            overprint(f'Updated {update_counter} on last round. Waiting for {sleep_interval} seconds...')

            sleep(sleep_interval)
    except KeyboardInterrupt:
        print("\n\nClosing...")
    
    ftp.quit()
    exit(0)

if __name__ == "__main__":
    main()