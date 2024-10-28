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

class Configuration:
    def __init__(self) -> None:
        self.host = None
        self.port = None
        self.user = None
        self.password = None
        self.remote_dir = None
        self.local_dir = None
        self.swiss_timing = None
        self.replace = None
        # self.comp_name = None
        # self.comp_start = None
        # self.comp_end = None
        self.move_pdf = None

    def from_ini(self,config_filepath) -> None:
        config_obj = configparser.RawConfigParser()
        config_obj.read(config_filepath)

        self.host = config_obj.get('FTP','Hostname')
        self.port = config_obj.get('FTP','Port')
        self.user = config_obj.get('FTP','Username')
        self.password = config_obj.get('FTP','Password')

        self.remote_dir = config_obj.get('Directories','Remote')
        
        self.local_dir = os.path.abspath(os.path.normpath(config_obj.get('Directories','Local')))

        try:
            self.replace = os.path.abspath(os.path.normpath(config_obj.get('Edits','ReplacementList')))
            if self.replace == "":
                self.replace = None
        except configparser.NoOptionError:
            self.replace = None
        
        try:
            swiss_timing = config_obj.get('Directories','SwissTiming')
            if swiss_timing == "":
                self.swiss_timing = r'C:\SwissTiming\OVR\FSManager'
        except configparser.NoOptionError:
            self.swiss_timing = r'C:\SwissTiming\OVR\FSManager'

        # try:
        #     isu = config_obj.get('Edits','ReplaceIsu')
        #     if isu == "":
        #         self.replace_isu = None
        # except configparser.NoOptionError:
        #     self.replace_isu = None

        # self.comp_name = config_obj.get('Edits','CompetitionDisplayName')
        # self.comp_start = config_obj.get('Edits','StartDate')
        # self.comp_end = config_obj.get('Edits','EndDate')

        self.move_pdf = config_obj.getboolean('Management','MovePDF')

    def __str__(self) -> str:
        return f'''Current config:

--- FTP ---
Hostname: {self.host}
Port: {self.port}
Username: {self.user}
Password: {self.password}

--- Directories ---
Local directory: {self.local_dir}
Remote directory: {self.remote_dir}
Swiss Timing Directory: {self.swiss_timing}

--- Edits ---
Text replacement file: {self.replace}

--- Management ---
Move PDFs to website folder: {self.move_pdf}
'''
    
def flatten(lst):
    for item in lst:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item

def flatten_list(lst):
    return list(flatten(lst))

def copy_pdfs(swiss_timing_folder,local_dir):
    dirname = os.path.join(swiss_timing_folder,'Export',os.path.basename(local_dir),'PDF')
    file_paths = []
    for root, _, files in os.walk(dirname):
        for file in files:
            abs_path = os.path.abspath(os.path.join(root, file))
            file_paths.append(abs_path)
    pdfs = [pdf for pdf in file_paths if 'JudgesDetailsperSkater.pdf' in pdf]
    
    currently_present_pdfs = [file for file in os.listdir(local_dir) if 'JudgesDetailsperSkater.pdf' in file]

    for file in pdfs:
        if os.path.basename(file) not in currently_present_pdfs:
            overprint(f'Copying "{file}" to "{local_dir}"...')
            shutil.copyfile(os.path.normpath(file), os.path.normpath(os.path.join(local_dir,os.path.basename(file))))
    
def overprint(content):
    print(end='\x1b[2K')
    print(content,end='\r')

def ftp_connect(hostname,user,password,remote_dir,port=""):
    print(f'Connecting to FTP site {hostname}:{port} as {user}...')

    if port != "":
        port = "".join([':',port])

    try:
        ftp = FTP(f'{hostname}{port}')
    except Exception as e:
        print('Connection to remote failed with the following error:\n')
        print(e)
        print('Trying connecting without port.')
        try:
            ftp = FTP(f'{hostname}')
        except Exception as e:
            print('\nPlease review your connection settings in your environment file.')
            exit(1)
    
    try:
        ftp.login(user=user, passwd=password)
    except Exception as e:
        print('Authentication failed with the following error:\n')
        print(e)
        print('\nPlease review your connection settings in your environment file.')
        exit(1)
    
    print('Connection successful! Server returned following welcome message:\n')
    print(ftp.getwelcome())
    
    try:
        ftp.cwd(remote_dir)
    except Exception as e:
        print('Could not find directory on remote. Server returned following error:\n')
        print(e)
        print('\nPlease review your connection settings in your environment file.')
        exit(1)
    
    print('\nMonitoring local directory for changes...')
    print('\nTo close connection, press Ctrl-C.\n')

    return ftp

# def edit_header_image(filepath, start_date, end_date, comp_name):
#     with open(filepath,'r') as f:
#         data = f.read()

#     initial_data = data

#     data = data.replace('$COMP_NAME',comp_name)
#     data = data.replace('$START_DATE',start_date)
#     data = data.replace('$END_DATE',end_date)

#     if data != initial_data:
#         with open(filepath, 'w') as f:
#             f.write(data)

def replace_text(filepath:str, old_text:list[str], new_text:list[str]):
    with open(filepath,'r') as f:
        page = f.read()
    
    for i, entry in enumerate(old_text):
        page = page.replace(entry, new_text[i])

    with open(filepath, 'w') as f:
        f.write(page)

# def remove_isu(filepath, replace='GBR'):
#     flag_find = '<img src="../flags/ISU.GIF">'
#     flag_replace = f'<img src="../flags/{replace}.GIF">'
#     noc_find = 'ISU'
#     noc_replace = f'{replace}'

#     with open(filepath, 'r') as f:
#         data = f.read()
    
#     data = data.replace(flag_find, flag_replace).replace(noc_find,noc_replace)

#     with open(filepath, 'w') as f:
#         f.write(data)

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

    config = Configuration()
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
    # if config.replace_isu is not None:
    #     for page in segments.loc[:,'segment_judges_link']:
    #         remove_isu(page, replace=config.replace_isu)

    ftp = ftp_connect(config.host, config.user, config.password, config.remote_dir, config.port)

    if config.replace is not None:
        try:
            replacements = pd.read_csv(config.replace, dtype=str)
        except Exception as e:
            print('Could not open replacements file with following error:')
            print(e)
            print('Exiting...')
            exit(1)

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

                if config.replace is not None:
                    for file in local_filelist:
                        if os.path.splitext(file)[1] == '.htm':
                            replacements.fillna('',inplace=True)
                            replace_text(file,replacements['OldText'],replacements['NewText'])
                        # edit_header_image(file, config.comp_start, config.comp_end, config.comp_name)

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