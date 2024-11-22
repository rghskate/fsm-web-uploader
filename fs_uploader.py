from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import os
import shutil
from ftplib import FTP, all_errors
from time import sleep
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
        self.move_pdf = None
        self.save_file = None

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
            self.swiss_timing = config_obj.get('Directories','SwissTiming')
            if self.swiss_timing == "":
                self.swiss_timing = r'C:\SwissTiming\OVR\FSManager'
        except configparser.NoOptionError:
            self.swiss_timing = r'C:\SwissTiming\OVR\FSManager'

        try:
            self.save_file = config_obj.get('Management','SaveFile')
            if self.save_file == "":
                self.save_file = None
        except configparser.NoOptionError:
            self.save_file = None

        try:
            self.move_pdf = config_obj.getboolean('Management','MovePDF')
            if self.move_pdf == "":
                self.move_pdf = False
        except (configparser.NoOptionError, ValueError):
            self.move_pdf = False

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
Save file location: {self.save_file}
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

def replace_text(filepath:str, old_text:list[str], new_text:list[str]):
    with open(filepath,'r') as f:
        page = f.read()
    
    for i, entry in enumerate(old_text):
        page = page.replace(entry, new_text[i])

    with open(filepath, 'w') as f:
        f.write(page)

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

def verify_file_status(index_page:str):
    copyright_notices = [r'&copy;',r'<a href="http://www.isu.org">International Skating Union</a>', r'All Rights Reserved.']

    if not all(substring in index_page for substring in copyright_notices):
        return False
    else:
        return True
        

def find_results_table(html_soup:BeautifulSoup, tag_name:str='table', attributes:dict={'width':'70%'}, target_table_index:int=0) -> list:
    results_table = html_soup.find_all(tag_name,attributes)[target_table_index]
    return results_table

def build_segment_table(results_table: BeautifulSoup):
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

    return segments

def update_ftp_server(ftp:FTP,filetable_current:pd.DataFrame, config:Configuration,
                      replacements:pd.DataFrame, segments:pd.DataFrame,
                      manual_time:datetime|None=None, keepalive_interval:int=5,
                      sleep_interval:int=5) -> pd.DataFrame:
    run = True
    time_last_update = datetime.now()
    while run == True:
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
                return filetable_current
            except Exception as e:
                print('Encountered unxpected exception during update with following error message:')
                print(e)
                return filetable_current