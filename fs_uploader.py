from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import os
from ftplib import FTP
from dotenv import dotenv_values
from time import sleep
import argparse
import hashlib

def overprint(content):
    print(end='\x1b[2K')
    print(content,end='\r')

def remove_isu(filepath, replace='GBR'):
    flag_find = '<img src="../flags/ISU.GIF">'
    flag_replace = f'<img src="../flags/{replace}.GIF">'
    noc_find = '<td>ISU</td>'
    noc_replace = f'<td>{replace}</td>'

    with open(filepath, 'r') as f:
        data = f.read()
    
    data = data.replace(flag_find, flag_replace).replace(noc_find,noc_replace)

    with open(filepath, 'w') as f:
        f.write(data)

def hash_sha256(filepath:str):
    try:
        with open(filepath,'rb') as f:
            file_hash = hashlib.sha256()
            while chunk := f.read(8192):
                file_hash.update(chunk)
        return file_hash.hexdigest()
    except FileNotFoundError:
        return None

def upload_updated_files(ftp:FTP, current_filetable:pd.DataFrame, old_filetable:pd.DataFrame):
    old_filetable = old_filetable.reset_index(drop=True)
    update_counter = 0
    brand_new_files = current_filetable.loc[~current_filetable['filepaths'].isin(old_filetable['filepaths']),'filepaths']
    comparable_files = current_filetable.loc[current_filetable['filepaths'].isin(old_filetable['filepaths']),:].reset_index(drop=True)

    if len(brand_new_files) > 0:
        for path in brand_new_files:
            with open(path,'rb') as file:
                ftp.storbinary(f'STOR {path}', file)
                overprint(f'Updated {path} on remote')
            update_counter += 1

    for i in range(0,len(comparable_files)):
        if comparable_files.loc[i,'hashes'] != old_filetable.loc[i,'hashes']:
            with open(comparable_files.loc[i,"filepaths"],'rb') as file:
                ftp.storbinary(f'STOR {comparable_files.loc[i,"filepaths"]}', file)
                overprint(f'Updated {comparable_files.loc[i,"filepaths"]} on remote')
            update_counter += 1
    
    return update_counter

def main():
    parser = argparse.ArgumentParser()
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
    replace_isu = env.get('REPLACE_ISU')
    keepalive_interval = 780
    local_dir = os.path.normpath(os.path.normpath(os.path.abspath(env['LOCAL_DIR'])))
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

    # Remove references to ISU from judges pages
    if replace_isu is not None:
        for page in segments.loc[:,'segment_judges_link']:
            remove_isu(page, replace='GBR')

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
    
    print('\nMonitoring local directory for changes...')
    print('\nTo close connection, press Ctrl-C.\n')

    
    filetable_current = pd.DataFrame({'filepaths':'',
                                          'hashes':''}, index = [0])
    try:
        while True:
            overprint('Checking for changes...')
            filetable_previous = filetable_current
            local_filelist = pd.Series(os.listdir('.'))

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
                    ftp.getwelcome()
                    time_last_update = datetime.now()
                else:
                    overprint(f'Time since last update = {(datetime.now()-time_last_update)}')
            else:
                overprint(f'Updated {update_counter} on last round.')
                time_last_update = datetime.now()

            sleep(sleep_interval)
    except KeyboardInterrupt:
        print("\n\nClosing...")
    
    ftp.quit()
    print(replace_isu)
    print('Connection closed.')
    exit(0)

if __name__ == "__main__":
    main()